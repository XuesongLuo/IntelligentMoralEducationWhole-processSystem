from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from datetime import datetime

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.auth_user import AuthUser
from app.models.student_user import StudentUser
from app.models.teacher_user import TeacherUser
from app.models.student_roster import StudentRoster
from app.models.teacher_invite import TeacherInvite
from app.schemas.common import ResponseModel
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserInfo,
    StudentRegisterRequest,
    TeacherRegisterRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def build_user_info(user: AuthUser) -> dict:
    student_no = user.student_profile.student_no if user.student_profile else None
    teacher_no = user.teacher_profile.teacher_no if user.teacher_profile else None

    return {
        "id": user.id,
        "real_name": user.real_name,
        "role": user.role,
        "student_no": student_no,
        "teacher_no": teacher_no,
        "phone": user.phone,
    }


# 登录
@router.post("/login", response_model=ResponseModel)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(AuthUser)
        .outerjoin(StudentUser, StudentUser.auth_user_id == AuthUser.id)
        .outerjoin(TeacherUser, TeacherUser.auth_user_id == AuthUser.id)
        .filter(
            or_(
                AuthUser.phone == payload.account,
                StudentUser.student_no == payload.account,
                TeacherUser.teacher_no == payload.account,
            )
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    token = create_access_token(subject=str(user.id))

    return ResponseModel(
        data={
            "token": token,
            "token_type": "bearer",
            "user_info": build_user_info(user),
        }
    )

# 学生注册
@router.post("/register/student", response_model=ResponseModel)
def register_student(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    # 1. 是否已注册
    phone_exists = db.query(AuthUser).filter(AuthUser.phone == payload.phone).first()
    student_exists = db.query(StudentUser).filter(StudentUser.student_no == payload.student_no).first()
    if phone_exists or student_exists:
        raise HTTPException(status_code=400, detail="学号或手机号已注册")
    
    # 2. 名单库强校验：姓名 + 学号
    roster = db.query(StudentRoster).filter(
        StudentRoster.student_no == payload.student_no,
        StudentRoster.real_name == payload.real_name,
        StudentRoster.is_enabled == True
    ).first()
    if not roster:
        raise HTTPException(status_code=400, detail="姓名与学号不匹配，不允许注册")

    # 3. 创建用户
    auth_user = AuthUser(
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        real_name=payload.real_name,
        role="student",
        is_active=True,
    )
    db.add(auth_user)
    db.flush()

    student_user = StudentUser(
        auth_user_id=auth_user.id,
        student_no=payload.student_no,
    )
    db.add(student_user)
    db.commit()
    db.refresh(auth_user)

    # 4. 直接签发 token
    token = create_access_token(subject=str(auth_user.id))
    return ResponseModel(
        data={
            "token": token,
            "token_type": "bearer",
            "user_info": {
                "id": auth_user.id,
                "real_name": auth_user.real_name,
                "role": auth_user.role,
                "student_no": student_user.student_no,
                "teacher_no": None,
                "phone": auth_user.phone,
            }
        },
        message="学生注册成功"
    )

# 老师注册
@router.post("/register/teacher", response_model=ResponseModel)
def register_teacher(payload: TeacherRegisterRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    if payload.invite_code != settings.TEACHER_INVITE_CODE:
        raise HTTPException(status_code=400, detail="教师邀请码错误")
    """
    invite = db.query(TeacherInvite).filter(
        TeacherInvite.invite_code == payload.invite_code
    ).first()

    if not invite:
        raise HTTPException(status_code=400, detail="教师邀请码不存在")

    if invite.is_used:
        raise HTTPException(status_code=400, detail="教师邀请码已被使用")

    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="教师邀请码已过期")
    """
    phone_exists = db.query(AuthUser).filter(AuthUser.phone == payload.phone).first()
    teacher_exists = db.query(TeacherUser).filter(TeacherUser.teacher_no == payload.teacher_no).first()
    if phone_exists or teacher_exists:
        raise HTTPException(status_code=400, detail="工号或手机号已注册")

    auth_user = AuthUser(
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        real_name=payload.real_name,
        role="teacher",
        is_active=True,
    )
    db.add(auth_user)
    db.flush()
    # 把邀请码标记为已使用
    """
    invite.is_used = True
    invite.used_by_user_id = user.id
    """
    teacher_user = TeacherUser(
        auth_user_id=auth_user.id,
        teacher_no=payload.teacher_no,
        teacher_invite_verified=True,
    )
    db.add(teacher_user)
    db.commit()
    db.refresh(auth_user)

    token = create_access_token(subject=str(auth_user.id))
    return ResponseModel(
        data={
            "token": token,
            "token_type": "bearer",
            "user_info": {
                "id": auth_user.id,
                "real_name": auth_user.real_name,
                "role": auth_user.role,
                "student_no": None,
                "teacher_no": teacher_user.teacher_no,
                "phone": auth_user.phone,
            }
        },
        message="老师注册成功"
    )



@router.get("/me", response_model=ResponseModel)
def me(current_user: AuthUser = Depends(get_current_user)):
    return ResponseModel(data=build_user_info(current_user))
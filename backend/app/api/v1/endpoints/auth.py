from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from datetime import datetime

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
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

# 登录
@router.post("/login", response_model=ResponseModel)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            or_(
                User.student_no == payload.account,
                User.teacher_no == payload.account,
                User.phone == payload.account,
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

    data = LoginResponse(
        token=token,
        user_info=UserInfo(
            id=user.id,
            real_name=user.real_name,
            role=user.role,
            student_no=user.student_no,
            teacher_no=user.teacher_no,
            phone=user.phone,
        ),
    )

    return ResponseModel(data=data)

# 学生注册
@router.post("/register/student", response_model=ResponseModel)
def register_student(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    # 1. 是否已注册
    existed = db.query(User).filter(
        or_(
            User.student_no == payload.student_no,
            User.phone == payload.phone
        )
    ).first()
    if existed:
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
    user = User(
        student_no=payload.student_no,
        teacher_no=None,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        real_name=payload.real_name,
        role="student",
        teacher_invite_verified=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 4. 直接签发 token
    token = create_access_token(subject=str(user.id))
    return ResponseModel(
        data={
            "token": token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "real_name": user.real_name,
                "role": user.role,
                "student_no": user.student_no,
                "teacher_no": user.teacher_no,
                "phone": user.phone,
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
    existed = db.query(User).filter(
        or_(
            User.teacher_no == payload.teacher_no,
            User.phone == payload.phone
        )
    ).first()
    if existed:
        raise HTTPException(status_code=400, detail="工号或手机号已注册")

    user = User(
        student_no=None,
        teacher_no=payload.teacher_no,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        real_name=payload.real_name,
        role="teacher",
        teacher_invite_verified=True,
        is_active=True
    )
    db.add(user)
    # 把邀请码标记为已使用
    """
    db.flush()  # 先拿到 user.id
    invite.is_used = True
    invite.used_by_user_id = user.id
    """
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return ResponseModel(
        data={
            "token": token,
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "real_name": user.real_name,
                "role": user.role,
                "student_no": user.student_no,
                "teacher_no": user.teacher_no,
                "phone": user.phone,
            }
        },
        message="老师注册成功"
    )



@router.get("/me", response_model=ResponseModel)
def me(current_user: User = Depends(get_current_user)):
    data = UserInfo(
        id=current_user.id,
        real_name=current_user.real_name,
        role=current_user.role,
        student_no=current_user.student_no,
        teacher_no=current_user.teacher_no,
        phone=current_user.phone
    )
    return ResponseModel(data=data)
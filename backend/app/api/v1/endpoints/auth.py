from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from datetime import datetime
import random
import re

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.auth_user import AuthUser
from app.models.student_user import StudentUser
from app.models.teacher_user import TeacherUser
from app.models.student_roster import StudentRoster
from app.models.teacher_invite import TeacherInvite
from app.models.teacher_roster import TeacherRoster
from app.schemas.common import ResponseModel
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    LoginResponseModel,
    RegisterResponse,
    RegisterResponseModel,
    SendSmsCodeRequest,
    SendSmsCodeResponse,
    SendSmsCodeResponseModel,
    StudentRegisterRequest,
    TeacherRegisterRequest,
    UserInfo,
    UserInfoResponseModel
)

router = APIRouter(prefix="/auth", tags=["auth"])
redis_client = get_redis()

def build_user_info(user: AuthUser) -> UserInfo:
    student_no = user.student_profile.student_no if user.student_profile else None
    teacher_no = user.teacher_profile.teacher_no if user.teacher_profile else None

    return UserInfo(
        id=user.id,
        real_name=user.real_name,
        role=user.role,
        student_no=student_no,
        teacher_no=teacher_no,
        phone=user.phone,
    )

def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"^1[3-9]\d{9}$", phone))


def sms_code_key(phone: str) -> str:
    return f"auth:sms_code:{phone}"


def sms_cooldown_key(phone: str) -> str:
    return f"auth:sms_cooldown:{phone}"


def forgot_password_limit_key(username: str) -> str:
    return f"auth:forgot_password_limit:{username}"


def generate_sms_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def verify_sms_code(phone: str, sms_code: str):
    cached_code = redis_client.get(sms_code_key(phone))
    if not cached_code:
        raise HTTPException(status_code=400, detail="验证码已过期或不存在")
    if cached_code != sms_code:
        raise HTTPException(status_code=400, detail="验证码错误")
    redis_client.delete(sms_code_key(phone))


def check_forgot_password_rate_limit(username: str):
    settings = get_settings()
    key = forgot_password_limit_key(username)
    current = redis_client.get(key)
    if current and int(current) >= settings.FORGOT_PASSWORD_LIMIT_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="找回密码尝试过于频繁，请稍后再试",
        )

    current_count = redis_client.incr(key)
    if current_count == 1:
        redis_client.expire(key, settings.FORGOT_PASSWORD_LIMIT_WINDOW_SECONDS)

# 短信验证
@router.post("/send-code", response_model=ResponseModel)
def send_sms_code(payload: SendSmsCodeRequest):
    settings = get_settings()

    if not validate_phone(payload.phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")

    if redis_client.get(sms_cooldown_key(payload.phone)):
        raise HTTPException(status_code=400, detail="验证码发送过于频繁，请稍后再试")

    code = generate_sms_code()

    redis_client.setex(
        sms_code_key(payload.phone),
        settings.SMS_CODE_EXPIRE_SECONDS,
        code,
    )
    redis_client.setex(
        sms_cooldown_key(payload.phone),
        settings.SMS_SEND_INTERVAL_SECONDS,
        "1",
    )

    # 开发环境先走 mock
    debug_code = code if settings.SMS_MODE == "mock" else None
    print(f"[SMS MOCK] phone={payload.phone}, code={code}")

    return SendSmsCodeResponseModel(
        message="验证码发送成功",
        data=SendSmsCodeResponse(
            expire_seconds=settings.SMS_CODE_EXPIRE_SECONDS,
            debug_code=debug_code,
        ),
    )


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

    data = LoginResponse(
        token=token,
        token_type="bearer",
        user_info=build_user_info(user),
    )

    return LoginResponseModel(data=data)

# 学生注册
@router.post("/register/student", response_model=ResponseModel)
def register_student(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    # 0. 验证码判断
    verify_sms_code(payload.phone, payload.sms_code)
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
    try:
        db.add(auth_user)
        db.flush()

        student_user = StudentUser(
            auth_user_id=auth_user.id,
            student_no=payload.student_no,
        )
        db.add(student_user)
        db.commit()
        db.refresh(auth_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="手机号或学号已注册")

    # 4. 直接签发 token
    token = create_access_token(subject=str(auth_user.id))
    data = RegisterResponse(
        token=token,
        token_type="bearer",
        user_info=build_user_info(auth_user),
    )

    return RegisterResponseModel(
        data=data,
        message="学生注册成功",
    )

# 老师注册
@router.post("/register/teacher", response_model=ResponseModel)
def register_teacher(payload: TeacherRegisterRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    verify_sms_code(payload.phone, payload.sms_code)
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

    roster = db.query(TeacherRoster).filter(
        TeacherRoster.teacher_no == payload.teacher_no,
        TeacherRoster.real_name == payload.real_name,
        TeacherRoster.is_enabled == True
    ).first()
    if not roster:
        raise HTTPException(status_code=400, detail="姓名与工号不匹配，不允许注册")

    auth_user = AuthUser(
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        real_name=payload.real_name,
        role="teacher",
        is_active=True,
    )
    try:
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
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="手机号或工号已注册")

    token = create_access_token(subject=str(auth_user.id))
    data = RegisterResponse(
        token=token,
        token_type="bearer",
        user_info=build_user_info(auth_user),
    )

    return RegisterResponseModel(
        data=data,
        message="老师注册成功",
    )



@router.get("/me", response_model=ResponseModel)
def me(current_user: AuthUser = Depends(get_current_user)):
    return UserInfoResponseModel(
        data=build_user_info(current_user)
    )


@router.post("/forgot-password", response_model=ResponseModel)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    check_forgot_password_rate_limit(payload.username)

    user = (
        db.query(AuthUser)
        .outerjoin(StudentUser, StudentUser.auth_user_id == AuthUser.id)
        .outerjoin(TeacherUser, TeacherUser.auth_user_id == AuthUser.id)
        .filter(
            AuthUser.real_name == payload.realName,
            or_(
                StudentUser.student_no == payload.username,
                TeacherUser.teacher_no == payload.username,
            )
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="姓名与学号/工号不匹配")

    user.password_hash = get_password_hash(payload.newPassword)
    db.commit()

    return ResponseModel(message="密码重置成功")

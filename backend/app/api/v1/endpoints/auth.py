from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ResponseModel)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == payload.account,
                User.student_no == payload.account,
                User.teacher_no == payload.account,
                User.phone == payload.account,
                User.email == payload.account,
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
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            student_no=user.student_no,
            teacher_no=user.teacher_no,
            phone=user.phone,
            email=user.email,
        ),
    )

    return ResponseModel(data=data)


@router.get("/me", response_model=ResponseModel)
def me(current_user: User = Depends(get_current_user)):
    data = UserInfo(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        role=current_user.role,
        student_no=current_user.student_no,
        teacher_no=current_user.teacher_no,
        phone=current_user.phone,
        email=current_user.email,
    )
    return ResponseModel(data=data)
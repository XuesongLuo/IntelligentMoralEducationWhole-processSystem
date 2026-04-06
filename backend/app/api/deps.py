from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import parse_token_subject
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    subject = parse_token_subject(token)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的登录凭证",
        )

    user = (
        db.query(User)
        .filter(
            or_(
                User.id == int(subject) if subject.isdigit() else False,
                User.username == subject,
            )
        )
        .first()
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    return user
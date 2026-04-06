from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TeacherInvite(Base):
    __tablename__ = "teacher_invites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invite_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("auth_users.id"), nullable=False)
    used_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("auth_users.id"), nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
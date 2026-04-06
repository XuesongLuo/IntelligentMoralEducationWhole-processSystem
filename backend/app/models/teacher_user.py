from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TeacherUser(Base):
    __tablename__ = "teacher_users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    auth_user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    teacher_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    teacher_invite_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    auth_user = relationship("AuthUser", back_populates="teacher_profile")
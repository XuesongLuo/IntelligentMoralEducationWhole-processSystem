from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StudentUser(Base):
    __tablename__ = "student_users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    auth_user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    student_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    auth_user = relationship("AuthUser", back_populates="student_profile")
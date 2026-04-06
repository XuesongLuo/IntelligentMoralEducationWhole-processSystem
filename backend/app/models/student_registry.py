from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudentRegistry(Base):
    __tablename__ = "student_registry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_no: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_activated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bound_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
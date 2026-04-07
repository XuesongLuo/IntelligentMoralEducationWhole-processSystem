from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserResourceRecord(Base):
    __tablename__ = "user_resource_records"
    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("learning_resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    first_clicked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_clicked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
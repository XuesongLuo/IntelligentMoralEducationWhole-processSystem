from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    paper_type: Mapped[str] = mapped_column(
        Enum("survey", "integrity", "ideology", name="attempt_paper_type_enum"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        Enum("in_progress", "submitted", "ai_processing", "completed", name="attempt_status_enum"),
        nullable=False,
        default="in_progress",
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    force_submitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

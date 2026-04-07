from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssessmentAIReport(Base):
    __tablename__ = "assessment_ai_reports"
    __table_args__ = (
        UniqueConstraint("attempt_id", name="uq_ai_report_attempt"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "completed", "failed", name="ai_report_status_enum"),
        nullable=False,
        default="pending",
        index=True,
    )

    score_research_integrity: Mapped[float | None] = mapped_column(nullable=True)
    score_communication_anxiety: Mapped[float | None] = mapped_column(nullable=True)
    score_career_identity: Mapped[float | None] = mapped_column(nullable=True)
    score_humanistic_care: Mapped[float | None] = mapped_column(nullable=True)
    score_comprehensive_balance: Mapped[float | None] = mapped_column(nullable=True)

    total_score: Mapped[float | None] = mapped_column(nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response_json: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
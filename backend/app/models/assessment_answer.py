from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    answer_json: Mapped[dict | list | str | None] = mapped_column(JSON, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    judged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
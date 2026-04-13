from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.json_text import JSONText


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    paper_type: Mapped[str] = mapped_column(
        Enum("survey", "integrity", name="question_paper_type_enum"),
        nullable=False,
        index=True,
    )
    question_type: Mapped[str] = mapped_column(
        Enum("single", "multiple", "boolean", "fill_blank", "essay", name="question_type_enum"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[dict | list | None] = mapped_column(JSONText, nullable=True)
    answer_json: Mapped[dict | list | str | None] = mapped_column(JSONText, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

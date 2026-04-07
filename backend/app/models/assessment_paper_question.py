from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AssessmentPaperQuestion(Base):
    __tablename__ = "assessment_paper_questions"
    __table_args__ = (
        UniqueConstraint("paper_id", "question_id", name="uq_paper_question"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_papers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
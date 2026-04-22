from app.database import Base
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"))
    membership_id: Mapped[int] = mapped_column(Integer, ForeignKey("memberships.id"))
    text: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    question = relationship("Question", back_populates="answers")
    membership = relationship("Membership", back_populates="answers")

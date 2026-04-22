from app.database import Base
from sqlalchemy import String, Integer, DateTime, Date, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import date, datetime

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    circle_id: Mapped[int] = mapped_column(Integer, ForeignKey("circles.id"))
    text: Mapped[str] = mapped_column(String)
    asked_date: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    circle = relationship("Circle", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

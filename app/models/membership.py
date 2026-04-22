from sqlalchemy import Integer, ForeignKey, String, UniqueConstraint, func, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Membership(Base):
    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    circle_id: Mapped[int] = mapped_column(Integer, ForeignKey("circles.id"))
    display_name: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "circle_id", name="uq_membership_user_circle"),
    )

    user = relationship("User", back_populates="memberships")
    circle = relationship("Circle", back_populates="members")
    answers = relationship("Answer", back_populates="membership")

# app/schemas/question.py
from pydantic import BaseModel
from datetime import date, datetime

class QuestionOut(BaseModel):
    id: int
    circle_id: int
    text: str
    asked_date: date
    created_at: datetime
    asked_member_display_name: str | None = None  # who is being asked today

    model_config = {"from_attributes": True}

class QuestionUpdate(BaseModel):
    text: str

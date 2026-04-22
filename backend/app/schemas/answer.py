# app/schemas/answer.py
from pydantic import BaseModel
from datetime import datetime

class AnswerCreate(BaseModel):
    text: str

class AnswerOut(BaseModel):
    id: int
    question_id: int
    text: str
    created_at: datetime
    display_name: str | None = None  # None when circle is anonymous

    model_config = {"from_attributes": True}
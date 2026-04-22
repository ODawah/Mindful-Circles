# app/schemas/membership.py
from pydantic import BaseModel
from datetime import datetime

class JoinCircle(BaseModel):
    display_name: str

class MemberOut(BaseModel):
    id: int
    display_name: str
    joined_at: datetime
    order: int

    model_config = {"from_attributes": True}

class MemberOutAnonymous(BaseModel):
    id: int
    joined_at: datetime
    order: int

    model_config = {"from_attributes": True}
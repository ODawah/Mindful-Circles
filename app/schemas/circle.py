from pydantic import BaseModel
from datetime import datetime

class CircleCreate(BaseModel):
    name: str
    description: str | None = None
    is_anonymous: bool = False

class CircleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_anonymous: bool | None = None

class CircleOut(BaseModel):
    id: int
    name: str
    description: str | None
    is_anonymous: bool
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
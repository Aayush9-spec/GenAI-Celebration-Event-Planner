from typing import Optional
from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    content: str


class ChatMessageOut(BaseModel):
    id: int
    event_id: int
    role: str  # "user" | "model"
    content: str
    created_at: str

    model_config = {"from_attributes": True}

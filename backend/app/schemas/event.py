from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


class EventCreate(BaseModel):
    event_type: str  # wedding | birthday | community
    title: str
    event_date: date
    guest_count: int
    total_budget: float
    city: Optional[str] = None
    description: Optional[str] = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v):
        allowed = {"wedding", "birthday", "community"}
        if v not in allowed:
            raise ValueError(f"event_type must be one of {allowed}")
        return v

    @field_validator("guest_count")
    @classmethod
    def validate_guest_count(cls, v):
        if v < 1:
            raise ValueError("guest_count must be at least 1")
        return v

    @field_validator("total_budget")
    @classmethod
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError("total_budget must be greater than 0")
        return v

    @field_validator("event_date")
    @classmethod
    def validate_event_date(cls, v):
        from datetime import date, timedelta
        if v < date.today() + timedelta(days=6):
            raise ValueError("event_date must be at least 1 week in the future")
        return v


class EventUpdate(BaseModel):
    event_type: Optional[str] = None
    title: Optional[str] = None
    event_date: Optional[date] = None
    guest_count: Optional[int] = None
    total_budget: Optional[float] = None
    city: Optional[str] = None
    description: Optional[str] = None


class EventOut(BaseModel):
    id: int
    event_type: str
    title: str
    event_date: date
    guest_count: int
    total_budget: float
    city: Optional[str] = None
    description: Optional[str] = None
    user_id: int
    plan_count: int = 0

    model_config = {"from_attributes": True}

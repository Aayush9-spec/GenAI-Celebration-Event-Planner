from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    budget_breakdown = Column(JSON, nullable=True)
    timeline = Column(JSON, nullable=True)
    vendor_checklist = Column(JSON, nullable=True)
    theme_ideas = Column(JSON, nullable=True)
    raw_ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="plans")

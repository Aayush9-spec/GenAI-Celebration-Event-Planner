from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(20), nullable=False)  # "wedding", "birthday", "community"
    title = Column(String(200), nullable=False)
    event_date = Column(Date, nullable=False)
    guest_count = Column(Integer, nullable=False)
    total_budget = Column(Float, nullable=False)
    city = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="events")
    plans = relationship("Plan", back_populates="event", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="event", cascade="all, delete-orphan")

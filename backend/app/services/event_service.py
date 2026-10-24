from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.plan import Plan
from app.schemas.event import EventCreate, EventUpdate


def create_event(db: Session, user_id: int, event_in: EventCreate) -> Event:
    event = Event(
        user_id=user_id,
        event_type=event_in.event_type,
        title=event_in.title,
        event_date=event_in.event_date,
        guest_count=event_in.guest_count,
        total_budget=event_in.total_budget,
        city=event_in.city,
        description=event_in.description,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_events_by_user(db: Session, user_id: int) -> List[Event]:
    return db.query(Event).filter(Event.user_id == user_id).order_by(Event.created_at.desc()).all()


def get_event(db: Session, event_id: int, user_id: int) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return event


def update_event(db: Session, event_id: int, user_id: int, event_in: EventUpdate) -> Event:
    event = get_event(db, event_id, user_id)
    update_data = event_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event_id: int, user_id: int) -> None:
    event = get_event(db, event_id, user_id)
    db.delete(event)
    db.commit()


def get_plan_count(db: Session, event_id: int) -> int:
    return db.query(Plan).filter(Plan.event_id == event_id).count()

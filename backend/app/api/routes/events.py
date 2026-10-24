from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"])


def _enrich(event, db: Session) -> EventOut:
    """Attach computed plan_count to an event before serialising."""
    out = EventOut.model_validate(event)
    out.plan_count = event_service.get_plan_count(db, event.id)
    return out


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.create_event(db, current_user.id, event_in)
    return _enrich(event, db)


@router.get("/", response_model=List[EventOut])
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    events = event_service.get_events_by_user(db, current_user.id)
    return [_enrich(e, db) for e in events]


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.get_event(db, event_id, current_user.id)
    return _enrich(event, db)


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.update_event(db, event_id, current_user.id, event_in)
    return _enrich(event, db)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.delete_event(db, event_id, current_user.id)

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageIn, ChatMessageOut
from app.services import chat_service, event_service

router = APIRouter(prefix="/events/{event_id}/chat", tags=["chat"])


def _serialize_msg(msg) -> dict:
    return {
        "id": msg.id,
        "event_id": msg.event_id,
        "role": msg.role,
        "content": msg.content,
        "created_at": str(msg.created_at),
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def send_message(
    event_id: int,
    msg_in: ChatMessageIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a user message and receive an AI response."""
    event = event_service.get_event(db, event_id, current_user.id)
    model_msg = chat_service.send_message(db, event, msg_in.content)
    return _serialize_msg(model_msg)


@router.get("/", response_model=List[dict])
def get_history(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full chat history for an event."""
    event_service.get_event(db, event_id, current_user.id)
    messages = chat_service.get_history(db, event_id, limit=50)
    return [_serialize_msg(m) for m in messages]


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear all chat history for an event."""
    event_service.get_event(db, event_id, current_user.id)
    chat_service.clear_history(db, event_id)

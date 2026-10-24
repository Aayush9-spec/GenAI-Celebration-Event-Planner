from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.chat import ChatMessage
from app.models.event import Event
from app.models.plan import Plan
from app.services import gemini_service


def get_history(db: Session, event_id: int, limit: int = 20) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.event_id == event_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )


def _to_gemini_history(messages: List[ChatMessage]) -> List[Dict[str, Any]]:
    """Convert DB ChatMessage records to Gemini history format."""
    return [{"role": msg.role, "parts": [msg.content]} for msg in messages]


def send_message(db: Session, event: Event, user_content: str) -> ChatMessage:
    """
    Save the user message, call Gemini, save the model reply,
    and return the model's ChatMessage record.
    """
    # Build event details dict
    event_details = {
        "event_type": event.event_type,
        "title": event.title,
        "event_date": str(event.event_date),
        "guest_count": event.guest_count,
        "total_budget": event.total_budget,
        "city": event.city,
        "description": event.description,
    }

    # Get latest plan summary for context
    latest_plan = (
        db.query(Plan)
        .filter(Plan.event_id == event.id)
        .order_by(Plan.created_at.desc())
        .first()
    )
    plan_summary = None
    if latest_plan and latest_plan.budget_breakdown:
        total = latest_plan.budget_breakdown.get("total", 0)
        plan_summary = f"Budget total: ₹{total:,.0f}. Plan generated on {latest_plan.created_at}."

    # Get history
    history_msgs = get_history(db, event.id, limit=20)
    gemini_history = _to_gemini_history(history_msgs)

    # Save user message
    user_msg = ChatMessage(event_id=event.id, role="user", content=user_content)
    db.add(user_msg)
    db.commit()

    # Call Gemini
    ai_response = gemini_service.chat_with_assistant(
        event_details=event_details,
        history=gemini_history,
        user_message=user_content,
        latest_plan_summary=plan_summary,
    )

    # Save model response
    model_msg = ChatMessage(event_id=event.id, role="model", content=ai_response)
    db.add(model_msg)
    db.commit()
    db.refresh(model_msg)

    return model_msg


def clear_history(db: Session, event_id: int) -> None:
    db.query(ChatMessage).filter(ChatMessage.event_id == event_id).delete()
    db.commit()

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.plan import Plan
from app.services import gemini_service


def generate_and_save_plan(db: Session, event: Event) -> Plan:
    """Call Gemini to generate a plan, persist it, and return the Plan ORM object."""
    event_details = {
        "event_type": event.event_type,
        "title": event.title,
        "event_date": str(event.event_date),
        "guest_count": event.guest_count,
        "total_budget": event.total_budget,
        "city": event.city,
        "description": event.description,
    }

    plan_data = gemini_service.generate_full_plan(event_details)

    plan = Plan(
        event_id=event.id,
        budget_breakdown=plan_data.get("budget_breakdown"),
        timeline=plan_data.get("timeline"),
        vendor_checklist=plan_data.get("vendor_checklist"),
        theme_ideas=plan_data.get("theme_ideas"),
        raw_ai_response=str(plan_data),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_latest_plan(db: Session, event_id: int) -> Optional[Plan]:
    return (
        db.query(Plan)
        .filter(Plan.event_id == event_id)
        .order_by(Plan.created_at.desc())
        .first()
    )


def get_all_plans(db: Session, event_id: int) -> List[Plan]:
    return (
        db.query(Plan)
        .filter(Plan.event_id == event_id)
        .order_by(Plan.created_at.desc())
        .all()
    )

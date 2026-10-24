from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services import event_service, plan_service

router = APIRouter(prefix="/events/{event_id}/plans", tags=["plans"])


def _serialize_plan(plan) -> Dict[str, Any]:
    return {
        "id": plan.id,
        "event_id": plan.event_id,
        "budget_breakdown": plan.budget_breakdown,
        "timeline": plan.timeline,
        "vendor_checklist": plan.vendor_checklist,
        "theme_ideas": plan.theme_ideas,
        "created_at": str(plan.created_at),
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def generate_plan(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new AI plan for the event (archives previous plans)."""
    event = event_service.get_event(db, event_id, current_user.id)
    try:
        plan = plan_service.generate_and_save_plan(db, event)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"AI plan generation failed: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during plan generation: {str(e)}",
        )
    return _serialize_plan(plan)


@router.get("/latest")
def get_latest_plan(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the most recently generated plan for this event."""
    event_service.get_event(db, event_id, current_user.id)  # ownership check
    plan = plan_service.get_latest_plan(db, event_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No plan found for this event")
    return _serialize_plan(plan)


@router.get("/")
def list_plans(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all plan versions (history) for this event."""
    event_service.get_event(db, event_id, current_user.id)
    plans = plan_service.get_all_plans(db, event_id)
    return [_serialize_plan(p) for p in plans]

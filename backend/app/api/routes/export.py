from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services import event_service, plan_service, pdf_service

router = APIRouter(prefix="/events/{event_id}/plans", tags=["export"])


@router.get("/export/pdf")
def export_plan_pdf(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export the latest event plan as a downloadable PDF."""
    event = event_service.get_event(db, event_id, current_user.id)
    plan = plan_service.get_latest_plan(db, event_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No plan found for this event. Generate a plan first.",
        )
    pdf_bytes = pdf_service.generate_plan_pdf(event, plan)
    filename = f"event_plan_{event.title.replace(' ', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

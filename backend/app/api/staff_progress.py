"""Routes exposing paralegal progress data."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.models import User, UserRole
from app.db.session import get_db
from app.schemas.progress import CaseProgressSummary, ProgressFilter, FeedbackChecklistUpdate, FeedbackChecklistItem
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/staff/progress", tags=["staff-progress"])


@router.get("", response_model=List[CaseProgressSummary])
def list_progress(
    blocked_only: bool = Query(False, description="Show only blocked cases"),
    assignee_id: Optional[str] = Query(None, description="Filter by paralegal user id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[CaseProgressSummary]:
    """Return aggregated progress data for the requesting paralegal/lawyer."""
    allowed_roles = {UserRole.STAFF, UserRole.LAWYER, UserRole.ADMIN}
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="해당 리소스에 대한 권한이 없습니다.")

    filters = ProgressFilter(blocked_only=blocked_only, assignee_id=assignee_id)
    service = ProgressService(db)

    if current_user.role == UserRole.STAFF:
        user_scope = current_user.id
    else:
        user_scope = assignee_id or current_user.id

    return service.list_progress(user_scope, filters=filters)


@router.patch("/{case_id}/checklist/{item_id}", response_model=FeedbackChecklistItem)
def update_checklist_item(
    case_id: str,
    item_id: str,
    payload: FeedbackChecklistUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackChecklistItem:
    allowed_roles = {UserRole.STAFF, UserRole.LAWYER, UserRole.ADMIN}
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="해당 리소스에 대한 권한이 없습니다.")

    service = ProgressService(db)
    try:
        return service.update_checklist_item(
            case_id=case_id,
            item_id=item_id,
            status=payload.status,
            updated_by=current_user.id,
            notes=payload.notes,
        )
    except ValueError as exc:  # invalid status/item
        raise HTTPException(status_code=400, detail=str(exc)) from exc

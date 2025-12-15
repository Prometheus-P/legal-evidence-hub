"""Routes exposing paralegal progress data."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_role, get_current_user
from app.db.models import User, UserRole
from app.schemas.progress import CaseProgressSummary, ProgressFilter, FeedbackChecklistUpdate, FeedbackChecklistItem
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/staff/progress", tags=["staff-progress"])

# Roles allowed to access staff progress endpoints
STAFF_PROGRESS_ROLES = ["staff", "lawyer", "admin"]


@router.get("", response_model=List[CaseProgressSummary])
def list_progress(
    blocked_only: bool = Query(False, description="Show only blocked cases"),
    assignee_id: Optional[str] = Query(None, description="Filter by paralegal user id"),
    user_id: str = Depends(require_role(STAFF_PROGRESS_ROLES)),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[CaseProgressSummary]:
    """Return aggregated progress data for the requesting paralegal/lawyer."""
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
    user_id: str = Depends(require_role(STAFF_PROGRESS_ROLES)),
    db: Session = Depends(get_db),
) -> FeedbackChecklistItem:
    service = ProgressService(db)
    try:
        return service.update_checklist_item(
            case_id=case_id,
            item_id=item_id,
            status=payload.status,
            updated_by=user_id,
            notes=payload.notes,
        )
    except ValueError as exc:  # invalid status/item
        raise HTTPException(status_code=400, detail=str(exc)) from exc

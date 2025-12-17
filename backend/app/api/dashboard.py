"""
Dashboard API endpoints (US7 - Today View)
Task T092

Endpoints:
- GET /dashboard/today - Get today's urgent items and this week's tasks
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user_id
from app.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ============================================
# Response Schemas
# ============================================

class TodayItem(BaseModel):
    """Schema for a today/urgent item"""
    id: str
    title: str
    event_type: str
    start_time: Optional[str] = None
    location: Optional[str] = None
    case_id: Optional[str] = None
    case_title: Optional[str] = None
    description: Optional[str] = None


class WeekItem(BaseModel):
    """Schema for a this week item"""
    id: str
    title: str
    event_type: str
    start_date: str
    start_time: Optional[str] = None
    days_remaining: int
    location: Optional[str] = None
    case_id: Optional[str] = None
    case_title: Optional[str] = None
    description: Optional[str] = None


class TodayResponse(BaseModel):
    """Response schema for GET /dashboard/today"""
    date: str
    urgent: List[TodayItem]
    this_week: List[WeekItem]
    all_complete: bool


# ============================================
# Endpoints
# ============================================

@router.get(
    "/today",
    response_model=TodayResponse,
    summary="Get today's dashboard items"
)
async def get_today_items(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get today's urgent items and this week's upcoming tasks.

    Returns:
    - **date**: Today's date (YYYY-MM-DD)
    - **urgent**: Today's deadlines and court dates (sorted by time)
    - **this_week**: Items within 7 days (sorted by days_remaining)
    - **all_complete**: True if no urgent items for today

    Includes events from:
    - User's personal calendar
    - Cases the user has access to
    """
    service = DashboardService(db)
    return service.get_today_items(user_id)

"""
Procedure API Endpoints
US3 - 절차 단계 관리 (Procedure Stage Tracking)

Endpoints for managing litigation procedure stages
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user_id, verify_case_read_access, verify_case_write_access
from app.services.procedure_service import ProcedureService
from app.schemas.procedure import (
    ProcedureStageCreate,
    ProcedureStageUpdate,
    ProcedureStageResponse,
    ProcedureTimelineResponse,
    TransitionToNextStage,
    UpcomingDeadlinesResponse,
    STAGE_LABELS,
)


router = APIRouter(prefix="/cases/{case_id}/procedure", tags=["Procedure"])


def get_procedure_service(db: Session = Depends(get_db)) -> ProcedureService:
    """Dependency to get procedure service"""
    return ProcedureService(db)


# ============================================
# Timeline Endpoints
# ============================================
@router.get("", response_model=ProcedureTimelineResponse)
async def get_procedure_timeline(
    case_id: str,
    _: str = Depends(verify_case_read_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Get complete procedure timeline for a case

    사건의 전체 절차 타임라인을 조회합니다.
    """
    return service.get_timeline(case_id)


@router.post("/initialize", response_model=ProcedureTimelineResponse)
async def initialize_procedure_timeline(
    case_id: str,
    start_filed: bool = Query(True, description="소장 접수 단계를 진행중으로 시작"),
    user_id: str = Depends(verify_case_write_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Initialize procedure timeline for a case

    사건의 절차 타임라인을 초기화합니다.
    모든 단계를 대기 상태로 생성합니다.
    """
    service.initialize_case_timeline(case_id, user_id, start_filed)
    return service.get_timeline(case_id)


# ============================================
# Stage CRUD Endpoints
# ============================================
@router.post("/stages", response_model=ProcedureStageResponse, status_code=status.HTTP_201_CREATED)
async def create_procedure_stage(
    case_id: str,
    data: ProcedureStageCreate,
    user_id: str = Depends(verify_case_write_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Create a new procedure stage

    새로운 절차 단계를 생성합니다.
    """
    try:
        record = service.create_stage(case_id, data, user_id)
        return ProcedureStageResponse.from_orm_with_labels(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stages/{stage_id}", response_model=ProcedureStageResponse)
async def get_procedure_stage(
    case_id: str,
    stage_id: str,
    _: str = Depends(verify_case_read_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Get a specific procedure stage

    특정 절차 단계의 상세 정보를 조회합니다.
    """
    record = service.get_stage(stage_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure stage not found"
        )
    if record.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Stage does not belong to this case"
        )
    return ProcedureStageResponse.from_orm_with_labels(record)


@router.patch("/stages/{stage_id}", response_model=ProcedureStageResponse)
async def update_procedure_stage(
    case_id: str,
    stage_id: str,
    data: ProcedureStageUpdate,
    _: str = Depends(verify_case_write_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Update a procedure stage

    절차 단계 정보를 수정합니다.
    """
    # Verify stage belongs to case
    existing = service.get_stage(stage_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure stage not found"
        )
    if existing.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Stage does not belong to this case"
        )

    record = service.update_stage(stage_id, data)
    return ProcedureStageResponse.from_orm_with_labels(record)


@router.delete("/stages/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_procedure_stage(
    case_id: str,
    stage_id: str,
    _: str = Depends(verify_case_write_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Delete a procedure stage

    절차 단계를 삭제합니다.
    """
    # Verify stage belongs to case
    existing = service.get_stage(stage_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure stage not found"
        )
    if existing.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Stage does not belong to this case"
        )

    service.delete_stage(stage_id)


# ============================================
# Stage Transition Endpoints
# ============================================
@router.post("/stages/{stage_id}/complete", response_model=ProcedureStageResponse)
async def complete_procedure_stage(
    case_id: str,
    stage_id: str,
    outcome: str = Query(None, description="결과 (조정성립/불성립, 인용/기각 등)"),
    _: str = Depends(verify_case_write_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Mark a procedure stage as completed

    절차 단계를 완료 처리합니다.
    """
    # Verify stage belongs to case
    existing = service.get_stage(stage_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure stage not found"
        )
    if existing.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Stage does not belong to this case"
        )

    try:
        record = service.complete_stage(stage_id, outcome)
        return ProcedureStageResponse.from_orm_with_labels(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/stages/{stage_id}/skip", response_model=ProcedureStageResponse)
async def skip_procedure_stage(
    case_id: str,
    stage_id: str,
    reason: str = Query(None, description="건너뛴 사유"),
    _: str = Depends(verify_case_write_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Skip a procedure stage

    절차 단계를 건너뜁니다.
    """
    # Verify stage belongs to case
    existing = service.get_stage(stage_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedure stage not found"
        )
    if existing.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Stage does not belong to this case"
        )

    try:
        record = service.skip_stage(stage_id, reason)
        return ProcedureStageResponse.from_orm_with_labels(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/transition", response_model=dict)
async def transition_to_next_stage(
    case_id: str,
    data: TransitionToNextStage,
    user_id: str = Depends(verify_case_write_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Transition to the next procedure stage

    다음 절차 단계로 이동합니다.
    현재 단계가 완료 처리되고 다음 단계가 진행중으로 설정됩니다.
    """
    try:
        completed, next_stage = service.transition_to_next(case_id, data, user_id)

        result = {
            "success": True,
            "message": f"'{STAGE_LABELS.get(data.next_stage, data.next_stage)}' 단계로 이동했습니다.",
            "next_stage": ProcedureStageResponse.from_orm_with_labels(next_stage),
        }
        if completed:
            result["completed_stage"] = ProcedureStageResponse.from_orm_with_labels(completed)

        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/next-stages", response_model=List[dict])
async def get_valid_next_stages(
    case_id: str,
    _: str = Depends(verify_case_read_access),
    service: ProcedureService = Depends(get_procedure_service)
):
    """
    Get valid next stages from current position

    현재 위치에서 이동 가능한 다음 단계 목록을 조회합니다.
    """
    stages = service.get_valid_next_stages(case_id)
    return [
        {"stage": stage.value, "label": label}
        for stage, label in stages
    ]


# ============================================
# Deadline Endpoints
# ============================================
deadlines_router = APIRouter(prefix="/procedure/deadlines", tags=["Procedure"])


@deadlines_router.get("", response_model=UpcomingDeadlinesResponse)
async def get_upcoming_deadlines(
    days_ahead: int = Query(7, ge=1, le=30, description="조회할 기간 (일)"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get upcoming procedure deadlines

    다가오는 절차 기일을 조회합니다.
    """
    service = ProcedureService(db)
    return service.get_upcoming_deadlines(user_id, days_ahead)

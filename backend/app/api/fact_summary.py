"""
Fact Summary API Router
014-case-fact-summary: T005, T011, T012, T018, T029

엔드포인트:
- GET /cases/{case_id}/fact-summary - 사실관계 조회
- POST /cases/{case_id}/fact-summary/generate - 사실관계 생성
- PATCH /cases/{case_id}/fact-summary - 사실관계 수정
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user_id
from app.schemas.fact_summary import (
    FactSummaryResponse,
    FactSummaryGenerateRequest,
    FactSummaryGenerateResponse,
    FactSummaryUpdateRequest,
    FactSummaryUpdateResponse,
)
from app.services.fact_summary_service import FactSummaryService

router = APIRouter(prefix="/cases", tags=["Fact Summary"])


@router.get(
    "/{case_id}/fact-summary",
    response_model=FactSummaryResponse,
    summary="사실관계 조회",
    description="사건의 저장된 사실관계(AI 생성본 또는 변호사 수정본)를 조회합니다."
)
async def get_fact_summary(
    case_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    사실관계 조회 API (T012)

    - **case_id**: 사건 ID

    Returns:
        FactSummaryResponse: 사실관계 데이터 (ai_summary, modified_summary 등)

    Raises:
        404: 사실관계가 존재하지 않음
        403: 사건 접근 권한 없음
    """
    service = FactSummaryService(db)
    result = service.get_fact_summary(case_id, user_id)

    if not result:
        raise HTTPException(status_code=404, detail="사실관계가 존재하지 않습니다")

    return result


@router.post(
    "/{case_id}/fact-summary/generate",
    response_model=FactSummaryGenerateResponse,
    summary="사실관계 생성",
    description="사건의 증거들을 종합하여 AI 사실관계 요약을 생성합니다."
)
async def generate_fact_summary(
    case_id: str,
    request: FactSummaryGenerateRequest = FactSummaryGenerateRequest(),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    사실관계 생성 API (T011)

    - **case_id**: 사건 ID
    - **force_regenerate**: True면 기존 수정본 백업 후 재생성

    Returns:
        FactSummaryGenerateResponse: 생성된 AI 사실관계

    Raises:
        400: 증거 없음 또는 이미 존재 (force_regenerate=False)
        403: 사건 접근 권한 없음
        404: 사건 없음
    """
    service = FactSummaryService(db)
    return service.generate_fact_summary(
        case_id=case_id,
        user_id=user_id,
        force_regenerate=request.force_regenerate
    )


@router.patch(
    "/{case_id}/fact-summary",
    response_model=FactSummaryUpdateResponse,
    summary="사실관계 수정",
    description="변호사가 AI 생성 사실관계를 수정하여 저장합니다."
)
async def update_fact_summary(
    case_id: str,
    request: FactSummaryUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    사실관계 수정 API (T018)

    - **case_id**: 사건 ID
    - **modified_summary**: 수정된 사실관계 텍스트

    Returns:
        FactSummaryUpdateResponse: 수정 결과

    Raises:
        400: 잘못된 요청
        403: 사건 접근 권한 없음
        404: 사실관계 없음
    """
    service = FactSummaryService(db)
    return service.update_fact_summary(
        case_id=case_id,
        user_id=user_id,
        modified_summary=request.modified_summary
    )

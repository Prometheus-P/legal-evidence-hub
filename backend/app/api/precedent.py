"""
Precedent Search API Router
012-precedent-integration: T022-T023

엔드포인트: GET /cases/{case_id}/similar-precedents
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user_id
from app.schemas.precedent import PrecedentSearchResponse
from app.services.precedent_service import PrecedentService

router = APIRouter(prefix="/cases", tags=["Precedent"])


@router.get(
    "/{case_id}/similar-precedents",
    response_model=PrecedentSearchResponse,
    summary="유사 판례 검색",
    description="사건의 유책사유를 기반으로 유사한 판례를 검색합니다."
)
async def search_similar_precedents(
    case_id: str,
    limit: int = Query(default=10, ge=1, le=20, description="최대 반환 개수"),
    min_score: float = Query(default=0.5, ge=0, le=1, description="최소 유사도 점수"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    유사 판례 검색 API (T022)

    - **case_id**: 검색 대상 사건 ID
    - **limit**: 최대 반환 개수 (1-20, 기본값 10)
    - **min_score**: 최소 유사도 점수 (0-1, 기본값 0.5)

    Returns:
        PrecedentSearchResponse: 판례 목록 및 검색 컨텍스트
    """
    # TODO: 사건 접근 권한 검증
    # case = db.query(Case).filter(Case.id == case_id).first()
    # if not case:
    #     raise HTTPException(status_code=404, detail="Case not found")
    # if not has_case_access(user_id, case_id):
    #     raise HTTPException(status_code=403, detail="Access denied")

    service = PrecedentService(db)
    return service.search_similar_precedents(
        case_id=case_id,
        limit=limit,
        min_score=min_score
    )

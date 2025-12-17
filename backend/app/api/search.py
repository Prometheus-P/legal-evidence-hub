"""
Search API - Global search endpoint
007-lawyer-portal-v1: US6 (Global Search)
009-mvp-gap-closure: US2 (RAG Semantic Search)
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.dependencies import get_current_user_id
from app.core.error_messages import ErrorMessages
from app.services.search_service import SearchService
from app.utils.qdrant import search_evidence_by_semantic
from app.repositories.case_repository import CaseRepository


router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def search(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    categories: Optional[str] = Query(
        None,
        description="Comma-separated list of categories: cases,clients,evidence,events"
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per category"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    글로벌 검색

    사건, 의뢰인, 증거, 일정을 통합 검색합니다.
    Cmd/Ctrl + K 단축키로 호출되는 검색 팔레트에서 사용됩니다.

    **검색 대상**:
    - **cases**: 사건 제목, 설명, 의뢰인명
    - **clients**: 의뢰인 이름, 이메일
    - **evidence**: 파일명, AI 요약, 레이블
    - **events**: 일정 제목, 설명, 장소

    **접근 제어**:
    - 사용자가 접근 가능한 케이스의 데이터만 검색됩니다.

    Args:
        q: 검색어 (최소 2자)
        categories: 검색 카테고리 (쉼표 구분, 선택 사항)
        limit: 카테고리별 최대 결과 수

    Returns:
        검색 결과 목록
    """
    service = SearchService(db)

    # Parse categories if provided
    category_list = None
    if categories:
        category_list = [c.strip() for c in categories.split(",") if c.strip()]

    result = service.search(
        query=q,
        user_id=user_id,
        categories=category_list,
        limit=limit
    )

    return result


@router.get("/quick-access")
async def get_quick_access(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    바로가기 정보 조회

    검색 팔레트의 바로가기 섹션에 표시할 정보를 반환합니다.
    - 오늘의 일정
    - 이번 주 마감 사건

    Returns:
        바로가기 정보
    """
    service = SearchService(db)
    return service.get_quick_access(user_id)


@router.get("/recent")
async def get_recent_searches(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    최근 검색어 조회

    사용자의 최근 검색 기록을 반환합니다.

    Args:
        limit: 최대 결과 수

    Returns:
        최근 검색어 목록
    """
    service = SearchService(db)
    return {"recent_searches": service.get_recent_searches(user_id, limit)}


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=2, description="Search query for semantic search"),
    case_id: str = Query(..., description="Case ID to search within (case_id isolation)"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to return"),
    labels: Optional[str] = Query(None, description="Comma-separated labels to filter (e.g., '폭언,불륜')"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    RAG Semantic Search (Qdrant 기반)

    특정 케이스 내 증거를 의미론적으로 검색합니다.
    Draft 생성 시 관련 증거 검색에 사용됩니다.

    **접근 제어**:
    - 사용자가 해당 케이스의 멤버여야 검색 가능합니다.
    - 케이스별로 Qdrant 컬렉션이 격리되어 있어 다른 케이스 데이터에 접근할 수 없습니다.

    Args:
        q: 검색어 (최소 2자)
        case_id: 검색할 케이스 ID (case isolation)
        top_k: 반환할 결과 수 (기본값: 5)
        labels: 필터링할 레이블 (쉼표 구분, 선택 사항)

    Returns:
        Qdrant semantic search 결과 (유사도 점수 포함)
    """
    # Access control: verify user has access to the case
    case_repo = CaseRepository(db)
    if not case_repo.is_user_member_of_case(user_id, case_id):
        raise HTTPException(
            status_code=403,
            detail=ErrorMessages.CASE_PERMISSION_DENIED
        )

    # Build filters if labels provided
    filters = None
    if labels:
        label_list = [label.strip() for label in labels.split(",") if label.strip()]
        if label_list:
            filters = {"labels": label_list}

    # Execute Qdrant semantic search
    results = search_evidence_by_semantic(
        case_id=case_id,
        query=q,
        top_k=top_k,
        filters=filters
    )

    return {
        "query": q,
        "case_id": case_id,
        "results": results,
        "total": len(results)
    }

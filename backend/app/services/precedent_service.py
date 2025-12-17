"""
Precedent Search Service
012-precedent-integration: T019-T024

비즈니스 로직: 유사 판례 검색 및 반환
"""

import logging
from typing import List
from sqlalchemy.orm import Session

from app.schemas.precedent import (
    PrecedentCase,
    PrecedentSearchResponse,
    QueryContext,
    DivisionRatio,
)
from app.utils.precedent_search import (
    search_similar_precedents as qdrant_search,
    get_fallback_precedents,
)

logger = logging.getLogger(__name__)


class PrecedentService:
    """판례 검색 서비스 (T019)"""

    def __init__(self, db: Session):
        self.db = db

    def search_similar_precedents(
        self,
        case_id: str,
        limit: int = 10,
        min_score: float = 0.5
    ) -> PrecedentSearchResponse:
        """
        사건 기반 유사 판례 검색 (T020)

        Args:
            case_id: 검색 대상 사건 ID
            limit: 최대 결과 수
            min_score: 최소 유사도 점수

        Returns:
            PrecedentSearchResponse: 판례 목록 및 쿼리 컨텍스트
        """
        # T021: 사건의 유책사유 추출
        fault_types = self.get_fault_types(case_id)

        if not fault_types:
            # 유책사유가 없으면 기본 검색어 사용
            query = "이혼 판례 재산분할"
        else:
            # 유책사유를 검색 쿼리로 변환
            query = " ".join(fault_types)

        try:
            # Qdrant 검색 실행
            raw_results = qdrant_search(query, limit=limit, min_score=min_score)

            if not raw_results:
                # T024: Fallback 데이터 사용
                logger.warning(f"No Qdrant results for case {case_id}, using fallback")
                raw_results = get_fallback_precedents()

            # 결과를 PrecedentCase 스키마로 변환
            precedents = []
            for item in raw_results:
                division_ratio = None
                if item.get("division_ratio"):
                    dr = item["division_ratio"]
                    division_ratio = DivisionRatio(
                        plaintiff=dr.get("plaintiff", 50),
                        defendant=dr.get("defendant", 50)
                    )

                precedent = PrecedentCase(
                    case_ref=item.get("case_ref", ""),
                    court=item.get("court", ""),
                    decision_date=item.get("decision_date", ""),
                    summary=item.get("summary", ""),
                    division_ratio=division_ratio,
                    key_factors=item.get("key_factors", []),
                    similarity_score=item.get("similarity_score", 0.0)
                )
                precedents.append(precedent)

            return PrecedentSearchResponse(
                precedents=precedents,
                query_context=QueryContext(
                    fault_types=fault_types,
                    total_found=len(precedents)
                )
            )

        except Exception as e:
            logger.error(f"Precedent search error for case {case_id}: {e}")
            # 오류 시 Fallback 데이터 반환
            return self._get_fallback_response(fault_types)

    def get_fault_types(self, case_id: str) -> List[str]:
        """
        사건의 유책사유 추출 (T021)

        DynamoDB 또는 PostgreSQL에서 사건의 유책사유 레이블을 조회합니다.
        """
        try:
            # TODO: 실제 구현에서는 DynamoDB evidence 테이블에서 labels 조회
            # 현재는 샘플 데이터 반환
            return ["부정행위", "별거"]
        except Exception as e:
            logger.error(f"Failed to get fault types for case {case_id}: {e}")
            return []

    def _get_fallback_response(self, fault_types: List[str]) -> PrecedentSearchResponse:
        """T024: Fallback 응답 생성"""
        fallback_data = get_fallback_precedents()

        precedents = []
        for item in fallback_data:
            division_ratio = None
            if item.get("division_ratio"):
                dr = item["division_ratio"]
                division_ratio = DivisionRatio(
                    plaintiff=dr.get("plaintiff", 50),
                    defendant=dr.get("defendant", 50)
                )

            precedent = PrecedentCase(
                case_ref=item.get("case_ref", ""),
                court=item.get("court", ""),
                decision_date=item.get("decision_date", ""),
                summary=item.get("summary", ""),
                division_ratio=division_ratio,
                key_factors=item.get("key_factors", []),
                similarity_score=item.get("similarity_score", 0.0)
            )
            precedents.append(precedent)

        return PrecedentSearchResponse(
            precedents=precedents,
            query_context=QueryContext(
                fault_types=fault_types,
                total_found=len(precedents)
            )
        )

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
from app.utils.dynamo import get_evidence_by_case

logger = logging.getLogger(__name__)

# Article 840 카테고리 → 한글 레이블 매핑
CATEGORY_KO_MAP = {
    "adultery": "부정행위",
    "desertion": "악의의 유기",
    "mistreatment_by_inlaws": "시댁 부당대우",
    "harm_to_own_parents": "친부모 해악",
    "unknown_whereabouts": "생사불명",
    "irreconcilable_differences": "혼인지속 곤란",
    "domestic_violence": "가정폭력",
    "financial_misconduct": "재정 비행",
    "general": "일반",
}

# AI Worker가 저장하는 한글 풀네임 → 짧은 키워드 매핑
# (민법 제840조 이혼사유)
ARTICLE_840_FULLNAME_MAP = {
    # 1호: 배우자에 부정한 행위가 있었을 때
    "1호_부정행위": "부정행위",
    "1호_배우자의 부정행위": "부정행위",
    # 2호: 배우자가 악의로 다른 일방을 유기한 때
    "2호_악의의 유기": "악의의 유기",
    "2호_배우자의 악의적 유기": "악의의 유기",
    # 3호: 배우자 또는 그 직계존속으로부터 심히 부당한 대우를 받았을 때
    "3호_배우자 또는 그 직계존속으로부터의 폭언": "가정폭력",
    "3호_배우자 또는 그 직계존속으로부터 심히 부당한 대우": "가정폭력",
    "3호_시댁 부당대우": "시댁 부당대우",
    # 4호: 자기의 직계존속이 배우자로부터 심히 부당한 대우를 받았을 때
    "4호_친부모에 대한 부당대우": "친부모 해악",
    "4호_직계존속에 대한 부당대우": "친부모 해악",
    # 5호: 배우자의 생사가 3년 이상 분명하지 아니한 때
    "5호_생사불명": "생사불명",
    "5호_배우자 생사불명 3년 이상": "생사불명",
    # 6호: 기타 혼인을 계속하기 어려운 중대한 사유가 있을 때
    "5호_기타 혼인을 계속하기 어려운 중대한 사유": "혼인지속 곤란",
    "6호_기타 혼인을 계속하기 어려운 중대한 사유": "혼인지속 곤란",
    "6호_혼인지속 곤란": "혼인지속 곤란",
    # 기타 자주 나오는 패턴
    "가정폭력": "가정폭력",
    "폭언": "가정폭력",
    "폭행": "가정폭력",
    "부정행위": "부정행위",
    "외도": "부정행위",
    "불륜": "부정행위",
    "재정 비행": "재정 비행",
    "도박": "재정 비행",
    "채무": "재정 비행",
}


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
        logger.info(f"[PrecedentSearch] Starting search for case_id={case_id}")

        # T021: 사건의 유책사유 추출
        fault_types = self.get_fault_types(case_id)
        logger.info(f"[PrecedentSearch] Extracted fault_types={fault_types}")

        if not fault_types:
            # 유책사유가 없으면 기본 검색어 사용
            query = "이혼 판례 재산분할"
        else:
            # 유책사유를 검색 쿼리로 변환
            query = " ".join(fault_types)

        logger.info(f"[PrecedentSearch] Search query: {query}")
        using_fallback = False

        try:
            # Qdrant 검색 실행
            raw_results = qdrant_search(query, limit=limit, min_score=min_score)

            if not raw_results:
                # T024: Fallback 데이터 사용 (fault_types 기반 필터링)
                logger.warning(f"No Qdrant results for case {case_id}, using fallback with fault_types={fault_types}")
                raw_results = get_fallback_precedents(fault_types)
                using_fallback = True

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

            logger.info(f"[PrecedentSearch] Results: {len(precedents)} precedents, using_fallback={using_fallback}")

            return PrecedentSearchResponse(
                precedents=precedents,
                query_context=QueryContext(
                    fault_types=fault_types,
                    total_found=len(precedents)
                )
            )

        except Exception as e:
            logger.error(f"[PrecedentSearch] Error for case {case_id}: {e}")
            # 오류 시 Fallback 데이터 반환
            return self._get_fallback_response(fault_types)

    def get_fault_types(self, case_id: str) -> List[str]:
        """
        사건의 유책사유 추출 (T021)

        DynamoDB evidence 테이블에서 article_840_tags.categories 조회
        """
        try:
            # DynamoDB에서 해당 케이스의 증거 목록 조회
            evidences = get_evidence_by_case(case_id)

            if not evidences:
                logger.info(f"No evidence found for case {case_id}, using default query")
                return []

            # 각 증거의 article_840_tags.categories 수집
            fault_types = set()
            for evidence in evidences:
                # article_840_tags에서 categories 추출
                tags = evidence.get("article_840_tags")
                if tags and isinstance(tags, dict):
                    categories = tags.get("categories", [])
                    for cat in categories:
                        # 문자열인 경우 그대로 사용
                        if isinstance(cat, str):
                            fault_types.add(cat)

                # labels 필드에서도 추출 (백업)
                labels = evidence.get("labels")
                if labels and isinstance(labels, list):
                    for label in labels:
                        if isinstance(label, str) and label not in ["general", "일반"]:
                            fault_types.add(label)

            # 한글 레이블로 변환 (풀네임 → 짧은 키워드 → 최종 레이블)
            korean_labels = set()
            for cat in fault_types:
                # 1차: AI Worker 풀네임 매핑 시도
                if cat in ARTICLE_840_FULLNAME_MAP:
                    korean_labels.add(ARTICLE_840_FULLNAME_MAP[cat])
                # 2차: 영문 키 → 한글 레이블 매핑 시도
                elif cat in CATEGORY_KO_MAP:
                    label = CATEGORY_KO_MAP[cat]
                    if label not in ["일반", "general"]:
                        korean_labels.add(label)
                # 3차: 그대로 사용 (이미 짧은 한글인 경우)
                elif cat not in ["일반", "general"]:
                    korean_labels.add(cat)

            result = list(korean_labels)
            logger.info(f"Case {case_id}: extracted fault_types={result} from {len(evidences)} evidences")
            return result

        except Exception as e:
            logger.error(f"Failed to get fault types for case {case_id}: {e}")
            return []

    def _get_fallback_response(self, fault_types: List[str]) -> PrecedentSearchResponse:
        """T024: Fallback 응답 생성 (fault_types 기반 필터링)"""
        fallback_data = get_fallback_precedents(fault_types)

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

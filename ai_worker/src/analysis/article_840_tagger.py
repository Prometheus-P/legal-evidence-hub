"""
Article 840 Automatic Tagger

민법 840조 이혼 사유 자동 태깅 모듈

Given: 증거 메시지
When: 내용 분석
Then: 해당하는 민법 840조 카테고리 자동 분류

Note: 키워드 설정은 config/legal_keywords.yaml에서 관리
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from src.parsers.base import Message
from src.analysis.context_matcher import ContextAwareKeywordMatcher
from config import ConfigLoader


class Article840Category(str, Enum):
    """
    민법 840조 이혼 사유 카테고리

    Korean Civil Code Article 840 - Grounds for Divorce
    """
    ADULTERY = "adultery"  # 제1호: 배우자의 부정행위
    DESERTION = "desertion"  # 제2호: 악의의 유기
    MISTREATMENT_BY_INLAWS = "mistreatment_by_inlaws"  # 제3호: 배우자 직계존속의 부당대우
    HARM_TO_OWN_PARENTS = "harm_to_own_parents"  # 제4호: 자기 직계존속 피해
    UNKNOWN_WHEREABOUTS = "unknown_whereabouts"  # 제5호: 생사불명 3년
    IRRECONCILABLE_DIFFERENCES = "irreconcilable_differences"  # 제6호: 혼인 지속 곤란사유
    DOMESTIC_VIOLENCE = "domestic_violence"  # 제6호 세부: 가정폭력
    FINANCIAL_MISCONDUCT = "financial_misconduct"  # 제6호 세부: 재정 비행
    GENERAL = "general"  # 일반 증거 (특정 조항에 해당하지 않음)


class TaggingResult(BaseModel):
    """
    태깅 결과

    Attributes:
        categories: 분류된 카테고리 리스트 (다중 카테고리 가능)
        confidence: 신뢰도 점수 (0.0-1.0)
        matched_keywords: 매칭된 키워드 리스트
        reasoning: 분류 이유
    """
    categories: List[Article840Category] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    matched_keywords: List[str] = Field(default_factory=list)
    reasoning: str = ""


class Article840Tagger:
    """
    민법 840조 자동 태거

    Given: 증거 메시지 내용
    When: 키워드 분석 수행
    Then: 해당하는 민법 840조 카테고리 자동 분류

    Features:
    - 7가지 카테고리 분류 (6개 조항 + 일반)
    - 다중 카테고리 태깅 지원
    - 신뢰도 점수 계산
    - 일괄 처리 (batch) 지원
    """

    def __init__(self, use_context_matching: bool = False, use_kiwi: bool = False):
        """
        초기화 - 카테고리별 키워드 사전 구성

        Args:
            use_context_matching: 문맥 인식 키워드 매칭 활성화 (부정문 감지)
            use_kiwi: Kiwi 형태소 분석기 사용 여부

        Note:
            키워드 설정은 config/legal_keywords.yaml에서 로드됩니다.
        """
        self.use_context_matching = use_context_matching
        self._context_matcher: Optional[ContextAwareKeywordMatcher] = None

        if use_context_matching:
            self._context_matcher = ContextAwareKeywordMatcher(use_kiwi=use_kiwi)

        # YAML 설정에서 키워드 로드
        self.keywords = self._load_keywords_from_config()

    def _load_keywords_from_config(self) -> Dict[Article840Category, Dict[str, Any]]:
        """
        config/legal_keywords.yaml에서 키워드 로드

        Returns:
            카테고리별 키워드 및 가중치 딕셔너리
        """
        legal_keywords = ConfigLoader.get_all_legal_categories()

        # YAML 키 → Article840Category 매핑
        category_mapping = {
            "adultery": Article840Category.ADULTERY,
            "desertion": Article840Category.DESERTION,
            "mistreatment_by_inlaws": Article840Category.MISTREATMENT_BY_INLAWS,
            "harm_to_own_parents": Article840Category.HARM_TO_OWN_PARENTS,
            "unknown_whereabouts": Article840Category.UNKNOWN_WHEREABOUTS,
            "irreconcilable_differences": Article840Category.IRRECONCILABLE_DIFFERENCES,
            "domestic_violence": Article840Category.DOMESTIC_VIOLENCE,
            "financial_misconduct": Article840Category.FINANCIAL_MISCONDUCT,
            "general": Article840Category.GENERAL,
        }

        keywords = {}
        for yaml_key, category_enum in category_mapping.items():
            if yaml_key in legal_keywords:
                data = legal_keywords[yaml_key]
                keywords[category_enum] = {
                    "keywords": data.get("keywords", []),
                    "weight": data.get("weight", 1)
                }
            else:
                # 설정에 없는 카테고리는 빈 키워드로 초기화
                keywords[category_enum] = {"keywords": [], "weight": 1}

        return keywords

    def tag(self, message: Message) -> TaggingResult:
        """
        단일 메시지 태깅

        Given: Message 객체
        When: 키워드 매칭 및 카테고리 분류
        Then: TaggingResult 반환

        Args:
            message: 태깅할 메시지

        Returns:
            TaggingResult: 분류 결과 (카테고리, 신뢰도, 키워드)
        """
        # 빈 메시지 처리
        if not message.content or message.content.strip() == "":
            return TaggingResult(
                categories=[Article840Category.GENERAL],
                confidence=0.0,
                matched_keywords=[],
                reasoning="Empty message - classified as general"
            )

        content_lower = message.content.lower()

        # 각 카테고리별로 키워드 매칭
        category_matches = {}
        all_matched_keywords = []

        # 부정문 체크용 변수
        negated_keywords = []

        for category, data in self.keywords.items():
            matched_keywords = []
            for keyword in data["keywords"]:
                if keyword in content_lower:
                    # 부정문 체크 (context_matching 활성화 시)
                    is_negated = False
                    if self.use_context_matching and self._context_matcher:
                        result = self._context_matcher.analyze(message.content, [keyword])
                        if result.has_negation:
                            is_negated = True
                            if keyword not in negated_keywords:
                                negated_keywords.append(keyword)

                    # 부정되지 않은 키워드만 매칭
                    if not is_negated:
                        if keyword not in all_matched_keywords:
                            all_matched_keywords.append(keyword)
                            matched_keywords.append(keyword)

            if matched_keywords:
                category_matches[category] = {
                    "keywords": matched_keywords,
                    "count": len(matched_keywords),
                    "weight": data["weight"]
                }

        # 카테고리 결정
        if not category_matches:
            # 키워드 매칭이 없으면 GENERAL
            reasoning = "No specific keywords matched - classified as general"
            if negated_keywords:
                reasoning += f" [부정된 키워드: {', '.join(negated_keywords)}]"
            return TaggingResult(
                categories=[Article840Category.GENERAL],
                confidence=0.1,
                matched_keywords=[],
                reasoning=reasoning
            )

        # GENERAL만 매칭되면 GENERAL로 분류
        if len(category_matches) == 1 and Article840Category.GENERAL in category_matches:
            return TaggingResult(
                categories=[Article840Category.GENERAL],
                confidence=0.3,
                matched_keywords=all_matched_keywords,
                reasoning=f"Only general keywords matched: {', '.join(all_matched_keywords)}"
            )

        # 가중치 기반 정렬 (weight가 높고, 매칭 키워드가 많은 순서)
        sorted_categories = sorted(
            category_matches.items(),
            key=lambda x: (x[1]["weight"] * x[1]["count"], x[1]["count"]),
            reverse=True
        )

        # 상위 카테고리들 선택 (GENERAL 제외)
        selected_categories = []
        for category, match_data in sorted_categories:
            if category != Article840Category.GENERAL:
                selected_categories.append(category)

        # GENERAL 제외하고 매칭이 없으면 GENERAL 추가
        if not selected_categories:
            selected_categories = [Article840Category.GENERAL]

        # 신뢰도 계산
        confidence = self._calculate_confidence(
            total_keywords=len(all_matched_keywords),
            category_count=len(selected_categories)
        )

        # 분류 이유 생성
        reasoning = self._generate_reasoning(
            categories=selected_categories,
            matched_keywords=all_matched_keywords,
            category_matches=category_matches
        )

        # 부정된 키워드 정보 추가
        if negated_keywords:
            reasoning += f" [부정된 키워드: {', '.join(negated_keywords)}]"

        return TaggingResult(
            categories=selected_categories,
            confidence=confidence,
            matched_keywords=all_matched_keywords,
            reasoning=reasoning
        )

    def tag_batch(self, messages: List[Message]) -> List[TaggingResult]:
        """
        여러 메시지 일괄 태깅

        Args:
            messages: 메시지 리스트

        Returns:
            List[TaggingResult]: 각 메시지의 태깅 결과
        """
        results = []
        for message in messages:
            result = self.tag(message)
            results.append(result)
        return results

    def _calculate_confidence(
        self,
        total_keywords: int,
        category_count: int
    ) -> float:
        """
        신뢰도 점수 계산

        Args:
            total_keywords: 매칭된 총 키워드 개수
            category_count: 분류된 카테고리 개수

        Returns:
            float: 신뢰도 점수 (0.0-1.0)
        """
        if total_keywords == 0:
            return 0.0

        # 기본 신뢰도: 키워드 개수에 비례
        base_confidence = min(0.3 + (total_keywords * 0.2), 1.0)

        # 다중 카테고리는 신뢰도 약간 감소
        if category_count > 1:
            base_confidence *= 0.9

        return round(base_confidence, 2)

    def _generate_reasoning(
        self,
        categories: List[Article840Category],
        matched_keywords: List[str],
        category_matches: dict
    ) -> str:
        """
        분류 이유 생성

        Args:
            categories: 분류된 카테고리 리스트
            matched_keywords: 매칭된 키워드 리스트
            category_matches: 카테고리별 매칭 정보

        Returns:
            str: 분류 이유 설명
        """
        if not categories or categories == [Article840Category.GENERAL]:
            return f"General evidence with keywords: {', '.join(matched_keywords[:3])}"

        # 카테고리 이름 매핑
        category_names = {
            Article840Category.ADULTERY: "Adultery (Article 840-1)",
            Article840Category.DESERTION: "Malicious Desertion (Article 840-2)",
            Article840Category.MISTREATMENT_BY_INLAWS: "Mistreatment by In-laws (Article 840-3)",
            Article840Category.HARM_TO_OWN_PARENTS: "Harm to Own Parents (Article 840-4)",
            Article840Category.UNKNOWN_WHEREABOUTS: "Unknown Whereabouts (Article 840-5)",
            Article840Category.IRRECONCILABLE_DIFFERENCES: "Irreconcilable Differences (Article 840-6)",
            Article840Category.DOMESTIC_VIOLENCE: "Domestic Violence (Article 840-6)",
            Article840Category.FINANCIAL_MISCONDUCT: "Financial Misconduct (Article 840-6)",
            Article840Category.GENERAL: "General Evidence"
        }

        category_list = [category_names[cat] for cat in categories]

        reasoning = f"Classified as {', '.join(category_list)} based on {len(matched_keywords)} keywords"

        # 주요 키워드 추가
        if matched_keywords:
            top_keywords = matched_keywords[:3]
            reasoning += f": {', '.join(top_keywords)}"

        return reasoning

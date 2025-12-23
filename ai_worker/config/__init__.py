"""
AI Worker Configuration Loader

YAML 기반 설정 관리 시스템.
하드코딩된 프롬프트, 키워드, 설정값을 외부 파일로 관리합니다.

Usage:
    from config import ConfigLoader

    # 단일 설정 파일 로드
    legal_keywords = ConfigLoader.load("legal_keywords")

    # 프롬프트 로드
    system_prompt = ConfigLoader.get_prompt("ai_system", "system_prompt")

    # 모델 설정 로드
    model_config = ConfigLoader.get_model_config("gpt-4o-mini")
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, List

import yaml

logger = logging.getLogger(__name__)

# 설정 디렉토리 경로
CONFIG_DIR = Path(__file__).parent


class ConfigLoader:
    """
    YAML 설정 파일 로더 (캐싱 적용)

    Features:
    - YAML 파일 로드 및 캐싱
    - 프롬프트 템플릿 조회
    - 모델 설정 조회
    - 키워드 목록 조회
    """

    _cache: Dict[str, Any] = {}
    _prompts_cache: Dict[str, Dict] = {}

    @classmethod
    def load(cls, name: str, reload: bool = False) -> Dict[str, Any]:
        """
        YAML 설정 파일 로드

        Args:
            name: 설정 파일 이름 (확장자 제외)
            reload: 캐시 무시하고 재로드

        Returns:
            설정 딕셔너리

        Example:
            legal_keywords = ConfigLoader.load("legal_keywords")
            limits = ConfigLoader.load("limits")
        """
        if name in cls._cache and not reload:
            return cls._cache[name]

        # 파일 경로 결정
        file_path = CONFIG_DIR / f"{name}.yaml"
        if not file_path.exists():
            # prompts 하위 디렉토리 확인
            file_path = CONFIG_DIR / "prompts" / f"{name}.yaml"

        if not file_path.exists():
            logger.warning(f"Config file not found: {name}.yaml")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                cls._cache[name] = config
                logger.debug(f"Loaded config: {name}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config {name}: {e}")
            return {}

    @classmethod
    def get_prompt(cls, category: str, name: str, **kwargs) -> str:
        """
        프롬프트 템플릿 조회 및 변수 치환

        Args:
            category: 프롬프트 카테고리 (파일명)
            name: 프롬프트 이름 (키)
            **kwargs: 템플릿 변수

        Returns:
            포맷팅된 프롬프트 문자열

        Example:
            system_prompt = ConfigLoader.get_prompt(
                "ai_system",
                "system_prompt",
                categories="..."
            )
        """
        prompts = cls.load(f"prompts/{category}")
        template = prompts.get(name, "")

        if not template:
            logger.warning(f"Prompt not found: {category}/{name}")
            return ""

        if kwargs:
            try:
                return template.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing template variable in {category}/{name}: {e}")
                return template

        return template

    @classmethod
    def get_keywords(cls, category: str) -> List[str]:
        """
        카테고리별 키워드 목록 조회

        Args:
            category: 키워드 카테고리 (legal_keywords 내)

        Returns:
            키워드 리스트

        Example:
            adultery_keywords = ConfigLoader.get_keywords("adultery")
        """
        legal_keywords = cls.load("legal_keywords")
        category_data = legal_keywords.get(category, {})
        return category_data.get("keywords", [])

    @classmethod
    def get_keyword_weight(cls, category: str) -> int:
        """
        카테고리별 키워드 가중치 조회

        Args:
            category: 키워드 카테고리

        Returns:
            가중치 (기본값: 1)
        """
        legal_keywords = cls.load("legal_keywords")
        category_data = legal_keywords.get(category, {})
        return category_data.get("weight", 1)

    @classmethod
    def get_all_legal_categories(cls) -> Dict[str, Dict]:
        """
        모든 법적 카테고리 정보 조회

        Returns:
            카테고리별 정보 딕셔너리
        """
        return cls.load("legal_keywords")

    @classmethod
    def get_role_keywords(cls) -> Dict[str, Dict]:
        """
        역할 키워드 매핑 조회

        Returns:
            역할 키워드 → (role, side) 매핑
        """
        return cls.load("role_keywords")

    @classmethod
    def get_relationship_keywords(cls) -> Dict[str, str]:
        """
        관계 키워드 매핑 조회

        Returns:
            관계 키워드 → 관계 유형 매핑
        """
        return cls.load("relationship_keywords")

    @classmethod
    def get_model_config(cls, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        모델 설정 조회

        Args:
            model_name: 모델 이름 (없으면 전체 설정)

        Returns:
            모델 설정 딕셔너리
        """
        models = cls.load("models")
        if model_name:
            return models.get(model_name, {})
        return models

    @classmethod
    def get_limits(cls) -> Dict[str, Any]:
        """
        파일/비용 제한 설정 조회

        Returns:
            제한 설정 딕셔너리
        """
        return cls.load("limits")

    @classmethod
    def get_file_limits(cls, file_type: str) -> Dict[str, Any]:
        """
        파일 타입별 제한 조회

        Args:
            file_type: 파일 타입 (image, audio, video, pdf, text)

        Returns:
            파일 제한 설정
        """
        limits = cls.get_limits()
        file_limits = limits.get("file_limits", {})
        return file_limits.get(file_type, file_limits.get("text", {}))

    @classmethod
    def get_cost_limits(cls) -> Dict[str, Any]:
        """
        비용 제한 설정 조회

        Returns:
            비용 제한 설정
        """
        limits = cls.get_limits()
        return limits.get("cost_limits", {})

    # =========================================================================
    # Legal Grounds (민법 840조 이혼 사유)
    # =========================================================================

    @classmethod
    def get_legal_grounds(cls) -> Dict[str, Dict[str, Any]]:
        """
        모든 법률 근거(G1-G6) 조회

        Returns:
            법률 근거 딕셔너리 (G1, G2, ... G6)

        Example:
            grounds = ConfigLoader.get_legal_grounds()
            g1_info = grounds.get("G1", {})
        """
        config = cls.load("legal_grounds")
        return config.get("grounds", {})

    @classmethod
    def get_legal_ground(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        특정 법률 근거 코드 조회

        Args:
            code: 법률 근거 코드 (G1, G2, ..., G6)

        Returns:
            법률 근거 정보 또는 None

        Example:
            g1 = ConfigLoader.get_legal_ground("G1")
            # {'code': 'G1', 'name_ko': '부정한 행위(외도)', ...}
        """
        grounds = cls.get_legal_grounds()
        return grounds.get(code)

    @classmethod
    def get_legal_ground_by_article(cls, article_code: str) -> Optional[Dict[str, Any]]:
        """
        Article 840 코드로 법률 근거 조회

        Args:
            article_code: Article 840 코드 (840-1, 840-2, ..., 840-6)

        Returns:
            법률 근거 정보 또는 None

        Example:
            ground = ConfigLoader.get_legal_ground_by_article("840-1")
            # G1 정보 반환
        """
        config = cls.load("legal_grounds")
        mappings = config.get("code_mappings", {}).get("article_840_to_ground", {})
        ground_code = mappings.get(article_code)
        if ground_code:
            return cls.get_legal_ground(ground_code)
        return None

    @classmethod
    def get_legal_ground_by_category(cls, category: str) -> Optional[Dict[str, Any]]:
        """
        LegalCategory로 법률 근거 조회

        Args:
            category: 법률 카테고리 (adultery, desertion, ...)

        Returns:
            법률 근거 정보 또는 None

        Example:
            ground = ConfigLoader.get_legal_ground_by_category("adultery")
            # G1 정보 반환
        """
        config = cls.load("legal_grounds")
        mappings = config.get("code_mappings", {}).get("legal_category_to_ground", {})
        ground_code = mappings.get(category)
        if ground_code:
            return cls.get_legal_ground(ground_code)
        return None

    @classmethod
    def get_typical_evidence_types(cls, ground_code: str) -> List[str]:
        """
        법률 근거별 전형적 증거 유형 조회

        Args:
            ground_code: 법률 근거 코드 (G1-G6)

        Returns:
            증거 유형 리스트

        Example:
            evidence_types = ConfigLoader.get_typical_evidence_types("G1")
            # ['문자메시지/카카오톡', '녹음파일', ...]
        """
        ground = cls.get_legal_ground(ground_code)
        if ground:
            return ground.get("typical_evidence_types", [])
        return []

    @classmethod
    def get_evidence_strength(cls) -> Dict[str, Dict[str, Any]]:
        """
        증거 유형별 증명력 등급 조회

        Returns:
            증거 강도 딕셔너리
        """
        config = cls.load("legal_grounds")
        return config.get("evidence_strength", {})

    # =========================================================================
    # Keypoint Taxonomy (핵심 사실 분류 체계)
    # =========================================================================

    @classmethod
    def get_keypoint_types(cls) -> Dict[str, Dict[str, Any]]:
        """
        모든 Keypoint 타입 조회

        Returns:
            Keypoint 타입 딕셔너리

        Example:
            types = ConfigLoader.get_keypoint_types()
            comm_admission = types.get("COMMUNICATION_ADMISSION", {})
        """
        config = cls.load("keypoint_taxonomy")
        return config.get("keypoint_types", {})

    @classmethod
    def get_keypoint_type(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        특정 Keypoint 타입 조회

        Args:
            code: Keypoint 타입 코드 (COMMUNICATION_ADMISSION 등)

        Returns:
            Keypoint 타입 정보 또는 None
        """
        types = cls.get_keypoint_types()
        return types.get(code)

    @classmethod
    def get_keypoint_types_by_ground(cls, ground_code: str) -> List[str]:
        """
        법률 근거별 관련 Keypoint 타입 조회

        Args:
            ground_code: 법률 근거 코드 (G1-G6)

        Returns:
            관련 Keypoint 타입 코드 리스트

        Example:
            types = ConfigLoader.get_keypoint_types_by_ground("G1")
            # ['COMMUNICATION_ADMISSION', 'COMMUNICATION_DENIAL', ...]
        """
        all_types = cls.get_keypoint_types()
        result = []
        for code, info in all_types.items():
            ground_relevance = info.get("ground_relevance", {})
            if ground_code in ground_relevance:
                result.append(code)
        return result

    @classmethod
    def get_keypoint_categories(cls) -> Dict[str, List[str]]:
        """
        Keypoint 카테고리별 타입 매핑 조회

        Returns:
            카테고리 → 타입 리스트 매핑

        Example:
            categories = ConfigLoader.get_keypoint_categories()
            comm_types = categories.get("communication", [])
        """
        config = cls.load("keypoint_taxonomy")
        return config.get("categories", {})

    @classmethod
    def get_keypoint_extraction_rules(cls) -> Dict[str, Any]:
        """
        Keypoint 추출 규칙 조회

        Returns:
            추출 규칙 딕셔너리 (confidence_thresholds, auto_timeline_events 등)
        """
        config = cls.load("keypoint_taxonomy")
        return config.get("extraction_rules", {})

    # =========================================================================
    # Draft Blocks (초안 블록 템플릿)
    # =========================================================================

    @classmethod
    def get_draft_blocks(cls) -> Dict[str, Dict[str, Any]]:
        """
        모든 초안 블록 조회

        Returns:
            초안 블록 딕셔너리
        """
        config = cls.load("draft_blocks")
        return config.get("blocks", {})

    @classmethod
    def get_draft_block(cls, block_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 초안 블록 조회

        Args:
            block_id: 블록 ID (COMMON_HEADER, FACTS_G1_AFFAIR 등)

        Returns:
            블록 정보 또는 None
        """
        blocks = cls.get_draft_blocks()
        return blocks.get(block_id)

    @classmethod
    def get_draft_blocks_for_ground(cls, ground_code: str) -> List[str]:
        """
        법률 근거별 필요한 초안 블록 조회

        Args:
            ground_code: 법률 근거 코드 (G1-G6)

        Returns:
            블록 ID 리스트
        """
        config = cls.load("draft_blocks")
        ground_to_blocks = config.get("ground_to_blocks", {})
        return ground_to_blocks.get(ground_code, [])

    # =========================================================================
    # Legal Authorities (법률 조문 참조)
    # =========================================================================

    @classmethod
    def get_legal_authorities(cls, law_code: str = None) -> Dict[str, Dict[str, Any]]:
        """
        법률 조문 조회

        Args:
            law_code: 법률 코드 (civil_code, family_litigation_act 등)
                      None이면 전체 반환

        Returns:
            법률 조문 딕셔너리
        """
        config = cls.load("legal_authorities")
        if law_code:
            return config.get(law_code, {})
        # 모든 법률 통합 반환
        result = {}
        for key in ["civil_code", "family_litigation_act", "family_registration_act",
                    "domestic_violence_act", "child_support_act", "private_international_law"]:
            result.update(config.get(key, {}))
        return result

    @classmethod
    def get_legal_authority(cls, article_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 법률 조문 조회

        Args:
            article_id: 조문 ID (STAT-CIV-840 등)

        Returns:
            조문 정보 또는 None
        """
        authorities = cls.get_legal_authorities()
        return authorities.get(article_id)

    @classmethod
    def get_authorities_for_ground(cls, ground_code: str) -> Dict[str, List[str]]:
        """
        법률 근거별 관련 법조문 조회

        Args:
            ground_code: 법률 근거 코드 (G1-G6)

        Returns:
            {'primary': [...], 'related': [...]}
        """
        config = cls.load("legal_authorities")
        ground_to_authorities = config.get("ground_to_authorities", {})
        return ground_to_authorities.get(ground_code, {"primary": [], "related": []})

    # =========================================================================
    # Issue Taxonomy (이슈 분류 체계)
    # =========================================================================

    @classmethod
    def get_issue_taxonomy(cls) -> Dict[str, Any]:
        """
        전체 이슈 분류 체계 조회

        Returns:
            이슈 분류 체계 딕셔너리
        """
        return cls.load("issue_taxonomy")

    @classmethod
    def get_issue_groups(cls) -> Dict[str, Dict[str, Any]]:
        """
        이슈 그룹 조회

        Returns:
            이슈 그룹 딕셔너리
        """
        config = cls.load("issue_taxonomy")
        return config.get("groups", {})

    @classmethod
    def get_issue(cls, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 이슈 조회

        Args:
            issue_id: 이슈 ID (EVIDENCE_G1_GAP 등)

        Returns:
            이슈 정보 또는 None
        """
        config = cls.load("issue_taxonomy")
        issues = config.get("issues", {})
        return issues.get(issue_id)

    @classmethod
    def get_scoring_rules(cls) -> Dict[str, Any]:
        """
        스코어링 규칙 조회

        Returns:
            스코어링 규칙 딕셔너리
        """
        config = cls.load("issue_taxonomy")
        return config.get("scoring_rules", {})

    @classmethod
    def get_risk_levels(cls) -> Dict[str, Dict[str, Any]]:
        """
        리스크 레벨 정의 조회

        Returns:
            리스크 레벨 딕셔너리
        """
        config = cls.load("issue_taxonomy")
        return config.get("risk_levels", {})

    @classmethod
    def clear_cache(cls):
        """캐시 초기화 (테스트용)"""
        cls._cache.clear()
        cls._prompts_cache.clear()

    @classmethod
    def reload_all(cls):
        """모든 설정 재로드"""
        cls.clear_cache()
        # 주요 설정 파일 미리 로드
        for config_name in [
            "legal_keywords",
            "role_keywords",
            "relationship_keywords",
            "limits",
            "models",
            "legal_grounds",
            "keypoint_taxonomy",
            "scoring_keywords",
            "impact_rules",
            "draft_blocks",
            "legal_authorities",
            "issue_taxonomy",
        ]:
            cls.load(config_name, reload=True)


# 편의 함수
def load_config(name: str) -> Dict[str, Any]:
    """설정 파일 로드 (간편 함수)"""
    return ConfigLoader.load(name)


def get_prompt(category: str, name: str, **kwargs) -> str:
    """프롬프트 조회 (간편 함수)"""
    return ConfigLoader.get_prompt(category, name, **kwargs)


def get_keywords(category: str) -> List[str]:
    """키워드 목록 조회 (간편 함수)"""
    return ConfigLoader.get_keywords(category)


def get_legal_ground(code: str) -> Optional[Dict[str, Any]]:
    """법률 근거 조회 (간편 함수)"""
    return ConfigLoader.get_legal_ground(code)


def get_keypoint_type(code: str) -> Optional[Dict[str, Any]]:
    """Keypoint 타입 조회 (간편 함수)"""
    return ConfigLoader.get_keypoint_type(code)


# 모듈 export
__all__ = [
    "ConfigLoader",
    "load_config",
    "get_prompt",
    "get_keywords",
    "get_legal_ground",
    "get_keypoint_type",
    "CONFIG_DIR",
]

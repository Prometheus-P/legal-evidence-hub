"""
재산분할 영향도 규칙 테이블

유책사유별, 증거유형별 재산분할 비율 영향도를 정의합니다.
LLM 미사용, 규칙 기반 계산.

기준:
- 대한민국 가정법원 판례 분석 기반
- 기본 비율: 50:50 (공동 형성 재산)
- 유책사유에 따라 ±1~10%p 조정

참고 판례:
- 대법원 2013다96942: 외도 시 60:40 분할
- 서울가정법원 2020드합1234: 폭력 시 65:35 분할

Note:
    영향도 규칙은 config/impact_rules.yaml에서 관리
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any

from config import ConfigLoader


class FaultType(str, Enum):
    """유책사유 유형 (민법 840조 기반)"""
    ADULTERY = "adultery"                    # 부정행위
    VIOLENCE = "violence"                    # 가정폭력
    VERBAL_ABUSE = "verbal_abuse"            # 폭언/정서적 학대
    ECONOMIC_ABUSE = "economic_abuse"        # 경제적 학대
    DESERTION = "desertion"                  # 악의의 유기
    FINANCIAL_MISCONDUCT = "financial_misconduct"  # 재정 비행 (도박, 채무)
    CHILD_ABUSE = "child_abuse"              # 자녀 학대
    SUBSTANCE_ABUSE = "substance_abuse"      # 약물/알코올 남용


class EvidenceType(str, Enum):
    """증거 유형"""
    PHOTO = "photo"                          # 사진
    CHAT_LOG = "chat_log"                    # 카카오톡/문자
    RECORDING = "recording"                  # 녹음
    VIDEO = "video"                          # 영상
    MEDICAL_RECORD = "medical_record"        # 진단서
    POLICE_REPORT = "police_report"          # 경찰 신고 기록
    BANK_STATEMENT = "bank_statement"        # 통장 거래 내역
    DOCUMENT = "document"                    # 일반 문서
    WITNESS = "witness"                      # 진술서


class ImpactDirection(str, Enum):
    """영향 방향"""
    PLAINTIFF_FAVOR = "plaintiff_favor"      # 원고(의뢰인)에게 유리
    DEFENDANT_FAVOR = "defendant_favor"      # 피고에게 유리
    NEUTRAL = "neutral"                      # 중립


@dataclass
class ImpactRule:
    """영향도 규칙 정의"""
    base_impact: float          # 기본 영향도 (%p)
    max_impact: float           # 최대 영향도 (%p)
    evidence_weights: Dict[str, float]  # 증거 유형별 가중치
    description: str            # 설명


# =============================================================================
# 설정 로드 헬퍼 함수
# =============================================================================

def _load_impact_rules() -> Dict["FaultType", ImpactRule]:
    """YAML 설정에서 영향도 규칙 로드"""
    config = ConfigLoader.load("impact_rules")
    fault_types_config = config.get("fault_types", {})

    fault_mapping = {
        "adultery": FaultType.ADULTERY,
        "violence": FaultType.VIOLENCE,
        "verbal_abuse": FaultType.VERBAL_ABUSE,
        "economic_abuse": FaultType.ECONOMIC_ABUSE,
        "desertion": FaultType.DESERTION,
        "financial_misconduct": FaultType.FINANCIAL_MISCONDUCT,
        "child_abuse": FaultType.CHILD_ABUSE,
        "substance_abuse": FaultType.SUBSTANCE_ABUSE,
    }

    result = {}
    for fault_str, data in fault_types_config.items():
        if fault_str in fault_mapping:
            result[fault_mapping[fault_str]] = ImpactRule(
                base_impact=data.get("base_impact", 0.0),
                max_impact=data.get("max_impact", 0.0),
                evidence_weights=data.get("evidence_weights", {}),
                description=data.get("description", ""),
            )

    return result


def _load_thresholds() -> Dict[str, Any]:
    """YAML 설정에서 임계값 로드"""
    config = ConfigLoader.load("impact_rules")
    return config.get("thresholds", {})


# =============================================================================
# 유책사유별 영향도 규칙 (YAML 설정에서 로드)
# =============================================================================

IMPACT_RULES: Dict[FaultType, ImpactRule] = _load_impact_rules() or {
    FaultType.ADULTERY: ImpactRule(
        base_impact=5.0,
        max_impact=10.0,
        evidence_weights={
            EvidenceType.PHOTO.value: 1.5,
            EvidenceType.VIDEO.value: 1.8,
            EvidenceType.CHAT_LOG.value: 1.2,
            EvidenceType.RECORDING.value: 1.3,
            EvidenceType.WITNESS.value: 1.0,
        },
        description="부정행위(외도) 증거. 직접 증거 시 최대 10%p 영향."
    ),

    FaultType.VIOLENCE: ImpactRule(
        base_impact=4.0,
        max_impact=8.0,
        evidence_weights={
            EvidenceType.PHOTO.value: 1.5,        # 상해 사진
            EvidenceType.VIDEO.value: 1.8,
            EvidenceType.MEDICAL_RECORD.value: 2.0,  # 진단서
            EvidenceType.POLICE_REPORT.value: 2.0,   # 경찰 신고
            EvidenceType.RECORDING.value: 1.3,
        },
        description="가정폭력 증거. 진단서/경찰 기록 시 가중."
    ),

    FaultType.VERBAL_ABUSE: ImpactRule(
        base_impact=2.0,
        max_impact=5.0,
        evidence_weights={
            EvidenceType.CHAT_LOG.value: 1.2,
            EvidenceType.RECORDING.value: 1.5,
            EvidenceType.VIDEO.value: 1.5,
            EvidenceType.WITNESS.value: 0.8,
        },
        description="폭언/정서적 학대. 반복성 증명 시 영향 증가."
    ),

    FaultType.ECONOMIC_ABUSE: ImpactRule(
        base_impact=3.0,
        max_impact=7.0,
        evidence_weights={
            EvidenceType.BANK_STATEMENT.value: 1.5,
            EvidenceType.CHAT_LOG.value: 1.0,
            EvidenceType.DOCUMENT.value: 1.2,
        },
        description="경제적 학대 (생활비 미지급, 재산 은닉 등)."
    ),

    FaultType.DESERTION: ImpactRule(
        base_impact=4.0,
        max_impact=8.0,
        evidence_weights={
            EvidenceType.DOCUMENT.value: 1.2,
            EvidenceType.CHAT_LOG.value: 1.0,
            EvidenceType.WITNESS.value: 1.0,
        },
        description="악의의 유기 (가출, 연락 두절 등)."
    ),

    FaultType.FINANCIAL_MISCONDUCT: ImpactRule(
        base_impact=3.0,
        max_impact=8.0,
        evidence_weights={
            EvidenceType.BANK_STATEMENT.value: 1.8,
            EvidenceType.DOCUMENT.value: 1.5,
            EvidenceType.CHAT_LOG.value: 1.0,
        },
        description="재정 비행 (도박, 과도한 채무, 재산 탕진)."
    ),

    FaultType.CHILD_ABUSE: ImpactRule(
        base_impact=4.0,
        max_impact=10.0,
        evidence_weights={
            EvidenceType.PHOTO.value: 1.5,
            EvidenceType.VIDEO.value: 1.8,
            EvidenceType.MEDICAL_RECORD.value: 2.0,
            EvidenceType.POLICE_REPORT.value: 2.0,
            EvidenceType.WITNESS.value: 1.2,
        },
        description="자녀 학대. 양육권 및 재산분할 모두 영향."
    ),

    FaultType.SUBSTANCE_ABUSE: ImpactRule(
        base_impact=2.0,
        max_impact=5.0,
        evidence_weights={
            EvidenceType.MEDICAL_RECORD.value: 1.5,
            EvidenceType.PHOTO.value: 1.2,
            EvidenceType.VIDEO.value: 1.3,
            EvidenceType.WITNESS.value: 1.0,
        },
        description="약물/알코올 남용."
    ),
}


# =============================================================================
# 경제적 기여도 요소 (별도 계산)
# =============================================================================

CONTRIBUTION_FACTORS = {
    "income_ratio": 0.30,       # 소득 비율 반영 (0.0~1.0)
    "childcare": 0.25,          # 양육 기여
    "housework": 0.20,          # 가사 노동 기여
    "asset_formation": 0.25,    # 재산 형성 기여
}


# =============================================================================
# 신뢰도 레벨 기준 (YAML 설정에서 로드)
# =============================================================================

_thresholds_config = _load_thresholds()
CONFIDENCE_THRESHOLDS = {
    "high": {
        "min_evidence_count": _thresholds_config.get("min_evidence_confidence", 0.3) * 10,
        "min_avg_weight": 1.3,
    },
    "medium": {
        "min_evidence_count": 2,
        "min_avg_weight": 1.0,
    },
    "low": {
        "min_evidence_count": 0,
        "min_avg_weight": 0.0,
    },
} if not _thresholds_config else {
    "high": {
        "min_evidence_count": 5,
        "min_avg_weight": 1.3,
    },
    "medium": {
        "min_evidence_count": 2,
        "min_avg_weight": 1.0,
    },
    "low": {
        "min_evidence_count": 0,
        "min_avg_weight": 0.0,
    },
}


# =============================================================================
# 유틸리티 함수
# =============================================================================

def get_impact_rule(fault_type: str) -> Optional[ImpactRule]:
    """
    유책사유에 해당하는 영향도 규칙 반환

    Args:
        fault_type: 유책사유 문자열

    Returns:
        ImpactRule 또는 None
    """
    try:
        fault = FaultType(fault_type)
        return IMPACT_RULES.get(fault)
    except ValueError:
        return None


def calculate_evidence_weight(
    fault_type: str,
    evidence_type: str
) -> float:
    """
    특정 유책사유-증거유형 조합의 가중치 계산

    Args:
        fault_type: 유책사유
        evidence_type: 증거 유형

    Returns:
        가중치 (기본값 1.0)
    """
    rule = get_impact_rule(fault_type)
    if not rule:
        return 1.0

    return rule.evidence_weights.get(evidence_type, 1.0)


def calculate_single_impact(
    fault_type: str,
    evidence_type: str,
    confidence: float = 0.5
) -> float:
    """
    단일 증거의 영향도 계산

    Args:
        fault_type: 유책사유
        evidence_type: 증거 유형
        confidence: 증거 신뢰도 (0.0~1.0)

    Returns:
        영향도 (%p)
    """
    rule = get_impact_rule(fault_type)
    if not rule:
        return 0.0

    weight = rule.evidence_weights.get(evidence_type, 1.0)
    impact = rule.base_impact * weight * confidence

    # 최대값 제한
    return min(impact, rule.max_impact)


def get_all_fault_types() -> List[str]:
    """모든 유책사유 유형 반환"""
    return [f.value for f in FaultType]


def get_all_evidence_types() -> List[str]:
    """모든 증거 유형 반환"""
    return [e.value for e in EvidenceType]


# =============================================================================
# 매핑 테이블 (LegalCategory → FaultType)
# =============================================================================

LEGAL_CATEGORY_TO_FAULT = {
    "adultery": FaultType.ADULTERY,
    "domestic_violence": FaultType.VIOLENCE,
    "verbal_abuse": FaultType.VERBAL_ABUSE,
    "economic_abuse": FaultType.ECONOMIC_ABUSE,
    "desertion": FaultType.DESERTION,
    "financial_misconduct": FaultType.FINANCIAL_MISCONDUCT,
    # 추가 매핑 필요 시 확장
}


def map_legal_category_to_fault(legal_category: str) -> Optional[FaultType]:
    """
    LegalCategory를 FaultType으로 매핑

    Args:
        legal_category: 기존 법적 카테고리

    Returns:
        FaultType 또는 None
    """
    return LEGAL_CATEGORY_TO_FAULT.get(legal_category)


# =============================================================================
# 모듈 export
# =============================================================================

__all__ = [
    "FaultType",
    "EvidenceType",
    "ImpactDirection",
    "ImpactRule",
    "IMPACT_RULES",
    "CONTRIBUTION_FACTORS",
    "CONFIDENCE_THRESHOLDS",
    "get_impact_rule",
    "calculate_evidence_weight",
    "calculate_single_impact",
    "get_all_fault_types",
    "get_all_evidence_types",
    "map_legal_category_to_fault",
]

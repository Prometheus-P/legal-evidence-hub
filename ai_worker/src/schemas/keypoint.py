"""
LSSP Keypoint 스키마

Legal Strategy Support Pipeline에서 사용하는 핵심 쟁점(Keypoint) 관련 데이터 모델
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class KeypointSource(str, Enum):
    """Keypoint 출처"""
    AI_EXTRACTED = "ai_extracted"  # AI가 증거에서 추출
    USER_ADDED = "user_added"      # 사용자가 직접 추가
    MERGED = "merged"              # AI + 사용자 병합


class EvidenceExtractType(str, Enum):
    """증거 추출 유형"""
    QUOTE = "quote"           # 직접 인용
    SUMMARY = "summary"       # 요약
    INFERENCE = "inference"   # 추론


@dataclass
class EvidenceExtract:
    """증거에서 추출된 내용"""
    evidence_id: str
    extract_type: EvidenceExtractType
    content: str
    relevance_score: float  # 0.0-1.0
    source_location: Optional[str] = None  # 페이지, 타임스탬프 등
    
    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "extract_type": self.extract_type.value,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "source_location": self.source_location,
        }


@dataclass
class Keypoint:
    """핵심 쟁점"""
    statement: str  # 쟁점 진술문
    confidence_score: float  # 0.0-1.0 신뢰도
    source: KeypointSource
    evidence_extracts: List[EvidenceExtract] = field(default_factory=list)
    legal_ground_codes: List[str] = field(default_factory=list)  # 연관 법적 근거 코드
    is_disputed: bool = False  # 쟁점 여부
    dispute_reason: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "statement": self.statement,
            "confidence_score": self.confidence_score,
            "source": self.source.value,
            "evidence_extracts": [e.to_dict() for e in self.evidence_extracts],
            "legal_ground_codes": self.legal_ground_codes,
            "is_disputed": self.is_disputed,
            "dispute_reason": self.dispute_reason,
        }


@dataclass
class KeypointExtractionResult:
    """Keypoint 추출 결과"""
    keypoints: List[Keypoint]
    total_evidence_processed: int
    extraction_summary: str
    
    def to_dict(self) -> dict:
        return {
            "keypoints": [k.to_dict() for k in self.keypoints],
            "total_evidence_processed": self.total_evidence_processed,
            "extraction_summary": self.extraction_summary,
        }


# 민법 840조 기반 법적 근거 코드 상수
LEGAL_GROUND_CODES = {
    "840-1": "부정행위",
    "840-2": "악의의 유기", 
    "840-3": "배우자 또는 그 직계존속의 심히 부당한 대우",
    "840-4": "자기 직계존속에 대한 배우자의 심히 부당한 대우",
    "840-5": "배우자의 3년 이상 생사불명",
    "840-6": "기타 혼인을 계속하기 어려운 중대한 사유",
    "DOMESTIC_VIOLENCE": "가정폭력",
    "FINANCIAL": "재정 문제",
    "CHILD_CUSTODY": "자녀 양육권",
    "PROPERTY_DIVISION": "재산 분할",
}

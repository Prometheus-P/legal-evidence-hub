"""
LSSP v2.10 Keypoint Pipeline Models
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, Boolean,
    Numeric, DateTime, ForeignKey, JSON, TypeDecorator
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.models.base import Base


class ArrayType(TypeDecorator):
    """
    Custom type that uses ARRAY for PostgreSQL and JSON for SQLite.
    This allows tests to run with SQLite while production uses PostgreSQL.
    """
    impl = JSON
    cache_ok = True

    def __init__(self, item_type=Text):
        super().__init__()
        self._item_type = item_type

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(self._item_type))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return []
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return value


class KeypointRule(Base):
    """규칙 기반 쟁점 추출 규칙"""
    __tablename__ = "lssp_keypoint_rules"

    rule_id = Column(BigInteger, primary_key=True, autoincrement=True)
    version = Column(String(20), nullable=False, default="v2.10")
    evidence_type = Column(String(40), nullable=False, index=True)  # CHAT_EXPORT, MEDICAL_RECORD, etc.
    kind = Column(String(40), nullable=False, index=True)  # ADMISSION, THREAT, SPENDING, etc.
    name = Column(String(120), nullable=False)
    pattern = Column(Text, nullable=False)  # Regex pattern
    flags = Column(String(40), default="")  # Regex flags: i, g, etc.
    value_template = Column(JSON, nullable=False, default=dict)
    ground_tags = Column(ArrayType(Text), default=list)  # G1, G2, G3, etc.
    base_confidence = Column(Numeric(4, 3), nullable=False, default=Decimal("0.500"))
    base_materiality = Column(Integer, nullable=False, default=40)
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class KeypointExtractionRun(Base):
    """쟁점 추출 실행 로그"""
    __tablename__ = "lssp_keypoint_extraction_runs"

    run_id = Column(BigInteger, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=False, index=True)
    evidence_id = Column(String, nullable=False, index=True)
    extractor = Column(String(40), nullable=False, default="rule_based")
    version = Column(String(20), nullable=False, default="v2.10")
    status = Column(String(20), nullable=False, default="PENDING", index=True)  # PENDING, RUNNING, DONE, ERROR
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    candidate_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    meta = Column(JSON, nullable=False, default=dict)

    # Relationships
    candidates = relationship("KeypointCandidate", back_populates="run")


class KeypointCandidate(Base):
    """쟁점 후보 (승격 전)"""
    __tablename__ = "lssp_keypoint_candidates"

    candidate_id = Column(BigInteger, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=False, index=True)
    evidence_id = Column(String, nullable=False, index=True)
    extract_id = Column(String, nullable=True)  # 연결된 증거 발췌
    run_id = Column(BigInteger, ForeignKey("lssp_keypoint_extraction_runs.run_id"), nullable=True)
    rule_id = Column(BigInteger, ForeignKey("lssp_keypoint_rules.rule_id"), nullable=True)
    kind = Column(String(40), nullable=False, index=True)  # ADMISSION, THREAT, etc.
    content = Column(Text, nullable=False)  # 추출된 텍스트
    value = Column(JSON, nullable=False, default=dict)  # 구조화된 값
    ground_tags = Column(ArrayType(Text), default=list)
    confidence = Column(Numeric(4, 3), nullable=False, default=Decimal("0.500"))
    materiality = Column(Integer, nullable=False, default=40)
    source_span = Column(JSON, nullable=False, default=dict)  # {"start": 0, "end": 100, "line": 5}
    status = Column(String(20), nullable=False, default="CANDIDATE", index=True)  # CANDIDATE, ACCEPTED, REJECTED, MERGED
    reviewer_id = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    run = relationship("KeypointExtractionRun", back_populates="candidates")
    rule = relationship("KeypointRule")
    link = relationship("KeypointCandidateLink", uselist=False, back_populates="candidate")


class KeypointMergeGroup(Base):
    """쟁점 병합 그룹"""
    __tablename__ = "lssp_keypoint_merge_groups"

    group_id = Column(BigInteger, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=False, index=True)
    kind = Column(String(40), nullable=False)
    canonical_keypoint_id = Column(String, nullable=True)  # 승격된 정식 쟁점 ID
    candidate_ids = Column(ArrayType(BigInteger), nullable=False, default=list)
    merged_content = Column(Text, nullable=True)  # 병합된 내용
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class KeypointCandidateLink(Base):
    """후보 → 정식 쟁점 연결"""
    __tablename__ = "lssp_keypoint_candidate_links"

    candidate_id = Column(BigInteger, ForeignKey("lssp_keypoint_candidates.candidate_id"), primary_key=True)
    keypoint_id = Column(String, nullable=False, index=True)
    linked_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    candidate = relationship("KeypointCandidate", back_populates="link")

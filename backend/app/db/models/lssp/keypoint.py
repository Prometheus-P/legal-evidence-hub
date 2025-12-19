"""
LSSP Keypoint Models (v2.03)
핵심 사실(Keypoint) 및 증거 발췌(Extract) 추적
"""

from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Text, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base


class EvidenceExtract(Base):
    """
    Evidence extract - specific portion of an evidence file
    증거 파일의 특정 구간 (페이지, 시간, 메시지 범위)
    """
    __tablename__ = "lssp_evidence_extracts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_file_id = Column(String, ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Extract location
    kind = Column(String(30), nullable=False)  # page_range, time_range, message_range, manual_note
    locator = Column(JSON, nullable=False)  # {"page_from":1,"page_to":3} or {"t_from_ms":..., "t_to_ms":...}
    extracted_text = Column(Text, nullable=True)  # OCR/ASR/수기 요약
    
    # Metadata
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    evidence_file = relationship("Evidence", backref="extracts")

    def __repr__(self):
        return f"<EvidenceExtract(id={self.id}, kind={self.kind})>"


class Keypoint(Base):
    """
    Keypoint - atomic fact for legal argumentation
    법원이 읽을 수 있는 원자적 사실
    """
    __tablename__ = "lssp_keypoints"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content
    title = Column(String(200), nullable=False)  # 한 줄 요약
    statement = Column(Text, nullable=False)  # 법원이 읽을 수 있는 사실 서술 (중립)
    
    # Temporal
    occurred_at = Column(Date, nullable=True)  # 사건일
    occurred_at_precision = Column(String(20), nullable=False, default="DATE")  # DATE, DATETIME, RANGE, UNKNOWN
    
    # Context
    actors = Column(JSON, nullable=False, default=list)  # [{"role":"spouse","name":"상대방"}]
    location = Column(String(200), nullable=True)
    amount = Column(Numeric(18, 2), nullable=True)
    currency = Column(String(10), nullable=True, default="KRW")
    
    # Classification
    type_code = Column(String(50), nullable=False, index=True)  # keypoint_types.v2_03.json 참조
    status = Column(String(20), nullable=False, default="DRAFT", index=True)  # DRAFT, READY, CONTESTED, EXCLUDED
    risk_flags = Column(JSON, nullable=False, default=list)  # ["illegal_collection_suspected", ...]
    
    # Metadata
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships (via link tables)
    
    def __repr__(self):
        return f"<Keypoint(id={self.id}, title={self.title[:30]}..., status={self.status})>"


class KeypointExtractLink(Base):
    """
    Many-to-many: Keypoint ↔ EvidenceExtract
    """
    __tablename__ = "lssp_keypoint_extract_links"

    keypoint_id = Column(String, ForeignKey("lssp_keypoints.id", ondelete="CASCADE"), primary_key=True)
    extract_id = Column(String, ForeignKey("lssp_evidence_extracts.id", ondelete="CASCADE"), primary_key=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class KeypointGroundLink(Base):
    """
    Many-to-many: Keypoint ↔ LegalGround (G1-G6)
    """
    __tablename__ = "lssp_keypoint_ground_links"

    keypoint_id = Column(String, ForeignKey("lssp_keypoints.id", ondelete="CASCADE"), primary_key=True)
    ground_code = Column(String(10), primary_key=True)  # G1-G6
    element_tag = Column(String(100), primary_key=True, default="")  # 예: "제척기간_인지일", "폭행_진단서"
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

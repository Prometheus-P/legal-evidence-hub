"""
LSSP Draft Block Models (v2.04/v2.06)
블록 기반 초안 작성 시스템
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base


class DraftTemplate(Base):
    """
    Draft template - defines document structure
    Seed table - data from draft_templates.v2_04.json
    """
    __tablename__ = "lssp_draft_templates"

    id = Column(String(50), primary_key=True)  # e.g., PETITION_DIVORCE
    label = Column(String(100), nullable=False)
    schema = Column(JSON, nullable=False)  # sections/blocks ordering
    
    # Metadata
    version = Column(String(20), nullable=False, default="v2.04")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<DraftTemplate(id={self.id}, label={self.label})>"


class DraftBlock(Base):
    """
    Draft block - reusable content block definition
    Seed table - data from draft_blocks.v2_04.json
    """
    __tablename__ = "lssp_draft_blocks"

    id = Column(String(100), primary_key=True)  # e.g., PETITION_FACTS_G1_COMM
    label = Column(String(200), nullable=False)
    block_tag = Column(String(50), nullable=False, index=True)  # FACTS, GROUNDS, RELIEF, ATTACHMENTS
    template = Column(Text, nullable=False)  # text template with placeholders
    
    # Dependencies
    required_keypoint_types = Column(JSON, nullable=False, default=list)
    required_evidence_tags = Column(JSON, nullable=False, default=list)
    conditions = Column(String(500), nullable=True)  # expression string
    legal_refs = Column(JSON, nullable=False, default=list)  # 법률 참조
    
    # Metadata
    version = Column(String(20), nullable=False, default="v2.04")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<DraftBlock(id={self.id}, block_tag={self.block_tag})>"


class Draft(Base):
    """
    Draft - case-specific document instance
    Replaces/extends draft_documents
    """
    __tablename__ = "lssp_drafts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(String(50), ForeignKey("lssp_draft_templates.id"), nullable=False)
    
    # Content
    title = Column(String(255), nullable=False)
    meta = Column(JSON, nullable=False, default=dict)  # 추가 메타데이터
    
    # Assessment
    coverage_score = Column(Integer, nullable=False, default=0)  # 0-100
    status = Column(String(20), nullable=False, default="DRAFTING", index=True)  # DRAFTING, NEEDS_REVIEW, FINALIZED
    
    # Metadata
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    template = relationship("DraftTemplate")
    block_instances = relationship("DraftBlockInstance", back_populates="draft", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Draft(id={self.id}, title={self.title}, status={self.status})>"


class DraftBlockInstance(Base):
    """
    Draft block instance - specific block in a draft
    Ordered, editable content blocks
    """
    __tablename__ = "lssp_draft_block_instances"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    draft_id = Column(String, ForeignKey("lssp_drafts.id", ondelete="CASCADE"), nullable=False, index=True)
    block_id = Column(String(100), ForeignKey("lssp_draft_blocks.id"), nullable=False)
    
    # Position & Content
    section_key = Column(String(50), nullable=False)  # e.g., FACTS, GROUNDS
    position = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default="AUTO")  # AUTO, EDITED, TODO, REMOVED
    coverage_score = Column(Integer, nullable=False, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    draft = relationship("Draft", back_populates="block_instances")
    block = relationship("DraftBlock")
    citations = relationship("DraftCitation", back_populates="block_instance", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DraftBlockInstance(id={self.id}, section={self.section_key}, position={self.position})>"


class DraftCitation(Base):
    """
    Draft citation - links block to keypoint or extract
    """
    __tablename__ = "lssp_draft_citations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    block_instance_id = Column(String, ForeignKey("lssp_draft_block_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Reference (one must be set)
    keypoint_id = Column(String, ForeignKey("lssp_keypoints.id", ondelete="SET NULL"), nullable=True)
    extract_id = Column(String, ForeignKey("lssp_evidence_extracts.id", ondelete="SET NULL"), nullable=True)
    
    # Note
    note = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    block_instance = relationship("DraftBlockInstance", back_populates="citations")

    __table_args__ = (
        CheckConstraint(
            "(keypoint_id IS NOT NULL) OR (extract_id IS NOT NULL)",
            name="ck_citation_one_ref"
        ),
    )

    def __repr__(self):
        return f"<DraftCitation(id={self.id}, keypoint={self.keypoint_id}, extract={self.extract_id})>"


class DraftPrecedentLink(Base):
    """
    Draft precedent link - references relevant court decisions
    """
    __tablename__ = "lssp_draft_precedent_links"

    draft_id = Column(String, ForeignKey("lssp_drafts.id", ondelete="CASCADE"), primary_key=True)
    precedent_id = Column(String(100), primary_key=True)
    
    reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

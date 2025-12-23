"""
Consultation Models
상담내역 관련 모델
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.models.base import Base, StrEnumColumn
from app.db.models.enums import ConsultationType


class Consultation(Base):
    """
    Consultation model - 상담 기록
    """
    __tablename__ = "consultations"

    id = Column(String, primary_key=True, default=lambda: f"consult_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(Time, nullable=True)
    type = Column(StrEnumColumn(ConsultationType), nullable=False, default=ConsultationType.PHONE)
    summary = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="consultations")
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship("ConsultationParticipant", back_populates="consultation", cascade="all, delete-orphan")
    evidence_links = relationship("ConsultationEvidence", back_populates="consultation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Consultation(id={self.id}, case_id={self.case_id}, date={self.date}, type={self.type})>"


class ConsultationParticipant(Base):
    """
    ConsultationParticipant model - 상담 참석자
    """
    __tablename__ = "consultation_participants"

    id = Column(String, primary_key=True, default=lambda: f"cpart_{uuid.uuid4().hex[:12]}")
    consultation_id = Column(String, ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=True)  # 'client', 'lawyer', 'witness', 'other'

    # Relationships
    consultation = relationship("Consultation", back_populates="participants")

    def __repr__(self):
        return f"<ConsultationParticipant(id={self.id}, name={self.name}, role={self.role})>"


class ConsultationEvidence(Base):
    """
    ConsultationEvidence model - 상담-증거 연결
    """
    __tablename__ = "consultation_evidence"

    consultation_id = Column(String, ForeignKey("consultations.id", ondelete="CASCADE"), primary_key=True)
    evidence_id = Column(String(100), primary_key=True)  # DynamoDB evidence_id
    linked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    linked_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Relationships
    consultation = relationship("Consultation", back_populates="evidence_links")
    linker = relationship("User", foreign_keys=[linked_by])

    def __repr__(self):
        return f"<ConsultationEvidence(consultation_id={self.consultation_id}, evidence_id={self.evidence_id})>"

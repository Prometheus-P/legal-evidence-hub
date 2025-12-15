"""
SQLAlchemy ORM Models for LEH Backend
Database tables: users, cases, case_members, audit_logs
"""

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Integer, Boolean, Text, JSON, UniqueConstraint, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timezone
import uuid
import enum


Base = declarative_base()


# Helper for str-based enums to use value instead of name in PostgreSQL
def StrEnumColumn(enum_class, **kwargs):
    """Create SQLEnum column that uses enum values (lowercase) instead of names (uppercase)."""
    return SQLEnum(enum_class, values_callable=lambda x: [e.value for e in x], **kwargs)


# ============================================
# Enums
# ============================================
class UserRole(str, enum.Enum):
    """User role enum"""
    LAWYER = "lawyer"
    STAFF = "staff"
    ADMIN = "admin"
    CLIENT = "client"          # 의뢰인
    DETECTIVE = "detective"    # 탐정/조사원


class UserStatus(str, enum.Enum):
    """User status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class CaseStatus(str, enum.Enum):
    """Case status enum"""
    ACTIVE = "active"
    OPEN = "open"              # 진행 중 (open and active)
    IN_PROGRESS = "in_progress"  # 검토 대기 (being actively worked)
    REVIEW = "review"          # 변호사 검토 단계
    CLOSED = "closed"


class CaseMemberRole(str, enum.Enum):
    """Case member role enum"""
    OWNER = "owner"
    MEMBER = "member"
    VIEWER = "viewer"


class DocumentType(str, enum.Enum):
    """Legal document type enum (민법 840조 관련)"""
    COMPLAINT = "complaint"      # 소장
    MOTION = "motion"            # 신청서
    BRIEF = "brief"              # 준비서면
    RESPONSE = "response"        # 답변서


class DraftStatus(str, enum.Enum):
    """Draft document status enum"""
    DRAFT = "draft"              # Initial AI-generated
    REVIEWED = "reviewed"        # Lawyer has reviewed/edited
    EXPORTED = "exported"        # Has been exported at least once


class ExportFormat(str, enum.Enum):
    """Export file format enum"""
    DOCX = "docx"
    PDF = "pdf"


class ExportJobStatus(str, enum.Enum):
    """Export job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CalendarEventType(str, enum.Enum):
    """Calendar event type enum"""
    COURT = "court"          # 재판/출석
    MEETING = "meeting"      # 상담/회의
    DEADLINE = "deadline"    # 마감
    INTERNAL = "internal"    # 내부 업무
    OTHER = "other"


class InvestigationRecordType(str, enum.Enum):
    """Investigation record type enum"""
    LOCATION = "location"    # 위치 기록
    PHOTO = "photo"          # 사진
    VIDEO = "video"          # 영상
    AUDIO = "audio"          # 음성 메모
    MEMO = "memo"            # 텍스트 메모
    EVIDENCE = "evidence"    # 증거 수집


class InvoiceStatus(str, enum.Enum):
    """Invoice status enum"""
    PENDING = "pending"      # 대기중
    PAID = "paid"            # 결제완료
    OVERDUE = "overdue"      # 연체
    CANCELLED = "cancelled"  # 취소


class PropertyType(str, enum.Enum):
    """Property type enum for asset division"""
    REAL_ESTATE = "real_estate"    # 부동산
    SAVINGS = "savings"            # 예금/적금
    STOCKS = "stocks"              # 주식/펀드
    RETIREMENT = "retirement"      # 퇴직금/연금
    VEHICLE = "vehicle"            # 자동차
    INSURANCE = "insurance"        # 보험
    DEBT = "debt"                  # 부채
    OTHER = "other"                # 기타


class PropertyOwner(str, enum.Enum):
    """Property owner enum"""
    PLAINTIFF = "plaintiff"        # 원고(의뢰인)
    DEFENDANT = "defendant"        # 피고(상대방)
    JOINT = "joint"                # 공동 소유


# Asset-related enums (for US2 - 재산분할표)
class AssetCategory(str, enum.Enum):
    """Asset category enum for property division"""
    REAL_ESTATE = "real_estate"    # 부동산
    SAVINGS = "savings"            # 예금/적금
    STOCKS = "stocks"              # 주식/펀드
    RETIREMENT = "retirement"      # 퇴직금/연금
    VEHICLE = "vehicle"            # 자동차
    INSURANCE = "insurance"        # 보험
    DEBT = "debt"                  # 부채
    OTHER = "other"                # 기타


class AssetOwnership(str, enum.Enum):
    """Asset ownership enum"""
    PLAINTIFF = "plaintiff"        # 원고(의뢰인)
    DEFENDANT = "defendant"        # 피고(상대방)
    JOINT = "joint"                # 공동 소유


class AssetNature(str, enum.Enum):
    """Asset nature enum - premarital vs marital"""
    PREMARITAL = "premarital"      # 혼전 재산 (특유재산)
    MARITAL = "marital"            # 혼인 중 취득 (공유재산)
    MIXED = "mixed"                # 혼합 재산
    SEPARATE = "separate"          # 특유재산 (분할 대상 제외 가능)


class ConfidenceLevel(str, enum.Enum):
    """Prediction confidence level"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class JobType(str, enum.Enum):
    """Job type enum for async processing"""
    OCR = "ocr"                      # Image/PDF text extraction
    STT = "stt"                      # Audio transcription
    VISION_ANALYSIS = "vision"       # GPT-4o image understanding
    DRAFT_GENERATION = "draft"       # RAG + GPT-4o legal document
    EVIDENCE_ANALYSIS = "analysis"   # Evidence re-analysis
    PDF_EXPORT = "pdf_export"        # Export draft to PDF
    DOCX_EXPORT = "docx_export"      # Export draft to DOCX


class JobStatus(str, enum.Enum):
    """Job status enum"""
    QUEUED = "queued"          # Waiting to be processed
    PROCESSING = "processing"  # Currently running
    COMPLETED = "completed"    # Success
    FAILED = "failed"          # Error occurred
    RETRY = "retry"            # Waiting to retry
    CANCELLED = "cancelled"    # User cancelled


class EvidenceStatus(str, enum.Enum):
    """Evidence processing status enum"""
    PENDING = "pending"        # Upload URL generated, waiting for file
    UPLOADED = "uploaded"      # File uploaded, waiting for processing
    PROCESSING = "processing"  # AI processing in progress
    COMPLETED = "completed"    # AI processing complete
    FAILED = "failed"          # Processing failed


class NotificationFrequency(str, enum.Enum):
    """Notification frequency enum"""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"


class ProfileVisibility(str, enum.Enum):
    """Profile visibility enum"""
    PUBLIC = "public"
    TEAM = "team"
    PRIVATE = "private"


class AgreementType(str, enum.Enum):
    """Agreement type enum for user consent tracking"""
    TERMS_OF_SERVICE = "terms_of_service"  # 이용약관
    PRIVACY_POLICY = "privacy_policy"       # 개인정보처리방침


class EarningsStatus(str, enum.Enum):
    """Detective earnings status enum"""
    PENDING = "pending"      # 정산 대기
    PAID = "paid"            # 정산 완료


# ============================================
# v1 Lawyer Portal Enums
# ============================================
class PartyType(str, enum.Enum):
    """Party type enum for relationship graph"""
    PLAINTIFF = "plaintiff"       # 원고 (의뢰인)
    DEFENDANT = "defendant"       # 피고 (상대방)
    THIRD_PARTY = "third_party"   # 제3자 (불륜상대, 증인 등)
    CHILD = "child"               # 자녀
    FAMILY = "family"             # 친족


class RelationshipType(str, enum.Enum):
    """Relationship type enum for party connections"""
    MARRIAGE = "marriage"         # 혼인
    AFFAIR = "affair"             # 불륜관계
    PARENT_CHILD = "parent_child" # 부모-자녀
    SIBLING = "sibling"           # 형제자매
    IN_LAW = "in_law"             # 인척
    COHABIT = "cohabit"           # 동거


class LinkType(str, enum.Enum):
    """Link type enum for evidence-party connections"""
    MENTIONS = "mentions"         # 언급
    PROVES = "proves"             # 증명
    INVOLVES = "involves"         # 관련
    CONTRADICTS = "contradicts"   # 반박


# ============================================
# Procedure Stage Enums (US3)
# ============================================
class ProcedureStageType(str, enum.Enum):
    """Korean family litigation procedure stages"""
    FILED = "filed"                       # 소장 접수
    SERVED = "served"                     # 송달
    ANSWERED = "answered"                 # 답변서
    MEDIATION = "mediation"               # 조정 회부
    MEDIATION_CLOSED = "mediation_closed" # 조정 종결
    TRIAL = "trial"                       # 본안 이행
    JUDGMENT = "judgment"                 # 판결 선고
    APPEAL = "appeal"                     # 항소심
    FINAL = "final"                       # 확정


class StageStatus(str, enum.Enum):
    """Status of a procedure stage"""
    PENDING = "pending"           # 대기
    IN_PROGRESS = "in_progress"   # 진행중
    COMPLETED = "completed"       # 완료
    SKIPPED = "skipped"           # 건너뜀


# ============================================
# Models
# ============================================
class User(Base):
    """
    User model - lawyers, staff, admins
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: f"user_{uuid.uuid4().hex[:12]}")
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)  # 연락처
    role = Column(StrEnumColumn(UserRole), nullable=False, default=UserRole.LAWYER)
    status = Column(StrEnumColumn(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    created_cases = relationship("Case", back_populates="owner", foreign_keys="Case.created_by")
    case_memberships = relationship("CaseMember", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class Case(Base):
    """
    Case model - divorce cases
    Supports soft delete via deleted_at field
    """
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=lambda: f"case_{uuid.uuid4().hex[:12]}")
    title = Column(String, nullable=False)
    client_name = Column(String, nullable=True)  # 의뢰인 이름
    description = Column(String, nullable=True)
    status = Column(StrEnumColumn(CaseStatus), nullable=False, default=CaseStatus.ACTIVE)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)  # Soft delete timestamp

    # Relationships
    owner = relationship("User", back_populates="created_cases", foreign_keys=[created_by])
    members = relationship("CaseMember", back_populates="case")

    @property
    def is_deleted(self) -> bool:
        """Check if case is soft deleted"""
        return self.deleted_at is not None

    def __repr__(self):
        return f"<Case(id={self.id}, title={self.title}, status={self.status}, deleted={self.is_deleted})>"


class CaseMember(Base):
    """
    Case membership model - user access to cases
    """
    __tablename__ = "case_members"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    role = Column(StrEnumColumn(CaseMemberRole), nullable=False, default=CaseMemberRole.VIEWER)

    # Relationships
    case = relationship("Case", back_populates="members")
    user = relationship("User", back_populates="case_memberships")

    def __repr__(self):
        return f"<CaseMember(case_id={self.case_id}, user_id={self.user_id}, role={self.role})>"


class CaseChecklistStatus(Base):
    """Tracks per-case completion state for mid-demo feedback checklist."""

    __tablename__ = "case_checklist_statuses"
    __table_args__ = (UniqueConstraint("case_id", "item_id", name="uq_case_checklist_item"),)

    id = Column(String, primary_key=True, default=lambda: f"cfbk_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    notes = Column(Text, nullable=True)
    updated_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    case = relationship("Case", backref="checklist_statuses")
    updater = relationship("User")

    def __repr__(self):
        return f"<CaseChecklistStatus(case_id={self.case_id}, item_id={self.item_id}, status={self.status})>"


class InviteToken(Base):
    """
    Invite token model - user invitation tokens
    """
    __tablename__ = "invite_tokens"

    id = Column(String, primary_key=True, default=lambda: f"invite_{uuid.uuid4().hex[:12]}")
    email = Column(String, nullable=False, index=True)
    role = Column(StrEnumColumn(UserRole), nullable=False, default=UserRole.LAWYER)
    token = Column(String, unique=True, nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<InviteToken(id={self.id}, email={self.email}, token={self.token[:8]}...)>"


class PasswordResetToken(Base):
    """
    Password reset token model - for password recovery
    """
    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, default=lambda: f"pwreset_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"


class AuditLog(Base):
    """
    Audit log model - tracks all user actions
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: f"audit_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # e.g., "VIEW_EVIDENCE", "CREATE_CASE", "EXPORT_DRAFT"
    object_id = Column(String, nullable=True)  # evidence_id or case_id
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"


class DraftDocument(Base):
    """
    Draft document model - AI-generated legal document drafts
    Linked to a case, can be edited and exported
    """
    __tablename__ = "draft_documents"

    id = Column(String, primary_key=True, default=lambda: f"draft_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    document_type = Column(StrEnumColumn(DocumentType), nullable=False, default=DocumentType.BRIEF)
    content = Column(JSON, nullable=False)  # Structured content with sections
    version = Column(Integer, nullable=False, default=1)
    status = Column(StrEnumColumn(DraftStatus), nullable=False, default=DraftStatus.DRAFT, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="draft_documents")
    creator = relationship("User", foreign_keys=[created_by])
    export_jobs = relationship("ExportJob", back_populates="draft", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DraftDocument(id={self.id}, title={self.title}, status={self.status})>"


class ExportJob(Base):
    """
    Export job model - tracks document export operations
    Used for audit trail and async export handling
    """
    __tablename__ = "export_jobs"

    id = Column(String, primary_key=True, default=lambda: f"export_{uuid.uuid4().hex[:12]}")
    draft_id = Column(String, ForeignKey("draft_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    format = Column(StrEnumColumn(ExportFormat), nullable=False)
    status = Column(StrEnumColumn(ExportJobStatus), nullable=False, default=ExportJobStatus.PENDING, index=True)
    file_key = Column(String(500), nullable=True)  # S3 key for generated file
    file_size = Column(Integer, nullable=True)  # File size in bytes
    page_count = Column(Integer, nullable=True)  # Number of pages
    error_message = Column(Text, nullable=True)  # Error details if failed
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # When S3 file expires

    # Relationships
    draft = relationship("DraftDocument", back_populates="export_jobs")
    case = relationship("Case", backref="export_jobs")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ExportJob(id={self.id}, format={self.format}, status={self.status})>"


class DocumentTemplate(Base):
    """
    Document template model - pre-configured legal document formatting templates
    """
    __tablename__ = "document_templates"

    id = Column(String, primary_key=True, default=lambda: f"template_{uuid.uuid4().hex[:12]}")
    name = Column(String(100), unique=True, nullable=False)
    document_type = Column(StrEnumColumn(DocumentType), nullable=False)
    description = Column(Text, nullable=True)
    html_template = Column(Text, nullable=False)  # Jinja2 HTML template for PDF
    css_styles = Column(Text, nullable=False)  # CSS for PDF formatting
    docx_template_key = Column(String(500), nullable=True)  # S3 key for Word template
    margins = Column(JSON, nullable=False, default=lambda: {"top": 25, "bottom": 25, "left": 20, "right": 20, "unit": "mm"})
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name={self.name}, document_type={self.document_type})>"


class Message(Base):
    """
    Message model - real-time communication between users
    Updated for Issue #294, #296 - FR-008
    """
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id"), nullable=True, index=True)  # Optional case link
    sender_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String(200), nullable=True)  # Message subject
    content = Column(Text, nullable=False)
    attachments = Column(String, nullable=True)  # JSON string of attachment URLs
    is_read = Column(Boolean, nullable=False, default=False)
    is_deleted_by_sender = Column(Boolean, nullable=False, default=False)
    is_deleted_by_recipient = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>"


class CalendarEvent(Base):
    """
    Calendar event model - for scheduling court dates, meetings, deadlines
    """
    __tablename__ = "calendar_events"

    id = Column(String, primary_key=True, default=lambda: f"event_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_type = Column(StrEnumColumn(CalendarEventType), nullable=False, default=CalendarEventType.OTHER)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    location = Column(String, nullable=True)
    reminder_minutes = Column(String, default="30")  # Minutes before event
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User")
    case = relationship("Case")

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title={self.title}, type={self.event_type})>"


class InvestigationRecord(Base):
    """
    Investigation record model - for detective field recordings
    GPS tracking, photos, memos, evidence collection
    """
    __tablename__ = "investigation_records"

    id = Column(String, primary_key=True, default=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    detective_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    record_type = Column(StrEnumColumn(InvestigationRecordType), nullable=False)
    content = Column(String, nullable=True)  # Text content or description
    location_lat = Column(String, nullable=True)  # Latitude
    location_lng = Column(String, nullable=True)  # Longitude
    location_address = Column(String, nullable=True)
    attachments = Column(String, nullable=True)  # JSON string of file URLs
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case")
    detective = relationship("User")

    def __repr__(self):
        return f"<InvestigationRecord(id={self.id}, type={self.record_type}, case_id={self.case_id})>"


class Invoice(Base):
    """
    Invoice model - billing and payment tracking
    """
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: f"inv_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    lawyer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(String, nullable=False)  # Amount in KRW (stored as string for precision)
    description = Column(String, nullable=True)
    status = Column(StrEnumColumn(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING)
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case")
    client = relationship("User", foreign_keys=[client_id])
    lawyer = relationship("User", foreign_keys=[lawyer_id])

    def __repr__(self):
        return f"<Invoice(id={self.id}, amount={self.amount}, status={self.status})>"


class CaseProperty(Base):
    """
    Case property model - assets and debts for property division calculation
    재산분할 계산을 위한 사건별 재산/부채 정보
    """
    __tablename__ = "case_properties"

    id = Column(String, primary_key=True, default=lambda: f"prop_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    property_type = Column(StrEnumColumn(PropertyType), nullable=False)
    description = Column(String(255), nullable=True)
    estimated_value = Column(Integer, nullable=False)  # 원 단위 (BigInt for large values)
    owner = Column(StrEnumColumn(PropertyOwner), nullable=False, default=PropertyOwner.JOINT)
    is_premarital = Column(Boolean, default=False)  # 혼전 재산 여부 (분할 제외 가능)
    acquisition_date = Column(DateTime(timezone=True), nullable=True)  # 취득일
    notes = Column(Text, nullable=True)  # 추가 메모
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="properties")

    def __repr__(self):
        return f"<CaseProperty(id={self.id}, type={self.property_type}, value={self.estimated_value})>"


class DivisionPrediction(Base):
    """
    Division prediction model - AI-generated property division predictions
    AI 기반 재산분할 예측 결과 저장
    """
    __tablename__ = "division_predictions"

    id = Column(String, primary_key=True, default=lambda: f"pred_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # 총 재산 정보
    total_property_value = Column(Integer, nullable=False)  # 총 재산액 (원)
    total_debt_value = Column(Integer, default=0)  # 총 부채액 (원)
    net_value = Column(Integer, nullable=False)  # 순자산 (재산 - 부채)

    # 분할 비율
    plaintiff_ratio = Column(Integer, nullable=False)  # 원고 비율 (0-100)
    defendant_ratio = Column(Integer, nullable=False)  # 피고 비율 (0-100)
    plaintiff_amount = Column(Integer, nullable=False)  # 원고 예상 수령액
    defendant_amount = Column(Integer, nullable=False)  # 피고 예상 수령액

    # 분석 결과
    evidence_impacts = Column(JSON, nullable=True)  # 증거별 영향도 리스트
    similar_cases = Column(JSON, nullable=True)  # 유사 판례 리스트
    confidence_level = Column(StrEnumColumn(ConfidenceLevel), nullable=False, default=ConfidenceLevel.MEDIUM)

    # 메타
    version = Column(Integer, default=1)  # 예측 버전 (재계산 시 증가)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="predictions")

    def __repr__(self):
        return f"<DivisionPrediction(id={self.id}, ratio={self.plaintiff_ratio}:{self.defendant_ratio})>"


class Asset(Base):
    """
    Asset model for detailed property division tracking
    US2 - 재산분할표 (Asset Division Sheet)
    """
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: f"asset_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic info
    category = Column(StrEnumColumn(AssetCategory), nullable=False)
    ownership = Column(StrEnumColumn(AssetOwnership), nullable=False)
    nature = Column(StrEnumColumn(AssetNature), nullable=True, default=AssetNature.MARITAL)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Valuation
    current_value = Column(Integer, nullable=False)  # 현재 가치 (원)
    acquisition_value = Column(Integer, nullable=True)  # 취득 가치 (원)
    acquisition_date = Column(DateTime(timezone=True), nullable=True)
    valuation_date = Column(DateTime(timezone=True), nullable=True)
    valuation_source = Column(String(100), nullable=True)  # 감정기관 등

    # Division proposal
    division_ratio_plaintiff = Column(Integer, nullable=True, default=50)  # 원고 분할 비율 (0-100)
    division_ratio_defendant = Column(Integer, nullable=True, default=50)  # 피고 분할 비율 (0-100)
    proposed_allocation = Column(StrEnumColumn(AssetOwnership), nullable=True)  # 제안된 귀속자

    # Evidence link
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="assets")

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, value={self.current_value})>"


class AssetDivisionSummary(Base):
    """
    Asset division summary - calculated division result per case
    US2 - 재산분할표 계산 결과
    """
    __tablename__ = "asset_division_summaries"

    id = Column(String, primary_key=True, default=lambda: f"summary_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Division calculation results
    total_marital_assets = Column(Integer, default=0)     # 혼인 중 재산 총액
    total_separate_plaintiff = Column(Integer, default=0)  # 원고 특유재산
    total_separate_defendant = Column(Integer, default=0)  # 피고 특유재산
    total_debts = Column(Integer, default=0)              # 총 부채액
    net_marital_value = Column(Integer, default=0)        # 순 혼인재산 (자산-부채)

    # Calculated shares
    plaintiff_share = Column(Integer, default=0)          # 원고 분할액
    defendant_share = Column(Integer, default=0)          # 피고 분할액
    settlement_amount = Column(Integer, default=0)        # 정산금 (양수=원고→피고)

    # Current holdings
    plaintiff_holdings = Column(Integer, default=0)       # 원고 현재 보유액
    defendant_holdings = Column(Integer, default=0)       # 피고 현재 보유액

    # Calculation parameters
    plaintiff_ratio = Column(Integer, default=50)         # 원고 비율 (0-100)
    defendant_ratio = Column(Integer, default=50)         # 피고 비율 (0-100)

    # Legacy fields (backward compatibility)
    total_assets = Column(Integer, default=0)             # (legacy) 총 재산액
    net_value = Column(Integer, default=0)                # (legacy) 순자산
    plaintiff_assets = Column(Integer, default=0)         # (legacy)
    defendant_assets = Column(Integer, default=0)         # (legacy)
    joint_assets = Column(Integer, default=0)             # (legacy)
    category_breakdown = Column(JSON, nullable=True)      # (legacy)

    # Metadata
    notes = Column(Text, nullable=True)                   # 계산 메모
    calculated_by = Column(String, nullable=True)         # 계산 수행자

    # Timestamps
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="asset_division_summaries")

    def __repr__(self):
        return f"<AssetDivisionSummary(case_id={self.case_id}, settlement={self.settlement_amount})>"


class Evidence(Base):
    """
    Evidence model - uploaded evidence files for cases
    Metadata is stored here, actual files in S3, AI analysis results in DynamoDB/Qdrant
    """
    __tablename__ = "evidence"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)

    # File info
    file_name = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    file_type = Column(String, nullable=True)  # MIME type
    file_size = Column(String, nullable=True)  # Size in bytes (stored as string for SQLite compatibility)
    description = Column(String, nullable=True)

    # Processing status
    status = Column(String, nullable=False, default="pending")  # pending, uploaded, processing, completed, failed

    # AI analysis results (stored as JSON strings for SQLite compatibility)
    ai_labels = Column(String, nullable=True)  # JSON array: ["폭언", "불륜", ...]
    ai_summary = Column(String, nullable=True)  # AI-generated summary
    ai_score = Column(String, nullable=True)  # Evidence strength score

    # Upload tracking
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="evidence_items")
    uploader = relationship("User")

    @property
    def ai_labels_list(self) -> list:
        """Parse ai_labels JSON string to list"""
        import json
        if not self.ai_labels:
            return []
        try:
            return json.loads(self.ai_labels)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self):
        return f"<Evidence(id={self.id}, file_name={self.file_name}, status={self.status})>"


class Job(Base):
    """
    Job model - tracks async processing tasks (OCR, STT, draft generation, etc.)
    """
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: f"job_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    job_type = Column(StrEnumColumn(JobType), nullable=False)
    status = Column(StrEnumColumn(JobStatus), nullable=False, default=JobStatus.QUEUED)

    # Related resources
    evidence_id = Column(String, nullable=True, index=True)  # For evidence-related jobs

    # Job data (stored as JSON strings)
    input_data = Column(String, nullable=True)   # JSON: {s3_key, file_type, parameters, ...}
    output_data = Column(String, nullable=True)  # JSON: Result from AI processing
    error_details = Column(String, nullable=True)  # JSON: {error_code, message, traceback, ...}

    # Progress tracking
    progress = Column(String, default="0")  # 0-100 for long-running jobs

    # Retry tracking
    retry_count = Column(String, default="0")
    max_retries = Column(String, default="3")

    # AWS Lambda correlation
    lambda_request_id = Column(String, nullable=True)  # For CloudWatch logs correlation

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    case = relationship("Case")
    user = relationship("User")

    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"


class UserSettings(Base):
    """
    User settings model - stores user preferences and notification settings
    """
    __tablename__ = "user_settings"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # Profile settings
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), nullable=False, default="Asia/Seoul")
    language = Column(String(10), nullable=False, default="ko")

    # Notification settings
    email_notifications = Column(Boolean, nullable=False, default=True)
    push_notifications = Column(Boolean, nullable=False, default=True)
    notification_frequency = Column(
        SQLEnum(NotificationFrequency),
        nullable=False,
        default=NotificationFrequency.IMMEDIATE
    )

    # Privacy settings
    profile_visibility = Column(
        SQLEnum(ProfileVisibility),
        nullable=False,
        default=ProfileVisibility.TEAM
    )

    # Security settings
    two_factor_enabled = Column(Boolean, nullable=False, default=False)
    last_password_change = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    user = relationship("User", backref="settings")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, language={self.language})>"


# ============================================
# v1 Lawyer Portal Models
# ============================================
class PartyNode(Base):
    """
    Party node model - represents a person in the relationship graph
    원고, 피고, 제3자, 자녀, 친족 등 사건에 등장하는 인물
    """
    __tablename__ = "party_nodes"

    id = Column(String, primary_key=True, default=lambda: f"party_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(StrEnumColumn(PartyType), nullable=False)
    name = Column(String(100), nullable=False)
    alias = Column(String(50), nullable=True)  # 소장용 가명 (김○○)
    birth_year = Column(Integer, nullable=True)
    occupation = Column(String(100), nullable=True)
    position_x = Column(Integer, nullable=False, default=0)  # React Flow X coordinate
    position_y = Column(Integer, nullable=False, default=0)  # React Flow Y coordinate
    extra_data = Column(JSON, nullable=True, default=dict)  # Additional info (renamed from metadata)
    # 012-precedent-integration: T036-T038 자동 추출 필드
    is_auto_extracted = Column(Boolean, default=False, nullable=False)  # AI가 추출했는지 여부
    extraction_confidence = Column(Float, nullable=True)  # 추출 신뢰도 (0.0-1.0)
    source_evidence_id = Column(String, nullable=True)  # 추출 근거 증거 ID
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="party_nodes")
    source_relationships = relationship(
        "PartyRelationship",
        foreign_keys="PartyRelationship.source_party_id",
        back_populates="source_party",
        cascade="all, delete-orphan"
    )
    target_relationships = relationship(
        "PartyRelationship",
        foreign_keys="PartyRelationship.target_party_id",
        back_populates="target_party",
        cascade="all, delete-orphan"
    )
    evidence_links = relationship("EvidencePartyLink", back_populates="party", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PartyNode(id={self.id}, name={self.name}, type={self.type})>"


class PartyRelationship(Base):
    """
    Party relationship model - represents a connection between two parties
    혼인, 불륜, 부모-자녀, 형제자매, 인척, 동거 관계
    """
    __tablename__ = "party_relationships"

    id = Column(String, primary_key=True, default=lambda: f"rel_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    source_party_id = Column(String, ForeignKey("party_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_party_id = Column(String, ForeignKey("party_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(StrEnumColumn(RelationshipType), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)  # 관계 시작일
    end_date = Column(DateTime(timezone=True), nullable=True)    # 관계 종료일
    notes = Column(Text, nullable=True)
    # 012-precedent-integration: T039 자동 추출 필드
    is_auto_extracted = Column(Boolean, default=False, nullable=False)  # AI가 추출했는지 여부
    extraction_confidence = Column(Float, nullable=True)  # 추출 신뢰도 (0.0-1.0)
    evidence_text = Column(Text, nullable=True)  # 관계 추론 근거 텍스트
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="party_relationships")
    source_party = relationship(
        "PartyNode",
        foreign_keys=[source_party_id],
        back_populates="source_relationships"
    )
    target_party = relationship(
        "PartyNode",
        foreign_keys=[target_party_id],
        back_populates="target_relationships"
    )
    evidence_links = relationship("EvidencePartyLink", back_populates="relationship", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PartyRelationship(id={self.id}, type={self.type}, source={self.source_party_id}, target={self.target_party_id})>"


class EvidencePartyLink(Base):
    """
    Evidence-party link model - connects evidence to parties, relationships, or assets
    증거와 당사자/관계/자산 간의 연결
    """
    __tablename__ = "evidence_party_links"

    id = Column(String, primary_key=True, default=lambda: f"link_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(String(100), nullable=False, index=True)  # References DynamoDB evidence
    party_id = Column(String, ForeignKey("party_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    relationship_id = Column(String, ForeignKey("party_relationships.id", ondelete="CASCADE"), nullable=True, index=True)
    link_type = Column(StrEnumColumn(LinkType), nullable=False, default=LinkType.MENTIONS)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", backref="evidence_party_links")
    party = relationship("PartyNode", back_populates="evidence_links")
    relationship = relationship("PartyRelationship", back_populates="evidence_links")

    def __repr__(self):
        return f"<EvidencePartyLink(id={self.id}, evidence_id={self.evidence_id}, link_type={self.link_type})>"


# ============================================
# Procedure Stage Model (US3)
# ============================================
class ProcedureStageRecord(Base):
    """
    Procedure stage record - tracks the progress of a divorce case through stages
    이혼 사건의 단계별 진행 상황 기록
    """
    __tablename__ = "procedure_stage_records"

    id = Column(String, primary_key=True, default=lambda: f"stage_{uuid.uuid4().hex[:12]}")
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Stage info
    stage = Column(StrEnumColumn(ProcedureStageType), nullable=False)
    status = Column(StrEnumColumn(StageStatus), nullable=False, default=StageStatus.PENDING)
    order_index = Column(Integer, nullable=False, default=0)  # Display order

    # Dates
    scheduled_date = Column(DateTime(timezone=True), nullable=True)  # 예정일
    started_at = Column(DateTime(timezone=True), nullable=True)      # 시작일
    completed_at = Column(DateTime(timezone=True), nullable=True)    # 완료일 (legacy)
    completed_date = Column(DateTime(timezone=True), nullable=True)  # 완료일

    # Court info
    court_reference = Column(String(100), nullable=True)  # 사건번호
    judge_name = Column(String(50), nullable=True)        # 담당 판사
    court_room = Column(String(50), nullable=True)        # 법정

    # Details
    notes = Column(Text, nullable=True)
    documents = Column(JSON, nullable=True, default=list)  # Related document IDs
    outcome = Column(String(100), nullable=True)          # 결과

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String, nullable=True)  # 작성자 ID

    # Relationships
    case = relationship("Case", backref=backref("procedure_stages", passive_deletes=True))

    def __repr__(self):
        return f"<ProcedureStageRecord(id={self.id}, stage={self.stage}, status={self.status})>"


class UserAgreement(Base):
    """
    User agreement model - tracks user consent history for legal terms
    사용자 약관 동의 이력 (FR-025: 법적 고지 및 약관)
    """
    __tablename__ = "user_agreements"

    id = Column(String, primary_key=True, default=lambda: f"agree_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agreement_type = Column(StrEnumColumn(AgreementType), nullable=False)
    agreed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    version = Column(String(20), nullable=False)  # e.g., "1.0", "2024.1"
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)  # Browser/client info

    # Relationships
    user = relationship("User", backref="agreements")

    def __repr__(self):
        return f"<UserAgreement(id={self.id}, user_id={self.user_id}, type={self.agreement_type}, version={self.version})>"


# ============================================
# Detective Portal Models (US11)
# ============================================
class DetectiveEarnings(Base):
    """
    Detective earnings model - tracks detective payments per case
    탐정 정산 데이터 관리 (FR-040)
    """
    __tablename__ = "detective_earnings"

    id = Column(String, primary_key=True, default=lambda: f"earn_{uuid.uuid4().hex[:12]}")
    detective_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Payment info
    amount = Column(Integer, nullable=False)  # 금액 (원 단위)
    description = Column(String(500), nullable=True)  # 정산 내역 설명

    # Status
    status = Column(StrEnumColumn(EarningsStatus), nullable=False, default=EarningsStatus.PENDING, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)  # 정산 완료일

    # Relationships
    detective = relationship("User", foreign_keys=[detective_id])
    case = relationship("Case", backref="detective_earnings")

    def __repr__(self):
        return f"<DetectiveEarnings(id={self.id}, detective_id={self.detective_id}, amount={self.amount}, status={self.status})>"


# ============================================
# Notification & Communication Models (Issue #294-296)
# ============================================
class NotificationType(str, enum.Enum):
    """Notification type enum"""
    CASE_UPDATE = "case_update"
    MESSAGE = "message"
    EVIDENCE = "evidence"
    DEADLINE = "deadline"
    SYSTEM = "system"


class Notification(Base):
    """
    Notification model - user notifications
    Issue #294, #295 - FR-007
    """
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: f"notif_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(StrEnumColumn(NotificationType), nullable=False, default=NotificationType.SYSTEM)
    title = Column(String(100), nullable=False)
    content = Column(String(500), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    related_id = Column(String, nullable=True)  # case_id, message_id, etc.
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", backref="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"


# ============================================
# Client/Detective Contact Models (Issue #294, #297-298)
# ============================================
class ClientContact(Base):
    """
    Client contact model - Lawyer's client contacts
    Issue #294, #297 - FR-009~010, FR-015
    """
    __tablename__ = "client_contacts"

    id = Column(String, primary_key=True, default=lambda: f"client_{uuid.uuid4().hex[:12]}")
    lawyer_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    lawyer = relationship("User", backref="client_contacts")

    def __repr__(self):
        return f"<ClientContact(id={self.id}, name={self.name}, lawyer_id={self.lawyer_id})>"


class DetectiveContact(Base):
    """
    Detective contact model - Lawyer's detective contacts
    Issue #294, #298 - FR-011~012, FR-016
    """
    __tablename__ = "detective_contacts"

    id = Column(String, primary_key=True, default=lambda: f"det_{uuid.uuid4().hex[:12]}")
    lawyer_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    specialty = Column(String(100), nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    lawyer = relationship("User", backref="detective_contacts")

    def __repr__(self):
        return f"<DetectiveContact(id={self.id}, name={self.name}, specialty={self.specialty})>"

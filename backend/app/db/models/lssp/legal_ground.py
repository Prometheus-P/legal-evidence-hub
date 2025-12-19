"""
LSSP Legal Ground Models (v2.01)
민법 제840조 이혼 사유 (G1-G6)
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from datetime import datetime, timezone

from app.db.models.base import Base


class LegalGround(Base):
    """
    Legal grounds for divorce (민법 제840조)
    Seed table - data from legal_grounds.v2_01.json
    """
    __tablename__ = "lssp_legal_grounds"

    code = Column(String(10), primary_key=True)  # G1, G2, G3, G4, G5, G6
    name_ko = Column(String(100), nullable=False)
    elements = Column(JSON, nullable=False, default=list)  # 요건 목록
    limitation = Column(JSON, nullable=True)  # 제척기간 정보
    notes = Column(Text, nullable=True)
    
    # Metadata
    version = Column(String(20), nullable=False, default="v2.01")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<LegalGround(code={self.code}, name_ko={self.name_ko})>"


class CaseLegalGroundLink(Base):
    """
    Many-to-many link between Case and LegalGround
    사건에 적용되는 이혼 사유들
    """
    __tablename__ = "lssp_case_legal_ground_links"

    case_id = Column(String, primary_key=True, index=True)
    ground_code = Column(String(10), primary_key=True)
    
    # Assessment
    is_primary = Column(Boolean, nullable=False, default=False)  # 주요 사유 여부
    strength_score = Column(String(20), nullable=True)  # STRONG, MODERATE, WEAK
    notes = Column(Text, nullable=True)
    
    # Metadata
    assessed_by = Column(String, nullable=True)  # user_id or 'AI'
    assessed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<CaseLegalGroundLink(case_id={self.case_id}, ground_code={self.ground_code})>"

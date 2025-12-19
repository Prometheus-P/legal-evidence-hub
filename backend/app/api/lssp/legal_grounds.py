"""
LSSP Legal Grounds API (v2.01)
민법 제840조 이혼 사유 조회 및 사건 연결
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.db.models.lssp import LegalGround, CaseLegalGroundLink
from app.core.dependencies import get_current_user
from app.db.models import User

router = APIRouter(prefix="/legal-grounds", tags=["LSSP - Legal Grounds"])


# ============================================
# Schemas
# ============================================

class LimitationSchema(BaseModel):
    type: Optional[str] = None
    known_within_months: Optional[int] = None
    occurred_within_years: Optional[int] = None
    needs_legal_review: Optional[bool] = None

class LegalGroundResponse(BaseModel):
    code: str
    name_ko: str
    elements: List[str]
    limitation: Optional[LimitationSchema] = None
    notes: Optional[str] = None
    version: str

    class Config:
        from_attributes = True


class CaseLegalGroundLinkCreate(BaseModel):
    ground_code: str
    is_primary: bool = False
    strength_score: Optional[str] = None  # STRONG, MODERATE, WEAK
    notes: Optional[str] = None


class CaseLegalGroundLinkResponse(BaseModel):
    case_id: str
    ground_code: str
    is_primary: bool
    strength_score: Optional[str]
    notes: Optional[str]
    assessed_by: Optional[str]
    assessed_at: datetime
    ground: Optional[LegalGroundResponse] = None

    class Config:
        from_attributes = True


# ============================================
# Endpoints
# ============================================

@router.get("", response_model=List[LegalGroundResponse])
async def list_legal_grounds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    전체 이혼 사유(G1-G6) 목록 조회
    """
    grounds = db.query(LegalGround).order_by(LegalGround.code).all()
    return grounds


@router.get("/{code}", response_model=LegalGroundResponse)
async def get_legal_ground(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    특정 이혼 사유 상세 조회
    """
    ground = db.query(LegalGround).filter(LegalGround.code == code.upper()).first()
    if not ground:
        raise HTTPException(status_code=404, detail=f"Legal ground {code} not found")
    return ground


@router.get("/cases/{case_id}/grounds", response_model=List[CaseLegalGroundLinkResponse])
async def get_case_legal_grounds(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사건에 적용된 이혼 사유 목록 조회
    """
    links = db.query(CaseLegalGroundLink).filter(
        CaseLegalGroundLink.case_id == case_id
    ).all()
    
    # Attach ground details
    result = []
    for link in links:
        ground = db.query(LegalGround).filter(LegalGround.code == link.ground_code).first()
        link_dict = {
            "case_id": link.case_id,
            "ground_code": link.ground_code,
            "is_primary": link.is_primary,
            "strength_score": link.strength_score,
            "notes": link.notes,
            "assessed_by": link.assessed_by,
            "assessed_at": link.assessed_at,
            "ground": ground,
        }
        result.append(CaseLegalGroundLinkResponse(**link_dict))
    
    return result


@router.post("/cases/{case_id}/grounds", response_model=CaseLegalGroundLinkResponse, status_code=status.HTTP_201_CREATED)
async def add_case_legal_ground(
    case_id: str,
    data: CaseLegalGroundLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사건에 이혼 사유 추가
    """
    # Validate ground code
    ground = db.query(LegalGround).filter(LegalGround.code == data.ground_code.upper()).first()
    if not ground:
        raise HTTPException(status_code=400, detail=f"Invalid ground code: {data.ground_code}")
    
    # Check if already linked
    existing = db.query(CaseLegalGroundLink).filter(
        CaseLegalGroundLink.case_id == case_id,
        CaseLegalGroundLink.ground_code == data.ground_code.upper()
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Ground {data.ground_code} already linked to case")
    
    # Create link
    link = CaseLegalGroundLink(
        case_id=case_id,
        ground_code=data.ground_code.upper(),
        is_primary=data.is_primary,
        strength_score=data.strength_score,
        notes=data.notes,
        assessed_by=current_user.id,
    )
    
    db.add(link)
    db.commit()
    db.refresh(link)
    
    return CaseLegalGroundLinkResponse(
        case_id=link.case_id,
        ground_code=link.ground_code,
        is_primary=link.is_primary,
        strength_score=link.strength_score,
        notes=link.notes,
        assessed_by=link.assessed_by,
        assessed_at=link.assessed_at,
        ground=ground,
    )


@router.delete("/cases/{case_id}/grounds/{ground_code}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_case_legal_ground(
    case_id: str,
    ground_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사건에서 이혼 사유 제거
    """
    link = db.query(CaseLegalGroundLink).filter(
        CaseLegalGroundLink.case_id == case_id,
        CaseLegalGroundLink.ground_code == ground_code.upper()
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()

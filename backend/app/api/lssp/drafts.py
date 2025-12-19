"""
LSSP Drafts API (v2.04/v2.06)
블록 기반 초안 생성 및 관리
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.db.models.lssp import (
    Draft, DraftTemplate, DraftBlock,
    DraftBlockInstance, DraftCitation, DraftPrecedentLink
)
from app.core.dependencies import get_current_user
from app.db.models import User

router = APIRouter(prefix="/drafts", tags=["LSSP - Drafts"])


# ============================================
# Schemas
# ============================================

class DraftTemplateResponse(BaseModel):
    id: str
    label: str
    template_schema: dict = Field(alias="schema")  # ORM 'schema' → API 'template_schema'
    version: str
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both 'schema' and 'template_schema'


class DraftBlockResponse(BaseModel):
    id: str
    label: str
    block_tag: str
    template: str
    required_keypoint_types: List[str]
    required_evidence_tags: List[str]
    conditions: Optional[str]
    legal_refs: List[dict]
    version: str

    class Config:
        from_attributes = True


class DraftCreate(BaseModel):
    template_id: str
    title: str
    meta: dict = {}


class DraftUpdate(BaseModel):
    title: Optional[str] = None
    meta: Optional[dict] = None
    status: Optional[str] = None  # DRAFTING, NEEDS_REVIEW, FINALIZED


class DraftResponse(BaseModel):
    id: str
    case_id: str
    template_id: str
    title: str
    meta: dict
    coverage_score: int
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlockInstanceCreate(BaseModel):
    block_id: str
    section_key: str
    position: int
    text: str
    status: str = "AUTO"  # AUTO, EDITED, TODO, REMOVED


class BlockInstanceUpdate(BaseModel):
    text: Optional[str] = None
    position: Optional[int] = None
    status: Optional[str] = None
    coverage_score: Optional[int] = None


class CitationCreate(BaseModel):
    keypoint_id: Optional[str] = None
    extract_id: Optional[str] = None
    note: Optional[str] = None


class CitationResponse(BaseModel):
    id: str
    block_instance_id: str
    keypoint_id: Optional[str]
    extract_id: Optional[str]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BlockInstanceResponse(BaseModel):
    id: str
    draft_id: str
    block_id: str
    section_key: str
    position: int
    text: str
    status: str
    coverage_score: int
    created_at: datetime
    updated_at: datetime
    citations: List[CitationResponse] = []
    block: Optional[DraftBlockResponse] = None

    class Config:
        from_attributes = True


class DraftDetailResponse(DraftResponse):
    block_instances: List[BlockInstanceResponse] = []
    template: Optional[DraftTemplateResponse] = None
    precedent_ids: List[str] = []


class PrecedentLinkCreate(BaseModel):
    precedent_id: str
    reason: Optional[str] = None


# ============================================
# Template & Block Endpoints (Seed Data)
# ============================================

@router.get("/templates", response_model=List[DraftTemplateResponse])
async def list_draft_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안 템플릿 목록 조회
    """
    return db.query(DraftTemplate).order_by(DraftTemplate.id).all()


@router.get("/templates/{template_id}", response_model=DraftTemplateResponse)
async def get_draft_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안 템플릿 상세 조회
    """
    template = db.query(DraftTemplate).filter(DraftTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/blocks", response_model=List[DraftBlockResponse])
async def list_draft_blocks(
    block_tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안 블록 목록 조회
    """
    query = db.query(DraftBlock)
    if block_tag:
        query = query.filter(DraftBlock.block_tag == block_tag.upper())
    return query.order_by(DraftBlock.id).all()


@router.get("/blocks/{block_id}", response_model=DraftBlockResponse)
async def get_draft_block(
    block_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안 블록 상세 조회
    """
    block = db.query(DraftBlock).filter(DraftBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


# ============================================
# Draft CRUD Endpoints
# ============================================

@router.post("/cases/{case_id}", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    case_id: str,
    data: DraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    새 초안 생성
    """
    import uuid
    
    # Validate template
    template = db.query(DraftTemplate).filter(DraftTemplate.id == data.template_id).first()
    if not template:
        raise HTTPException(status_code=400, detail=f"Invalid template: {data.template_id}")
    
    draft = Draft(
        id=str(uuid.uuid4()),
        case_id=case_id,
        template_id=data.template_id,
        title=data.title,
        meta=data.meta,
        created_by=current_user.id,
    )
    
    db.add(draft)
    db.commit()
    db.refresh(draft)
    
    return draft


@router.get("/cases/{case_id}", response_model=List[DraftResponse])
async def list_case_drafts(
    case_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사건의 초안 목록 조회
    """
    query = db.query(Draft).filter(Draft.case_id == case_id)
    if status:
        query = query.filter(Draft.status == status.upper())
    return query.order_by(Draft.updated_at.desc()).all()


@router.get("/{draft_id}", response_model=DraftDetailResponse)
async def get_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안 상세 조회 (블록 인스턴스 포함)
    """
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    return _build_draft_detail(db, draft)


@router.patch("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    data: DraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안 메타데이터 수정
    """
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(draft, field, value)
    
    db.commit()
    db.refresh(draft)
    
    return draft


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안 삭제
    """
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    db.delete(draft)  # Cascade deletes block instances
    db.commit()


# ============================================
# Block Instance Endpoints
# ============================================

@router.post("/{draft_id}/blocks", response_model=BlockInstanceResponse, status_code=status.HTTP_201_CREATED)
async def add_block_instance(
    draft_id: str,
    data: BlockInstanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안에 블록 인스턴스 추가
    """
    import uuid
    
    # Validate draft exists
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    # Validate block exists
    block = db.query(DraftBlock).filter(DraftBlock.id == data.block_id).first()
    if not block:
        raise HTTPException(status_code=400, detail=f"Invalid block: {data.block_id}")
    
    instance = DraftBlockInstance(
        id=str(uuid.uuid4()),
        draft_id=draft_id,
        block_id=data.block_id,
        section_key=data.section_key,
        position=data.position,
        text=data.text,
        status=data.status,
    )
    
    db.add(instance)
    db.commit()
    db.refresh(instance)
    
    return _build_block_instance_response(db, instance)


@router.get("/{draft_id}/blocks", response_model=List[BlockInstanceResponse])
async def list_block_instances(
    draft_id: str,
    section_key: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안의 블록 인스턴스 목록 조회
    """
    query = db.query(DraftBlockInstance).filter(DraftBlockInstance.draft_id == draft_id)
    if section_key:
        query = query.filter(DraftBlockInstance.section_key == section_key)
    
    instances = query.order_by(
        DraftBlockInstance.section_key,
        DraftBlockInstance.position
    ).all()
    
    return [_build_block_instance_response(db, inst) for inst in instances]


@router.patch("/blocks/{instance_id}", response_model=BlockInstanceResponse)
async def update_block_instance(
    instance_id: str,
    data: BlockInstanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    블록 인스턴스 수정
    """
    instance = db.query(DraftBlockInstance).filter(DraftBlockInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Block instance not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instance, field, value)
    
    # Mark as edited if text changed
    if "text" in update_data and instance.status == "AUTO":
        instance.status = "EDITED"
    
    db.commit()
    db.refresh(instance)
    
    return _build_block_instance_response(db, instance)


@router.delete("/blocks/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block_instance(
    instance_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    블록 인스턴스 삭제
    """
    instance = db.query(DraftBlockInstance).filter(DraftBlockInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Block instance not found")
    
    db.delete(instance)
    db.commit()


# ============================================
# Citation Endpoints
# ============================================

@router.post("/blocks/{instance_id}/citations", response_model=CitationResponse, status_code=status.HTTP_201_CREATED)
async def add_citation(
    instance_id: str,
    data: CitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    블록에 인용(키포인트/발췌 참조) 추가
    """
    import uuid
    
    if not data.keypoint_id and not data.extract_id:
        raise HTTPException(status_code=400, detail="Must provide keypoint_id or extract_id")
    
    instance = db.query(DraftBlockInstance).filter(DraftBlockInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Block instance not found")
    
    citation = DraftCitation(
        id=str(uuid.uuid4()),
        block_instance_id=instance_id,
        keypoint_id=data.keypoint_id,
        extract_id=data.extract_id,
        note=data.note,
    )
    
    db.add(citation)
    db.commit()
    db.refresh(citation)
    
    return citation


@router.delete("/citations/{citation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_citation(
    citation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    인용 삭제
    """
    citation = db.query(DraftCitation).filter(DraftCitation.id == citation_id).first()
    if not citation:
        raise HTTPException(status_code=404, detail="Citation not found")
    
    db.delete(citation)
    db.commit()


# ============================================
# Precedent Link Endpoints
# ============================================

@router.post("/{draft_id}/precedents", status_code=status.HTTP_201_CREATED)
async def add_precedent_link(
    draft_id: str,
    data: PrecedentLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안에 판례 연결 추가
    """
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    # Check if already linked
    existing = db.query(DraftPrecedentLink).filter(
        DraftPrecedentLink.draft_id == draft_id,
        DraftPrecedentLink.precedent_id == data.precedent_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Precedent already linked")
    
    link = DraftPrecedentLink(
        draft_id=draft_id,
        precedent_id=data.precedent_id,
        reason=data.reason,
    )
    
    db.add(link)
    db.commit()
    
    return {"draft_id": draft_id, "precedent_id": data.precedent_id, "reason": data.reason}


@router.delete("/{draft_id}/precedents/{precedent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_precedent_link(
    draft_id: str,
    precedent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    초안에서 판례 연결 제거
    """
    link = db.query(DraftPrecedentLink).filter(
        DraftPrecedentLink.draft_id == draft_id,
        DraftPrecedentLink.precedent_id == precedent_id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Precedent link not found")
    
    db.delete(link)
    db.commit()


# ============================================
# Helpers
# ============================================

def _build_block_instance_response(db: Session, instance: DraftBlockInstance) -> BlockInstanceResponse:
    """Build block instance response with citations and block details"""
    citations = db.query(DraftCitation).filter(
        DraftCitation.block_instance_id == instance.id
    ).all()
    
    block = db.query(DraftBlock).filter(DraftBlock.id == instance.block_id).first()
    
    return BlockInstanceResponse(
        id=instance.id,
        draft_id=instance.draft_id,
        block_id=instance.block_id,
        section_key=instance.section_key,
        position=instance.position,
        text=instance.text,
        status=instance.status,
        coverage_score=instance.coverage_score,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        citations=[CitationResponse.model_validate(c) for c in citations],
        block=DraftBlockResponse.model_validate(block) if block else None,
    )


def _build_draft_detail(db: Session, draft: Draft) -> DraftDetailResponse:
    """Build full draft detail with block instances"""
    instances = db.query(DraftBlockInstance).filter(
        DraftBlockInstance.draft_id == draft.id
    ).order_by(
        DraftBlockInstance.section_key,
        DraftBlockInstance.position
    ).all()
    
    template = db.query(DraftTemplate).filter(DraftTemplate.id == draft.template_id).first()
    
    precedent_links = db.query(DraftPrecedentLink).filter(
        DraftPrecedentLink.draft_id == draft.id
    ).all()
    
    return DraftDetailResponse(
        id=draft.id,
        case_id=draft.case_id,
        template_id=draft.template_id,
        title=draft.title,
        meta=draft.meta,
        coverage_score=draft.coverage_score,
        status=draft.status,
        created_by=draft.created_by,
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        block_instances=[_build_block_instance_response(db, inst) for inst in instances],
        template=DraftTemplateResponse.model_validate(template) if template else None,
        precedent_ids=[link.precedent_id for link in precedent_links],
    )

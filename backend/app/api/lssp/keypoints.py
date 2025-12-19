"""
LSSP Keypoints API (v2.03)
핵심 사실 추출 및 관리
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

from app.db.session import get_db
from app.db.models.lssp import (
    Keypoint, EvidenceExtract,
    KeypointExtractLink, KeypointGroundLink
)
from app.core.dependencies import get_current_user
from app.db.models import User

router = APIRouter(prefix="/keypoints", tags=["LSSP - Keypoints"])


# ============================================
# Schemas
# ============================================

class ActorSchema(BaseModel):
    role: str  # spouse, child, witness, etc.
    name: Optional[str] = None


class EvidenceExtractCreate(BaseModel):
    evidence_file_id: str
    kind: str  # page_range, time_range, message_range, manual_note
    locator: dict  # {"page_from":1,"page_to":3} or {"t_from_ms":..., "t_to_ms":...}
    extracted_text: Optional[str] = None


class EvidenceExtractResponse(BaseModel):
    id: str
    case_id: str
    evidence_file_id: str
    kind: str
    locator: dict
    extracted_text: Optional[str]
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class KeypointCreate(BaseModel):
    title: str = Field(..., max_length=200)
    statement: str
    occurred_at: Optional[date] = None
    occurred_at_precision: str = "DATE"  # DATE, DATETIME, RANGE, UNKNOWN
    actors: List[ActorSchema] = []
    location: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: str = "KRW"
    type_code: str
    risk_flags: List[str] = []
    # Optional: link to extracts on creation
    extract_ids: List[str] = []
    # Optional: link to grounds on creation
    ground_codes: List[str] = []


class KeypointUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    statement: Optional[str] = None
    occurred_at: Optional[date] = None
    occurred_at_precision: Optional[str] = None
    actors: Optional[List[ActorSchema]] = None
    location: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    type_code: Optional[str] = None
    status: Optional[str] = None  # DRAFT, READY, CONTESTED, EXCLUDED
    risk_flags: Optional[List[str]] = None


class KeypointResponse(BaseModel):
    id: str
    case_id: str
    title: str
    statement: str
    occurred_at: Optional[date]
    occurred_at_precision: str
    actors: List[dict]
    location: Optional[str]
    amount: Optional[Decimal]
    currency: Optional[str]
    type_code: str
    status: str
    risk_flags: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    # Linked data
    extract_ids: List[str] = []
    ground_codes: List[str] = []

    class Config:
        from_attributes = True


class KeypointLinkRequest(BaseModel):
    extract_ids: Optional[List[str]] = None
    ground_codes: Optional[List[str]] = None


# ============================================
# Evidence Extract Endpoints
# ============================================

@router.post("/cases/{case_id}/extracts", response_model=EvidenceExtractResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence_extract(
    case_id: str,
    data: EvidenceExtractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    증거 발췌 생성 (특정 페이지, 시간 구간, 메시지 범위)
    """
    import uuid
    
    extract = EvidenceExtract(
        id=str(uuid.uuid4()),
        case_id=case_id,
        evidence_file_id=data.evidence_file_id,
        kind=data.kind,
        locator=data.locator,
        extracted_text=data.extracted_text,
        created_by=current_user.id,
    )
    
    db.add(extract)
    db.commit()
    db.refresh(extract)
    
    return extract


@router.get("/cases/{case_id}/extracts", response_model=List[EvidenceExtractResponse])
async def list_evidence_extracts(
    case_id: str,
    evidence_file_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사건의 증거 발췌 목록 조회
    """
    query = db.query(EvidenceExtract).filter(EvidenceExtract.case_id == case_id)
    
    if evidence_file_id:
        query = query.filter(EvidenceExtract.evidence_file_id == evidence_file_id)
    
    return query.order_by(EvidenceExtract.created_at.desc()).all()


# ============================================
# Keypoint Endpoints
# ============================================

@router.post("/cases/{case_id}", response_model=KeypointResponse, status_code=status.HTTP_201_CREATED)
async def create_keypoint(
    case_id: str,
    data: KeypointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    키포인트(핵심 사실) 생성
    """
    import uuid
    
    keypoint = Keypoint(
        id=str(uuid.uuid4()),
        case_id=case_id,
        title=data.title,
        statement=data.statement,
        occurred_at=data.occurred_at,
        occurred_at_precision=data.occurred_at_precision,
        actors=[a.model_dump() for a in data.actors],
        location=data.location,
        amount=data.amount,
        currency=data.currency,
        type_code=data.type_code,
        risk_flags=data.risk_flags,
        created_by=current_user.id,
    )
    
    db.add(keypoint)
    db.flush()  # Get ID before creating links
    
    # Create extract links
    for extract_id in data.extract_ids:
        link = KeypointExtractLink(keypoint_id=keypoint.id, extract_id=extract_id)
        db.add(link)
    
    # Create ground links
    for ground_code in data.ground_codes:
        link = KeypointGroundLink(keypoint_id=keypoint.id, ground_code=ground_code.upper())
        db.add(link)
    
    db.commit()
    db.refresh(keypoint)
    
    return _build_keypoint_response(db, keypoint)


@router.get("/cases/{case_id}", response_model=List[KeypointResponse])
async def list_keypoints(
    case_id: str,
    status: Optional[str] = None,
    type_code: Optional[str] = None,
    ground_code: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    사건의 키포인트 목록 조회
    """
    query = db.query(Keypoint).filter(Keypoint.case_id == case_id)
    
    if status:
        query = query.filter(Keypoint.status == status.upper())
    if type_code:
        query = query.filter(Keypoint.type_code == type_code)
    if ground_code:
        # Join with ground links
        query = query.join(KeypointGroundLink).filter(
            KeypointGroundLink.ground_code == ground_code.upper()
        )
    
    keypoints = query.order_by(Keypoint.occurred_at.desc().nullslast()).offset(offset).limit(limit).all()
    
    return [_build_keypoint_response(db, kp) for kp in keypoints]


@router.get("/{keypoint_id}", response_model=KeypointResponse)
async def get_keypoint(
    keypoint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    키포인트 상세 조회
    """
    keypoint = db.query(Keypoint).filter(Keypoint.id == keypoint_id).first()
    if not keypoint:
        raise HTTPException(status_code=404, detail="Keypoint not found")
    
    return _build_keypoint_response(db, keypoint)


@router.patch("/{keypoint_id}", response_model=KeypointResponse)
async def update_keypoint(
    keypoint_id: str,
    data: KeypointUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    키포인트 수정
    """
    keypoint = db.query(Keypoint).filter(Keypoint.id == keypoint_id).first()
    if not keypoint:
        raise HTTPException(status_code=404, detail="Keypoint not found")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Convert actors to dict if present
    if "actors" in update_data and update_data["actors"] is not None:
        update_data["actors"] = [a.model_dump() if hasattr(a, 'model_dump') else a for a in update_data["actors"]]
    
    for field, value in update_data.items():
        setattr(keypoint, field, value)
    
    db.commit()
    db.refresh(keypoint)
    
    return _build_keypoint_response(db, keypoint)


@router.post("/{keypoint_id}/links", response_model=KeypointResponse)
async def update_keypoint_links(
    keypoint_id: str,
    data: KeypointLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    키포인트에 증거/사유 연결 추가
    """
    keypoint = db.query(Keypoint).filter(Keypoint.id == keypoint_id).first()
    if not keypoint:
        raise HTTPException(status_code=404, detail="Keypoint not found")
    
    # Add extract links
    if data.extract_ids:
        existing = {link.extract_id for link in db.query(KeypointExtractLink).filter(
            KeypointExtractLink.keypoint_id == keypoint_id
        ).all()}
        
        for extract_id in data.extract_ids:
            if extract_id not in existing:
                db.add(KeypointExtractLink(keypoint_id=keypoint_id, extract_id=extract_id))
    
    # Add ground links
    if data.ground_codes:
        existing = {link.ground_code for link in db.query(KeypointGroundLink).filter(
            KeypointGroundLink.keypoint_id == keypoint_id
        ).all()}
        
        for ground_code in data.ground_codes:
            if ground_code.upper() not in existing:
                db.add(KeypointGroundLink(keypoint_id=keypoint_id, ground_code=ground_code.upper()))
    
    db.commit()
    db.refresh(keypoint)
    
    return _build_keypoint_response(db, keypoint)


@router.delete("/{keypoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keypoint(
    keypoint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    키포인트 삭제
    """
    keypoint = db.query(Keypoint).filter(Keypoint.id == keypoint_id).first()
    if not keypoint:
        raise HTTPException(status_code=404, detail="Keypoint not found")
    
    db.delete(keypoint)  # Cascade deletes links
    db.commit()


# ============================================
# Helpers
# ============================================

def _build_keypoint_response(db: Session, keypoint: Keypoint) -> KeypointResponse:
    """Build response with linked extract and ground IDs"""
    extract_links = db.query(KeypointExtractLink).filter(
        KeypointExtractLink.keypoint_id == keypoint.id
    ).all()
    
    ground_links = db.query(KeypointGroundLink).filter(
        KeypointGroundLink.keypoint_id == keypoint.id
    ).all()
    
    return KeypointResponse(
        id=keypoint.id,
        case_id=keypoint.case_id,
        title=keypoint.title,
        statement=keypoint.statement,
        occurred_at=keypoint.occurred_at,
        occurred_at_precision=keypoint.occurred_at_precision,
        actors=keypoint.actors,
        location=keypoint.location,
        amount=keypoint.amount,
        currency=keypoint.currency,
        type_code=keypoint.type_code,
        status=keypoint.status,
        risk_flags=keypoint.risk_flags,
        created_by=keypoint.created_by,
        created_at=keypoint.created_at,
        updated_at=keypoint.updated_at,
        extract_ids=[link.extract_id for link in extract_links],
        ground_codes=[link.ground_code for link in ground_links],
    )


# ============================================
# AI Extraction Endpoints
# ============================================

class AIExtractionRequest(BaseModel):
    """AI 쟁점 추출 요청"""
    evidence_file_ids: Optional[List[str]] = None  # None이면 전체 증거 대상
    use_fast_path: bool = True  # LegalAnalysis 기반 빠른 추출
    use_gpt: bool = True  # GPT 상세 추출


class AIExtractionResponse(BaseModel):
    """AI 쟁점 추출 결과"""
    case_id: str
    extracted_count: int
    saved_count: int
    keypoint_ids: List[str]
    errors: List[str] = []
    processing_time_ms: int


class LegalGroundSummaryItem(BaseModel):
    """법적 사유별 요약"""
    ground_code: str
    ground_name: str
    keypoint_count: int
    evidence_count: int
    keypoint_ids: List[str]


class LegalGroundSummaryResponse(BaseModel):
    """법적 사유 요약 응답"""
    case_id: str
    total_keypoints: int
    grounds: List[LegalGroundSummaryItem]


@router.post("/cases/{case_id}/extract", response_model=AIExtractionResponse)
async def extract_keypoints_with_ai(
    case_id: str,
    request: AIExtractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI를 사용한 핵심 쟁점 자동 추출
    
    증거 파일에서 핵심 쟁점을 자동으로 추출하여 저장합니다.
    - use_fast_path: LegalAnalysis 기반 빠른 추출 (기존 분석 결과 활용)
    - use_gpt: GPT를 사용한 상세 추출 (더 정확하지만 느림)
    """
    import time
    import uuid
    import os
    import httpx
    
    start_time = time.time()
    errors = []
    keypoint_ids = []
    
    # AI Worker 호출
    ai_worker_url = os.getenv("AI_WORKER_URL", "http://localhost:8001")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{ai_worker_url}/api/v1/keypoints/extract",
                json={
                    "case_id": case_id,
                    "evidence_file_ids": request.evidence_file_ids,
                    "use_fast_path": request.use_fast_path,
                    "use_gpt": request.use_gpt,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI Worker error: {response.text}"
                )
            
            result = response.json()
            extracted_keypoints = result.get("keypoints", [])
            errors.extend(result.get("errors", []))
            
    except httpx.RequestError as e:
        # AI Worker 연결 실패 시 직접 추출 시도 (fallback)
        errors.append(f"AI Worker connection failed: {str(e)}, using fallback")
        extracted_keypoints = await _fallback_extract(case_id, request, db)
    
    # 추출된 쟁점 저장
    for kp_data in extracted_keypoints:
        try:
            keypoint = Keypoint(
                id=str(uuid.uuid4()),
                case_id=case_id,
                title=kp_data.get("statement", "")[:200],
                statement=kp_data.get("statement", ""),
                type_code=kp_data.get("type_code", "FACT"),
                status="DRAFT",
                risk_flags=[],
                actors=[],
                created_by=current_user.id,
            )
            db.add(keypoint)
            db.flush()
            
            # Ground 연결
            for ground_code in kp_data.get("legal_ground_codes", []):
                db.add(KeypointGroundLink(
                    keypoint_id=keypoint.id,
                    ground_code=ground_code.upper()
                ))
            
            keypoint_ids.append(keypoint.id)
            
        except Exception as e:
            errors.append(f"Failed to save keypoint: {str(e)}")
    
    db.commit()
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return AIExtractionResponse(
        case_id=case_id,
        extracted_count=len(extracted_keypoints),
        saved_count=len(keypoint_ids),
        keypoint_ids=keypoint_ids,
        errors=errors,
        processing_time_ms=processing_time,
    )


@router.get("/cases/{case_id}/legal-ground-summary", response_model=LegalGroundSummaryResponse)
async def get_legal_ground_summary(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    법적 사유별 쟁점 요약
    
    사건의 쟁점을 법적 사유(이혼사유 등)별로 그룹화하여 반환합니다.
    """
    from sqlalchemy import func
    from app.db.models.lssp import LegalGround
    
    # 사건의 전체 키포인트 수
    total = db.query(func.count(Keypoint.id)).filter(
        Keypoint.case_id == case_id
    ).scalar() or 0
    
    # 법적 사유별 집계
    ground_stats = db.query(
        KeypointGroundLink.ground_code,
        func.count(KeypointGroundLink.keypoint_id).label("kp_count"),
        func.array_agg(KeypointGroundLink.keypoint_id).label("kp_ids")
    ).join(
        Keypoint, Keypoint.id == KeypointGroundLink.keypoint_id
    ).filter(
        Keypoint.case_id == case_id
    ).group_by(
        KeypointGroundLink.ground_code
    ).all()
    
    # 법적 사유 이름 조회
    ground_codes = [stat[0] for stat in ground_stats]
    grounds_map = {}
    if ground_codes:
        grounds = db.query(LegalGround).filter(
            LegalGround.code.in_(ground_codes)
        ).all()
        grounds_map = {g.code: g.name_ko for g in grounds}
    
    items = []
    for ground_code, kp_count, kp_ids in ground_stats:
        items.append(LegalGroundSummaryItem(
            ground_code=ground_code,
            ground_name=grounds_map.get(ground_code, ground_code),
            keypoint_count=kp_count,
            evidence_count=0,  # TODO: 증거 연결 후 구현
            keypoint_ids=kp_ids or [],
        ))
    
    return LegalGroundSummaryResponse(
        case_id=case_id,
        total_keypoints=total,
        grounds=sorted(items, key=lambda x: x.keypoint_count, reverse=True),
    )


async def _fallback_extract(
    case_id: str,
    request: AIExtractionRequest,
    db: Session,
) -> List[dict]:
    """
    AI Worker 연결 실패 시 직접 추출 (간소화 버전)
    실제로는 AI Worker의 KeypointExtractor 호출
    """
    # TODO: 직접 OpenAI 호출 또는 빈 리스트 반환
    return []

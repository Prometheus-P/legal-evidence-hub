"""
Pydantic schemas for Auto-Extraction API
012-precedent-integration: T009-T010
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.party import PartyType, RelationshipType, PartyNodeResponse, RelationshipResponse


class AutoExtractedPartyRequest(BaseModel):
    """Schema for AI Worker auto-extracted party (T009)"""
    name: str = Field(..., min_length=1, max_length=100, description="Party name")
    type: PartyType = Field(..., description="Party type")
    extraction_confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")
    source_evidence_id: str = Field(..., description="Source evidence ID")


class AutoExtractedPartyResponse(BaseModel):
    """Response for auto-extracted party creation"""
    created: List[PartyNodeResponse] = Field(default_factory=list, description="Created parties")
    duplicates: List[Dict[str, Any]] = Field(default_factory=list, description="Duplicate parties")


class AutoExtractedRelationshipRequest(BaseModel):
    """Schema for AI Worker auto-extracted relationship (T010)"""
    source_party_name: str = Field(..., description="Source party name")
    target_party_name: str = Field(..., description="Target party name")
    type: RelationshipType = Field(..., description="Relationship type")
    extraction_confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")
    evidence_text: Optional[str] = Field(None, description="Evidence text for inference")


class AutoExtractedRelationshipResponse(BaseModel):
    """Response for auto-extracted relationship creation"""
    created: List[RelationshipResponse] = Field(default_factory=list, description="Created relationships")
    skipped: List[Dict[str, Any]] = Field(default_factory=list, description="Skipped relationships")

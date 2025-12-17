"""
Pydantic schemas for Party Graph API
007-lawyer-portal-v1: US1 (Party Relationship Graph) and US4 (Evidence-Party Links)
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime


# ============================================================
# Enums (matching SQLAlchemy enums in models.py)
# ============================================================

class PartyType(str, Enum):
    """Party type enum"""
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    THIRD_PARTY = "third_party"
    CHILD = "child"
    FAMILY = "family"


class RelationshipType(str, Enum):
    """Relationship type enum"""
    MARRIAGE = "marriage"
    AFFAIR = "affair"
    PARENT_CHILD = "parent_child"
    SIBLING = "sibling"
    IN_LAW = "in_law"
    COHABIT = "cohabit"


class LinkType(str, Enum):
    """Evidence link type enum"""
    MENTIONS = "mentions"
    PROVES = "proves"
    INVOLVES = "involves"
    CONTRADICTS = "contradicts"


# ============================================================
# Position Schema (for React Flow coordinates)
# ============================================================

class Position(BaseModel):
    """Position coordinates for React Flow node placement"""
    x: float = Field(default=0, description="X coordinate")
    y: float = Field(default=0, description="Y coordinate")


# ============================================================
# Party Node Schemas
# ============================================================

class PartyNodeCreate(BaseModel):
    """Schema for creating a new party node"""
    type: PartyType = Field(..., description="Party type")
    name: str = Field(..., min_length=1, max_length=100, description="Party name")
    alias: Optional[str] = Field(None, max_length=50, description="Alias for legal documents (e.g., 김○○)")
    birth_year: Optional[int] = Field(None, ge=1900, le=2100, description="Birth year (YYYY)")
    occupation: Optional[str] = Field(None, max_length=100, description="Occupation")
    position: Position = Field(default_factory=Position, description="React Flow position")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PartyNodeUpdate(BaseModel):
    """Schema for updating a party node (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    alias: Optional[str] = Field(None, max_length=50)
    birth_year: Optional[int] = Field(None, ge=1900, le=2100)
    occupation: Optional[str] = Field(None, max_length=100)
    position: Optional[Position] = None
    metadata: Optional[Dict[str, Any]] = None


class PartyNodeResponse(BaseModel):
    """Schema for party node response"""
    id: str
    case_id: str
    type: PartyType
    name: str
    alias: Optional[str] = None
    birth_year: Optional[int] = None
    occupation: Optional[str] = None
    position: Position
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Relationship Schemas
# ============================================================

class RelationshipCreate(BaseModel):
    """Schema for creating a new relationship between parties"""
    source_party_id: str = Field(..., description="Source party UUID")
    target_party_id: str = Field(..., description="Target party UUID")
    type: RelationshipType = Field(..., description="Relationship type")
    start_date: Optional[date] = Field(None, description="Relationship start date")
    end_date: Optional[date] = Field(None, description="Relationship end date")
    notes: Optional[str] = Field(None, description="Notes about the relationship")

    @field_validator('target_party_id')
    @classmethod
    def validate_no_self_reference(cls, v, info):
        """Ensure source and target are different"""
        if info.data.get('source_party_id') and v == info.data['source_party_id']:
            raise ValueError("Source and target party cannot be the same")
        return v


class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship (all fields optional)"""
    type: Optional[RelationshipType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class RelationshipResponse(BaseModel):
    """Schema for relationship response"""
    id: str
    case_id: str
    source_party_id: str
    target_party_id: str
    type: RelationshipType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Evidence-Party Link Schemas
# ============================================================

class EvidenceLinkCreate(BaseModel):
    """Schema for creating an evidence-party link"""
    evidence_id: str = Field(..., min_length=1, max_length=100, description="DynamoDB evidence ID")
    party_id: Optional[str] = Field(None, description="Linked party UUID")
    relationship_id: Optional[str] = Field(None, description="Linked relationship UUID")
    link_type: LinkType = Field(default=LinkType.MENTIONS, description="Link type")

    @field_validator('party_id')
    @classmethod
    def validate_at_least_one_target(cls, v, info):
        """Ensure at least one link target is provided"""
        if not v and not info.data.get('relationship_id'):
            raise ValueError("At least one of party_id or relationship_id must be provided")
        return v


class EvidenceLinkResponse(BaseModel):
    """Schema for evidence link response"""
    id: str
    case_id: str
    evidence_id: str
    party_id: Optional[str] = None
    relationship_id: Optional[str] = None
    link_type: LinkType
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Party Graph Combined Response
# ============================================================

class PartyGraphResponse(BaseModel):
    """Complete party graph data for React Flow rendering"""
    nodes: List[PartyNodeResponse] = Field(default_factory=list, description="Party nodes")
    relationships: List[RelationshipResponse] = Field(default_factory=list, description="Party relationships")


# ============================================================
# List Response Schemas
# ============================================================

class PartyListResponse(BaseModel):
    """Paginated party list response"""
    items: List[PartyNodeResponse]
    total: int


class RelationshipListResponse(BaseModel):
    """Paginated relationship list response"""
    items: List[RelationshipResponse]
    total: int


class EvidenceLinkListResponse(BaseModel):
    """Paginated evidence link list response"""
    items: List[EvidenceLinkResponse]
    total: int

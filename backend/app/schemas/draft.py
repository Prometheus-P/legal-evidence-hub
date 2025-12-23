"""
Draft Schemas - Draft generation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DraftPreviewRequest(BaseModel):
    """Draft preview request schema"""
    sections: list[str] = Field(default=["청구취지", "청구원인"])
    language: str = "ko"
    style: str = "법원 제출용_표준"


class DraftCitation(BaseModel):
    """Draft citation schema"""
    evidence_id: str
    snippet: str
    labels: list[str]


class DraftPreviewResponse(BaseModel):
    """Draft preview response schema"""
    case_id: str
    draft_text: str
    citations: list[DraftCitation]
    generated_at: datetime


class DraftExportFormat(str, Enum):
    """Draft export format options"""
    DOCX = "docx"
    PDF = "pdf"

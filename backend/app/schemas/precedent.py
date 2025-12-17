"""
Pydantic schemas for Precedent Search API
012-precedent-integration: T007-T008
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class DivisionRatio(BaseModel):
    """재산분할 비율"""
    plaintiff: int = Field(..., ge=0, le=100, description="원고 비율")
    defendant: int = Field(..., ge=0, le=100, description="피고 비율")


class PrecedentCase(BaseModel):
    """판례 정보 스키마 (T007)"""
    case_ref: str = Field(..., description="사건번호 (예: 2020다12345)")
    court: str = Field(..., description="법원 (예: 서울가정법원)")
    decision_date: str = Field(..., description="선고일 (ISO 8601)")
    summary: str = Field(..., description="판결 요지")
    division_ratio: Optional[DivisionRatio] = Field(None, description="재산분할 비율")
    key_factors: List[str] = Field(default_factory=list, description="주요 요인")
    similarity_score: float = Field(..., ge=0, le=1, description="유사도 점수")


class QueryContext(BaseModel):
    """검색 컨텍스트"""
    fault_types: List[str] = Field(default_factory=list, description="유책사유 목록")
    total_found: int = Field(0, description="총 검색 결과 수")


class PrecedentSearchResponse(BaseModel):
    """판례 검색 응답 스키마 (T008)"""
    precedents: List[PrecedentCase] = Field(default_factory=list, description="판례 목록")
    query_context: QueryContext = Field(default_factory=QueryContext, description="검색 컨텍스트")


class PrecedentSearchRequest(BaseModel):
    """판례 검색 요청 스키마 (optional query params)"""
    limit: int = Field(10, ge=1, le=20, description="최대 반환 개수")
    min_score: float = Field(0.5, ge=0, le=1, description="최소 유사도 점수")

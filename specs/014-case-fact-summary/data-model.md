# Data Model: 사건 전체 사실관계 요약

**Feature**: 014-case-fact-summary
**Date**: 2025-12-22

## 1. DynamoDB: CaseFactSummary

### Table: leh_case_summary (기존 테이블 활용)

| Attribute | Type | Description |
|-----------|------|-------------|
| `case_id` (PK) | String | 사건 ID (case_XXXXX) |
| `ai_summary` | String | AI 생성 원본 사실관계 (최대 10,000자) |
| `modified_summary` | String (nullable) | 변호사 수정 사실관계 |
| `previous_version` | String (nullable) | 재생성 전 이전 수정본 (1-버전 백업) |
| `evidence_ids` | List[String] | 사용된 증거 ID 목록 |
| `fault_types` | List[String] | 추출된 유책사유 목록 |
| `created_at` | String (ISO8601) | AI 요약 최초 생성 시간 |
| `modified_at` | String (ISO8601, nullable) | 마지막 수정 시간 |
| `modified_by` | String (nullable) | 수정한 사용자 ID |
| `regenerated_at` | String (ISO8601, nullable) | 재생성 시간 |

### Access Patterns

1. **GetItem**: case_id로 사실관계 조회
2. **PutItem**: 신규 생성 또는 전체 업데이트
3. **UpdateItem**: 부분 필드 업데이트 (modified_summary 등)

### Example Item

```json
{
  "case_id": "case_abc123",
  "ai_summary": "### 사건 개요\n혼인기간 8년...\n\n### 사실관계\n1. [증거1] 2023년 3월 - 배우자의 외도 정황 발견...\n2. [증거2] 2023년 5월 - 폭언 녹음...",
  "modified_summary": "### 사건 개요\n혼인기간 8년 (2015.03 ~ 2023.11)...\n\n### 사실관계\n1. [증거1] 2023년 3월 15일 - 피고의 외도 정황 최초 인지. 카카오톡 대화에서 제3자와의 부적절한 관계 확인...",
  "previous_version": null,
  "evidence_ids": ["evt_001", "evt_002", "evt_003"],
  "fault_types": ["부정행위", "가정폭력"],
  "created_at": "2025-12-22T10:00:00Z",
  "modified_at": "2025-12-22T11:30:00Z",
  "modified_by": "user_lawyer123",
  "regenerated_at": null
}
```

---

## 2. Backend Pydantic Schemas

### File: `backend/app/schemas/fact_summary.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FactSummaryBase(BaseModel):
    """사실관계 요약 기본 스키마"""
    ai_summary: str = Field(..., description="AI 생성 원본 사실관계")
    modified_summary: Optional[str] = Field(None, description="변호사 수정 사실관계")
    evidence_ids: List[str] = Field(default_factory=list, description="사용된 증거 ID 목록")
    fault_types: List[str] = Field(default_factory=list, description="추출된 유책사유")


class FactSummaryResponse(FactSummaryBase):
    """사실관계 조회 응답"""
    case_id: str
    created_at: datetime
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    has_previous_version: bool = Field(False, description="이전 버전 존재 여부")


class FactSummaryGenerateRequest(BaseModel):
    """사실관계 생성 요청"""
    force_regenerate: bool = Field(False, description="기존 요약 무시하고 재생성")


class FactSummaryGenerateResponse(BaseModel):
    """사실관계 생성 응답"""
    case_id: str
    ai_summary: str
    evidence_count: int
    fault_types: List[str]
    generated_at: datetime


class FactSummaryUpdateRequest(BaseModel):
    """사실관계 수정 요청"""
    modified_summary: str = Field(..., min_length=1, max_length=15000)


class FactSummaryUpdateResponse(BaseModel):
    """사실관계 수정 응답"""
    case_id: str
    modified_summary: str
    modified_at: datetime
    modified_by: str
```

---

## 3. Frontend TypeScript Types

### File: `frontend/src/types/fact-summary.ts`

```typescript
export interface FactSummary {
  case_id: string;
  ai_summary: string;
  modified_summary: string | null;
  evidence_ids: string[];
  fault_types: string[];
  created_at: string;
  modified_at: string | null;
  modified_by: string | null;
  has_previous_version: boolean;
}

export interface FactSummaryGenerateRequest {
  force_regenerate?: boolean;
}

export interface FactSummaryGenerateResponse {
  case_id: string;
  ai_summary: string;
  evidence_count: number;
  fault_types: string[];
  generated_at: string;
}

export interface FactSummaryUpdateRequest {
  modified_summary: string;
}

export interface FactSummaryUpdateResponse {
  case_id: string;
  modified_summary: string;
  modified_at: string;
  modified_by: string;
}
```

---

## 4. Relationships

```
┌─────────────────┐
│     Case        │
│  (PostgreSQL)   │
│  - id           │
│  - title        │
│  - status       │
└────────┬────────┘
         │ 1:1
         ▼
┌─────────────────┐
│ CaseFactSummary │
│   (DynamoDB)    │
│  - case_id (PK) │
│  - ai_summary   │
│  - modified_... │
└────────┬────────┘
         │ references
         ▼
┌─────────────────┐
│    Evidence     │
│   (DynamoDB)    │
│  - evidence_id  │
│  - case_id      │
│  - ai_summary   │◄── 개별 증거 요약 수집
└─────────────────┘
```

---

## 5. State Transitions

```
                    ┌─────────────┐
                    │   Empty     │
                    │ (no summary)│
                    └──────┬──────┘
                           │ POST /generate
                           ▼
                    ┌─────────────┐
                    │  Generated  │
                    │(ai_summary) │
                    └──────┬──────┘
                           │ PATCH /update
                           ▼
                    ┌─────────────┐
                    │  Modified   │
                    │(+ modified) │
                    └──────┬──────┘
                           │ POST /generate (force)
                           ▼
                    ┌─────────────┐
                    │ Regenerated │
                    │(+ previous) │
                    └─────────────┘
```

---

## 6. Validation Rules

| Field | Rule |
|-------|------|
| `case_id` | 존재하는 Case ID, 사용자 접근 권한 필요 |
| `ai_summary` | 1~10,000자, 필수 |
| `modified_summary` | 1~15,000자 (수정 시 더 길어질 수 있음) |
| `evidence_ids` | 해당 case_id에 속한 증거만 포함 |
| `fault_types` | 민법 840조 카테고리 또는 자유 텍스트 |

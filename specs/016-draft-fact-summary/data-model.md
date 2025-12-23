# Data Model: Draft Generation with Fact-Summary

**Feature**: 016-draft-fact-summary
**Date**: 2025-12-23

## Entities

### 1. Case Fact Summary (Existing - No Changes)

**Storage**: DynamoDB (`leh_case_summary` table)

| Field | Type | Description |
|:------|:-----|:------------|
| `case_id` | string (PK) | 사건 ID |
| `ai_summary` | string | AI 생성 사실관계 요약 |
| `modified_summary` | string | null | 변호사 수정 요약 (우선 사용) |
| `modified_by` | string | null | 수정자 user_id |
| `modified_at` | ISO8601 | null | 수정 일시 |
| `regenerated_at` | ISO8601 | 마지막 재생성 일시 |
| `previous_version` | string | null | 재생성 전 버전 백업 |

### 2. Draft Preview Response (Existing - No Changes)

**Storage**: In-memory (API Response)

| Field | Type | Description |
|:------|:-----|:------------|
| `case_id` | string | 사건 ID |
| `draft_text` | string | 생성된 초안 텍스트 |
| `citations` | list[Citation] | 증거 인용 목록 |
| `precedent_citations` | list[PrecedentCitation] | 판례 인용 목록 |
| `generated_at` | datetime | 생성 일시 |
| `preview_disclaimer` | string | AI 생성 면책 조항 |

### 3. Draft Job (Existing - No Changes)

**Storage**: PostgreSQL (`jobs` table)

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | UUID (PK) | Job ID |
| `case_id` | string (FK) | 사건 ID |
| `user_id` | string (FK) | 요청자 ID |
| `job_type` | enum | DRAFT_GENERATION |
| `status` | enum | QUEUED → PROCESSING → COMPLETED/FAILED |
| `progress` | string | 진행률 (0-100) |
| `input_data` | JSON | 요청 파라미터 |
| `output_data` | JSON | 결과 데이터 |
| `error_details` | JSON | 에러 정보 |
| `created_at` | datetime | 생성 일시 |
| `started_at` | datetime | 시작 일시 |
| `completed_at` | datetime | 완료 일시 |

## Relationships

```
Case (1) ────────── (1) CaseFactSummary
  │
  └─────────────── (N) DraftJob
                        │
                        └── (1) DraftPreviewResponse (in output_data)
```

## State Transitions

### Draft Generation Flow (Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                    generate_draft_preview()                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Validate case access                                        │
│       ↓                                                         │
│  2. Get fact summary from DynamoDB                              │
│       ↓                                                         │
│  ┌──────────────────┐                                          │
│  │ Fact summary     │──[없음]──→ ValidationError                │
│  │ exists?          │           "사실관계 요약을 먼저 생성해주세요" │
│  └──────────────────┘                                          │
│       ↓ [있음]                                                   │
│  3. Get legal knowledge (RAG - 유지)                            │
│       ↓                                                         │
│  4. Get precedents (RAG - 유지)                                 │
│       ↓                                                         │
│  5. Get consultations (RAG - 유지)                              │
│       ↓                                                         │
│  6. Build prompt with fact_summary_context                      │
│     (evidence_context = 빈 리스트)                               │
│       ↓                                                         │
│  7. Call OpenAI GPT-4o-mini                                     │
│       ↓                                                         │
│  8. Return DraftPreviewResponse                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Async Draft Generation Flow (Updated)

```
┌───────────────────────────────────────────────────────────────────┐
│                  start_async_draft_preview()                       │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Create Job (status: QUEUED)                                   │
│       ↓                                                           │
│  2. Schedule BackgroundTask                                       │
│       ↓                                                           │
│  3. Return job_id immediately                                     │
│                                                                   │
│  ─────────── BackgroundTask ───────────                          │
│                                                                   │
│  4. Update Job (status: PROCESSING)                               │
│       ↓                                                           │
│  5. Execute generate_draft_preview() [same logic as above]        │
│       ↓                                                           │
│  6a. Success → Update Job (status: COMPLETED, output_data)        │
│  6b. Error → Update Job (status: FAILED, error_details)           │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Validation Rules

### Fact Summary Validation

| Rule | Condition | Error |
|:-----|:----------|:------|
| Required | `fact_summary` is None or empty string | ValidationError("사실관계 요약을 먼저 생성해주세요") |

### No Changes to Existing Validation

- Case access validation: 기존 유지
- Evidence list validation: **제거** (더 이상 증거 필수 아님)

## Migration Notes

### Breaking Changes
- 증거 없이도 초안 생성 가능 (fact-summary만 있으면 됨)
- 기존: 증거 없음 → ValidationError
- 신규: fact-summary 없음 → ValidationError

### Backward Compatibility
- API 스키마 변경 없음
- 응답 형식 변경 없음
- 기존 클라이언트 호환

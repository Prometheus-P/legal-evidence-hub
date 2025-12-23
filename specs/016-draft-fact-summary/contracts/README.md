# API Contracts: Draft Generation with Fact-Summary

**Feature**: 016-draft-fact-summary
**Date**: 2025-12-23

## No API Changes

이 기능은 **API 스키마 변경 없음**입니다.

### Existing Endpoints (Unchanged)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/cases/{case_id}/draft-preview` | 동기 초안 생성 |
| POST | `/cases/{case_id}/draft-preview/async` | 비동기 초안 생성 시작 |
| GET | `/cases/{case_id}/draft-preview/async/{job_id}` | 비동기 작업 상태 조회 |

### Request Schema (Unchanged)

```json
{
  "sections": ["청구취지", "청구원인"],
  "language": "ko",
  "style": "formal"
}
```

### Response Schema (Unchanged)

```json
{
  "case_id": "string",
  "draft_text": "string",
  "citations": [],
  "precedent_citations": [],
  "generated_at": "ISO8601",
  "preview_disclaimer": "string"
}
```

### New Error Response

| Status | Condition | Body |
|:-------|:----------|:-----|
| 400 | Fact summary 없음 | `{"detail": "사실관계 요약을 먼저 생성해주세요...", "status_code": 400}` |

## Why No Changes?

1. **내부 로직만 변경**: RAG 검색 → Fact-Summary 사용
2. **응답 형식 동일**: 클라이언트 호환성 유지
3. **기존 에러 패턴 따름**: ValidationError 사용

## Backward Compatibility

- 기존 클라이언트: 100% 호환
- Frontend 변경: 없음 (에러 메시지 표시만)

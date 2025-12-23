# Quickstart: Draft Generation with Fact-Summary

**Feature**: 016-draft-fact-summary
**Date**: 2025-12-23

## Overview

이 기능은 초안 생성 시 증거 파일 RAG 검색을 제거하고, 사실관계 요약(fact-summary) 텍스트만 사용하여 GPT에 전달합니다. 이를 통해 컨텍스트 크기를 75-85% 감소시키고 OpenAI API 타임아웃 문제를 해결합니다.

## Prerequisites

1. **Fact Summary 생성 완료**
   - 초안 생성 전 사건의 사실관계 요약이 생성되어 있어야 함
   - 사건 상세 → 사실관계 요약 탭에서 생성

2. **DynamoDB 테이블**
   - `leh_case_summary` 테이블에 fact-summary 저장됨

## Quick Test

### 1. Fact Summary 확인

```bash
# Staging API에서 fact-summary 확인
curl -X GET "https://dpbf86zqulqfy.cloudfront.net/api/v1/cases/{case_id}/fact-summary" \
  -H "Authorization: Bearer {token}"
```

예상 응답:
```json
{
  "case_id": "case_xxx",
  "ai_summary": "원고와 피고는 2020년 결혼하여...",
  "modified_summary": null,
  "status": "generated"
}
```

### 2. 초안 생성 (Sync)

```bash
curl -X POST "https://dpbf86zqulqfy.cloudfront.net/api/v1/cases/{case_id}/draft-preview" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"sections": ["청구취지", "청구원인"]}'
```

예상 응답 (60초 이내):
```json
{
  "case_id": "case_xxx",
  "draft_text": "소장\n\n원고: ...\n피고: ...\n\n청구취지\n...",
  "citations": [],
  "precedent_citations": [...],
  "generated_at": "2025-12-23T12:00:00Z",
  "preview_disclaimer": "이 초안은 AI가 생성한 것으로..."
}
```

### 3. 초안 생성 (Async - 권장)

```bash
# 1. 비동기 작업 시작
curl -X POST "https://dpbf86zqulqfy.cloudfront.net/api/v1/cases/{case_id}/draft-preview/async" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"sections": ["청구취지", "청구원인"]}'

# 응답
{
  "job_id": "job_xxx",
  "case_id": "case_xxx",
  "status": "queued",
  "created_at": "2025-12-23T12:00:00Z"
}

# 2. 상태 폴링
curl -X GET "https://dpbf86zqulqfy.cloudfront.net/api/v1/cases/{case_id}/draft-preview/async/{job_id}" \
  -H "Authorization: Bearer {token}"

# 완료 시 응답
{
  "job_id": "job_xxx",
  "status": "completed",
  "progress": 100,
  "result": {
    "case_id": "case_xxx",
    "draft_text": "...",
    ...
  }
}
```

## Error Handling

### Fact Summary 없음

```json
{
  "detail": "사실관계 요약을 먼저 생성해주세요. [사건 상세] → [사실관계 요약] 탭에서 생성할 수 있습니다.",
  "status_code": 400
}
```

→ 해결: 사건 상세 페이지에서 "사실관계 요약 생성" 버튼 클릭

## Implementation Files

| File | Changes |
|:-----|:--------|
| `backend/app/services/draft_service.py` | RAG 검색 제거, fact-summary 검증 추가 |
| `backend/app/services/draft/rag_orchestrator.py` | evidence 검색 스킵 |
| `backend/app/services/draft/prompt_builder.py` | evidence_context 빈 리스트 처리 |

## Testing

### Unit Test

```bash
cd backend
pytest tests/unit/test_draft_service.py -v
```

### Staging E2E Test

```bash
cd frontend
npx playwright test e2e/staging-draft-verification.spec.ts
```

## Rollback

문제 발생 시 `dev` 브랜치로 롤백:

```bash
git checkout dev
git push upstream dev --force-with-lease  # 주의: 권한 필요
```

또는 Lambda 콘솔에서 이전 버전으로 배포.

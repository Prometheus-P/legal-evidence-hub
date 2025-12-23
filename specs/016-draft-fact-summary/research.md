# Research: Draft Generation with Fact-Summary

**Feature**: 016-draft-fact-summary
**Date**: 2025-12-23

## Research Task 1: 현재 RAG 검색 구조 분석

### Decision
RAG 검색을 완전히 제거하지 않고, evidence RAG만 스킵하고 legal/precedent/consultation RAG는 유지한다.

### Rationale
- Evidence RAG가 타임아웃의 주요 원인 (대용량 증거 파일 검색)
- Legal knowledge RAG는 법률 조문 참조에 필수적
- Precedent RAG는 유사 판례 인용에 필요
- Consultation RAG는 상담 내역 참조에 유용

### Current Implementation Analysis

**draft_service.py:generate_draft_preview()**
```python
# Line 146 - RAG 검색 (제거 대상)
rag_results = self.rag_orchestrator.perform_rag_search(case_id, request.sections)
evidence_results = rag_results.get("evidence", [])  # 제거
legal_results = rag_results.get("legal", [])         # 유지

# Line 157 - Fact summary 조회 (유지)
fact_summary_context = self._get_fact_summary_context(case_id)
```

### Alternatives Considered

| Option | Pros | Cons | Decision |
|:-------|:-----|:-----|:---------|
| A. RAG 완전 제거 | 가장 빠름 | 법률 조문/판례 인용 불가 | Rejected |
| B. Evidence RAG만 제거 | 균형 잡힌 접근 | 약간의 지연 | **Selected** |
| C. RAG 캐싱 추가 | 성능 향상 | 복잡성 증가 | Rejected |

---

## Research Task 2: Fact-Summary 데이터 구조

### Decision
기존 `get_case_fact_summary()` 함수를 그대로 사용하고, `modified_summary` 우선 사용 로직 유지.

### Data Schema (DynamoDB: leh_case_summary)
```json
{
  "case_id": "string (PK)",
  "ai_summary": "string",
  "modified_summary": "string | null",
  "modified_by": "string | null",
  "modified_at": "ISO8601 | null",
  "regenerated_at": "ISO8601"
}
```

### Existing Code (draft_service.py:629-658)
```python
def _get_fact_summary_context(self, case_id: str) -> str:
    summary_data = get_case_fact_summary(case_id)
    if not summary_data:
        return ""

    # Prefer lawyer-modified summary over AI-generated
    fact_summary = summary_data.get("modified_summary") or summary_data.get("ai_summary", "")
    if not fact_summary:
        return ""

    return f"""[사건 사실관계 요약]
{fact_summary}
---
위 사실관계는 변호사가 검토/수정한 내용입니다. 초안 작성 시 이 사실관계를 우선적으로 참조하세요."""
```

### Rationale
- 기존 로직이 이미 lawyer-modified → AI-generated 우선순위 처리
- 추가 개발 불필요, 재사용

---

## Research Task 3: 에러 처리 전략

### Decision
Fact-summary가 없는 경우 `ValidationError`를 발생시키고, 사용자에게 명확한 안내 메시지 제공.

### Error Flow
```
1. generate_draft_preview() 호출
2. _get_fact_summary_context() 호출
3. fact_summary가 빈 문자열인 경우:
   → raise ValidationError("사실관계 요약을 먼저 생성해주세요. [사건 상세] → [사실관계 요약] 탭에서 생성할 수 있습니다.")
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|:-------|:-----|:-----|:---------|
| A. 에러 발생 | 명확한 사용자 안내 | 기존 흐름 변경 | **Selected** |
| B. 빈 초안 생성 | 호환성 유지 | 품질 저하, 혼란 | Rejected |
| C. 기존 RAG 폴백 | 기능 유지 | 타임아웃 재발 | Rejected |

---

## Research Task 4: Prompt 최적화

### Decision
Evidence context를 빈 리스트로 전달하고, Prompt에서 fact-summary를 최우선 참조하도록 기존 안내문 유지.

### Prompt Structure (Current)
```
**사건 정보:** ...
**사건 사실관계 요약 (변호사 검토/수정본):**  ← 최우선 참조
{fact_summary_context}
**관련 법률 조문:**  ← 유지
{legal_str}
**유사 판례 참고자료:**  ← 유지
{precedent_str}
**증거 자료:**  ← 빈 리스트 "(증거 자료 없음 - 기본 템플릿으로 작성)"
{evidence_str}
```

### Expected Token Reduction
| Context Type | Before (tokens) | After (tokens) | Reduction |
|:-------------|:----------------|:---------------|:----------|
| Evidence | ~5,000-20,000 | 0 | 100% |
| Fact Summary | 0 | ~500-1,500 | N/A |
| Legal | ~1,000 | ~1,000 | 0% |
| Precedent | ~1,500 | ~1,500 | 0% |
| **Total** | **~8,000-24,000** | **~3,000-4,000** | **~75-85%** |

---

## Research Task 5: 테스트 전략

### Decision
기존 테스트에서 RAG 검색 모킹을 업데이트하고, fact-summary 기반 테스트 케이스 추가.

### Test Cases
1. **Happy Path**: fact-summary 있음 → 초안 생성 성공
2. **No Summary**: fact-summary 없음 → ValidationError
3. **Empty Summary**: 빈 문자열 → ValidationError
4. **Async Draft**: 비동기 초안 생성 → 동일 로직 적용

### Mocking Strategy
```python
# Before
@patch('app.services.draft_service.search_evidence_by_semantic')
@patch('app.services.draft_service.get_case_fact_summary')

# After
@patch('app.services.draft_service.get_case_fact_summary')
# RAG 검색 모킹 제거 (더 이상 호출되지 않음)
```

---

## Summary of Decisions

| Topic | Decision | Impact |
|:------|:---------|:-------|
| RAG Search | Evidence RAG 제거, Legal/Precedent/Consultation 유지 | 타임아웃 해결 |
| Fact Summary | 기존 로직 재사용 | 변경 최소화 |
| Error Handling | ValidationError with 안내 메시지 | 명확한 UX |
| Prompt | evidence_context 빈 리스트 | 75-85% 토큰 감소 |
| Testing | 모킹 업데이트, 새 케이스 추가 | 회귀 방지 |

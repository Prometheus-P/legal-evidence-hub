# Implementation Plan: Draft Generation with Fact-Summary

**Branch**: `016-draft-fact-summary` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-draft-fact-summary/spec.md`

## Summary

초안 생성 시 RAG 검색으로 증거 파일을 GPT에 전달하면 컨텍스트가 너무 커서 OpenAI API 타임아웃(60초)이 발생한다. 이 문제를 해결하기 위해 증거 파일 RAG 검색을 제거하고, 이미 생성된 fact-summary 텍스트만 사용하여 초안을 생성한다. 컨텍스트 크기가 대폭 감소하여 타임아웃 없이 안정적으로 초안을 생성할 수 있다.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, OpenAI (gpt-4o-mini), boto3 (DynamoDB)
**Storage**: DynamoDB (leh_case_summary 테이블), PostgreSQL (RDS)
**Testing**: pytest
**Target Platform**: AWS Lambda + EC2 (Backend)
**Project Type**: Web application (Backend + Frontend)
**Performance Goals**: 초안 생성 60초 이내, 성공률 95% 이상
**Constraints**: OpenAI API 타임아웃 60초, Lambda 타임아웃 90초
**Scale/Scope**: 단일 case 당 1개의 fact-summary, 증거 개수 무관

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|:----------|:-------|:------|
| I. Evidence Integrity | PASS | 증거 데이터 변경 없음, fact-summary만 읽기 |
| II. Case Isolation | PASS | case_id 기반 접근, 교차 case 쿼리 없음 |
| III. No Auto-Submit | PASS | 변경 없음 - 초안은 여전히 "Preview Only" |
| IV. AWS-Only Storage | PASS | DynamoDB (fact-summary), S3 변경 없음 |
| V. Clean Architecture | PASS | Service → Repository/Utils 패턴 유지 |
| VI. Branch Protection | PASS | PR을 통한 dev 병합 |
| VII. TDD Cycle | N/A | 기존 테스트 수정만 필요, 새 테스트 불필요 |
| VIII. Semantic Versioning | N/A | 마이너 변경, 버전 범프 없음 |

## Project Structure

### Documentation (this feature)

```text
specs/016-draft-fact-summary/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API 변경 없음)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── services/
│   │   ├── draft_service.py          # 수정: RAG 검색 제거, fact-summary 전용
│   │   └── draft/
│   │       ├── rag_orchestrator.py   # 수정: evidence RAG 검색 조건부 스킵
│   │       └── prompt_builder.py     # 수정: evidence_context 없이 동작
│   └── utils/
│       └── dynamo.py                 # 기존: get_case_fact_summary() 사용
└── tests/
    └── unit/
        └── test_draft_service.py     # 수정: fact-summary 기반 테스트
```

**Structure Decision**: 기존 Backend 구조 유지, DraftService 내부 로직만 수정

## Complexity Tracking

> 복잡성 추가 없음 - 오히려 RAG 검색 제거로 단순화

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Implementation Approach

### Phase 0: Research Findings

1. **현재 구조 분석 완료**:
   - `draft_service.py:146` - `perform_rag_search()` 호출 (제거 대상)
   - `draft_service.py:157` - `_get_fact_summary_context()` 호출 (유지)
   - `draft_service.py:164-173` - PromptBuilder에 모든 context 전달 (단순화)

2. **fact-summary 데이터 확인**:
   - DynamoDB `leh_case_summary` 테이블에 저장
   - `get_case_fact_summary(case_id)` → `ai_summary` or `modified_summary`

3. **변경 범위 최소화**:
   - RAGOrchestrator.perform_rag_search() 호출 제거
   - evidence_context를 빈 리스트로 전달
   - fact_summary_context가 없으면 에러 반환

### Phase 1: Design

**핵심 변경점**:
1. `generate_draft_preview()`:
   - RAG 검색 제거 (`rag_orchestrator.perform_rag_search()` 호출 삭제)
   - fact-summary 존재 여부 검증 추가
   - evidence_results를 빈 리스트로 대체

2. `_execute_draft_generation_task()`:
   - 동일한 로직 적용 (비동기 초안 생성)

3. **에러 처리**:
   - fact-summary 없음 → ValidationError("사실관계 요약을 먼저 생성해주세요")

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|:-----|:-----------|:-------|:-----------|
| fact-summary 없는 사건 | Medium | Medium | 명확한 에러 메시지 및 UI 안내 |
| 초안 품질 저하 | Low | High | fact-summary에 핵심 정보 포함 전제 |
| 기존 테스트 실패 | High | Low | 테스트 모킹 업데이트 |

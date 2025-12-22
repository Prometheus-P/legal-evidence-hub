# Tasks: 사건 전체 사실관계 요약

**Input**: Design documents from `/specs/014-case-fact-summary/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD cycle applicable per Constitution VII - tests included where specified.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Backend/Frontend 기본 파일 생성 및 스키마 정의

- [x] T001 [P] Create Pydantic schemas in `backend/app/schemas/fact_summary.py`
- [x] T002 [P] Create TypeScript types in `frontend/src/types/fact-summary.ts`
- [x] T003 [P] Add DynamoDB CRUD functions in `backend/app/utils/dynamo.py` (get_case_fact_summary, put_case_fact_summary, update_case_fact_summary)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core service and API infrastructure that MUST complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create FactSummaryService class skeleton in `backend/app/services/fact_summary_service.py`
- [x] T005 Create API router skeleton in `backend/app/api/fact_summary.py`
- [x] T006 Register router in `backend/app/main.py` (add to app.include_router)
- [x] T007 [P] Create frontend API client skeleton in `frontend/src/lib/api/fact-summary.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - AI 기반 사실관계 자동 생성 (Priority: P1) 🎯 MVP

**Goal**: 개별 증거 AI 요약을 종합하여 사건 전체 사실관계를 자동 생성

**Independent Test**: "사실관계 생성" 버튼 클릭 시 시간순 사실관계 스토리 표시

### Implementation for User Story 1

- [x] T008 [US1] Implement `_build_generation_prompt()` in `backend/app/services/fact_summary_service.py` - 증거 요약을 받아 GPT 프롬프트 생성
- [x] T009 [US1] Implement `_collect_evidence_summaries()` in `backend/app/services/fact_summary_service.py` - DynamoDB에서 증거 요약 수집, 시간순 정렬
- [x] T010 [US1] Implement `generate_fact_summary()` in `backend/app/services/fact_summary_service.py` - GPT-4o-mini 호출, 결과 저장
- [x] T011 [US1] Implement `POST /cases/{case_id}/fact-summary/generate` endpoint in `backend/app/api/fact_summary.py`
- [x] T012 [US1] Implement `GET /cases/{case_id}/fact-summary` endpoint in `backend/app/api/fact_summary.py`
- [x] T013 [P] [US1] Implement `generateFactSummary()` API function in `frontend/src/lib/api/fact-summary.ts`
- [x] T014 [P] [US1] Implement `getFactSummary()` API function in `frontend/src/lib/api/fact-summary.ts`
- [x] T015 [US1] Create FactSummaryPanel component in `frontend/src/components/fact-summary/FactSummaryPanel.tsx` - 생성 버튼, 로딩 상태, 결과 표시
- [x] T016 [US1] Integrate FactSummaryPanel into case detail page in `frontend/src/app/lawyer/cases/[id]/LawyerCaseDetailClient.tsx`

**Checkpoint**: 사실관계 자동 생성 기능 완성 - 버튼 클릭으로 AI 요약 확인 가능

---

## Phase 4: User Story 2 - 사실관계 수정 및 저장 (Priority: P1)

**Goal**: 변호사가 AI 생성 사실관계를 편집하고 저장

**Independent Test**: 텍스트 편집 후 저장 → 다음 접속 시 수정 내용 유지

### Implementation for User Story 2

- [x] T017 [US2] Implement `update_fact_summary()` in `backend/app/services/fact_summary_service.py` - modified_summary 저장
- [x] T018 [US2] Implement `PATCH /cases/{case_id}/fact-summary` endpoint in `backend/app/api/fact_summary.py`
- [x] T019 [P] [US2] Implement `updateFactSummary()` API function in `frontend/src/lib/api/fact-summary.ts`
- [x] T020 [US2] Create FactSummaryEditor component in `frontend/src/components/fact-summary/FactSummaryPanel.tsx` - textarea, 저장 버튼 (inline 구현)
- [x] T021 [US2] Add unsaved changes warning (beforeunload event) in FactSummaryPanel
- [x] T022 [US2] Integrate FactSummaryEditor into FactSummaryPanel - 편집 모드 전환

**Checkpoint**: 사실관계 수정/저장 완성 - 수정 내용 영구 저장 가능

---

## Phase 5: User Story 3 - 사실관계 기반 초안 생성 (Priority: P2)

**Goal**: 수정된 사실관계가 초안 생성에 반영

**Independent Test**: 사실관계 수정 후 초안 생성 → 초안에 수정 내용 포함

### Implementation for User Story 3

- [x] T023 [US3] Add `get_case_fact_summary()` call in `backend/app/services/draft_service.py` - 사실관계 조회
- [x] T024 [US3] Modify `generate_draft_preview()` in `backend/app/services/draft_service.py` - 사실관계 컨텍스트 추가
- [x] T025 [US3] Update `build_draft_prompt()` in `backend/app/services/draft/prompt_builder.py` - fact_summary_context 파라미터 추가

**Checkpoint**: 초안 생성 시 수정된 사실관계 반영

---

## Phase 6: User Story 4 - 사실관계 기반 판례 추천 (Priority: P2)

**Goal**: 수정된 사실관계로 유사 판례 검색

**Independent Test**: 사실관계 수정 후 판례 검색 → 맥락 기반 검색 결과

### Implementation for User Story 4

- [x] T026 [US4] Add `get_case_fact_summary()` call in `backend/app/services/precedent_service.py`
- [x] T027 [US4] Modify `search_similar_precedents()` in `backend/app/services/precedent_service.py` - 사실관계 기반 검색 쿼리 사용

**Checkpoint**: 판례 검색이 사실관계 맥락 반영

---

## Phase 7: User Story 5 - 사실관계 재생성 (Priority: P3)

**Goal**: 새 증거 추가 시 사실관계 재생성, 이전 버전 백업

**Independent Test**: 재생성 버튼 클릭 → 기존 수정본 백업, 새 사실관계 생성

### Implementation for User Story 5

- [x] T028 [US5] Implement `regenerate_fact_summary()` in `backend/app/services/fact_summary_service.py` - previous_version 백업 로직
- [x] T029 [US5] Update `POST /generate` endpoint in `backend/app/api/fact_summary.py` - force_regenerate 파라미터 처리
- [x] T030 [US5] Add regenerate button and confirmation modal in `frontend/src/components/fact-summary/FactSummaryPanel.tsx`

**Checkpoint**: 재생성 기능 완성 - 이전 버전 백업 확인 가능

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 에지 케이스, 에러 처리, 문서화

- [x] T031 [P] Add error handling for no evidence case in FactSummaryService
- [x] T032 [P] Add error handling for API timeout (30s limit) in FactSummaryPanel
- [x] T033 [P] Add loading skeleton UI in FactSummaryPanel
- [x] T034 [P] Add toast notifications for success/error states in FactSummaryPanel
- [x] T035 Validate quickstart.md with actual API calls

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3-7 (User Stories)**: All depend on Phase 2 completion
- **Phase 8 (Polish)**: Depends on all user stories

### User Story Dependencies

- **US1 (사실관계 생성)**: Phase 2 완료 후 시작 - 다른 스토리에 의존 없음
- **US2 (수정/저장)**: Phase 2 완료 후 시작 - US1 UI 통합하나 독립 테스트 가능
- **US3 (초안 연계)**: Phase 2 완료 후 시작 - US1/US2와 데이터 공유
- **US4 (판례 연계)**: Phase 2 완료 후 시작 - US1/US2와 데이터 공유
- **US5 (재생성)**: Phase 2 완료 후 시작 - US1 기반 확장

### Parallel Opportunities

**Phase 1 내 병렬**:
```
T001 (schemas) || T002 (types) || T003 (dynamo utils)
```

**Phase 3 내 병렬**:
```
T013 (frontend API) || T014 (frontend API) - 동시 작성 가능
```

**Phase 4 내 병렬**:
```
T019 (frontend API) - 독립적
```

**User Story 간 병렬** (팀 작업 시):
```
US1 완료 후:
  Developer A: US3 (초안 연계)
  Developer B: US4 (판례 연계)
  Developer C: US5 (재생성)
```

---

## Parallel Example: Phase 1

```bash
# Launch all Phase 1 tasks together:
Task: "Create Pydantic schemas in backend/app/schemas/fact_summary.py"
Task: "Create TypeScript types in frontend/src/types/fact-summary.ts"
Task: "Add DynamoDB CRUD functions in backend/app/utils/dynamo.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (생성)
4. Complete Phase 4: User Story 2 (수정/저장)
5. **STOP and VALIDATE**: 생성 + 수정 기능 독립 테스트
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → 기반 완성
2. US1 (생성) → 테스트 → Deploy (MVP!)
3. US2 (수정) → 테스트 → Deploy
4. US3 + US4 (연계) → 테스트 → Deploy
5. US5 (재생성) → 테스트 → Deploy
6. Polish → Final Deploy

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Constitution VII: TDD 사이클 적용 권장
- API Gateway 30초 타임아웃 고려하여 GPT 호출 최적화 필요
- 각 User Story는 독립적으로 테스트 가능해야 함

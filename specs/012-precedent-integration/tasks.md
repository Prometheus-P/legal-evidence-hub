# Tasks: 판례 검색 시스템 완성 및 인물 관계도 통합

**Input**: Design documents from `/specs/012-precedent-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/precedent-api.yaml

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)

## Path Conventions

- **Backend**: `backend/app/` (FastAPI)
- **Frontend**: `frontend/src/` (Next.js)
- **AI Worker**: `ai_worker/src/` (Lambda)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and schema migrations

- [x] T001 Create feature branch `012-precedent-integration` from dev
- [x] T002 [P] Add `is_auto_extracted`, `extraction_confidence`, `source_evidence_id` columns to `party_nodes` table via Alembic migration in `backend/alembic/versions/`
- [x] T003 [P] Add `is_auto_extracted`, `extraction_confidence`, `evidence_text` columns to `party_relationships` table via Alembic migration in `backend/alembic/versions/`
- [x] T004 [P] Create Qdrant collection `leh_legal_knowledge` with 1536-dim vectors in `backend/app/utils/precedent_search.py`
- [x] T005 [P] Add index `idx_party_nodes_auto_extracted` on `party_nodes(is_auto_extracted)`
- [x] T006 [P] Add index `idx_party_relationships_auto_extracted` on `party_relationships(is_auto_extracted)`

**Checkpoint**: Database schema and vector store ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create `PrecedentCase` Pydantic schema in `backend/app/schemas/precedent.py`
- [x] T008 Create `PrecedentSearchResponse` schema in `backend/app/schemas/precedent.py`
- [x] T009 [P] Create `AutoExtractedPartyRequest` schema in `backend/app/schemas/auto_extraction.py`
- [x] T010 [P] Create `AutoExtractedRelationshipRequest` schema in `backend/app/schemas/auto_extraction.py`
- [x] T011 Create precedent TypeScript types in `frontend/src/types/precedent.ts`
- [x] T012 [P] Verify existing `search_legal_knowledge()` in `backend/app/utils/qdrant.py` works with new collection

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 4 - 판례 데이터 초기화 (Priority: P2) - EXECUTE FIRST

**Goal**: Load precedent data into Qdrant so search functionality works

**Independent Test**: Run `python scripts/fetch_and_store_legal_data.py --count 10` and verify data in Qdrant

**Why First**: User Stories 1, 2 depend on precedent data existing in Qdrant

### Implementation for User Story 4

- [x] T013 [US4] Verify `ai_worker/scripts/fetch_and_store_legal_data.py` script exists and is functional
- [x] T014 [US4] Add fallback sample data (10 cases) in `ai_worker/scripts/sample_precedents.json` for when API is unavailable
- [x] T015 [US4] Create `ai_worker/scripts/load_sample_precedents.py` for fallback data loading
- [x] T016 [US4] Fallback script created with full OpenAI embedding support
- [ ] T017 [US4] Run script to load initial data: `python scripts/load_sample_precedents.py` (requires runtime execution)
- [ ] T018 [US4] Verify Qdrant collection has data via `GET /collections/leh_legal_knowledge` (requires runtime execution)

**Checkpoint**: Qdrant has precedent data for search

---

## Phase 4: User Story 1 - 유사 판례 검색 및 열람 (Priority: P1)

**Goal**: Lawyers can search and view similar precedents from case detail page

**Independent Test**: Click "유사 판례 검색" button on case detail page to see precedent list

### Backend Implementation for User Story 1

- [x] T019 [US1] Create `PrecedentService` class in `backend/app/services/precedent_service.py`
- [x] T020 [US1] Implement `search_similar_precedents(case_id, limit, min_score)` method in `PrecedentService`
- [x] T021 [US1] Add fault type extraction from case evidence in `PrecedentService.get_fault_types(case_id)`
- [x] T022 [US1] Create `/cases/{case_id}/similar-precedents` GET endpoint in `backend/app/api/precedent.py`
- [x] T023 [US1] Register precedent router in `backend/app/main.py`
- [x] T024 [US1] Add Qdrant connection fallback (empty array + error message) in `PrecedentService`

### Frontend Implementation for User Story 1

- [x] T025 [P] [US1] Create `searchSimilarPrecedents(caseId, options)` API client in `frontend/src/lib/api/precedent.ts`
- [x] T026 [P] [US1] Create `PrecedentCard` component in `frontend/src/components/precedent/PrecedentCard.tsx`
- [x] T027 [US1] Create `PrecedentPanel` component in `frontend/src/components/precedent/PrecedentPanel.tsx`
- [x] T028 [US1] Create `PrecedentModal` component for detail view in `frontend/src/components/precedent/PrecedentModal.tsx`
- [x] T029 [US1] Add PrecedentPanel to case detail page in `frontend/src/app/lawyer/cases/[id]/page.tsx` (requires page integration)
- [x] T030 [US1] Add loading state and error handling to PrecedentPanel
- [x] T031 [US1] Handle empty results with "관련 판례를 찾을 수 없습니다" message

**Checkpoint**: User Story 1 complete - lawyers can search and view precedents

---

## Phase 5: User Story 2 - 초안 작성 시 판례 인용 (Priority: P1)

**Goal**: Draft generation automatically includes relevant precedents

**Independent Test**: Generate draft and verify precedent citations are included

### Implementation for User Story 2

- [ ] T032 [US2] Modify `DraftService` to call `PrecedentService.search_similar_precedents()` in `backend/app/services/draft_service.py`
- [ ] T033 [US2] Add precedent context to GPT-4o prompt in `DraftService.generate_draft()`
- [ ] T034 [US2] Include precedent citations in draft response structure
- [ ] T035 [US2] Update draft preview UI to display cited precedents in `frontend/src/components/draft/`

**Checkpoint**: User Story 2 complete - drafts include precedent citations

---

## Phase 6: User Story 3 - 인물 관계 자동 추출 (Priority: P2)

**Goal**: AI Worker auto-extracts parties and relationships, saves to Backend

**Independent Test**: Upload KakaoTalk evidence, verify new parties appear in relationship diagram

### Backend Implementation for User Story 3

- [ ] T036 [US3] Add `is_auto_extracted` field to `PartyNode` model in `backend/app/db/models/party.py`
- [ ] T037 [US3] Add `extraction_confidence` field to `PartyNode` model in `backend/app/db/models/party.py`
- [ ] T038 [US3] Add `source_evidence_id` field to `PartyNode` model in `backend/app/db/models/party.py`
- [ ] T039 [P] [US3] Add `is_auto_extracted`, `extraction_confidence`, `evidence_text` fields to `PartyRelationship` model in `backend/app/db/models/relationship.py`
- [ ] T040 [US3] Create `/cases/{case_id}/parties/auto-extract` POST endpoint in `backend/app/api/party.py`
- [ ] T041 [US3] Implement duplicate name detection in `PartyService.create_auto_extracted_party()` in `backend/app/services/party_service.py`
- [ ] T042 [US3] Create `/cases/{case_id}/relationships/auto-extract` POST endpoint in `backend/app/api/relationship.py`
- [ ] T043 [US3] Implement confidence threshold filter (0.7) in `RelationshipService.create_auto_extracted_relationship()` in `backend/app/services/relationship_service.py`

### AI Worker Implementation for User Story 3

- [ ] T044 [US3] Add Backend API client in `ai_worker/src/api_client.py` for calling `/parties/auto-extract`
- [ ] T045 [US3] Modify `handler.py` to call Backend API after `RelationshipInferrer` completes in `ai_worker/handler.py`
- [ ] T046 [US3] Add error handling for Backend API failures (retry 3x, then log to DynamoDB)
- [ ] T047 [US3] Add authentication headers (internal API key or Lambda IAM) to API client

### Frontend Implementation for User Story 3

- [ ] T048 [P] [US3] Add visual indicator for auto-extracted parties in `frontend/src/components/party-graph/PartyNode.tsx`
- [ ] T049 [US3] Add confidence badge to auto-extracted parties
- [ ] T050 [US3] Add edit/delete functionality for auto-extracted parties in party graph

**Checkpoint**: User Story 3 complete - auto-extracted parties appear in relationship diagram

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T051 [P] Update API documentation in `docs/specs/API_SPEC.md` for new endpoints
- [ ] T052 [P] Add unit tests for `PrecedentService` in `backend/tests/unit/test_precedent_service.py`
- [ ] T053 [P] Add contract tests for precedent API in `backend/tests/contract/test_precedent_api.py`
- [ ] T054 Run E2E tests `frontend/e2e/precedent.spec.ts` and fix any failures
- [ ] T055 Run quickstart.md verification steps
- [ ] T056 Update CLAUDE.md Recent Changes section

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 4 (Phase 3)**: Depends on Phase 2 - BLOCKS User Stories 1, 2 (needs data)
- **User Story 1 (Phase 4)**: Depends on Phase 3 (needs precedent data in Qdrant)
- **User Story 2 (Phase 5)**: Depends on Phase 4 (needs PrecedentService from US1)
- **User Story 3 (Phase 6)**: Depends on Phase 2 only (independent of precedent search)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation)
                       ↓
              ┌────────┴────────┐
              ↓                 ↓
      Phase 3 (US4)      Phase 6 (US3)
              ↓                 ↓
      Phase 4 (US1)       (independent)
              ↓
      Phase 5 (US2)
              ↓
      Phase 7 (Polish)
```

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002 (party_nodes migration) || T003 (party_relationships migration) || T004 (Qdrant collection)
T005 (party_nodes index) || T006 (party_relationships index)
```

**Phase 2 (Foundation)**:
```
T009 (PartyRequest schema) || T010 (RelationshipRequest schema) || T011 (TS types) || T012 (Qdrant verify)
```

**Phase 4 (US1)**:
```
Backend: T019 → T020 → T021 → T022 → T023 → T024
Frontend: T025 || T026 (parallel) → T027 → T028 → T029 → T030 → T031
Backend and Frontend can run in parallel after T024 completes
```

**Phase 6 (US3)**:
```
Backend: T036 → T037 → T038 (sequential - same file)
         T039 (parallel - different file)
         T040 → T041 → T042 → T043
AI Worker: T044 → T045 → T046 → T047
Frontend: T048 || T049 (parallel) → T050
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 4 Only)

1. Complete Phase 1: Setup (DB migrations, Qdrant collection)
2. Complete Phase 2: Foundational (schemas, types)
3. Complete Phase 3: User Story 4 (load precedent data)
4. Complete Phase 4: User Story 1 (search & display)
5. **STOP and VALIDATE**: Test precedent search independently
6. Deploy/demo if ready

### Incremental Delivery

1. **Setup + Foundation** → Infrastructure ready
2. **Add US4** → Precedent data loaded
3. **Add US1** → Test independently → Deploy/Demo (MVP!)
4. **Add US2** → Draft citations → Deploy/Demo
5. **Add US3** → Auto-extraction → Deploy/Demo
6. **Polish** → Tests, docs, cleanup

### Team Assignment (per CLAUDE.md)

- **L (vsun410)**: Phase 3 (US4), Phase 6 (US3) AI Worker tasks (T044-T047)
- **H (leaf446)**: Phase 1-2 (Setup/Foundation), Phase 4-5 (US1/US2) Backend tasks
- **P (Prometheus-P)**: Phase 4-6 Frontend tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US4 must complete before US1/US2 (data dependency)
- US3 can run in parallel with US1/US2 (no data dependency)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

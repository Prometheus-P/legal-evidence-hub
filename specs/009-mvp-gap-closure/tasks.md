# Tasks: MVP 구현 갭 해소 (Production Readiness)

**Input**: Design documents from `/specs/009-mvp-gap-closure/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks included only where necessary for CI coverage (US4).

**Organization**: Tasks grouped by user story. Most features are 70-100% complete - tasks focus on configuration, integration, and polish.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`
- **Frontend**: `frontend/src/`
- **AI Worker**: `ai_worker/`
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Setup (Verification)

**Purpose**: Verify existing implementation state before making changes

- [ ] T001 Verify AWS CLI is configured with correct credentials
- [ ] T002 [P] Verify OpenAI API key is set in environment
- [ ] T003 [P] Verify Qdrant Cloud instance is accessible
- [ ] T004 Run `git checkout 009-mvp-gap-closure` to ensure on correct branch

---

## Phase 2: Foundational (AWS Infrastructure)

**Purpose**: AWS configuration that MUST be complete before US1 can function

**⚠️ CRITICAL**: AI Worker cannot process files until this phase is complete

- [ ] T005 Create S3 bucket `leh-evidence-dev` via AWS CLI: `aws s3 mb s3://leh-evidence-dev --region ap-northeast-2`
- [ ] T006 [P] Create S3 bucket `leh-evidence-prod` via AWS CLI: `aws s3 mb s3://leh-evidence-prod --region ap-northeast-2`
- [ ] T007 Attach S3 policy to Lambda execution role `leh-ai-worker-role`
- [ ] T008 Configure S3 event notification on `leh-evidence-dev` to trigger `leh-ai-worker` Lambda
- [ ] T009 [P] Configure S3 event notification on `leh-evidence-prod` to trigger production Lambda
- [ ] T010 Verify Lambda function `leh-ai-worker` exists and has correct handler

**Checkpoint**: S3 → Lambda trigger chain is complete - US1 can now function

---

## Phase 3: User Story 1 - AI Worker 실서비스 연동 (Priority: P1) 🎯 MVP

**Goal**: Evidence files uploaded to S3 automatically trigger AI analysis

**Independent Test**: Upload file to `s3://leh-evidence-dev/cases/test-case/raw/test.jpg` and verify DynamoDB record created

### Implementation for User Story 1

- [ ] T011 [US1] Test S3 upload triggers Lambda by uploading test file via AWS CLI
- [ ] T012 [US1] Verify DynamoDB table `leh_evidence_dev` receives analysis results
- [ ] T013 [US1] Verify Qdrant collection `case_rag_{case_id}` receives embeddings
- [ ] T014 [US1] Check CloudWatch logs for Lambda execution success
- [ ] T015 [US1] Document S3 path pattern in `docs/guides/EVIDENCE_UPLOAD.md`

**Checkpoint**: AI Worker is fully operational - files are processed automatically

---

## Phase 4: User Story 2 - Backend RAG 검색 및 Draft 생성 (Priority: P1) 🎯 MVP

**Goal**: RAG search and Draft Preview APIs work with real data

**Independent Test**: Call `POST /cases/{id}/draft-preview` and verify AI-generated draft with citations

### Implementation for User Story 2

> **Note**: Backend RAG/Draft is 90-95% complete. Tasks focus on verification and minor fixes.

- [ ] T016 [US2] Verify `GET /search?q={query}&case_id={id}` returns Qdrant results in `backend/app/api/search.py`
- [ ] T017 [US2] Verify `POST /cases/{id}/draft-preview` generates draft with citations in `backend/app/api/drafts.py`
- [ ] T018 [US2] Verify `GET /cases/{id}/draft-export` generates DOCX/PDF in `backend/app/services/draft_service.py`
- [ ] T019 [US2] Test draft generation with real case data (requires US1 complete)
- [ ] T020 [US2] Add smoke test for RAG search in `backend/tests/integration/test_search_smoke.py`

**Checkpoint**: RAG search and Draft generation work with AI Worker processed data

---

## Phase 5: User Story 3 - Frontend 에러 처리 통일 (Priority: P2)

**Goal**: Consistent error handling across all frontend components

**Independent Test**: Simulate network error and verify toast notification appears with retry option

### Implementation for User Story 3

- [ ] T021 [US3] Install react-hot-toast: `cd frontend && npm install react-hot-toast`
- [ ] T022 [US3] Add Toaster component to `frontend/src/app/layout.tsx`
- [ ] T023 [P] [US3] Add toast notifications to API client error handling in `frontend/src/lib/api/client.ts`
- [ ] T024 [P] [US3] Create useRetry hook with exponential backoff in `frontend/src/hooks/useRetry.ts`
- [ ] T025 [US3] Unify loading state naming (isLoading) across hooks in `frontend/src/hooks/`
- [ ] T026 [US3] Add toast for 403 errors (permission denied) in `frontend/src/lib/api/client.ts`
- [ ] T027 [US3] Add toast for 500 errors (server error) in `frontend/src/lib/api/client.ts`
- [ ] T028 [US3] Update error boundary components to use toast in `frontend/src/components/shared/ErrorBoundary.tsx`

**Checkpoint**: All API errors show user-friendly toast notifications with retry options

---

## Phase 6: User Story 4 - CI 테스트 커버리지 정상화 (Priority: P2)

**Goal**: CI enforces test coverage and all tests actually run

**Independent Test**: Create PR and verify CI runs 300+ tests with 65%+ coverage

### Implementation for User Story 4

- [ ] T029 [US4] Update backend coverage threshold to 70% in `backend/pytest.ini`
- [ ] T030 [P] [US4] Update ai_worker coverage threshold to 70% in `ai_worker/pytest.ini`
- [ ] T031 [US4] Fix conftest.py skip logic in `ai_worker/tests/conftest.py` - skip only integration tests on missing env vars
- [ ] T032 [P] [US4] Add unit tests for draft_service.py in `backend/tests/unit/test_draft_service.py`
- [ ] T033 [P] [US4] Add unit tests for search_service.py in `backend/tests/unit/test_search_service.py`
- [ ] T034 [P] [US4] Add unit tests for qdrant.py in `backend/tests/unit/test_qdrant_client.py`
- [ ] T035 [US4] Verify CI workflow runs tests without skipping in `.github/workflows/ci.yml`
- [ ] T036 [US4] Run `pytest --cov=app --cov-report=term-missing` locally and fix coverage gaps

**Checkpoint**: CI enforces 70% coverage, all 300+ tests run without skips

---

## Phase 7: User Story 5 - 사건별 권한 제어 (Priority: P2)

**Goal**: All case-related APIs enforce membership and log access attempts

**Independent Test**: Call `/cases/{id}/evidence` without membership and verify 403 response + audit log

### Implementation for User Story 5

- [ ] T037 [US5] Audit `/cases/*` endpoints for permission checks in `backend/app/api/cases.py`
- [ ] T038 [P] [US5] Audit `/evidence/*` endpoints for permission checks in `backend/app/api/evidence.py`
- [ ] T039 [P] [US5] Audit `/drafts/*` endpoints for permission checks in `backend/app/api/drafts.py`
- [ ] T040 [US5] Ensure 403 (not 404) on unauthorized access across all audited endpoints
- [ ] T041 [US5] Add audit_log write for ACCESS_DENIED in `backend/app/services/audit_log_service.py`
- [ ] T042 [US5] Add permission check middleware in `backend/app/middleware/case_permission.py`
- [ ] T043 [US5] Add contract test for 403 response in `backend/tests/contract/test_permission_403.py`

**Checkpoint**: Unauthorized access returns 403 and is logged in audit_logs table

---

## Phase 8: User Story 6 - 기본 배포 파이프라인 (Priority: P3)

**Goal**: All components deploy automatically on merge

**Independent Test**: Merge to dev and verify staging deployment completes within 10 minutes

### Implementation for User Story 6

- [ ] T044 [US6] Enable AI Worker deployment in `.github/workflows/deploy_paralegal.yml` (remove `&& false`)
- [ ] T045 [US6] Verify AI Worker Dockerfile exists at `ai_worker/Dockerfile.lambda`
- [ ] T046 [US6] Add health check endpoint to AI Worker if missing
- [ ] T047 [P] [US6] Document manual rollback procedure in `docs/guides/ROLLBACK.md`
- [ ] T048 [P] [US6] Add deployment status badge to README.md
- [ ] T049 [US6] Test staging deployment by merging small change to dev branch
- [ ] T050 [US6] Verify CloudFront invalidation completes after frontend deploy

**Checkpoint**: All components (Backend, Frontend, AI Worker) deploy on merge to dev/main

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T051 [P] Update CLAUDE.md with new technologies and recent changes
- [ ] T052 [P] Run quickstart.md validation steps end-to-end
- [ ] T053 [P] Update API documentation in `docs/specs/API_SPEC.md` if endpoints changed
- [ ] T054 Create PR from `009-mvp-gap-closure` to `dev` with full changelog
- [ ] T055 Merge PR after review and verify staging deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS US1
- **Phase 3 (US1)**: Depends on Phase 2 (AWS infrastructure)
- **Phase 4 (US2)**: Depends on Phase 3 (needs AI-processed data for realistic testing)
- **Phase 5 (US3)**: Can start after Phase 1 - independent
- **Phase 6 (US4)**: Can start after Phase 1 - independent
- **Phase 7 (US5)**: Can start after Phase 1 - independent
- **Phase 8 (US6)**: Can start after Phase 1 - independent (but recommend after US1)
- **Phase 9 (Polish)**: Depends on all user stories complete

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (AI Worker) | Phase 2 (AWS) | - |
| US2 (RAG/Draft) | US1 (needs data) | - |
| US3 (Error Handling) | Phase 1 only | US4, US5, US6 |
| US4 (CI Tests) | Phase 1 only | US3, US5, US6 |
| US5 (Permissions) | Phase 1 only | US3, US4, US6 |
| US6 (Deployment) | Phase 1 only | US3, US4, US5 |

### Within Each User Story

1. Configuration/setup tasks first
2. Implementation tasks second
3. Verification/test tasks last
4. All [P] marked tasks can run in parallel

### Parallel Opportunities

**Phase 2 (AWS)**:
```
T005 (dev bucket) || T006 (prod bucket) - parallel
T008 (dev notification) || T009 (prod notification) - parallel
```

**Phase 5-7 (US3, US4, US5)** can run entirely in parallel:
```
US3 Frontend Error Handling
US4 CI Test Coverage
US5 Permissions
```

**Within US3**:
```
T023 (toast in client) || T024 (useRetry hook) - parallel
```

**Within US4**:
```
T029 (backend threshold) || T030 (ai_worker threshold) - parallel
T032 (draft tests) || T033 (search tests) || T034 (qdrant tests) - parallel
```

**Within US5**:
```
T037 (cases audit) || T038 (evidence audit) || T039 (drafts audit) - parallel
```

---

## Parallel Example: US3 + US4 + US5

```bash
# These three user stories can run in parallel after Phase 1

# Developer A: US3 Frontend Error Handling
Task: "Install react-hot-toast: cd frontend && npm install react-hot-toast"
Task: "Add Toaster component to frontend/src/app/layout.tsx"

# Developer B: US4 CI Tests
Task: "Update backend coverage threshold to 70% in backend/pytest.ini"
Task: "Add unit tests for draft_service.py in backend/tests/unit/test_draft_service.py"

# Developer C: US5 Permissions
Task: "Audit /cases/* endpoints for permission checks in backend/app/api/cases.py"
Task: "Add audit_log write for ACCESS_DENIED in backend/app/services/audit_log_service.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (verification)
2. Complete Phase 2: Foundational (AWS infrastructure)
3. Complete Phase 3: US1 (AI Worker operational)
4. Complete Phase 4: US2 (RAG/Draft functional)
5. **STOP and VALIDATE**: Test full evidence upload → draft generation flow
6. Deploy to staging for demo

### Incremental Delivery (Recommended)

1. **Week 1**: Phase 1-3 (Setup → AWS → US1) → AI Worker operational
2. **Week 2**: Phase 4-6 (US2, US3, US4) in parallel → Core features + quality
3. **Week 3**: Phase 7-8 (US5, US6) → Security + deployment
4. **Week 4**: Phase 9 (Polish) → Production ready

### Single Developer Strategy

Execute in priority order:
1. T001-T010: Setup + AWS (2-3 hours)
2. T011-T015: US1 verification (1 hour)
3. T016-T020: US2 verification (1 hour)
4. T021-T028: US3 error handling (3-4 hours)
5. T029-T036: US4 CI tests (4-6 hours)
6. T037-T043: US5 permissions (3-4 hours)
7. T044-T050: US6 deployment (2-3 hours)
8. T051-T055: Polish (2 hours)

**Total estimated time**: 20-25 hours

---

## Notes

- Most code is already implemented (70-100% complete per user story)
- Focus is on configuration, verification, and polish
- AWS tasks (Phase 2) require appropriate IAM permissions
- CI tasks (US4) may require running tests locally first to identify gaps
- Commit after each task or logical group
- Create PR after each user story for review

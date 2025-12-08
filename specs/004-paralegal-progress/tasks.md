# Tasks: Paralegal Progress Dashboard

**Input**: `/specs/004-paralegal-progress/spec.md` and plan.md
**Prerequisites**: Feature branch `004-paralegal-progress`, plan reviewed with team POC.
**Tests**: Required (Constitution Principle VII - TDD). Every functional task has a preceding test task.

**Format**: `[ID] [P?] [Story] Description`

- `[P]` indicates a task can run in parallel (touches disjoint files).
- `[Story]` maps to user stories (US1 Monitor Throughput, US2 Feedback Tasks, US3 Blocked Filter).
- Include explicit file paths and expected artifacts per task.

---

## Phase 0: Alignment & Schema Prep

- [X] T001 [US1] Confirm data sources (Postgres cases, DynamoDB evidence, AI status) and document fields in `specs/004-paralegal-progress/data-model.md`.
- [X] T002 [US1] Review 16-item mid-demo checklist with PM/legal ops; capture canonical IDs + descriptions in `specs/004-paralegal-progress/contracts/checklist.json`.

---

## Phase 1: Backend Aggregation (User Story 1)

### Tests First
- [X] T101 [US1] Create pytest fixtures/mocks for case repo + evidence repo + AI worker state in `backend/tests/test_services/test_progress_service.py`.
- [X] T102 [US1] Write service tests covering:
  - happy path with multiple cases
  - empty assignments
  - evidence counts aggregated per status
  - AI status fallback (no record)
  (Add parameterized tests referencing `ProgressFilter` DTO).

### Implementation
- [X] T103 [P] [US1] Implement `ProgressSummary` Pydantic schemas in `backend/app/schemas/progress.py`.
- [X] T104 [US1] Add `ProgressService` in `backend/app/services/progress_service.py`:
  - query assigned cases (respect RBAC),
  - join evidence counts (uploaded / processing / ai_ready),
  - include AI draft info + timestamps,
  - expose `list_progress(user_id, filters)`.
- [X] T105 [US1] Add FastAPI router `backend/app/api/staff_progress.py` with `GET /staff/progress`, hooking RBAC dependency (paralegal/lawyer) and returning schema.
- [X] T106 [US1] Register router via `backend/app/main.py` and update OpenAPI tags.
- [X] T107 [US1] Create API tests `backend/tests/test_api/test_staff_progress.py` asserting:
  - unauthorized users rejected
  - paralegal receives only their cases
  - P95 latency guard (use `time.perf_counter` mock to assert instrumentation)

---

## Phase 2: Feedback Checklist Integration (User Story 2)

### Tests First
- [X] T201 [US2] Extend service tests with mock checklist data verifying pending/completed counts and JSON contract from `contracts/checklist.json`.
- [X] T202 [US2] Add API tests for checklist serialization + empty fallback.

### Implementation
- [X] T203 [P] [US2] Persist checklist metadata source (static JSON). Loads from `specs/004-paralegal-progress/contracts/checklist.json` via ChecklistProvider.
- [X] T204 [US2] Update `ProgressService` to attach `FeedbackChecklistItem[]` per case, defaulting to 16 entries, mark complete vs pending.
- [X] T205 [US2] Add `outstanding_feedback_count` and `feedback_last_updated` fields to schema + tests.
- [X] T206 [US2] Emit structured logging (`logger.warning`) for observability on checklist fallback scenarios.

---

## Phase 3: Blocked & Filter UX (User Story 3)

### Tests First
- [X] T301 [US3] Write tests confirming filters `?blocked_only=true`, `?assignee_id=` map to appropriate service arguments.
- [X] T302 [US3] Add tests for `is_blocked` determination (e.g., evidence_failed, feedback_pending, ai_processing).

### Implementation
- [X] T303 [US3] Update service to compute `is_blocked` + `blocked_reason` and support filter parameters.
- [X] T304 [US3] Extend router query params + validation; ensure docs mention filter options.
- [X] T305 [US3] Add blocking logic (evidence_failed, feedback_pending, ai_processing) in service.

---

## Phase 4: Frontend Dashboard

### Tests First
- [X] T401 [US1] Create React Testing Library tests for the page shell at `frontend/src/app/staff/progress/page.test.tsx` verifying loading, success, and empty states.
- [X] T402 [US2] Add tests for `FeedbackChecklist` component (expand/collapse, pending count chips).
- [X] T403 [US3] Add tests for filter bar interactions (blocked toggle, assignee dropdown) ensuring hooks call API with correct params.
- [X] T404 [Optional] Add Playwright smoke `frontend/e2e/staff-progress.spec.ts` hitting deployed endpoint.

### Implementation
- [X] T405 [US1] Create API fetcher `frontend/src/lib/api/staffProgress.ts` (fetcher + types). Handle retries/backoff.
- [X] T406 [US1] Build `/staff/progress/page.tsx`:
  - wrap with auth guard (via middleware),
  - render list of `ProgressCard` components,
  - show skeleton loaders and manual refresh button.
- [X] T407 [US1] Implement `ProgressCard` component with status chips, evidence counts, AI badge, timestamp.
- [X] T408 [US2] Implement `FeedbackChecklist` component with accordion/pill count, referencing contract IDs, showing notes/owners.
- [X] T409 [US3] Add `ProgressFilters` (blocked toggle, assignee filter inline in page header).
- [X] T410 [US3] Integrate toast notifications for API errors (inline toast component).
- [X] T411 [US2] Add "Feedback complete" success banner when pending count = 0.
- [X] T412 [US1] Ensure responsive layout (2-column grid on ≥1024px, single column mobile) via Tailwind classes.

---

## Phase 5: Documentation & Ops

- [X] T501 API docs already present in `docs/specs/API_SPEC.md` Section 8 (Staff Progress Dashboard API).
- [X] T502 Add API reference snippet to `docs/specs/API_SPEC.md` for `/staff/progress` - ALREADY EXISTS.
- [X] T503 Update `CLAUDE.md` Recent Changes section with 004-paralegal-progress feature summary.
- [X] T504 Prepare release notes summarizing #92 + mention coverage impact for #91. See `RELEASE_NOTES.md`.

---

## Phase 6: Verification

- [X] T601 Run backend tests: `cd backend && python3 -m pytest tests/test_services/test_progress_service.py tests/test_api/test_staff_progress.py` - ALL 11 TESTS PASS.
- [X] T602 Run frontend tests: `cd frontend && npm test src/app/staff/progress/page.test.tsx` - ALL 5 TESTS PASS.
- [ ] T603 Manual QA checklist:
  - Load dashboard with seeded data,
  - Toggle filters,
  - Expand checklist,
  - Validate blocked cases highlight.
- [ ] T604 Capture screenshots/video for demo + attach to PR.

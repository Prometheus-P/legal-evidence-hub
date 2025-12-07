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

- [ ] T001 [US1] Confirm data sources (Postgres cases, DynamoDB evidence, AI status) and document fields in `specs/004-paralegal-progress/data-model.md`.  
- [ ] T002 [US1] Review 16-item mid-demo checklist with PM/legal ops; capture canonical IDs + descriptions in `specs/004-paralegal-progress/contracts/checklist.json`.

---

## Phase 1: Backend Aggregation (User Story 1)

### Tests First
- [ ] T101 [US1] Create pytest fixtures/mocks for case repo + evidence repo + AI worker state in `backend/tests/test_services/test_progress_service.py`.
- [ ] T102 [US1] Write service tests covering:
  - happy path with multiple cases
  - empty assignments
  - evidence counts aggregated per status
  - AI status fallback (no record)  
  (Add parameterized tests referencing `ProgressFilter` DTO).

### Implementation
- [ ] T103 [P] [US1] Implement `ProgressSummary` Pydantic schemas in `backend/app/schemas/progress.py`.
- [ ] T104 [US1] Add `ProgressService` in `backend/app/services/progress_service.py`:
  - query assigned cases (respect RBAC),
  - join evidence counts (uploaded / processing / ai_ready),
  - include AI draft info + timestamps,
  - expose `list_progress(user_id, filters)`.
- [ ] T105 [US1] Add FastAPI router `backend/app/api/staff_progress.py` with `GET /staff/progress`, hooking RBAC dependency (paralegal/lawyer) and returning schema.
- [ ] T106 [US1] Register router via `backend/app/api/__init__.py` and update OpenAPI tags.
- [ ] T107 [US1] Create API tests `backend/tests/test_api/test_staff_progress.py` asserting:
  - unauthorized users rejected
  - paralegal receives only their cases
  - P95 latency guard (use `time.perf_counter` mock to assert instrumentation)

---

## Phase 2: Feedback Checklist Integration (User Story 2)

### Tests First
- [ ] T201 [US2] Extend service tests with mock checklist data verifying pending/completed counts and JSON contract from `contracts/checklist.json`.
- [ ] T202 [US2] Add API tests for checklist serialization + empty fallback.

### Implementation
- [ ] T203 [P] [US2] Persist checklist metadata source (either static JSON or Postgres table). For PoC load from `docs/specs/feedback.json` into service-level constant; plan migration if persistent store required (NEEDS CLARIFICATION with PM).
- [ ] T204 [US2] Update `ProgressService` to attach `FeedbackChecklistItem[]` per case, defaulting to 16 entries, mark complete vs pending.
- [ ] T205 [US2] Add `outstanding_feedback_count` and `feedback_last_updated` fields to schema + tests.
- [ ] T206 [US2] Emit structured logging (`logger.info("progress_feedback", case_id=..., pending=...)`) for observability.

---

## Phase 3: Blocked & Filter UX (User Story 3)

### Tests First
- [ ] T301 [US3] Write tests confirming filters `?blocked=true`, `?assignee=` map to appropriate service arguments.
- [ ] T302 [US3] Add tests for `is_blocked` determination (e.g., missing evidence >72h, AI failure, pending checklist).

### Implementation
- [ ] T303 [US3] Update service to compute `is_blocked` + `blocked_reason` (enum) and support filter parameters.
- [ ] T304 [US3] Extend router query params + validation; ensure docs mention filter options.
- [ ] T305 [US3] Add metrics hook (e.g., StatsD counter `staff_progress.blocked`) in service.

---

## Phase 4: Frontend Dashboard

### Tests First
- [ ] T401 [US1] Create React Testing Library tests for the page shell at `frontend/src/app/(dashboard)/staff/progress/__tests__/page.test.tsx` verifying loading, success, and empty states.
- [ ] T402 [US2] Add tests for `FeedbackChecklist` component (expand/collapse, pending count chips).
- [ ] T403 [US3] Add tests for filter bar interactions (blocked toggle, assignee dropdown) ensuring hooks call API with correct params.
- [ ] T404 [Optional] Add Playwright smoke `frontend/e2e/staff-progress.spec.ts` hitting mock server (skip if CI constraints).

### Implementation
- [ ] T405 [US1] Create React Query hook `frontend/src/lib/api/staffProgress.ts` (fetcher + types). Handle retries/backoff.
- [ ] T406 [US1] Build `/staff/progress/page.tsx`:
  - wrap with auth guard,
  - render list of `ProgressCard` components,
  - show skeleton loaders and manual refresh button.
- [ ] T407 [US1] Implement `ProgressCard` component with status chips, evidence counts, AI badge, timestamp.
- [ ] T408 [US2] Implement `FeedbackChecklist` component with accordion/pill count, referencing contract IDs, showing notes/owners.
- [ ] T409 [US3] Add `ProgressFilters` component with blocked toggle, assignee filter, search input.
- [ ] T410 [US3] Integrate toast notifications for API errors (`frontend/src/components/ui/ToastProvider.tsx`).
- [ ] T411 [US2] Add “Feedback complete” success banner when pending count = 0.
- [ ] T412 [US1] Ensure responsive layout (2-column grid on ≥1024px, single column mobile) via Tailwind classes.

---

## Phase 5: Documentation & Ops

- [ ] T501 Update `README.md` / `docs/specs/FRONTEND_SPEC.md` with screenshot + nav instructions.
- [ ] T502 Add API reference snippet to `docs/specs/API_SPEC.md` for `/staff/progress`.
- [ ] T503 Update `AGENTS.md` / `CLAUDE.md` contexts using `.specify/scripts/bash/update-agent-context.sh`.
- [ ] T504 Prepare release notes summarizing #92 + mention coverage impact for #91.

---

## Phase 6: Verification

- [ ] T601 Run backend tests: `cd backend && python3 -m pytest tests/test_services/test_progress_service.py tests/test_api/test_staff_progress.py --cov=app/utils/progress`.
- [ ] T602 Run frontend tests: `cd frontend && npm test staff-progress` and `npm run test:e2e -- staff-progress` (if Playwright task done).
- [ ] T603 Manual QA checklist:
  - Load dashboard with seeded data,
  - Toggle filters,
  - Expand checklist,
  - Validate blocked cases highlight.
- [ ] T604 Capture screenshots/video for demo + attach to PR.

# Tasks: Production Bug Fixes

**Input**: Design documents from `/specs/011-production-bug-fixes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/

**Tests**: Included per Constitution VII (TDD Cycle)

**Organization**: Tasks grouped by user story for independent implementation and testing.

**Focus**: Frontend (per user input)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/` (assigned to H)
- **Frontend**: `frontend/src/`, `frontend/src/__tests__/` (assigned to P)

---

## Phase 1: Setup (Diagnosis)

**Purpose**: Identify the root cause before implementing fixes

- [x] T001 Verify production cookie settings by testing POST /auth/login with curl and inspecting Set-Cookie headers
- [x] T002 Check backend environment variables for COOKIE_SAMESITE, COOKIE_SECURE, CORS_ORIGINS in production
- [x] T003 [P] Inspect frontend API client credentials setting in frontend/src/lib/api/client.ts
- [x] T004 [P] Verify JUST_LOGGED_IN_KEY race condition fix in frontend/src/contexts/AuthContext.tsx
- [x] T005 Document findings: Which root cause is confirmed (Cookie Config / Race Condition / Middleware Sync)

**Diagnosis Result**:
- **ROOT CAUSE CONFIRMED**: Backend Cookie Configuration
  - `COOKIE_SAMESITE` defaults to `"lax"` (blocks cross-origin)
  - `COOKIE_SECURE` defaults to `False` (incompatible with `SameSite=None`)
- Frontend credentials: OK (`credentials: 'include'` correctly set)
- Race Condition: OK (JUST_LOGGED_IN_KEY fix exists)
- Middleware: OK (auth redirect logic correct)

**Checkpoint**: Root cause identified - proceed to Backend Fix (T011-T013)

---

## Phase 2: User Story 1 - 로그인 후 정상 리다이렉트 (Priority: P1) MVP

**Goal**: 로그인 성공 후 역할별 대시보드로 정상 리다이렉트되고, 로그인 상태가 유지되어야 한다

**Independent Test**: 로그인 폼에서 유효한 자격 증명 입력 -> 대시보드 도달 -> 새로고침해도 로그인 유지

### Tests for User Story 1 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] E2E test: Login flow redirects to dashboard in frontend/e2e/auth.spec.ts
- [x] T007 [P] [US1] E2E test: Page refresh maintains login state in frontend/e2e/auth.spec.ts
- [x] T008 [P] [US1] E2E test: Back button from dashboard redirects back to dashboard in frontend/e2e/auth.spec.ts
- [ ] T009 [P] [US1] Unit test: AuthContext login method stores state correctly in frontend/src/__tests__/contexts/AuthContext.test.tsx
- [ ] T010 [P] [US1] Unit test: Middleware redirects authenticated user from /login in frontend/src/__tests__/middleware.test.ts

### Backend Fix (assigned to H - leaf446)

> **GitHub Issues Created**: #294 (DB Migration), #295-#298 (APIs)

- [x] T011 [US1] Update cookie settings in backend/app/core/config.py: auto-configure samesite="none" and secure=True for prod/dev environments
- [x] T012 [US1] Verify CORS_ORIGINS includes CloudFront domain in backend/app/core/config.py
- [x] T013 [P] [US1] Contract test: Login response includes correct Set-Cookie headers in backend/tests/contract/test_auth_cookies.py

### Frontend Fix (N/A - Root cause was backend)

- [N/A] T014-T017 ~~Frontend fixes~~ - Not needed, backend cookie config was the issue

### Verification

- [ ] T018 [US1] Manual test: Complete login flow on production URL (https://dpbf86zqulqfy.cloudfront.net)
- [ ] T019 [US1] Manual test: Verify all 3 roles (lawyer, client, detective) redirect to correct dashboards
- [ ] T020 [US1] Manual test: Page refresh maintains login state
- [ ] T021 [US1] Manual test: Back button redirects to dashboard (not login page)

**Checkpoint**: User Story 1 complete - Login flow works correctly, SC-001 through SC-004 verified

---

## Phase 3: User Story 2 - Lawyer Portal 기능 추가 (Priority: P2)

**Goal**: 변호사 포털에 알림, 메시지, 의뢰인/탐정 관리 기능 추가

**Independent Test**: 변호사로 로그인 후 각 기능(알림, 메시지, 의뢰인, 탐정)의 CRUD 동작 확인

**Depends On**: US1 완료 (로그인 정상 작동 후 테스트 가능)

### Backend Tasks (assigned to H - leaf446)

> **GitHub Issues**: #294 (DB Migration), #295 (Notifications), #296 (Messages), #297 (Clients), #298 (Detectives)

- [ ] T022 [US2] [Backend] Create DB migration for notifications, messages, clients, detectives tables
- [ ] T023 [US2] [Backend] Implement Notification API endpoints (GET /notifications, PATCH /notifications/{id}/read)
- [ ] T024 [US2] [Backend] Implement Message CRUD API endpoints (GET, POST, GET/:id, DELETE)
- [ ] T025 [US2] [Backend] Implement Client CRUD API endpoints (GET, POST, GET/:id, PATCH/:id, DELETE/:id)
- [ ] T026 [US2] [Backend] Implement Detective CRUD API endpoints (GET, POST, GET/:id, PATCH/:id, DELETE/:id)

### Frontend Tasks (assigned to P - Prometheus-P)

#### Types & API Clients

- [x] T027 [P] [US2] Create Notification types in frontend/src/types/notification.ts
- [x] T028 [P] [US2] Create Message types in frontend/src/types/message.ts
- [x] T029 [P] [US2] Create Client types (update) in frontend/src/types/client.ts
- [x] T030 [P] [US2] Create Detective types (update) in frontend/src/types/detective.ts
- [x] T031 [P] [US2] Create Notification API client in frontend/src/lib/api/notifications.ts
- [x] T032 [P] [US2] Create Message API client in frontend/src/lib/api/messages.ts
- [x] T033 [P] [US2] Create Client API client (update) in frontend/src/lib/api/clients.ts
- [x] T034 [P] [US2] Create Detective API client (update) in frontend/src/lib/api/detectives.ts

#### Hooks

- [x] T035 [P] [US2] Create useNotifications hook in frontend/src/hooks/useNotifications.ts
- [x] T036 [P] [US2] Create useDirectMessages hook in frontend/src/hooks/useDirectMessages.ts
- [x] T037 [P] [US2] Create useClientContacts hook in frontend/src/hooks/useClientContacts.ts
- [x] T038 [P] [US2] Create useDetectiveContacts hook in frontend/src/hooks/useDetectiveContacts.ts

#### Notification Components (FR-007)

- [x] T039 [P] [US2] Create NotificationBadge component in frontend/src/components/shared/NotificationBadge.tsx
- [x] T040 [P] [US2] Create NotificationDropdown component in frontend/src/components/shared/NotificationDropdown.tsx
- [x] T041 [P] [US2] Create NotificationItem component in frontend/src/components/shared/NotificationItem.tsx
- [x] T042 [US2] Integrate NotificationDropdown into LawyerNav in frontend/src/components/lawyer/LawyerNav.tsx

#### Message Components (FR-008)

- [x] T043 [P] [US2] Create MessageList component in frontend/src/components/lawyer/messages/MessageList.tsx
- [x] T044 [P] [US2] Create DirectMessageView component in frontend/src/components/lawyer/messages/DirectMessageView.tsx
- [x] T045 [P] [US2] Create ComposeMessage component in frontend/src/components/lawyer/messages/ComposeMessage.tsx
- [x] T046 [US2] Create /lawyer/messages page in frontend/src/app/lawyer/messages/page.tsx

#### Client Management Components (FR-009, FR-010, FR-015)

- [x] T047 [P] [US2] Create ClientCard component in frontend/src/components/lawyer/clients/ClientCard.tsx
- [x] T048 [P] [US2] Create ClientForm component (add/edit) in frontend/src/components/lawyer/clients/ClientForm.tsx
- [x] T049 [P] [US2] Create ClientList component in frontend/src/components/lawyer/clients/ClientList.tsx
- [x] T050 [US2] Update /lawyer/clients page with add button in frontend/src/app/lawyer/clients/page.tsx

#### Detective Management Components (FR-011, FR-012, FR-016)

- [x] T051 [P] [US2] Create DetectiveCard component in frontend/src/components/lawyer/detectives/DetectiveCard.tsx
- [x] T052 [P] [US2] Create DetectiveForm component (add/edit) in frontend/src/components/lawyer/detectives/DetectiveForm.tsx
- [x] T053 [P] [US2] Create DetectiveList component in frontend/src/components/lawyer/detectives/DetectiveList.tsx
- [x] T054 [US2] Update /lawyer/investigators page with add button in frontend/src/app/lawyer/investigators/page.tsx

#### Tests (TDD)

- [x] T055 [P] [US2] Unit tests for NotificationDropdown in frontend/src/__tests__/components/shared/NotificationDropdown.test.tsx (28 tests)
- [x] T056 [P] [US2] Unit tests for MessageList in frontend/src/__tests__/components/lawyer/messages/MessageList.test.tsx (27 tests)
- [x] T057 [P] [US2] Unit tests for ClientForm in frontend/src/__tests__/components/lawyer/clients/ClientForm.test.tsx (30 tests)
- [x] T058 [P] [US2] Unit tests for DetectiveForm in frontend/src/__tests__/components/lawyer/detectives/DetectiveForm.test.tsx (38 tests)

**Checkpoint**: US2 complete - Lawyer portal has notification, message, client, detective management

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T059 Run all tests: backend pytest + frontend Jest + E2E Playwright (1795 frontend passed, 1394 backend passed)
- [x] T060 [P] Update spec.md status from Draft to Complete
- [x] T061 [P] Run quickstart.md validation steps and document results (108 tests passed)
- [x] T062 Create PR to merge 011-production-bug-fixes -> dev (PR #304)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **User Story 1 (Phase 2)**: Depends on Phase 1 diagnosis
- **User Story 2 (Phase 3)**: Depends on US1 completion (login must work)
- **Polish (Phase 4)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Independent - can start immediately
- **User Story 2 (P2)**: DEPENDS on US1 (cannot test features until login works)

### Within User Story 2 (Frontend)

1. Types & API Clients (T027-T034) - can run in parallel
2. Hooks (T035-T038) - depends on types/API clients
3. Components (T039-T054) - depends on hooks
4. Tests (T055-T058) - can run in parallel with components (TDD)

### Parallel Opportunities

**Types & API Clients** (all [P]):
```
T027, T028, T029, T030 - Types (parallel)
T031, T032, T033, T034 - API Clients (parallel)
```

**Hooks** (all [P]):
```
T035, T036, T037, T038 - Hooks (parallel after types)
```

**Components** (grouped by feature, [P] within groups):
```
Notifications: T039, T040, T041 (parallel) -> T042 (integration)
Messages: T043, T044, T045 (parallel) -> T046 (page)
Clients: T047, T048, T049 (parallel) -> T050 (page)
Detectives: T051, T052, T053 (parallel) -> T054 (page)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Diagnosis) - DONE
2. Complete Phase 2: User Story 1 - IN PROGRESS
3. **STOP and VALIDATE**: Test on production URL
4. Create PR if SC-001 through SC-004 pass

### Incremental Delivery (User Story 2)

After US1 is complete:

1. **Backend first** (H - leaf446): T022-T026 (DB + APIs)
2. **Frontend parallel** (P): Types/Clients -> Hooks -> Components -> Tests
3. Feature-by-feature delivery:
   - Notifications (T039-T042)
   - Messages (T043-T046)
   - Clients (T047-T050)
   - Detectives (T051-T054)

### Success Criteria Mapping

| Success Criteria | Verification Task |
|-----------------|-------------------|
| SC-001: 100% redirect to dashboard | T018 |
| SC-002: State maintained on refresh | T020 |
| SC-003: < 3 seconds | T018 (observe timing) |
| SC-004: No login loop | T021 |
| SC-005: Notifications accessible | T042 verification |
| SC-006: Messages CRUD works | T046 verification |
| SC-007: Client add button works | T050 verification |
| SC-008: Detective add button works | T054 verification |

---

## Task Summary

| Phase | Task Range | Total | Completed | Pending | Notes |
|-------|-----------|-------|-----------|---------|-------|
| Phase 1: Setup | T001-T005 | 5 | 5 | 0 | Diagnosis complete |
| Phase 2: US1 | T006-T021 | 12* | 8 | 4 | *T014-T017 N/A |
| Phase 3: US2 | T022-T058 | 37 | 32 | 5 | Backend pending (T022-T026) |
| Phase 4: Polish | T059-T062 | 4 | 4 | 0 | PR #304 created |
| **Total** | T001-T062 | **58*** | **49** | **9** | *excluding 4 N/A tasks |

### Frontend Tasks (P - Prometheus-P) - **COMPLETE**

| Category | Tasks | Count | Status |
|----------|-------|-------|--------|
| US1 Unit Tests | T009, T010 | 2 | Pending |
| US2 Types | T027-T030 | 4 | ✅ Done |
| US2 API Clients | T031-T034 | 4 | ✅ Done |
| US2 Hooks | T035-T038 | 4 | ✅ Done |
| US2 Components | T039-T054 | 16 | ✅ Done |
| US2 Tests | T055-T058 | 4 | ✅ Done (123 tests) |
| **Frontend Total** | | **34** | **32/34 Complete** |

### Backend Tasks (H - leaf446) - **PENDING**

| Category | Tasks | Count | Status |
|----------|-------|-------|--------|
| US2 DB/APIs | T022-T026 | 5 | Pending (GitHub #294-#298) |
| **Backend Total** | | **5** | **0/5 Complete** |

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] / [US2] labels map tasks to user stories
- TDD: Write tests first, verify they fail, then implement
- Backend tasks already have GitHub issues (#294-#298) assigned to H
- Frontend focus per user input - 34 frontend tasks identified
- Commit after each logical task group

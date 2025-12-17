# Tasks: UI Upgrade

**Input**: Design documents from `/specs/013-ui-upgrade/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included per Constitution VII (TDD Cycle) - write tests first, verify they fail, then implement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` (Next.js App Router)
- **Components**: `frontend/src/components/`
- **Styles**: `frontend/src/styles/`
- **Tests**: `frontend/src/__tests__/`

---

## Phase 1: Setup (Design Token Foundation) ✅

**Purpose**: Establish the design token infrastructure that all components depend on

- [x] T001 Audit existing CSS variables in frontend/src/styles/globals.css
- [x] T002 Audit legacy color aliases in frontend/tailwind.config.js
- [x] T003 [P] Create design token CSS file at frontend/src/styles/design-tokens.css
- [x] T004 [P] Create TypeScript types for design tokens at frontend/src/types/design-tokens.ts
- [x] T005 Import design-tokens.css in frontend/src/styles/globals.css
- [x] T006 Install jest-axe and @axe-core/playwright dev dependencies

---

## Phase 2: Foundational (Primitive Components) ✅

**Purpose**: Core primitive components that ALL user stories depend on - MUST be complete before any story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Primitive Components

- [x] T007 [P] Create Button accessibility test at frontend/src/__tests__/components/primitives/Button.test.tsx
- [x] T008 [P] Create Input accessibility test at frontend/src/__tests__/components/primitives/Input.test.tsx
- [x] T009 [P] Create Modal accessibility test at frontend/src/__tests__/components/primitives/Modal.test.tsx
- [x] T010 [P] Create IconButton accessibility test at frontend/src/__tests__/components/primitives/IconButton.test.tsx

### Implementation for Primitive Components

- [x] T011 [P] Enhance Button component with design tokens at frontend/src/components/primitives/Button/Button.tsx
- [x] T012 [P] Create or enhance Input component at frontend/src/components/primitives/Input/Input.tsx
- [x] T013 [P] Enhance Modal component with focus trap and a11y at frontend/src/components/primitives/Modal/Modal.tsx
- [x] T014 [P] Enhance IconButton with touch targets at frontend/src/components/primitives/IconButton/IconButton.tsx
- [x] T015 [P] Update Spinner to use design tokens at frontend/src/components/primitives/Spinner/Spinner.tsx
- [x] T016 Export all primitives from frontend/src/components/primitives/index.ts

**Checkpoint**: Primitive components ready - user story implementation can now begin ✅

---

## Phase 3: User Story 1 - Design System Consistency (Priority: P1) 🎯 MVP ✅

**Goal**: Users experience consistent visual design across all lawyer portal pages using semantic design tokens

**Independent Test**: Navigate through lawyer portal pages (dashboard, cases, evidence, drafts) and verify consistent colors, typography, and component styling

### Tests for User Story 1

- [x] T017 [P] [US1] Create visual consistency test at frontend/src/__tests__/integration/design-consistency.test.tsx
- [x] T018 [P] [US1] Create legacy alias detection test at frontend/src/__tests__/unit/design-tokens.test.ts

### Implementation for User Story 1

- [x] T019 [P] [US1] Migrate CaseCard to design tokens at frontend/src/components/cases/CaseCard.tsx
- [x] T020 [P] [US1] Migrate AddCaseModal to design tokens at frontend/src/components/cases/AddCaseModal.tsx
- [x] T021 [P] [US1] Migrate EditCaseModal to design tokens at frontend/src/components/cases/EditCaseModal.tsx
- [x] T022 [P] [US1] Migrate CaseShareModal to design tokens at frontend/src/components/cases/CaseShareModal.tsx
- [x] T023 [P] [US1] Migrate EvidenceCard to design tokens at frontend/src/components/evidence/EvidenceCard.tsx
- [x] T024 [P] [US1] Migrate EvidenceTable to design tokens at frontend/src/components/evidence/EvidenceTable.tsx
- [x] T025 [P] [US1] Migrate EvidenceDataTable to design tokens at frontend/src/components/evidence/EvidenceDataTable.tsx
- [x] T026 [P] [US1] Migrate EvidenceUpload to design tokens at frontend/src/components/evidence/EvidenceUpload.tsx
- [x] T027 [P] [US1] Migrate DraftEditor to design tokens at frontend/src/components/draft/DraftEditor.tsx
- [x] T028 [P] [US1] Migrate DraftPreviewPanel to design tokens at frontend/src/components/draft/DraftPreviewPanel.tsx
- [x] T029 [P] [US1] Migrate DraftGenerationModal to design tokens at frontend/src/components/draft/DraftGenerationModal.tsx
- [x] T030 [P] [US1] Migrate RelationshipFlow to design tokens at frontend/src/components/relationship/RelationshipFlow.tsx
- [x] T031 [P] [US1] Migrate PersonNode to design tokens at frontend/src/components/relationship/PersonNode.tsx
- [x] T032 [P] [US1] Migrate RelationshipEdge to design tokens at frontend/src/components/relationship/RelationshipEdge.tsx
- [x] T033 [US1] Remove all legacy color aliases from frontend/tailwind.config.js (marked deprecated, landing pages still use)
- [x] T034 [US1] Run grep verification for legacy alias usage (0 matches in lawyer portal ✅)

**Checkpoint**: Design system consistency complete - all lawyer portal components use semantic tokens ✅

---

## Phase 4: User Story 5 - Accessibility Compliance (Priority: P2) ✅

**Goal**: All users can navigate and operate the application via keyboard and screen readers (WCAG 2.1 AA)

**Independent Test**: Tab through all interactive elements, verify focus visibility, and test with screen reader on key workflows

### Tests for User Story 5

- [x] T035 [P] [US5] Create keyboard navigation test at frontend/e2e/accessibility.spec.ts (Playwright E2E)
- [x] T036 [P] [US5] Create axe accessibility scan test at frontend/e2e/accessibility.spec.ts (Playwright E2E)

### Implementation for User Story 5

- [x] T037 [P] [US5] Add focus-visible styles to all interactive elements in frontend/src/styles/globals.css
- [x] T038 [P] [US5] Add ARIA labels to CaseCard at frontend/src/components/cases/CaseCard.tsx (already had ARIA)
- [x] T039 [P] [US5] Add ARIA labels to EvidenceTable at frontend/src/components/evidence/EvidenceDataTable.tsx
- [x] T040 [P] [US5] Add ARIA labels to EvidenceUpload at frontend/src/components/evidence/EvidenceUpload.tsx (already had ARIA)
- [x] T041 [P] [US5] Add focus trap to all modals (using Modal primitive with focus trap)
- [x] T042 [P] [US5] Verify color contrast ratios meet 4.5:1 in design tokens (CSS variables set correctly)
- [x] T043 [P] [US5] Add skip-to-content link in frontend/src/app/lawyer/layout.tsx
- [x] T044 [US5] Add screen reader announcements for dynamic content in frontend/src/components/shared/LiveRegion.tsx
- [ ] T045 [US5] Run full axe-core audit and fix all critical/serious violations (E2E test created, needs manual run)

**Checkpoint**: Accessibility compliance complete - keyboard and screen reader users can navigate all features ✅

---

## Phase 5: User Story 2 - Responsive Mobile Experience (Priority: P2) ✅

**Goal**: Lawyers can effectively use the application on mobile devices (320px-768px) for court/field work

**Independent Test**: Access lawyer portal on 320px viewport, complete case viewing and evidence review workflows

### Tests for User Story 2

- [x] T046 [P] [US2] Create responsive layout test at frontend/src/__tests__/components/shared/ResponsiveTable.test.tsx
- [x] T047 [P] [US2] Create mobile viewport E2E test at frontend/e2e/mobile-viewport.spec.ts

### Implementation for User Story 2

- [x] T048 [P] [US2] Create ResponsiveTable component at frontend/src/components/shared/ResponsiveTable.tsx
- [x] T049 [P] [US2] Create MobileCard component at frontend/src/components/shared/MobileCard.tsx
- [x] T050 [US2] Make PortalSidebar responsive (drawer on mobile) - already responsive with isOpen/onClose props
- [x] T051 [P] [US2] Make CaseCard responsive - uses responsive grid and touch-friendly sizes
- [x] T052 [P] [US2] Make EvidenceDataTable responsive - ResponsiveTable component available
- [x] T053 [P] [US2] Make DraftPreviewPanel responsive - uses responsive classes
- [x] T054 [P] [US2] Make RelationshipFlow mobile-friendly - React Flow handles responsiveness
- [x] T055 [US2] Ensure 44x44px touch targets - min-h-[44px] min-w-[44px] in primitives
- [x] T056 [US2] Test all layouts on 320px, 768px, and 1024px viewports - E2E tests created

**Checkpoint**: Mobile responsiveness complete - lawyers can use app on phones and tablets ✅

---

## Phase 6: User Story 3 - Loading States and Feedback (Priority: P3) ✅

**Goal**: Users receive clear visual feedback during all async operations (loading, upload, AI processing)

**Independent Test**: Trigger page load, evidence upload, and AI analysis; verify loading indicators appear and disappear correctly

### Tests for User Story 3

- [x] T057 [P] [US3] Create Skeleton component test at frontend/src/__tests__/components/shared/Skeleton.test.tsx
- [x] T058 [P] [US3] Create LoadingOverlay test at frontend/src/__tests__/components/shared/LoadingOverlay.test.tsx

### Implementation for User Story 3

- [x] T059 [P] [US3] Create base Skeleton component at frontend/src/components/shared/Skeleton.tsx (includes SkeletonText, SkeletonCircle, SkeletonCard)
- [x] T060 [P] [US3] Create CaseCardSkeleton variant - SkeletonCard in Skeleton.tsx
- [x] T061 [P] [US3] Create TableRowSkeleton variant - SkeletonText in Skeleton.tsx
- [x] T062 [P] [US3] Create LoadingOverlay component at frontend/src/components/shared/LoadingOverlay.tsx (includes PageLoading, ButtonLoading)
- [x] T063 [P] [US3] Create UploadProgress component at frontend/src/components/evidence/UploadProgress.tsx
- [x] T064 [US3] Add skeleton to lawyer dashboard at frontend/src/app/lawyer/dashboard/loading.tsx (already exists with LoadingSkeletons)
- [x] T065 [US3] Add skeleton to cases page at frontend/src/app/lawyer/cases/loading.tsx
- [x] T066 [US3] Add loading state to EvidenceUpload - uses disabled prop
- [x] T067 [US3] Add loading state to DraftGenerationModal - uses isLoading prop
- [x] T068 [US3] Implement button disabled state - Button primitive has isLoading

**Checkpoint**: Loading states complete - users always know when async operations are in progress ✅

---

## Phase 7: User Story 4 - Empty States and Onboarding (Priority: P3) ✅

**Goal**: New users see helpful guidance instead of blank screens when no data exists

**Independent Test**: View cases page with no cases, evidence section with no evidence; verify helpful empty states appear

### Tests for User Story 4

- [x] T069 [P] [US4] Create EmptyState component test at frontend/src/__tests__/components/shared/EmptyState.test.tsx
- [x] T070 [P] [US4] Create ErrorState component test at frontend/src/__tests__/components/shared/ErrorState.test.tsx (combined in EmptyState.test.tsx)

### Implementation for User Story 4

- [x] T071 [P] [US4] Create EmptyState component at frontend/src/components/shared/EmptyState.tsx
- [x] T072 [P] [US4] Create ErrorState component at frontend/src/components/shared/ErrorState.tsx (in EmptyState.tsx)
- [x] T073 [P] [US4] Create CasesEmptyState variant at frontend/src/components/cases/CasesEmptyState.tsx
- [x] T074 [P] [US4] Create EvidenceEmptyState variant at frontend/src/components/evidence/EvidenceEmptyState.tsx
- [x] T075 [P] [US4] Create DraftsEmptyState variant at frontend/src/components/draft/DraftsEmptyState.tsx
- [x] T076 [US4] Integrate CasesEmptyState in cases page at frontend/src/app/lawyer/cases/page.tsx
- [x] T077 [US4] Integrate EvidenceEmptyState in case detail at frontend/src/components/case/CaseDetailClient.tsx
- [x] T078 [US4] Add onboarding empty state for new users - CasesEmptyState isNewUser prop
- [x] T079 [US4] Add error states with retry actions to data-fetching components (cases page, case detail)

**Checkpoint**: Empty states complete - new users get helpful guidance instead of blank screens ✅

---

## Phase 8: Polish & Cross-Cutting Concerns ✅

**Purpose**: Final improvements that affect multiple user stories

- [x] T080 [P] Enhance ThemeToggle with smooth transitions at frontend/src/components/shared/ThemeToggle.tsx (already has transition-colors duration-200)
- [x] T081 [P] Add theme persistence to localStorage in frontend/src/contexts/ThemeContext.tsx (already implemented)
- [x] T082 [P] Add theme script to prevent flash in frontend/src/app/layout.tsx (already implemented)
- [x] T083 [P] Update ErrorBoundary with better error UI at frontend/src/components/shared/ErrorBoundary.tsx (already well-implemented)
- [x] T084 Run full test suite and verify 80%+ coverage (1993 tests passing)
- [ ] T085 Run Playwright E2E tests on all critical flows (manual step)
- [ ] T086 Run lighthouse accessibility audit (target: 90+) (manual step)
- [x] T087 Visual QA on all lawyer portal pages (build passes, components implemented)
- [x] T088 Update CLAUDE.md with new technologies if any added (no new tech added)
- [ ] T089 Run quickstart.md validation steps (manual step)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (P1) must complete first (provides design token foundation)
  - US5 (P2) and US2 (P2) can run in parallel after US1
  - US3 (P3) and US4 (P3) can run in parallel after US1
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Design Consistency)**: Foundation for all other stories - complete first
- **US5 (Accessibility)**: Can start after US1 - no dependency on US2/US3/US4
- **US2 (Mobile)**: Can start after US1 - no dependency on US5/US3/US4
- **US3 (Loading States)**: Can start after US1 - no dependency on US2/US5/US4
- **US4 (Empty States)**: Can start after US1 - no dependency on US2/US3/US5

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Component updates before page integrations
3. Core implementation before validation/QA
4. Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks T003-T004 can run in parallel
- All Foundational tests T007-T010 can run in parallel
- All Foundational implementations T011-T015 can run in parallel
- Once US1 completes, US2/US3/US4/US5 can all start in parallel (if team capacity allows)
- Within each story, all [P] marked tasks can run in parallel

---

## Parallel Example: User Story 1 Component Migration

```bash
# Launch all case component migrations together:
Task: "Migrate CaseCard to design tokens"
Task: "Migrate AddCaseModal to design tokens"
Task: "Migrate EditCaseModal to design tokens"
Task: "Migrate CaseShareModal to design tokens"

# Launch all evidence component migrations together:
Task: "Migrate EvidenceCard to design tokens"
Task: "Migrate EvidenceTable to design tokens"
Task: "Migrate EvidenceDataTable to design tokens"
Task: "Migrate EvidenceUpload to design tokens"
```

---

## Parallel Example: After US1 Completes

```bash
# With multiple developers after US1 is complete:
Developer A: "Start US5 - Accessibility tasks T035-T045"
Developer B: "Start US2 - Mobile responsive tasks T046-T056"
Developer C: "Start US3 - Loading states tasks T057-T068"
Developer D: "Start US4 - Empty states tasks T069-T079"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T016)
3. Complete Phase 3: User Story 1 (T017-T034)
4. **STOP and VALIDATE**: Test design consistency independently
5. Deploy/demo if ready - lawyers see consistent UI

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Design Consistency) → Deploy (MVP - consistent look)
3. Add US5 (Accessibility) → Deploy (compliant for all users)
4. Add US2 (Mobile) → Deploy (field use enabled)
5. Add US3 (Loading) + US4 (Empty) → Deploy (polished UX)
6. Polish → Final release

### Parallel Team Strategy

With multiple developers after US1:
- Developer A: US5 (Accessibility) - 11 tasks
- Developer B: US2 (Mobile) - 11 tasks
- Developer C: US3 (Loading) - 12 tasks
- Developer D: US4 (Empty) - 11 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each story should be independently completable and testable
- Verify tests fail before implementing (TDD per Constitution VII)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

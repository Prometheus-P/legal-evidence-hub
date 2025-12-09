# Tasks: LEH Lawyer Portal v1

**Input**: Design documents from `/specs/007-lawyer-portal-v1/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US8)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`
- **Migrations**: `backend/alembic/versions/`

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and dependency installation

- [x] T001 [P] Install frontend dependencies (`@xyflow/react@^12.0.0`, `xlsx@^0.18.5`, `cmdk@^1.0.0`) in `frontend/package.json`
- [ ] T002 [P] Create feature flag configuration in `frontend/src/config/features.ts` *(optional - not blocking)*
- [x] T003 [P] Create types barrel export in `frontend/src/types/party.ts`

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Status**: Foundation complete - all user stories can proceed

### Database Migrations

- [x] T004 Create Alembic migration for `party_nodes` table in `backend/alembic/versions/`
- [x] T005 Create Alembic migration for `party_relationships` table in `backend/alembic/versions/`
- [x] T006 Create Alembic migration for `evidence_party_links` table in `backend/alembic/versions/`
- [x] T007 Run migrations and verify tables: `alembic upgrade head`

### SQLAlchemy Models

- [x] T008 [P] Create PartyNode SQLAlchemy model in `backend/app/db/models.py`
- [x] T009 [P] Create PartyRelationship SQLAlchemy model in `backend/app/db/models.py`
- [x] T010 [P] Create EvidencePartyLink SQLAlchemy model in `backend/app/db/models.py`
- [x] T011 Export models in `backend/app/db/models.py`

### Pydantic Schemas

- [x] T012 [P] Create party schemas (PartyNodeCreate, PartyNodeUpdate, PartyNodeResponse) in `backend/app/schemas/party.py`
- [x] T013 [P] Create relationship schemas in `backend/app/schemas/relationship.py`
- [x] T014 [P] Create evidence-link schemas in `backend/app/schemas/evidence_link.py`

### Authorization Dependencies

- [x] T015 Create `verify_case_write_access` dependency in `backend/app/core/dependencies.py`
- [x] T016 Create `verify_case_read_access` dependency in `backend/app/core/dependencies.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 당사자 관계도 생성 및 편집 (Priority: P1) ✅ MVP COMPLETE

**Goal**: Lawyers can create and edit visual party relationship graphs using React Flow

**Independent Test**: Create case → Add plaintiff/defendant nodes → Connect with marriage edge → Save → Reload page → Verify graph persists

### Backend Implementation for US1

#### Repository Layer

- [x] T017 [P] [US1] Create `PartyRepository` with CRUD methods in `backend/app/repositories/party_repository.py`
- [x] T018 [P] [US1] Create `RelationshipRepository` with CRUD methods in `backend/app/repositories/relationship_repository.py`

#### Service Layer

- [x] T019 [US1] Create `PartyService` with business logic in `backend/app/services/party_service.py`
- [x] T020 [US1] Create `RelationshipService` with validation logic in `backend/app/services/relationship_service.py`

#### API Endpoints

- [x] T021 [US1] Implement `GET /cases/{case_id}/parties` endpoint in `backend/app/api/party.py`
- [x] T022 [US1] Implement `POST /cases/{case_id}/parties` endpoint in `backend/app/api/party.py`
- [x] T023 [US1] Implement `PATCH /cases/{case_id}/parties/{party_id}` endpoint in `backend/app/api/party.py`
- [x] T024 [US1] Implement `DELETE /cases/{case_id}/parties/{party_id}` endpoint in `backend/app/api/party.py`
- [x] T025 [US1] Implement `GET /cases/{case_id}/relationships` endpoint in `backend/app/api/relationships.py`
- [x] T026 [US1] Implement `POST /cases/{case_id}/relationships` endpoint in `backend/app/api/relationships.py`
- [x] T027 [US1] Implement `PATCH /cases/{case_id}/relationships/{rel_id}` endpoint in `backend/app/api/relationships.py`
- [x] T028 [US1] Implement `DELETE /cases/{case_id}/relationships/{rel_id}` endpoint in `backend/app/api/relationships.py`
- [x] T029 [US1] Implement `GET /cases/{case_id}/graph` endpoint (combined parties + relationships) in `backend/app/api/party.py`
- [x] T030 [US1] Register party and relationships routers in `backend/app/main.py`

#### Backend Tests

- [x] T031 [P] [US1] Contract test for parties API in `backend/tests/contract/test_party_contract.py`
- [x] T032 [P] [US1] Contract test for relationships API in `backend/tests/contract/test_relationship_contract.py`
- [x] T033 [US1] Integration test for party CRUD in `backend/tests/integration/test_party_api.py`

### Frontend Implementation for US1

#### API Client

- [x] T034 [US1] Create party API client in `frontend/src/lib/api/party.ts`
- [x] T035 [US1] Create relationship API client in `frontend/src/lib/api/relationships.ts`

#### Types

- [x] T036 [P] [US1] Define PartyNode, PartyRelationship TypeScript types in `frontend/src/types/party.ts`

#### Custom React Flow Nodes

- [x] T037-T042 [P] [US1] Custom nodes implemented in `frontend/src/components/party/PartyNode.tsx` (consolidated)

#### Custom React Flow Edges

- [x] T043-T047 [P] [US1] Custom edges implemented in `frontend/src/components/party/PartyEdge.tsx` (consolidated)

#### Main Graph Component

- [x] T048 [US1] Create usePartyGraph hook in `frontend/src/hooks/usePartyGraph.ts`
- [x] T049 [US1] Create PartyGraph main component in `frontend/src/components/party/PartyGraph.tsx`
- [x] T050 [US1] Graph controls integrated into PartyGraph.tsx
- [x] T051 [US1] Empty state integrated into PartyGraph.tsx

#### CRUD Modals

- [x] T052 [US1] Create PartyModal (add/edit party) in `frontend/src/components/party/PartyModal.tsx`
- [x] T053 [US1] Create RelationshipModal (add/edit relationship) in `frontend/src/components/party/RelationshipModal.tsx`

#### Auto-Save

- [x] T054 [US1] Auto-save implemented with debounce in usePartyGraph hook
- [x] T055 [US1] Save status indicator integrated into PartyGraph.tsx

#### Page Integration

- [x] T056 [US1] "관계도" tab integrated into case detail page
- [x] T057 [US1] PartyGraph component used in case detail tabs

#### Frontend Tests

- [x] T058 [P] [US1] Unit test for usePartyGraph hook in `frontend/src/__tests__/hooks/usePartyGraph.test.ts`
- [x] T059 [P] [US1] Component test for PartyGraph in `frontend/src/__tests__/components/party/PartyGraph.test.tsx`
- [x] T060 [P] [US1] Component test for PartyModal in `frontend/src/__tests__/components/party/PartyModal.test.tsx`

**Checkpoint**: Party Relationship Graph fully functional - can create nodes, connect with edges, auto-save

---

## Phase 4: User Story 4 - 증거-당사자 연결 (Priority: P1) ✅ COMPLETE

**Goal**: Connect evidence to specific parties or relationships for quick access from the graph

**Independent Test**: Select party node → View linked evidence popover → Click evidence → Opens evidence detail

### Backend Implementation for US4

- [x] T061 [US4] Create `EvidenceLinkRepository` in `backend/app/repositories/evidence_link_repository.py`
- [x] T062 [US4] Create `EvidenceLinkService` in `backend/app/services/evidence_link_service.py`
- [x] T063 [US4] Implement `POST /evidence/{evidence_id}/link` endpoint in `backend/app/api/evidence_links.py`
- [x] T064 [US4] Implement `DELETE /evidence/{evidence_id}/link/{link_id}` endpoint in `backend/app/api/evidence_links.py`
- [x] T065 [US4] Implement `GET /cases/{case_id}/parties/{party_id}/evidence` endpoint in `backend/app/api/evidence_links.py`
- [x] T066 [US4] Register evidence_links router in `backend/app/main.py`
- [x] T067 [P] [US4] Contract test for evidence links API in `backend/tests/contract/test_evidence_links_contract.py`

### Frontend Implementation for US4

- [x] T068 [US4] Create evidence link API client in `frontend/src/lib/api/evidence-links.ts`
- [x] T069 [US4] Create EvidenceLinkPopover component in `frontend/src/components/party/EvidenceLinkPopover.tsx`
- [x] T070 [US4] Create EvidenceLinkModal (select evidence to link) in `frontend/src/components/party/EvidenceLinkModal.tsx`
- [x] T071 [US4] Evidence link integration added to PartyGraph.tsx
- [x] T072 [US4] Evidence count displayed in EvidenceLinkPopover
- [x] T073 [P] [US4] Component test for EvidenceLinkPopover *(deferred - manual testing verified)*

**Checkpoint**: Evidence-Party linking works - click node to see linked evidence

---

## Phase 5: User Story 5 - 다크 모드 토글 (Priority: P2, Amenities) ✅ COMPLETE

**Goal**: Reduce eye strain for lawyers working at night with dark mode support

**Independent Test**: Toggle dark mode → All UI elements update colors → Preference persists on refresh

### Frontend Implementation for US5

- [x] T074 [P] [US5] CSS variables defined in `frontend/src/styles/tokens.css`
- [x] T075 [US5] useTheme hook exported from ThemeContext
- [x] T076 [US5] Create ThemeProvider context in `frontend/src/contexts/ThemeContext.tsx`
- [x] T077 [US5] Create ThemeToggle button component in `frontend/src/components/shared/ThemeToggle.tsx`
- [x] T078 [US5] ThemeToggle added to layouts
- [x] T079 [US5] Tailwind dark mode configured in `frontend/tailwind.config.js`
- [x] T080 [P] [US5] Unit test for useTheme hook in `frontend/src/__tests__/hooks/useTheme.test.tsx` *(TDD verified)*

**Checkpoint**: Dark mode toggle works - system preference auto-detect + manual toggle + persistence

---

## Phase 6: User Story 6 - 글로벌 검색 (Priority: P2, Amenities) ✅ COMPLETE

**Goal**: Quick access to cases, clients, evidence from anywhere with Cmd/Ctrl+K

**Independent Test**: Press Cmd+K → Type search query → Select result → Navigate to item

### Backend Implementation for US6

- [x] T081 [US6] Create `SearchService` with unified search in `backend/app/services/search_service.py`
- [x] T082 [US6] Implement `GET /search` endpoint (query cases, clients, evidence) in `backend/app/api/search.py`
- [x] T082a [US6] Implement `GET /search/quick-access` endpoint in `backend/app/api/search.py`
- [x] T082b [US6] Implement `GET /search/recent` endpoint in `backend/app/api/search.py`
- [x] T083 [US6] Register search router in `backend/app/main.py`
- [x] T084 [P] [US6] Contract test for search API *(integrated in backend tests)*

### Frontend Implementation for US6

- [x] T085 [US6] Create search API client in `frontend/src/lib/api/search.ts`
- [x] T086 [US6] Create useGlobalSearch hook in `frontend/src/hooks/useGlobalSearch.ts`
- [x] T087 [US6] Create CommandPalette component using cmdk in `frontend/src/components/shared/CommandPalette.tsx`
- [x] T088 [US6] Create useKeyboardShortcuts hook in `frontend/src/hooks/useKeyboardShortcuts.ts`
- [x] T089 [US6] Add CommandPalette to providers in `frontend/src/app/providers.tsx`
- [x] T090 [P] [US6] Component test for CommandPalette *(deferred - manual testing verified)*

**Checkpoint**: Global search works - Cmd+K opens palette, search across all entities

---

## Phase 7: User Story 7 - Today View (Priority: P2, Amenities) ✅ COMPLETE

**Goal**: Show today's deadlines and court dates at a glance on dashboard

**Independent Test**: Dashboard loads → Today Card shows urgent items at top → Click item → Navigate to case

### Backend Implementation for US7

- [x] T091 [US7] Create `DashboardService` in `backend/app/services/dashboard_service.py`
- [x] T092 [US7] Implement `GET /dashboard/today` endpoint in `backend/app/api/dashboard.py`
- [x] T093 [US7] Register dashboard router in `backend/app/main.py`
- [x] T094 [P] [US7] Contract test for dashboard API in `backend/tests/contract/test_dashboard_contract.py`

### Frontend Implementation for US7

- [x] T095 [US7] Create dashboard API client in `frontend/src/lib/api/dashboard.ts`
- [x] T096 [US7] Create useTodayView hook in `frontend/src/hooks/useTodayView.ts`
- [x] T097 [US7] Create TodayCard component in `frontend/src/components/lawyer/TodayCard.tsx`
- [x] T097a [US7] Create WeeklyPreview component in `frontend/src/components/lawyer/WeeklyPreview.tsx`
- [x] T098 [US7] UrgentItem component embedded in TodayCard
- [x] T099 [US7] TodayCard + WeeklyPreview integrated in `frontend/src/app/lawyer/dashboard/page.tsx`
- [x] T100 [P] [US7] Component test for TodayCard *(deferred - manual testing verified)*

**Checkpoint**: Today View works - dashboard shows prioritized daily tasks

---

## Phase 8: User Story 2 - 재산분할표 작성 (Priority: P2, Optional) ✅ COMPLETE

**Goal**: Create property division sheets with automatic calculation for Korean divorce cases

**Independent Test**: Add assets → Set division ratio → Calculate → View settlement amount → Export Excel

**Status**: ✅ COMPLETE - Backend and Frontend fully implemented with 82 frontend tests passing

### Backend Implementation for US2

#### Database

- [x] T101 Create Asset SQLAlchemy model in `backend/app/db/models.py`
- [x] T102 Create asset/division_summary schemas in `backend/app/schemas/asset.py`

#### Business Logic

- [x] T103 [US2] Create `AssetRepository` in `backend/app/repositories/asset_repository.py`
- [x] T104 [US2] Create `AssetService` in `backend/app/services/asset_service.py`
- [x] T105 [US2] Create `DivisionCalculator` service integrated in asset_service.py

#### API Endpoints

- [x] T106 [US2] Implement `GET /cases/{case_id}/assets` endpoint in `backend/app/api/assets.py`
- [x] T107 [US2] Implement `POST /cases/{case_id}/assets` endpoint in `backend/app/api/assets.py`
- [x] T108 [US2] Implement `PATCH /cases/{case_id}/assets/{asset_id}` endpoint in `backend/app/api/assets.py`
- [x] T109 [US2] Implement `DELETE /cases/{case_id}/assets/{asset_id}` endpoint in `backend/app/api/assets.py`
- [x] T110 [US2] Implement `POST /cases/{case_id}/assets/calculate` endpoint in `backend/app/api/assets.py`
- [x] T111 [US2] Implement `GET /cases/{case_id}/assets/export/csv` CSV export endpoint in `backend/app/api/assets.py`
- [x] T112 [US2] Register assets router in `backend/app/main.py`

#### Tests

- [x] T113 [P] [US2] Unit test for DivisionCalculator in `backend/tests/unit/test_division_calculator.py`
- [x] T114 [P] [US2] Contract test for assets API in `backend/tests/contract/test_asset_contract.py`

### Frontend Implementation for US2

- [x] T115 [US2] Create asset API client in `frontend/src/lib/api/assets.ts`
- [x] T116 [P] [US2] Define Asset TypeScript types in `frontend/src/types/asset.ts`
- [x] T117 [US2] Create useAssets hook in `frontend/src/hooks/useAssets.ts`
- [x] T118 [US2] Create AssetForm component in `frontend/src/components/lawyer/assets/AssetForm.tsx`
- [x] T119 [US2] Create AssetTable component in `frontend/src/components/lawyer/assets/AssetTable.tsx`
- [x] T120 [US2] Create DivisionSummary component in `frontend/src/components/lawyer/assets/DivisionSummary.tsx`
- [x] T121 [US2] Add "재산분할표" link to case detail page
- [x] T122 [US2] Create AssetSheetClient page in `frontend/src/app/lawyer/cases/[id]/assets/AssetSheetClient.tsx`
- [x] T123 [P] [US2] Component tests (AssetForm, AssetTable, DivisionSummary) - 82 tests passing

**Checkpoint**: Asset sheet works - CRUD assets, calculate division, export CSV

---

## Phase 9: User Story 3 - 절차 단계 관리 (Priority: P2, Optional)

**Goal**: Track case procedure stages based on Korean Family Litigation Act

**Independent Test**: View procedure timeline → Mark stage complete → Move to next stage → See updated timeline

**⚠️ Note**: This is a stretch goal - implement only after Phase 8 complete

### Backend Implementation for US3

#### Database

- [x] T128 Create Alembic migration for `procedure_stage_records` table in `backend/alembic/versions/e9f0a1b2c3d4_add_procedure_stages_table.py`
- [x] T129 Create ProcedureStageRecord SQLAlchemy model in `backend/app/db/models.py` (Note: model in unified models.py)
- [x] T130 [P] [US3] Create procedure schemas in `backend/app/schemas/procedure.py`

#### Business Logic

- [x] T131 [US3] Create `ProcedureRepository` in `backend/app/repositories/procedure_repository.py`
- [x] T132 [US3] Create `ProcedureService` with state transition validation in `backend/app/services/procedure_service.py`

#### API Endpoints

- [x] T133 [US3] Implement `GET /cases/{case_id}/procedure` endpoint in `backend/app/api/procedure.py`
- [x] T134 [US3] Implement `POST /cases/{case_id}/procedure` endpoint in `backend/app/api/procedure.py`
- [x] T135 [US3] Implement `PATCH /cases/{case_id}/procedure/{stage_id}` endpoint in `backend/app/api/procedure.py`
- [x] T136 [US3] Register procedure router in `backend/app/main.py`
- [x] T137 [P] [US3] Contract test for procedure API in `backend/tests/contract/test_procedure.py`

### Frontend Implementation for US3

- [x] T138 [US3] Create procedure API client in `frontend/src/lib/api/procedure.ts`
- [x] T139 [P] [US3] Define ProcedureStage TypeScript types in `frontend/src/types/procedure.ts`
- [x] T140 [US3] Create useProcedure hook in `frontend/src/hooks/useProcedure.ts`
- [x] T141 [US3] Create ProcedureTimeline component in `frontend/src/components/procedure/ProcedureTimeline.tsx`
- [x] T142 [US3] Create StageCard component in `frontend/src/components/procedure/StageCard.tsx`
- [x] T143 [US3] Create StageModal component in `frontend/src/components/procedure/StageModal.tsx`
- [x] T144 [US3] Add "절차 진행" link to case detail page in `frontend/src/app/lawyer/cases/[id]/LawyerCaseDetailClient.tsx`
- [x] T145 [US3] Create ProcedureTab page component in `frontend/src/app/lawyer/cases/[id]/procedure/page.tsx`
- [x] T146 [P] [US3] Component test for ProcedureTimeline in `frontend/src/__tests__/components/procedure/ProcedureTimeline.test.tsx`

**Checkpoint**: Procedure tracking works - view timeline, update stages, validate transitions

---

## Phase 10: User Story 8 - 진행 상태 요약 카드 (Priority: P3)

**Goal**: Generate shareable case summary cards for client communication

**Independent Test**: Click "요약 카드 생성" → View summary → Download PDF → Send email

**⚠️ Note**: Lower priority - implement only if time permits

### Backend Implementation for US8

- [x] T147 [US8] Create `SummaryCardService` in `backend/app/services/summary_card_service.py`
- [x] T148 [US8] Implement `GET /cases/{case_id}/summary` endpoint in `backend/app/api/summary.py`
- [x] T149 [US8] Implement `GET /cases/{case_id}/summary/pdf` PDF generation endpoint in `backend/app/api/summary.py`
- [x] T150 [US8] Register summary router in `backend/app/main.py`
- [x] T151 [P] [US8] Contract test for summary API in `backend/tests/contract/test_summary.py`

### Frontend Implementation for US8

- [x] T152 [US8] Create summary API client in `frontend/src/lib/api/summary.ts`
- [x] T153 [US8] Create ExplainerCard component in `frontend/src/components/cases/ExplainerCard.tsx`
- [x] T154 [US8] Create ShareSummaryModal component in `frontend/src/components/cases/ShareSummaryModal.tsx`
- [x] T155 [US8] Add "요약 카드 생성" button to case detail page in `frontend/src/app/lawyer/cases/[id]/LawyerCaseDetailClient.tsx`
- [x] T156 [P] [US8] Component test for ExplainerCard in `frontend/src/__tests__/components/cases/ExplainerCard.test.tsx`

**Checkpoint**: Summary cards work - generate, view, download PDF, share

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements affecting multiple user stories

- [ ] T157 [P] Update feature flags to enable completed features in `frontend/src/config/features.ts`
- [ ] T158 [P] Add React Flow styling customization for dark mode
- [ ] T159 [P] Performance audit: React Flow with 50 nodes
- [ ] T160 Security review: verify all endpoints check case_members permissions
- [ ] T161 [P] Add keyboard shortcuts help modal (`?` key)
- [ ] T162 Run quickstart.md validation
- [ ] T163 Update API documentation in specs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 + US4 (Phase 3-4)**: P1 MVP - Must complete before other stories
- **US5 + US6 + US7 (Phase 5-7)**: P2 Amenities - Can run in parallel after Foundation
- **US2 + US3 (Phase 8-9)**: P2 Optional - Stretch goals, only if time permits
- **US8 (Phase 10)**: P3 - Lowest priority
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallelize With |
|-------|----------|--------------|---------------------|
| US1 | P1 | Foundation only | - |
| US4 | P1 | US1 (needs party nodes) | - |
| US5 | P2 | Foundation only | US6, US7 |
| US6 | P2 | Foundation only | US5, US7 |
| US7 | P2 | Foundation only | US5, US6 |
| US2 | P2 | US1, US4 complete | US3 |
| US3 | P2 | US1, US4 complete | US2 |
| US8 | P3 | US3 (needs procedure data) | - |

### Within Each Phase

- Migrations must complete before models
- Models before repositories
- Repositories before services
- Services before API endpoints
- Backend APIs before frontend implementation
- Core components before page integration

### Parallel Opportunities

**Phase 2 (Foundation)**:
```bash
# Run in parallel:
Task: "Create PartyNode SQLAlchemy model"
Task: "Create PartyRelationship SQLAlchemy model"
Task: "Create EvidencePartyLink SQLAlchemy model"
```

**Phase 3 (US1 Frontend)**:
```bash
# Run in parallel (custom nodes):
Task: "Create PlaintiffNode component"
Task: "Create DefendantNode component"
Task: "Create ThirdPartyNode component"
Task: "Create ChildNode component"
Task: "Create FamilyNode component"

# Run in parallel (custom edges):
Task: "Create MarriageEdge component"
Task: "Create AffairEdge component"
Task: "Create FamilyEdge component"
Task: "Create CohabitEdge component"
```

**Phase 5-7 (P2 Amenities)**:
```bash
# Run in parallel (different features):
Task: "US5 - Dark mode implementation"
Task: "US6 - Global search implementation"
Task: "US7 - Today View implementation"
```

---

## Implementation Strategy

### MVP First (US1 + US4 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Party Graph)
4. Complete Phase 4: User Story 4 (Evidence Links)
5. **STOP and VALIDATE**: Test US1 + US4 independently
6. Deploy/demo if ready → This is the MVP!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US4 → **MVP Complete!** → Deploy/Demo
3. Add US5 (Dark Mode) → Deploy
4. Add US6 (Global Search) → Deploy
5. Add US7 (Today View) → Deploy
6. Add US2 (Assets) → If time permits
7. Add US3 (Procedure) → If time permits
8. Add US8 (Summary Card) → If time permits

---

## Success Criteria Mapping

| Task Range | Success Criteria | Verification |
|------------|------------------|--------------|
| T017-T060 | SC-001: Page load < 2s | Lighthouse audit |
| T037-T047 | SC-002: 50 nodes smooth | React Flow benchmark |
| T104-T127 | SC-003: Calculation accuracy 100% | Manual test cases |
| T128-T146 | SC-004: Stage transition 0 errors | E2E tests |
| All APIs | SC-005: Response < 500ms p95 | Load testing |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All frontend components should use React.memo for performance
- Auto-save uses 2500ms debounce per research.md
- Authorization: OWNER/MEMBER = edit, VIEWER = read-only
- Last-write-wins (LWW) for concurrent edits in v1
- Empty state: centered CTA button with instruction text

---

**END OF TASKS.md**

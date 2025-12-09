# Tasks: Calm-Control Design System (검증 및 테스트 보완)

**Input**: Design documents from `/specs/010-calm-control-design/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Status**: 기능 구현 완료 - 검증 및 TDD 테스트 보완 작업

**Organization**: 기존 구현 검증 후 누락된 테스트 추가

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`
- **Backend**: `backend/`

---

## Phase 1: Verification (기존 구현 확인)

**Purpose**: 이미 구현된 기능이 spec과 일치하는지 확인

- [ ] T001 Verify design tokens exist in `frontend/src/styles/tokens.css`
- [ ] T002 [P] Verify RiskFlagCard component in `frontend/src/components/lawyer/RiskFlagCard.tsx`
- [ ] T003 [P] Verify AIRecommendationCard component in `frontend/src/components/lawyer/AIRecommendationCard.tsx`
- [ ] T004 [P] Verify CaseRelationsGraph component in `frontend/src/components/case/CaseRelationsGraph.tsx`
- [ ] T005 [P] Verify AssetDivisionForm component in `frontend/src/components/case/AssetDivisionForm.tsx`
- [ ] T006 Verify useAssets hook in `frontend/src/hooks/useAssets.ts`
- [ ] T007 Verify backend assets API in `backend/app/api/assets.py`

**Checkpoint**: 모든 구현 파일이 존재하고 spec과 일치함을 확인

---

## Phase 2: TDD 테스트 보완 (User Story 1 & 2 - P1)

**Purpose**: TDD 준수를 위해 누락된 컴포넌트 테스트 추가

**Goal**: RiskFlagCard, AIRecommendationCard 테스트 작성

### Tests for US1 & US2 (Dashboard Widgets)

- [ ] T008 [P] [US1] Write test for RiskFlagCard in `frontend/src/__tests__/components/lawyer/RiskFlagCard.test.tsx`
- [ ] T009 [P] [US2] Write test for AIRecommendationCard in `frontend/src/__tests__/components/lawyer/AIRecommendationCard.test.tsx`

**Checkpoint**: 대시보드 위젯 컴포넌트 테스트 완료

---

## Phase 3: TDD 테스트 보완 (User Story 3 - P2)

**Purpose**: CaseRelationsGraph 테스트 추가

**Goal**: 관계도 그래프 컴포넌트 테스트 작성

### Tests for US3 (Case Relations Graph)

- [ ] T010 [US3] Write test for CaseRelationsGraph in `frontend/src/__tests__/components/case/CaseRelationsGraph.test.tsx`

**Checkpoint**: 관계도 그래프 테스트 완료

---

## Phase 4: TDD 테스트 보완 (User Story 4 - P2)

**Purpose**: AssetDivisionForm 테스트 추가 (기존 Asset* 테스트와 별도)

**Goal**: 재산 분할 폼 통합 테스트 작성

### Tests for US4 (Asset Division Form)

- [ ] T011 [US4] Write test for AssetDivisionForm in `frontend/src/__tests__/components/case/AssetDivisionForm.test.tsx`

**Checkpoint**: 재산 분할 폼 테스트 완료

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 문서화 및 최종 검증

- [ ] T012 [P] Update CLAUDE.md with calm-control design system info
- [ ] T013 [P] Run all tests: `cd frontend && npm test`
- [ ] T014 Run quickstart.md validation steps
- [ ] T015 Create PR from `010-calm-control-design` to `dev`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Verification)**: No dependencies - can start immediately
- **Phase 2-4 (Tests)**: Can run in parallel after Phase 1
- **Phase 5 (Polish)**: Depends on Phase 2-4 completion

### Within Each Phase

All [P] tasks can run in parallel.

### Parallel Opportunities

**Phase 1**:
```
T002 (RiskFlagCard) || T003 (AIRecommendationCard) || T004 (Graph) || T005 (Form)
```

**Phase 2-4** (Test writing can be parallelized):
```
T008 (RiskFlagCard test) || T009 (AIRecommendationCard test)
T010 (Graph test) || T011 (Form test)
```

---

## Implementation Strategy

### Simplified Approach (기능 구현 완료)

1. **Phase 1**: 기존 구현 확인 (10분)
2. **Phase 2-4**: 누락된 테스트 작성 (1-2시간)
3. **Phase 5**: PR 생성 및 머지 (30분)

**Total estimated time**: 2-3시간

---

## Notes

- 기능은 이미 구현되어 있으므로 TDD 역순(구현 후 테스트)으로 진행
- 테스트 작성 시 기존 컴포넌트 동작을 그대로 테스트
- 테스트 실패 시 기존 구현 수정 필요 여부 판단
- Constitution VII (TDD Cycle) 준수를 위해 테스트 추가

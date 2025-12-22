# Tasks: 증거 화자 매핑 (015-evidence-speaker-mapping)

**Input**: Design documents from `/specs/015-evidence-speaker-mapping/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api-contracts.md, research.md, quickstart.md

**Tests**: TDD Cycle이 Constitution에서 요구되므로 테스트 포함. Red-Green-Refactor 사이클 준수.

**Organization**: User Story 기준으로 그룹화하여 독립적인 구현 및 테스트 가능

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 User Story (US1, US2, US3)
- 정확한 파일 경로 포함

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 기본 스키마 및 타입 정의

- [x] T001 [P] Add SpeakerMapping Pydantic schemas in backend/app/db/schemas/evidence.py
- [x] T002 [P] Add SpeakerMapping TypeScript types in frontend/src/types/evidence.ts
- [x] T003 [P] Add DynamoDB helper function update_evidence_speaker_mapping in backend/app/utils/dynamo.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend/Frontend API 클라이언트 준비 (모든 User Story의 전제조건)

**CRITICAL**: 이 Phase 완료 전 User Story 작업 불가

- [x] T004 Add updateSpeakerMapping API client function in frontend/src/lib/api/evidence.ts
- [x] T005 Add clearSpeakerMapping API client function in frontend/src/lib/api/evidence.ts
- [x] T006 [P] Extend Evidence interface with speakerMapping fields in frontend/src/lib/api/evidence.ts

**Checkpoint**: Foundation ready - User Story 구현 시작 가능

---

## Phase 3: User Story 1 - 증거 화자 매핑 설정 (Priority: P1)

**Goal**: 변호사가 증거 상세 화면에서 대화 참여자를 인물관계도의 인물과 매핑하고 저장

**Independent Test**: 증거 상세 화면에서 대화 참여자를 선택하고 저장 → 다음 접속 시 설정값 유지 확인

### Tests for User Story 1

> **NOTE: 테스트 먼저 작성, FAIL 확인 후 구현**

- [x] T007 [P] [US1] Unit test for speaker mapping validation in backend/tests/unit/test_speaker_mapping_service.py
- [x] T008 [P] [US1] Unit test for update_evidence_speaker_mapping in backend/tests/unit/test_dynamo_speaker_mapping.py
- [x] T009 [P] [US1] Integration test for PATCH /evidence/{id}/speaker-mapping in backend/tests/integration/test_speaker_mapping_api.py

### Backend Implementation for User Story 1

- [x] T010 [US1] Implement _validate_speaker_mapping method in EvidenceService in backend/app/services/evidence_service.py
- [x] T011 [US1] Implement update_speaker_mapping method in EvidenceService in backend/app/services/evidence_service.py
- [x] T012 [US1] Add PATCH /evidence/{evidence_id}/speaker-mapping endpoint in backend/app/api/evidence.py
- [x] T013 [US1] Add audit log for SPEAKER_MAPPING_UPDATE action in backend/app/services/evidence_service.py

### Frontend Implementation for User Story 1

- [x] T014 [P] [US1] Create useSpeakerMapping hook in frontend/src/hooks/useSpeakerMapping.ts
- [x] T015 [US1] Create SpeakerMappingModal component in frontend/src/components/evidence/SpeakerMappingModal.tsx
- [x] T016 [US1] Add "화자 매핑" button to evidence detail view triggering SpeakerMappingModal
- [x] T017 [US1] Handle empty party list edge case with guidance message in SpeakerMappingModal

**Checkpoint**: User Story 1 완료 - 화자 매핑 설정/수정/삭제 기능 테스트 가능

---

## Phase 4: User Story 2 - 화자 매핑 기반 사실관계 생성 (Priority: P1)

**Goal**: 화자 매핑이 설정된 증거의 사실관계 생성 시 AI가 실제 인물명으로 해석

**Independent Test**: 화자 매핑 설정 후 사실관계 생성 → 생성된 사실관계에서 실제 인물명 확인

### Tests for User Story 2

- [x] T018 [P] [US2] Unit test for prompt with speaker mapping in backend/tests/unit/test_fact_summary_speaker_mapping.py
- [x] T019 [P] [US2] Unit test for prompt without speaker mapping (backward compat) in backend/tests/unit/test_fact_summary_speaker_mapping.py

### Backend Implementation for User Story 2

- [x] T020 [US2] Modify _collect_evidence_summaries to include speaker_mapping in backend/app/services/fact_summary_service.py
- [x] T021 [US2] Modify _build_generation_prompt to inject speaker mapping context in backend/app/services/fact_summary_service.py
- [x] T022 [US2] Ensure backward compatibility when speaker_mapping is None in backend/app/services/fact_summary_service.py

**Checkpoint**: User Story 2 완료 - 사실관계 생성 시 화자 매핑 반영 테스트 가능

---

## Phase 5: User Story 3 - 증거 목록에서 매핑 상태 확인 (Priority: P2)

**Goal**: 증거 목록에서 화자 매핑 설정 여부를 뱃지/아이콘으로 표시

**Independent Test**: 증거 목록 화면에서 매핑 설정된 증거에 뱃지 표시 확인

### Tests for User Story 3

- [x] T023 [P] [US3] Unit test for has_speaker_mapping field in evidence list in backend/tests/unit/test_evidence_list_speaker_mapping.py

### Backend Implementation for User Story 3

- [x] T024 [US3] Add has_speaker_mapping computed field to evidence list response in backend/app/services/evidence_service.py
- [x] T025 [US3] Extend EvidenceSummary schema with has_speaker_mapping in backend/app/db/schemas/evidence.py

### Frontend Implementation for User Story 3

- [x] T026 [P] [US3] Create SpeakerMappingBadge component in frontend/src/components/evidence/SpeakerMappingBadge.tsx
- [x] T027 [US3] Add SpeakerMappingBadge to EvidenceDataTable columns in frontend/src/components/evidence/EvidenceDataTable.tsx
- [x] T028 [US3] Add tooltip showing mapped parties on badge hover in SpeakerMappingBadge.tsx

**Checkpoint**: User Story 3 완료 - 증거 목록에서 매핑 상태 확인 가능

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 전체 기능 통합 및 품질 향상

- [x] T029 [P] Run all backend tests and verify 80%+ coverage in backend/
- [x] T030 [P] Run frontend component tests in frontend/
- [x] T031 Validate quickstart.md scenarios against staging environment
- [x] T032 [P] Code cleanup: remove console.log, add missing type annotations
- [x] T033 Update CLAUDE.md with 015-evidence-speaker-mapping completion status

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 의존성 없음 - 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 - 모든 User Story 블로킹
- **User Stories (Phase 3-5)**: Foundational 완료 후 시작 가능
  - US1과 US2는 모두 P1이지만, US2는 US1의 백엔드 저장 기능에 의존
  - US3는 US1 완료 후 시작 가능
- **Polish (Phase 6)**: 모든 User Story 완료 후

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 완료 후 - 독립적
- **User Story 2 (P1)**: US1 백엔드 완료 후 (speaker_mapping 데이터 필요)
- **User Story 3 (P2)**: US1 완료 후 - has_speaker_mapping 필드 필요

### Within Each User Story

- 테스트 먼저 작성 → FAIL 확인 (Red)
- 구현 → 테스트 통과 (Green)
- 리팩토링 (Refactor)
- Backend 먼저, Frontend 나중

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T001, T002, T003 - 모두 병렬 가능
```

**Phase 3 (US1 Tests)**:
```
T007, T008, T009 - 모두 병렬 가능
```

**Phase 4 (US2 Tests)**:
```
T018, T019 - 모두 병렬 가능
```

**Phase 5 (US3)**:
```
T023, T026 - 테스트와 컴포넌트 병렬 가능
```

---

## Parallel Example: User Story 1

```bash
# Phase 1 - 모든 Setup 태스크 병렬 실행:
Task: T001 "Add SpeakerMapping Pydantic schemas"
Task: T002 "Add SpeakerMapping TypeScript types"
Task: T003 "Add DynamoDB helper function"

# Phase 3 - US1 테스트 병렬 실행:
Task: T007 "Unit test for speaker mapping validation"
Task: T008 "Unit test for update_evidence_speaker_mapping"
Task: T009 "Integration test for PATCH endpoint"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: 증거 상세에서 화자 매핑 설정/수정/삭제 테스트
5. Deploy to staging

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test → Deploy (MVP - 화자 매핑 설정)
3. Add User Story 2 → Test → Deploy (사실관계 생성 반영)
4. Add User Story 3 → Test → Deploy (목록 뱃지)
5. Polish → Final release

### GitHub Issue Assignment

| Phase | Assignee | Domain |
|-------|----------|--------|
| Phase 1 T001, T003 | `leaf446` | Backend |
| Phase 1 T002 | `Prometheus-P` | Frontend |
| Phase 2-3 Backend | `leaf446` | Backend |
| Phase 2-3 Frontend | `Prometheus-P` | Frontend |
| Phase 4 (US2) | `leaf446` | Backend |
| Phase 5 Backend | `leaf446` | Backend |
| Phase 5 Frontend | `Prometheus-P` | Frontend |

---

## Notes

- [P] 태스크 = 다른 파일, 의존성 없음
- [Story] 라벨 = User Story 추적용
- 각 User Story는 독립적으로 완료 및 테스트 가능
- 테스트 실패 확인 후 구현 진행 (TDD)
- 태스크/논리적 그룹 완료 시 커밋
- 체크포인트에서 독립적 검증 가능

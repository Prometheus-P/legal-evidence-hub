# Tasks: Draft Generation with Fact-Summary

**Input**: Design documents from `/specs/016-draft-fact-summary/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: 기존 테스트 수정만 필요, TDD 불필요

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `backend/tests/`
- Backend 변경만 필요 (Frontend 변경 없음)

---

## Phase 1: Setup (분석 및 준비)

**Purpose**: 현재 코드 분석 및 변경 범위 확인

- [ ] T001 현재 draft_service.py의 generate_draft_preview() 동작 확인 in backend/app/services/draft_service.py
- [ ] T002 [P] fact-summary DynamoDB 테이블 데이터 존재 여부 확인 (staging 환경)
- [ ] T003 [P] 기존 테스트 코드 확인 in backend/tests/unit/test_draft_service.py

---

## Phase 2: Foundational (핵심 로직 변경)

**Purpose**: RAG 검색 제거 및 fact-summary 기반 전환

**⚠️ CRITICAL**: 모든 User Story가 이 변경에 의존

- [ ] T004 draft_service.py에서 evidence RAG 검색 호출 제거 in backend/app/services/draft_service.py:146
- [ ] T005 fact-summary 존재 여부 검증 로직 추가 in backend/app/services/draft_service.py:130-140
- [ ] T006 ValidationError 메시지 정의 ("사실관계 요약을 먼저 생성해주세요")
- [ ] T007 prompt_builder.py에서 빈 evidence_context 처리 확인 in backend/app/services/draft/prompt_builder.py

**Checkpoint**: Foundation ready - generate_draft_preview()가 fact-summary 기반으로 동작

---

## Phase 3: User Story 1 - 사실관계 요약 기반 초안 생성 (Priority: P1) 🎯 MVP

**Goal**: fact-summary가 있는 사건에서 60초 이내 초안 생성 성공

**Independent Test**: staging에서 fact-summary 있는 사건으로 초안 생성 API 호출

### Implementation for User Story 1

- [ ] T008 [US1] generate_draft_preview()에서 RAG 검색 결과 대신 빈 리스트 전달 in backend/app/services/draft_service.py
- [ ] T009 [US1] evidence_results = [] 설정 및 evidence_context_str 처리 in backend/app/services/draft_service.py:147-148
- [ ] T010 [US1] fact_summary_context 우선 참조 로직 유지 확인 in backend/app/services/draft_service.py:157
- [ ] T011 [US1] prompt_builder에서 fact_summary_section이 최상단에 위치하는지 확인 in backend/app/services/draft/prompt_builder.py:193
- [ ] T012 [US1] 비동기 초안 생성(_execute_draft_generation_task)에도 동일 로직 적용 in backend/app/services/draft_service.py:766

**Checkpoint**: fact-summary가 있는 사건에서 초안 생성 성공 (타임아웃 없음)

---

## Phase 4: User Story 2 - 사실관계 요약 미존재 시 처리 (Priority: P2)

**Goal**: fact-summary 없는 사건에서 명확한 에러 메시지 반환

**Independent Test**: fact-summary 없는 사건에서 초안 생성 시 ValidationError 확인

### Implementation for User Story 2

- [ ] T013 [US2] _get_fact_summary_context() 반환값 검증 로직 추가 in backend/app/services/draft_service.py
- [ ] T014 [US2] fact-summary 빈 문자열일 때 ValidationError 발생 in backend/app/services/draft_service.py:140
- [ ] T015 [US2] 에러 메시지에 사실관계 요약 생성 안내 포함 in backend/app/services/draft_service.py
- [ ] T016 [US2] 비동기 초안 생성에서도 동일 에러 처리 in backend/app/services/draft_service.py:766

**Checkpoint**: fact-summary 없는 사건에서 적절한 에러 메시지 반환

---

## Phase 5: User Story 3 - 초안 품질 유지 (Priority: P3)

**Goal**: fact-summary 기반 초안이 법률 문서 형식을 갖추고 품질 유지

**Independent Test**: 생성된 초안에 청구취지, 청구원인, 증거 목록 포함 확인

### Implementation for User Story 3

- [ ] T017 [US3] legal_context, precedent_context, consultation_context 유지 확인 in backend/app/services/draft_service.py:148-155
- [ ] T018 [US3] prompt_builder 시스템 메시지에서 법률 문서 형식 유지 확인 in backend/app/services/draft/prompt_builder.py:94-122
- [ ] T019 [US3] 증거 인용 없이도 citations 빈 리스트로 정상 반환 확인 in backend/app/services/draft_service.py:197

**Checkpoint**: 생성된 초안이 법률 문서 형식을 갖춤

---

## Phase 6: 테스트 수정 및 검증

**Purpose**: 기존 테스트를 새 로직에 맞게 수정

- [ ] T020 [P] test_draft_service.py에서 RAG 검색 모킹 제거 in backend/tests/unit/test_draft_service.py
- [ ] T021 [P] fact-summary 기반 테스트 케이스 추가 in backend/tests/unit/test_draft_service.py
- [ ] T022 [P] fact-summary 없는 경우 ValidationError 테스트 추가 in backend/tests/unit/test_draft_service.py
- [ ] T023 pytest 실행하여 모든 테스트 통과 확인

---

## Phase 7: Staging 검증 및 Polish

**Purpose**: Staging 환경에서 실제 동작 검증

- [ ] T024 Staging 환경에 배포 (dev 브랜치 push)
- [ ] T025 [P] fact-summary 있는 사건에서 초안 생성 테스트 (Staging API)
- [ ] T026 [P] fact-summary 없는 사건에서 에러 메시지 확인 (Staging API)
- [ ] T027 타임아웃 발생하지 않는지 확인 (60초 이내 완료)
- [ ] T028 quickstart.md 검증 시나리오 실행

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 - 모든 User Story 차단
- **User Story 1 (Phase 3)**: Foundational 완료 필수
- **User Story 2 (Phase 4)**: Foundational 완료 필수 (US1과 병렬 가능)
- **User Story 3 (Phase 5)**: Foundational 완료 필수 (US1, US2와 병렬 가능)
- **테스트 수정 (Phase 6)**: US1-US3 구현 완료 후
- **Staging 검증 (Phase 7)**: 모든 구현 및 테스트 완료 후

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 완료 후 즉시 시작 - 다른 스토리 의존 없음
- **User Story 2 (P2)**: Foundational 완료 후 시작 - US1과 독립적
- **User Story 3 (P3)**: Foundational 완료 후 시작 - US1, US2와 독립적

### Parallel Opportunities

- T002, T003: 병렬 실행 가능 (다른 파일)
- T020, T021, T022: 병렬 실행 가능 (동일 파일 내 다른 함수)
- T025, T026: 병렬 실행 가능 (다른 테스트 시나리오)

---

## Parallel Example: User Story 1

```bash
# 핵심 구현 (순차 실행 - 동일 파일)
Task: "T008 [US1] generate_draft_preview()에서 RAG 검색 결과 대신 빈 리스트 전달"
Task: "T009 [US1] evidence_results = [] 설정 및 evidence_context_str 처리"
```

## Parallel Example: 테스트 수정

```bash
# 테스트 병렬 실행
Task: "T020 [P] test_draft_service.py에서 RAG 검색 모킹 제거"
Task: "T021 [P] fact-summary 기반 테스트 케이스 추가"
Task: "T022 [P] fact-summary 없는 경우 ValidationError 테스트 추가"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (분석)
2. Complete Phase 2: Foundational (핵심 로직 변경)
3. Complete Phase 3: User Story 1 (fact-summary 기반 초안 생성)
4. **STOP and VALIDATE**: Staging에서 테스트
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → 핵심 변경 완료
2. User Story 1 → Staging 테스트 → 배포 (MVP!)
3. User Story 2 → 에러 처리 추가 → 배포
4. User Story 3 → 품질 검증 → 배포
5. 테스트 수정 → 회귀 방지

---

## Summary

| Metric | Value |
|:-------|:------|
| Total Tasks | 28 |
| Phase 1 (Setup) | 3 |
| Phase 2 (Foundational) | 4 |
| Phase 3 (US1 - MVP) | 5 |
| Phase 4 (US2) | 4 |
| Phase 5 (US3) | 3 |
| Phase 6 (Tests) | 4 |
| Phase 7 (Staging) | 5 |
| Parallel Opportunities | 7 tasks |

---

## Notes

- [P] tasks = 다른 파일, 의존성 없음
- [Story] label = 특정 User Story에 매핑
- 대부분 동일 파일(draft_service.py) 수정이라 순차 실행 필요
- 커밋은 Phase 단위로 진행 권장
- 체크포인트마다 Staging 테스트 권장

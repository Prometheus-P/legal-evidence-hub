# Feature Specification: 판례 검색 시스템 완성 및 인물 관계도 통합

**Feature Branch**: `012-precedent-integration`
**Created**: 2025-12-12
**Status**: Draft
**Input**: 판례 검색 시스템 완성 및 인물 관계도 통합 - Frontend 판례 UI, Backend 판례 API, AI Worker 파이프라인 통합

## Background

기존 코드베이스 분석 결과:
- **인물 관계도**: Frontend/Backend/AI Worker 개별 구현 완료(90%), 통합 미완성(10%)
- **사건 마인드맵**: PartyGraph로 완전 구현됨 (100%)
- **판례 검색**: AI Worker 95% 완성, Backend 50%, Frontend 30% 미완성

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 유사 판례 검색 및 열람 (Priority: P1)

변호사가 현재 사건의 증거와 유책사유를 기반으로 유사한 이혼 판례를 검색하고 상세 내용을 확인합니다.

**Why this priority**: 변호사가 소장 작성 시 참고할 판례를 찾는 것은 법률 서비스의 핵심 가치입니다.

**Independent Test**: 케이스 상세 페이지에서 "유사 판례 검색" 버튼을 클릭하여 관련 판례 목록을 확인합니다.

**Acceptance Scenarios**:

1. **Given** 변호사가 사건을 보고 있을 때, **When** "유사 판례 검색" 버튼을 클릭하면, **Then** 판례 목록이 표시됩니다.
2. **Given** 판례 목록이 표시된 상태에서, **When** 개별 판례를 클릭하면, **Then** 판례 요지, 법원, 선고일이 표시됩니다.

---

### User Story 2 - 초안 작성 시 판례 인용 (Priority: P1)

변호사가 소장 초안을 생성할 때 관련 판례가 자동으로 인용됩니다.

**Why this priority**: 판례 인용은 소장의 설득력을 높이는 핵심 요소입니다.

**Independent Test**: 초안 생성 시 유사 판례가 자동으로 포함되어 있는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 유책사유가 분석된 상태에서, **When** 초안을 생성하면, **Then** 관련 판례가 참고자료로 포함됩니다.

---

### User Story 3 - 인물 관계 자동 추출 (Priority: P2)

증거 업로드 시 AI가 자동으로 인물과 관계를 추출하여 관계도에 반영합니다.

**Why this priority**: 수동 인물 입력은 번거로우며, AI 자동 추출은 핵심 차별화 기능입니다.

**Independent Test**: 카카오톡 대화 업로드 후 관계도에서 자동 추출된 인물을 확인합니다.

**Acceptance Scenarios**:

1. **Given** 증거가 업로드될 때, **When** AI Worker가 처리를 완료하면, **Then** 추출된 인물이 자동 생성됩니다.
2. **Given** AI가 관계를 추론했을 때, **When** 신뢰도가 0.7 이상이면, **Then** 관계도에 엣지가 추가됩니다.

---

### User Story 4 - 판례 데이터 초기화 (Priority: P2)

시스템 관리자가 법령정보 API에서 이혼 판례를 수집하여 검색 가능한 상태로 준비합니다.

**Why this priority**: 판례 데이터가 없으면 검색 기능이 동작하지 않습니다.

**Independent Test**: 데이터 로딩 스크립트 실행 후 판례 검색 API가 결과를 반환하는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 판례 데이터가 비어있을 때, **When** 로딩 스크립트를 실행하면, **Then** 최소 100건의 판례가 저장됩니다.

---

### Edge Cases

- 판례 검색 결과가 0건일 때? → "관련 판례를 찾을 수 없습니다" 메시지 표시
- AI가 추출한 인물이 이미 존재할 때? → 이름 기반 매칭 후 확인 모달 표시
- Qdrant 연결 실패 시? → Fallback 데이터 사용

## Requirements *(mandatory)*

### Functional Requirements

#### 판례 검색 시스템
- **FR-001**: 시스템은 유책사유 기반으로 유사 판례를 검색할 수 있어야 합니다.
- **FR-002**: 시스템은 판례의 요지, 법원, 선고일, 재산분할 비율을 표시해야 합니다.
- **FR-003**: 시스템은 판례 검색 결과를 관련성 순으로 정렬해야 합니다.
- **FR-004**: 시스템은 판례 검색 API 엔드포인트를 제공해야 합니다.
- **FR-005**: 시스템은 초안 생성 시 관련 판례를 자동으로 포함해야 합니다.

#### 인물 관계도 통합
- **FR-006**: 시스템은 AI Worker가 추출한 인물을 PartyNode로 자동 저장해야 합니다.
- **FR-007**: 시스템은 AI Worker가 추론한 관계를 PartyRelationship으로 저장해야 합니다.
- **FR-008**: 시스템은 자동 추출된 인물에 대해 편집/삭제 기능을 제공해야 합니다.

#### 데이터 인프라
- **FR-009**: 시스템은 법령정보 API에서 판례를 수집하여 벡터 저장소에 저장할 수 있어야 합니다.
- **FR-010**: 시스템은 판례 텍스트를 벡터로 변환하여 유사도 검색을 지원해야 합니다.

### Key Entities

- **PrecedentCase**: 판례 정보 (사건번호, 법원, 선고일, 요지, 재산분할 비율)
- **PartyNode**: 당사자 정보 (이름, 역할, 측면, 위치, 자동추출 여부)
- **PartyRelationship**: 당사자 간 관계 (유형, 시작일, 종료일, 신뢰도)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 변호사가 유사 판례 검색을 5초 이내에 완료할 수 있습니다.
- **SC-002**: 판례 검색 결과 중 최소 3건이 사건과 관련성이 있습니다.
- **SC-003**: 증거 업로드 후 2분 이내에 인물 관계가 자동 추출됩니다.
- **SC-004**: 자동 추출된 인물의 정확도가 80% 이상입니다.
- **SC-005**: 판례 데이터 초기 로딩이 30분 이내에 완료됩니다 (100건 기준).

---

## Assumptions

1. 국가법령정보 공동활용 API 접근 권한이 있습니다.
2. Qdrant 벡터 저장소가 배포 환경에서 접근 가능합니다.
3. OpenAI API가 사용 가능합니다.
4. 기존 AI Worker의 PersonExtractor, RelationshipInferrer가 정상 동작합니다.

## Out of Scope

- 판례 전문 열람 기능 (외부 링크로 대체)
- 판례 데이터 자동 업데이트 (수동 스크립트 실행)
- 복잡한 인물 매칭 알고리즘 (단순 이름 비교만 구현)

---

## Clarifications

### Session 2025-12-12

- Q: 판례 데이터 소스는 어디인가? → A: 국가법령정보센터 Open API (law.go.kr)
- Q: 국가법령정보센터 API 실패 시 Fallback 전략은? → A: Sample JSON 파일에서 Fallback 데이터 로드 (ai_worker/scripts/sample_precedents.json)
- Q: 판례 데이터 업데이트 주기는? → A: 수동 스크립트 실행 (MVP 단계, Out of Scope 유지)

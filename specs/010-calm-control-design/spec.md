# Feature Specification: Calm-Control Design System

**Feature Branch**: `010-calm-control-design`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "calm-control 디자인 시스템 - 저채도 색상, 안정적인 타이포그래피, 최소한의 애니메이션으로 변호사가 모든 것을 제어한다는 느낌을 주는 UI 디자인 시스템. 대시보드 위젯(RiskFlagCard, AIRecommendationCard), 사건 관계도 그래프, 재산 분할 폼 등의 컴포넌트 포함."

## 배경 (Background)

LEH(Legal Evidence Hub)는 이혼 사건을 다루는 법률 전문가를 위한 플랫폼입니다. 법률 업무의 특성상 사용자(변호사)는 신중하고 정확한 판단을 내려야 하며, UI는 이러한 전문적 업무를 지원해야 합니다.

**Calm-Control 디자인 철학**:
- **Calm**: 저채도 색상과 안정적인 타이포그래피로 시각적 피로를 줄이고 집중을 돕습니다
- **Control**: 모든 UI 요소가 예측 가능하게 동작하여 "변호사가 시스템을 완전히 제어한다"는 신뢰감을 줍니다

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 디자인 토큰 시스템 (Priority: P1)

변호사가 LEH 플랫폼을 사용할 때, 모든 페이지에서 일관된 시각적 경험을 제공받습니다. 저채도 색상 팔레트, 안정적인 타이포그래피, 일관된 간격 시스템이 적용되어 전문적이고 신뢰감 있는 느낌을 받습니다.

**Why this priority**: 디자인 토큰은 모든 UI 컴포넌트의 기반입니다. 이것이 먼저 정의되어야 다른 컴포넌트들이 일관성 있게 구현될 수 있습니다.

**Independent Test**: 디자인 토큰이 적용된 페이지를 열어 색상, 폰트, 간격이 정의된 스펙대로 렌더링되는지 확인

**Acceptance Scenarios**:

1. **Given** 디자인 토큰이 정의되어 있을 때, **When** 변호사가 어떤 페이지를 방문하든, **Then** 동일한 색상 팔레트(저채도 Teal 계열 primary, Neutral gray 계열 배경)가 적용됨
2. **Given** 디자인 토큰이 정의되어 있을 때, **When** 텍스트가 표시될 때, **Then** 정의된 타이포그래피 스케일(heading, body, caption)이 일관되게 적용됨
3. **Given** 디자인 토큰이 정의되어 있을 때, **When** 컴포넌트 간 간격이 필요할 때, **Then** 4px 기반 간격 시스템(4, 8, 12, 16, 24, 32, 48px)이 적용됨

---

### User Story 2 - 대시보드 위젯 컴포넌트 (Priority: P1)

변호사가 대시보드에서 사건 현황을 한눈에 파악할 수 있습니다. RiskFlagCard는 주의가 필요한 사건을 강조하고, AIRecommendationCard는 AI가 제안하는 다음 행동을 보여줍니다.

**Why this priority**: 대시보드는 변호사가 가장 자주 사용하는 화면이며, 핵심 정보를 효과적으로 전달해야 합니다.

**Independent Test**: 대시보드 페이지에서 RiskFlagCard와 AIRecommendationCard가 올바른 데이터와 함께 렌더링되는지 확인

**Acceptance Scenarios**:

1. **Given** 위험 플래그가 있는 사건이 있을 때, **When** 대시보드를 볼 때, **Then** RiskFlagCard에 위험 수준(high/medium/low), 사건명, 위험 설명이 표시됨
2. **Given** AI 추천 행동이 있을 때, **When** 대시보드를 볼 때, **Then** AIRecommendationCard에 추천 제목, 설명, 신뢰도(confidence), 액션 버튼이 표시됨
3. **Given** 카드 컴포넌트들이 표시될 때, **When** 사용자가 마우스를 올리면, **Then** 미세한 그림자 변화만 있고 과도한 애니메이션 없이 피드백 제공

---

### User Story 3 - 사건 관계도 그래프 (Priority: P2)

변호사가 사건에 관련된 당사자들(원고, 피고, 증인 등)의 관계를 시각적 그래프로 파악할 수 있습니다. 노드는 인물을, 엣지는 관계를 나타내며, 드래그로 레이아웃을 조정할 수 있습니다.

**Why this priority**: 관계도는 복잡한 이혼 사건에서 당사자 관계를 이해하는 데 도움이 되지만, 핵심 기능은 아닙니다.

**Independent Test**: 사건 상세 페이지의 관계도 탭에서 그래프가 렌더링되고 노드 드래그가 동작하는지 확인

**Acceptance Scenarios**:

1. **Given** 사건에 당사자 정보가 있을 때, **When** 관계도 탭을 클릭하면, **Then** 당사자들이 노드로 표시되고 관계가 엣지로 연결됨
2. **Given** 관계도 그래프가 표시될 때, **When** 노드를 드래그하면, **Then** 노드 위치가 변경되고 연결된 엣지가 따라 움직임
3. **Given** 관계도 그래프가 표시될 때, **When** 노드를 클릭하면, **Then** 해당 당사자의 상세 정보가 사이드 패널에 표시됨

---

### User Story 4 - 재산 분할 폼 (Priority: P2)

변호사가 이혼 사건의 재산 목록을 등록하고, 원고/피고 간 분할 비율을 설정하여 예상 분할 결과를 미리 볼 수 있습니다.

**Why this priority**: 재산 분할은 이혼 사건의 핵심 쟁점이지만, 기본 사건 관리 기능이 먼저 필요합니다.

**Independent Test**: 사건 상세 페이지의 재산 탭에서 재산 추가, 분할 비율 조정, 결과 미리보기가 동작하는지 확인

**Acceptance Scenarios**:

1. **Given** 사건 재산 탭에 있을 때, **When** "재산 추가" 버튼을 클릭하면, **Then** 재산 등록 폼(명칭, 유형, 가액, 취득일, 소유권)이 표시됨
2. **Given** 재산이 등록되어 있을 때, **When** 분할 비율 슬라이더를 조정하면, **Then** 원고/피고 비율이 실시간으로 업데이트됨
3. **Given** 재산 목록이 있을 때, **When** 화면을 볼 때, **Then** 총 재산, 총 부채, 순자산, 예상 정산금이 자동 계산되어 표시됨

---

### Edge Cases

- 관계도 그래프에 당사자가 없거나 1명만 있는 경우: 빈 상태 메시지 또는 단일 노드만 표시
- 재산 목록이 비어있는 경우: "등록된 재산이 없습니다" 메시지와 함께 추가 버튼 강조
- 재산 가액이 0원인 경우: 정상적으로 처리하되 분할 계산에서 제외
- 분할 비율 합이 100%가 아닌 경우: 입력 시점에 자동으로 100%로 보정

## Requirements *(mandatory)*

### Functional Requirements

**디자인 토큰**
- **FR-001**: 시스템은 저채도 색상 팔레트(Primary: Teal 계열, Neutral: Gray 계열, Semantic: 성공/경고/오류)를 제공해야 함
- **FR-002**: 시스템은 타이포그래피 스케일(h1~h6, body-lg, body, body-sm, caption)을 정의해야 함
- **FR-003**: 시스템은 4px 기반 간격 시스템(spacing-1~spacing-12)을 제공해야 함
- **FR-004**: 시스템은 일관된 그림자 스케일(shadow-sm, shadow-md, shadow-lg)을 정의해야 함

**대시보드 위젯**
- **FR-005**: RiskFlagCard는 위험 수준(high/medium/low), 사건명, 위험 설명을 표시해야 함
- **FR-006**: AIRecommendationCard는 추천 제목, 설명, 신뢰도(0-100%), 액션 버튼을 표시해야 함
- **FR-007**: 카드 호버 시 과도한 애니메이션 없이 미세한 시각적 피드백만 제공해야 함

**관계도 그래프**
- **FR-008**: 관계도는 당사자를 노드로, 관계를 엣지로 시각화해야 함
- **FR-009**: 노드는 드래그로 위치 조정이 가능해야 함
- **FR-010**: 노드 클릭 시 상세 정보 패널이 표시되어야 함
- **FR-011**: 당사자가 없는 경우 빈 상태 메시지를 표시해야 함

**재산 분할 폼**
- **FR-012**: 재산 등록 폼은 명칭, 유형(부동산/차량/금융/사업/개인/부채/기타), 가액, 취득일, 소유권(공동/원고/피고)을 입력받아야 함
- **FR-013**: 분할 비율 슬라이더는 원고/피고 비율을 조정할 수 있어야 하며, 합이 100%가 되도록 자동 보정해야 함
- **FR-014**: 분할 요약은 총 재산, 총 부채, 순자산, 원고 몫, 피고 몫, 예상 정산금을 계산하여 표시해야 함

### Key Entities

- **DesignToken**: 색상, 타이포그래피, 간격, 그림자 등 디자인 시스템의 기본 값
- **RiskFlag**: 사건의 위험 요소 (level, title, description, caseId)
- **AIRecommendation**: AI 추천 행동 (title, description, confidence, actionType, caseId)
- **Party**: 사건 당사자 (id, name, role, relationship)
- **Asset**: 재산 정보 (id, caseId, type, name, value, ownership, divisionRatio)
- **DivisionSummary**: 분할 계산 결과 (totalAssets, totalDebts, netValue, plaintiffShare, defendantShare, settlement)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 모든 페이지에서 정의된 색상 팔레트 외의 색상이 사용되지 않음 (일관성 100%)
- **SC-002**: 사용자가 대시보드 위젯에서 필요한 정보를 3초 이내에 파악할 수 있음
- **SC-003**: 관계도 그래프의 노드 드래그 응답 시간이 50ms 미만 (지연 없는 느낌)
- **SC-004**: 재산 분할 비율 변경 시 계산 결과가 즉시(100ms 이내) 업데이트됨
- **SC-005**: 모든 인터랙션(호버, 클릭)에서 과도한 애니메이션 없이 일관된 피드백 제공
- **SC-006**: 빈 상태 화면에서 사용자가 다음 행동(재산 추가, 당사자 추가 등)을 명확히 알 수 있음

## Assumptions

- 색상 팔레트는 WCAG 2.1 AA 기준 명암비를 충족함
- 타이포그래피는 한글과 영문 모두 지원하는 시스템 폰트(Pretendard 또는 Inter)를 사용함
- 관계도 그래프 라이브러리는 React Flow를 사용함 (이미 프로젝트에 설치됨)
- 재산 데이터는 백엔드 API(/cases/{id}/assets)를 통해 CRUD됨
- 애니메이션 duration은 최대 200ms로 제한하여 "즉각적인 제어감"을 유지함

## Out of Scope

- 다크 모드 지원 (향후 확장 고려)
- 애니메이션 커스터마이징 옵션
- 관계도 그래프 자동 레이아웃 알고리즘 최적화
- 재산 분할 법적 계산 로직 (단순 비율 계산만 수행)
- 모바일 반응형 최적화 (데스크톱 우선)

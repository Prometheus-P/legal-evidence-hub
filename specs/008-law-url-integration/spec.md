# Feature Specification: 법령한글주소 URL 통합

**Feature Branch**: `008-law-url-integration`
**Created**: 2025-12-08
**Status**: Draft
**Input**: 국가법령정보센터 법령한글주소 API를 LEH 프로젝트에 통합하여 법령/판례 인용 시 클릭 가능한 law.go.kr 딥링크를 생성

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 법령 조문 링크 확인 (Priority: P1)

변호사가 AI 초안 문서를 검토할 때, 인용된 법령 조문(예: 민법 제840조)을 클릭하여 국가법령정보센터에서 원문을 즉시 확인할 수 있다.

**Why this priority**: 법률 문서의 정확성 검증은 가장 핵심적인 업무이며, 원문 확인 없이는 법률 서비스를 제공할 수 없다. 법령 참조의 신뢰성이 서비스 가치의 근간이다.

**Independent Test**: 초안 생성 후 법령 인용 링크를 클릭하여 law.go.kr 해당 조문 페이지로 이동되는지 확인

**Acceptance Scenarios**:

1. **Given** AI가 "민법 제840조"를 인용한 초안을 생성했을 때, **When** 사용자가 해당 인용을 클릭하면, **Then** https://www.law.go.kr/법령/민법/제840조 페이지로 이동한다
2. **Given** 초안에 여러 법령 조문이 인용되어 있을 때, **When** 사용자가 각 인용을 클릭하면, **Then** 각각 해당하는 법령 조문 페이지로 정확히 이동한다
3. **Given** 법령명에 특수문자나 공백이 포함된 경우(예: "가사소송법"), **When** URL이 생성되면, **Then** URL 인코딩이 올바르게 적용되어 페이지가 정상 로드된다

---

### User Story 2 - 판례 링크 확인 (Priority: P2)

변호사가 AI 초안에서 인용된 판례(예: 대법원 2019다12345)를 클릭하여 국가법령정보센터에서 판결문 원문을 확인할 수 있다.

**Why this priority**: 판례는 법령 다음으로 중요한 법적 근거이며, 이혼 사건에서 선례 확인은 필수적이다.

**Independent Test**: 초안 내 판례 인용 링크를 클릭하여 law.go.kr 판례 페이지로 이동되는지 확인

**Acceptance Scenarios**:

1. **Given** AI가 "대법원 2019다12345 판결"을 인용한 초안을 생성했을 때, **When** 사용자가 해당 인용을 클릭하면, **Then** https://www.law.go.kr/판례/(2019다12345) 페이지로 이동한다
2. **Given** 판례에 판결일자가 포함된 경우, **When** URL이 생성되면, **Then** 사건번호와 판결일자가 모두 포함된 정확한 URL이 생성된다

---

### User Story 3 - 법률 검색 결과에서 원문 확인 (Priority: P3)

사용자가 법률 지식 검색(RAG) 결과를 확인할 때, 각 검색 결과에서 원문 링크를 통해 국가법령정보센터로 바로 이동할 수 있다.

**Why this priority**: 검색 결과의 맥락을 원문에서 확인하는 것은 법률 연구의 기본이며, 사용자 편의성을 크게 향상시킨다.

**Independent Test**: 법률 검색 수행 후 결과 항목의 링크를 클릭하여 원문 페이지로 이동되는지 확인

**Acceptance Scenarios**:

1. **Given** 사용자가 "이혼 사유"로 법률 지식을 검색했을 때, **When** 검색 결과에 민법 제840조가 포함되면, **Then** 해당 결과에 law.go.kr 링크가 함께 표시된다
2. **Given** 검색 결과에 판례가 포함된 경우, **When** 결과를 확인하면, **Then** 판례 원문으로 이동하는 링크가 제공된다

---

### Edge Cases

- 법령명이나 조문 번호가 누락된 경우 URL을 생성하지 않고 텍스트만 표시한다
- 폐지된 법령이나 개정된 조문의 경우 URL이 404를 반환할 수 있음을 사용자에게 안내한다
- 한글 URL 인코딩 실패 시 기본 law.go.kr 검색 페이지로 폴백한다
- 사건번호 형식이 표준과 다른 경우(예: 헌재결정례) 적절한 패턴으로 변환한다

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 법령명과 조문 번호를 입력받아 유효한 law.go.kr URL을 생성해야 한다
- **FR-002**: 시스템은 판례 사건번호와 판결일자를 입력받아 유효한 law.go.kr 판례 URL을 생성해야 한다
- **FR-003**: 생성된 URL은 한글 문자를 UTF-8로 인코딩하여 유효한 HTTP URL 형식이어야 한다
- **FR-004**: 초안 생성 시 법령/판례 인용에 자동으로 law.go.kr 링크를 포함해야 한다
- **FR-005**: 법률 지식 검색 결과에 해당 문서의 law.go.kr 링크를 포함해야 한다
- **FR-006**: URL 생성 실패 시 오류를 발생시키지 않고 링크 없이 텍스트만 반환해야 한다
- **FR-007**: 기존 API 응답과 하위 호환성을 유지해야 한다 (url 필드는 선택적)

### Key Entities

- **법령 URL (Statute URL)**: 법령명, 조문번호, 공포번호, 공포일자를 조합하여 생성되는 딥링크
- **판례 URL (Precedent URL)**: 사건번호, 판결일자, 법원명을 조합하여 생성되는 딥링크
- **법률 인용 (Legal Citation)**: 초안 문서 내에서 법령/판례를 참조하는 텍스트와 해당 URL의 조합

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 생성된 법령 URL의 95% 이상이 law.go.kr에서 정상적으로 해당 페이지를 로드해야 한다
- **SC-002**: 사용자가 법령 원문을 확인하는 시간이 기존 수동 검색 대비 80% 단축되어야 한다
- **SC-003**: 초안 문서 내 모든 법령/판례 인용에 클릭 가능한 링크가 포함되어야 한다
- **SC-004**: 기존 API 사용자의 코드 변경 없이 새 기능이 작동해야 한다 (하위 호환성)

## Assumptions

- 국가법령정보센터의 법령한글주소 API 규격이 안정적으로 유지된다
- 법령명과 조문 번호는 AI Worker의 파싱 결과에서 정확하게 추출된다
- 사용자는 외부 인터넷 접속이 가능한 환경에서 서비스를 사용한다
- 폐지된 법령이나 변경된 URL에 대한 처리는 향후 버전에서 개선한다

## Dependencies

- 기존 `legal_api_fetcher.py`의 법령/판례 데이터 구조
- 기존 `draft_service.py`의 인용 생성 로직
- 기존 `LegalSearchResult`, `DraftCitation` 스키마

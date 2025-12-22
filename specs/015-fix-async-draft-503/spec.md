# Feature Specification: 비동기 초안 생성 API 503 에러 해결

**Feature Branch**: `015-fix-async-draft-503`
**Created**: 2025-12-22
**Status**: Draft
**Input**: User description: "비동기 초안 생성 API 503 에러 해결 - POST /api/cases/{case_id}/draft-preview-async 엔드포인트에서 503 Service Unavailable 에러 발생. 배포는 성공했지만 실제 API 호출 시 503 반환. curl 테스트에서는 정상 작동했으나 브라우저에서 실패함."

## 문제 현황

### 증상
- `POST /api/cases/{case_id}/draft-preview-async` 엔드포인트에서 503 Service Unavailable 에러 발생
- GitHub Actions 배포는 성공적으로 완료됨
- curl 명령어로 직접 테스트 시 정상 작동 (job_id 반환)
- 브라우저(Frontend)에서 호출 시 503 에러 발생

### 핵심 단서
- **curl 성공, 브라우저 실패**: CORS, 인증, 또는 요청 형식 차이 가능성
- **503 Service Unavailable**: Lambda 함수 실행 실패 또는 CloudFront 라우팅 문제

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 초안 생성 정상 동작 (Priority: P1)

변호사가 사건 상세 페이지에서 "초안 생성" 버튼을 클릭하면, 비동기 작업이 시작되고 진행률 표시와 함께 초안이 생성되어야 한다.

**Why this priority**: 핵심 비즈니스 기능으로, 503 에러로 인해 전체 초안 생성 기능이 사용 불가능한 상태

**Independent Test**: 브라우저에서 초안 생성 버튼 클릭 후 진행률 바가 표시되고 초안이 생성되면 성공

**Acceptance Scenarios**:

1. **Given** 증거가 업로드된 사건이 있을 때, **When** 변호사가 "초안 생성" 버튼을 클릭하면, **Then** 비동기 작업이 시작되고 job_id가 반환된다
2. **Given** 비동기 작업이 시작되었을 때, **When** 프론트엔드가 상태를 폴링하면, **Then** 진행률(0-100%)이 업데이트되고 완료 시 초안 텍스트가 반환된다
3. **Given** 초안 생성이 완료되었을 때, **When** 결과가 화면에 표시되면, **Then** 사용자는 초안을 검토하고 편집할 수 있다

---

### User Story 2 - 에러 시 명확한 피드백 (Priority: P2)

초안 생성 중 오류가 발생하면, 사용자에게 명확한 에러 메시지를 표시하고 재시도 옵션을 제공해야 한다.

**Why this priority**: 오류 발생 시에도 사용자 경험을 유지해야 함

**Independent Test**: 의도적으로 에러를 발생시킨 후(예: 증거 없는 사건) 에러 메시지 확인

**Acceptance Scenarios**:

1. **Given** 증거가 없는 사건일 때, **When** 초안 생성을 시도하면, **Then** "증거를 먼저 업로드해주세요" 메시지가 표시된다
2. **Given** 서버 에러가 발생했을 때, **When** 사용자가 에러를 확인하면, **Then** "다시 시도" 버튼이 제공된다

---

### Edge Cases

- CloudFront가 새 엔드포인트를 Lambda로 라우팅하지 않을 때 어떻게 처리하는가?
- 브라우저 CORS preflight 요청이 실패할 때 어떻게 처리하는가?
- 인증 쿠키가 전송되지 않을 때 어떻게 처리하는가?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템 MUST 브라우저에서 `/api/cases/{case_id}/draft-preview-async` POST 요청을 정상 처리해야 한다
- **FR-002**: 시스템 MUST 비동기 작업 시작 시 즉시 job_id를 반환해야 한다 (30초 이내)
- **FR-003**: 시스템 MUST 작업 상태 폴링 시 현재 진행률과 상태를 반환해야 한다
- **FR-004**: 시스템 MUST 작업 완료 시 초안 텍스트와 인용 정보를 반환해야 한다
- **FR-005**: 시스템 MUST 에러 발생 시 구체적인 에러 메시지를 반환해야 한다
- **FR-006**: 시스템 MUST CORS preflight 요청(OPTIONS)을 정상 처리해야 한다
- **FR-007**: 시스템 MUST HTTP-only 쿠키 기반 인증을 지원해야 한다

### Key Entities

- **DraftJob**: 비동기 초안 생성 작업 (job_id, case_id, status, progress, result, error_message)
- **DraftPreviewResponse**: 초안 생성 결과 (draft_text, citations, precedent_citations)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 브라우저에서 초안 생성 요청 시 200 OK 응답을 받아야 한다 (503 에러 0%)
- **SC-002**: 초안 생성 작업이 2분 이내에 완료되어야 한다
- **SC-003**: 사용자가 진행률 표시를 통해 작업 상태를 실시간으로 확인할 수 있어야 한다
- **SC-004**: 에러 발생 시 5초 이내에 사용자에게 피드백이 제공되어야 한다

## Assumptions

- CloudFront 라우팅 설정이 `/api/*` 경로를 Lambda로 전달하도록 구성되어 있다
- Backend Lambda 함수는 정상 배포되어 실행 가능한 상태이다
- 기존 동기 방식 API (`/draft-preview`)가 정상 작동한다면 비동기 로직도 동일하게 작동해야 한다

## 원인 분석 대상

1. **CloudFront 라우팅**: 새 엔드포인트가 Lambda로 라우팅되지 않을 가능성
2. **CORS 설정**: OPTIONS preflight 요청 처리 누락 가능성
3. **Lambda 에러**: 코드 실행 중 예외 발생 가능성
4. **인증 문제**: 쿠키가 제대로 전달되지 않을 가능성
5. **프론트엔드 요청 형식**: curl과 다른 헤더/본문 형식 가능성

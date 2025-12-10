# Feature Specification: MVP 구현 갭 해소 (Production Readiness)

**Feature Branch**: `009-mvp-gap-closure`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "MVP 구현 갭 해소 - 문서/설계 대비 실제 구현 갭을 좁히고 production-ready 상태로 만들기"

## Clarifications

### Session 2025-12-09

- Q: Draft 생성 후 편집 방식? → A: 초안작성에 필요한 웹 편집툴 연결 (Web-based editor integration required)
- Q: 지원 증거 파일 형식? → A: Images + Audio + Video + PDF + Text (jpg, png, mp3, wav, mp4, pdf, txt, csv)
- Q: 웹 편집툴 구현 방식? → A: Rich text editor (TipTap/Quill) embedded in frontend
- Q: 최대 증거 파일 크기? → A: 500MB (영상 녹화 파일 지원)
- Q: Observability 요구사항? → A: Standard (CloudWatch logs + Lambda metrics + API latency tracking)

## 배경 (Background)

현재 LEH 프로젝트는 엔터프라이즈급 문서/설계가 완성되어 있으나, 실제 구현과의 갭이 존재:

- **AI Worker**: 코드/테스트 완성, S3 권한 미비로 배포 차단
- **Backend**: RAG 검색/Draft Preview API 미구현, 권한/감사로그 부분 적용
- **Frontend**: 버튼-API 스펙 불일치, 에러 처리 비일관성
- **Infra/CI**: IaC 미구성, 테스트 커버리지 CI에서 스킵

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Worker 실서비스 연동 (Priority: P1)

변호사가 증거 파일을 업로드하면, AI Worker가 자동으로 분석하여 타임라인/태그/요약을 생성한다.

**Why this priority**: AI Worker가 동작하지 않으면 핵심 기능(증거 분석, RAG 검색, Draft 생성)이 모두 불가능. 전체 시스템의 근간.

**Independent Test**: S3에 파일 업로드 후 DynamoDB/Qdrant에 분석 결과가 저장되는지 확인

**Acceptance Scenarios**:

1. **Given** S3 버킷 `leh-evidence-dev`가 존재하고, **When** 증거 파일이 `cases/{case_id}/raw/` 경로에 업로드되면, **Then** AI Worker Lambda가 트리거되어 5분 내 분석 완료
2. **Given** AI Worker가 분석 완료하면, **When** DynamoDB를 조회하면, **Then** 증거 메타데이터(요약, 840조 태그, 증거력 점수)가 저장됨
3. **Given** AI Worker가 분석 완료하면, **When** Qdrant를 조회하면, **Then** 임베딩 벡터가 `case_rag_{case_id}` 컬렉션에 저장됨

---

### User Story 2 - Backend RAG 검색 및 Draft 생성 (Priority: P1)

변호사가 사건 페이지에서 "AI 분석 요청" 버튼을 클릭하면, 관련 증거를 검색하고 초안을 생성한다.

**Why this priority**: 사용자가 직접 경험하는 핵심 AI 기능. 이 기능이 없으면 "AI 파라리걸" 가치 제안이 무효화됨.

**Independent Test**: 사건 상세 페이지에서 Draft 생성 요청 시 실제 초안이 반환되는지 확인

**Acceptance Scenarios**:

1. **Given** 사건에 3개 이상의 분석된 증거가 있을 때, **When** 변호사가 RAG 검색을 실행하면, **Then** 관련도 순으로 증거 목록이 반환됨
2. **Given** 사건 증거가 분석 완료된 상태에서, **When** Draft Preview를 요청하면, **Then** 증거 인용이 포함된 초안이 30초 내 반환됨
3. **Given** Draft가 생성되면, **Then** 각 문장에 출처 증거 ID가 명시됨

---

### User Story 3 - Frontend 에러 처리 통일 (Priority: P2)

사용자가 어떤 기능을 사용하든, 오류 발생 시 일관된 피드백을 받고 다음 행동을 알 수 있다.

**Why this priority**: 현재 에러 처리가 산발적이어서 사용자 경험 저하. P1 기능이 완성되어도 에러 시 UX가 나쁘면 서비스 신뢰도 하락.

**Independent Test**: 의도적으로 네트워크 오류/서버 오류 발생시키고 일관된 에러 메시지 확인

**Acceptance Scenarios**:

1. **Given** 사용자가 로그인한 상태에서, **When** 세션이 만료되면(401), **Then** 자동으로 로그인 페이지로 이동하고 "세션이 만료되었습니다" 메시지 표시
2. **Given** API 호출 중 네트워크 오류 발생 시, **When** 화면에 에러 표시, **Then** "다시 시도" 버튼과 함께 사용자 친화적 메시지 표시
3. **Given** 버튼 클릭 후 API 호출 중, **When** 로딩 상태일 때, **Then** 버튼이 비활성화되고 로딩 인디케이터 표시

---

### User Story 4 - CI 테스트 커버리지 정상화 (Priority: P2)

개발자가 PR을 올리면, 실제 테스트가 실행되어 코드 품질이 검증된다.

**Why this priority**: 현재 CI에서 테스트가 스킵되어 "테스트 통과"가 무의미. 품질 게이트 역할을 하지 못함.

**Independent Test**: PR 생성 시 CI에서 테스트 커버리지 65% 이상 달성 확인

**Acceptance Scenarios**:

1. **Given** ai_worker 코드 변경 PR, **When** CI 실행 시, **Then** 유닛 테스트 300개 이상이 실제 실행됨 (스킵 아님)
2. **Given** backend 코드 변경 PR, **When** CI 실행 시, **Then** 테스트 커버리지 65% 이상 달성
3. **Given** frontend 코드 변경 PR, **When** CI 실행 시, **Then** lint + 유닛 테스트 통과

---

### User Story 5 - 사건별 권한 제어 (Priority: P2)

사건에 소속되지 않은 사용자는 해당 사건의 정보에 접근할 수 없다.

**Why this priority**: 법률 정보의 민감성상 권한 제어는 필수. P1보다 낮지만 배포 전 반드시 필요.

**Independent Test**: 다른 사건 소속 사용자가 해당 사건 API 호출 시 403 반환 확인

**Acceptance Scenarios**:

1. **Given** 사용자 A가 사건 1의 멤버일 때, **When** 사건 2의 증거를 조회하면, **Then** 403 Forbidden 반환
2. **Given** case_members 테이블에 사용자-사건 매핑이 있을 때, **When** 해당 사건 API 호출 시, **Then** 정상 응답
3. **Given** 모든 사건 관련 API 호출 시, **When** 권한이 없으면, **Then** audit_logs 테이블에 접근 시도 기록됨

---

### User Story 6 - 기본 배포 파이프라인 (Priority: P3)

코드가 main 브랜치에 머지되면, 자동으로 production 환경에 배포된다.

**Why this priority**: MVP 기능이 완성되어야 배포 의미가 있음. P1/P2 완료 후 필요.

**Independent Test**: main 브랜치 머지 후 CloudFront URL에서 신규 기능 확인

**Acceptance Scenarios**:

1. **Given** dev 브랜치에 코드 머지, **When** CI 통과 후, **Then** staging 환경에 자동 배포
2. **Given** main 브랜치에 코드 머지, **When** CI 통과 후, **Then** production 환경에 배포 (수동 승인 후)
3. **Given** 배포 실패 시, **When** 롤백 필요하면, **Then** 이전 버전으로 5분 내 복구 가능

---

### Edge Cases

- AI Worker Lambda가 타임아웃(15분 초과) 발생 시 어떻게 처리?
  → DynamoDB에 `status: failed` 기록, 사용자에게 "분석 실패" 알림
- Qdrant 연결 실패 시 증거 업로드가 실패해야 하나?
  → 메타데이터는 DynamoDB에 저장, 벡터 저장만 재시도 큐에 추가
- 사건 소유자가 삭제된 경우 다른 멤버가 사건에 접근 가능한가?
  → 사건에 최소 1명의 OWNER 역할 필수, 없으면 관리자 개입 필요

## Requirements *(mandatory)*

### Functional Requirements

**AI Worker (US1)**
- **FR-001**: S3 버킷 `leh-evidence-dev`, `leh-evidence-prod` 생성 및 Lambda 실행 역할에 권한 부여
- **FR-001a**: 지원 파일 형식: Images (jpg, png), Audio (mp3, wav), Video (mp4), PDF, Text (txt, csv)
- **FR-001b**: 최대 파일 크기 500MB (S3 multipart upload, 대용량 영상 지원)
- **FR-002**: AI Worker Lambda가 S3 `ObjectCreated` 이벤트에 의해 자동 트리거됨
- **FR-003**: 분석 결과가 DynamoDB `leh_evidence` 테이블에 저장됨
- **FR-004**: 임베딩 벡터가 Qdrant `case_rag_{case_id}` 컬렉션에 저장됨

**Backend RAG/Draft (US2)**
- **FR-005**: `GET /search?q={query}&case_id={id}` API가 Qdrant에서 유사 증거를 검색하여 반환
- **FR-006**: `POST /cases/{id}/draft-preview` API가 GPT-4o를 사용하여 초안 생성
- **FR-007**: Draft 응답에 각 문장별 출처 증거 ID가 포함됨
- **FR-007a**: 생성된 Draft를 TipTap/Quill 기반 Rich Text Editor에서 수정 가능

**Frontend 에러 처리 (US3)**
- **FR-008**: 401 응답 시 자동으로 로그인 페이지 리다이렉트 및 메시지 표시
- **FR-009**: 네트워크 오류 시 토스트/배너로 사용자 친화적 메시지 표시
- **FR-010**: API 호출 중 버튼 비활성화 및 로딩 상태 표시

**CI 테스트 (US4)**
- **FR-011**: `ai_worker/tests/conftest.py`에서 환경변수 미설정 시 전체 스킵 대신 특정 통합 테스트만 스킵
- **FR-012**: CI에서 ai_worker 유닛 테스트 최소 300개 실행
- **FR-013**: CI에서 backend 테스트 커버리지 65% 이상 검증

**권한 제어 (US5)**
- **FR-014**: 모든 `/cases/*`, `/evidence/*`, `/draft/*` API에 사건 멤버 권한 검증 미들웨어 적용
- **FR-015**: 권한 없는 접근 시 403 반환 및 audit_logs 테이블에 기록
- **FR-016**: audit_logs 테이블에 사용자 ID, 액션, 타임스탬프, IP 기록

**배포 파이프라인 (US6)**
- **FR-017**: GitHub Actions에서 dev 머지 시 staging 자동 배포
- **FR-018**: GitHub Actions에서 main 머지 시 production 배포 (수동 승인)
- **FR-019**: 배포 실패 시 이전 버전으로 롤백 가능

### Key Entities

- **Evidence**: 증거 파일 메타데이터 (case_id, type, timestamp, ai_summary, labels, qdrant_id)
- **AuditLog**: 감사 로그 (user_id, action, resource_type, resource_id, ip_address, created_at)
- **CaseMember**: 사건-사용자 권한 매핑 (case_id, user_id, role: OWNER/MEMBER/VIEWER)

### Non-Functional Requirements

**Observability (NFR-001~003)**
- **NFR-001**: 모든 Lambda 함수에서 CloudWatch Logs로 구조화된 로그 출력
- **NFR-002**: Lambda 실행 시간, 메모리 사용량, 에러율 CloudWatch Metrics 수집
- **NFR-003**: Backend API 응답 시간 로깅 (p50, p95, p99 latency tracking)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 증거 파일 업로드 후 5분 이내에 AI 분석 완료 및 결과 조회 가능
- **SC-002**: RAG 검색 결과가 2초 이내에 반환됨
- **SC-003**: Draft Preview가 30초 이내에 생성됨
- **SC-004**: CI에서 ai_worker 테스트 300개 이상 실행 (스킵 제외)
- **SC-005**: Backend 테스트 커버리지 65% 이상 유지
- **SC-006**: 권한 없는 API 접근 시 100% 403 반환
- **SC-007**: dev→staging 배포가 CI 통과 후 10분 이내 완료
- **SC-008**: 모든 API 에러 시 사용자 친화적 메시지 표시율 100%

## Assumptions

- S3 버킷 생성 및 IAM 역할 설정은 AWS 콘솔 또는 CLI로 수동 진행 (Terraform 미사용)
- Qdrant Cloud 인스턴스는 이미 프로비저닝됨
- OpenAI API 키는 환경변수로 설정됨
- 현재 테스트 코드의 대부분은 유효하며, conftest.py 수정만으로 CI 실행 가능
- GitHub Actions 워크플로우 파일은 이미 존재하며 수정만 필요

## Out of Scope

- Terraform/IaC 완전 자동화 (수동 AWS 설정으로 대체)
- 실시간 알림 시스템 (WebSocket)
- 다국어 지원
- 모바일 앱
- 고급 분석 대시보드

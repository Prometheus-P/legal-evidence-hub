# Implementation Plan: Production Bug Fixes & Lawyer Portal Completion

**Branch**: `011-production-bug-fixes` | **Date**: 2025-12-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-production-bug-fixes/spec.md`

## Summary

프로덕션 배포 사이트의 로그인 리다이렉트 버그를 수정하고, Lawyer 포털의 핵심 기능(알림 드롭다운, 메시지 CRUD, 의뢰인/탐정 관리)을 완성한다. HTTP-only 쿠키 기반 JWT 인증의 cross-origin 문제 해결과 역할별 라우팅 정상화가 핵심이며, 이후 CRUD 기능 구현으로 실제 업무 수행이 가능한 상태로 만든다.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, React 18, Tailwind CSS, jose (JWT)
**Storage**: PostgreSQL (RDS), HTTP-only Cookies (JWT)
**Testing**: pytest (Backend), Jest + React Testing Library (Frontend), Playwright (E2E)
**Target Platform**: Web (CloudFront CDN, cross-origin API at api.legalevidence.hub)
**Project Type**: Web application (Backend + Frontend)
**Performance Goals**: 로그인 → 대시보드 도달 3초 이내
**Constraints**: HTTP-only 쿠키 (SameSite=None, Secure for cross-origin), CloudFront /api proxy
**Scale/Scope**: 3개 역할 (lawyer, client, detective), 16개 FR, 8개 SC

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | N/A | 이 기능은 증거 업로드를 다루지 않음 |
| II. Case Isolation | N/A | RAG 인덱스 변경 없음 |
| III. No Auto-Submit | N/A | AI 생성 콘텐츠 없음 |
| IV. AWS-Only Data Storage | PASS | 모든 데이터 AWS 내 유지 (RDS, S3) |
| V. Clean Architecture | PASS | Routers → Services → Repositories 패턴 준수 예정 |
| VI. Branch Protection | PASS | feat/* → dev → main PR 워크플로우 준수 |
| VII. TDD Cycle | PASS | Frontend 컴포넌트 테스트 작성 예정 |
| VIII. Semantic Versioning | PASS | 완료 시 v0.2.1 또는 v0.3.0 태그 |

**Gate Result**: PASS - 모든 관련 원칙 준수

## Project Structure

### Documentation (this feature)

```text
specs/011-production-bug-fixes/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── notifications-api.yaml
│   ├── messages-api.yaml
│   ├── clients-api.yaml
│   └── detectives-api.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── auth.py              # 로그인/쿠키 설정 수정
│   │   ├── notifications.py     # NEW: 알림 API
│   │   ├── messages.py          # NEW: 메시지 CRUD API
│   │   ├── clients.py           # NEW: 의뢰인 CRUD API
│   │   └── detectives.py        # NEW: 탐정 CRUD API
│   ├── services/
│   │   ├── notification_service.py  # NEW
│   │   ├── message_service.py       # NEW
│   │   ├── client_service.py        # NEW
│   │   └── detective_service.py     # NEW
│   ├── repositories/
│   │   ├── notification_repository.py  # NEW
│   │   ├── message_repository.py       # NEW
│   │   ├── client_repository.py        # NEW
│   │   └── detective_repository.py     # NEW
│   └── db/
│       ├── models.py            # Notification, Message, Client, Detective 모델
│       └── schemas.py           # Pydantic 스키마 추가
└── tests/
    ├── contract/
    │   ├── test_notifications.py
    │   ├── test_messages.py
    │   ├── test_clients.py
    │   └── test_detectives.py
    └── unit/

frontend/
├── src/
│   ├── app/
│   │   ├── lawyer/
│   │   │   ├── dashboard/page.tsx  # 대시보드 권한 수정
│   │   │   ├── clients/page.tsx    # 의뢰인 추가 버튼
│   │   │   ├── investigators/page.tsx  # 탐정 추가 버튼
│   │   │   └── messages/page.tsx   # 메시지 CRUD UI
│   │   └── login/page.tsx          # 리다이렉트 로직 수정
│   ├── components/
│   │   ├── shared/
│   │   │   └── NotificationDropdown.tsx  # NEW: 알림 드롭다운
│   │   ├── lawyer/
│   │   │   ├── ClientForm.tsx      # NEW: 의뢰인 추가 폼
│   │   │   ├── DetectiveForm.tsx   # NEW: 탐정 추가 폼
│   │   │   └── MessageComposer.tsx # NEW: 메시지 작성
│   │   └── auth/
│   │       └── RoleGuard.tsx       # 역할 기반 접근 제어 수정
│   ├── hooks/
│   │   ├── useNotifications.ts     # NEW
│   │   ├── useMessages.ts          # 기존 확장
│   │   ├── useClients.ts           # NEW
│   │   └── useDetectives.ts        # NEW
│   ├── lib/api/
│   │   ├── notifications.ts        # NEW
│   │   ├── messages.ts             # 기존 확장
│   │   ├── clients.ts              # NEW
│   │   └── detectives.ts           # NEW
│   └── middleware.ts               # 역할별 라우팅 수정
└── src/__tests__/
    ├── components/
    │   ├── NotificationDropdown.test.tsx
    │   ├── ClientForm.test.tsx
    │   └── DetectiveForm.test.tsx
    └── hooks/
```

**Structure Decision**: Web application (Backend + Frontend) 구조 사용. 기존 LEH 아키텍처 유지하며 신규 API 엔드포인트와 컴포넌트 추가.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | 모든 Constitution 원칙 준수 | - |

## Implementation Phases

### Phase 1: 로그인/인증 버그 수정 (US1)
- 쿠키 cross-origin 설정 수정 (SameSite=None, Secure)
- 역할별 대시보드 리다이렉트 정상화
- 페이지 새로고침 시 인증 상태 유지
- E2E 테스트로 검증

### Phase 2: 알림 드롭다운 구현 (FR-007)
- Backend: Notification 모델 및 API
- Frontend: NotificationDropdown 컴포넌트
- 알림 유형: case_update, message, system

### Phase 3: 메시지 CRUD (FR-008)
- Backend: Message 모델 및 CRUD API
- Frontend: 메시지 목록, 상세, 작성, 삭제 UI
- API 클라이언트 및 훅 구현

### Phase 4: 의뢰인/탐정 관리 (FR-009~016)
- Backend: Client, Detective 모델 및 CRUD API
- Frontend: 추가/수정 폼, 목록 UI
- 케이스 연결은 별도 기능으로 분리

### Phase 5: Dashboard 접근권한 (FR-013)
- middleware.ts 역할 체크 로직 검증
- RoleGuard 컴포넌트 동작 확인
- 페이지 렌더링 오류 디버깅

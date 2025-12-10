# Implementation Plan: MVP 구현 갭 해소 (Production Readiness)

**Branch**: `009-mvp-gap-closure` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-mvp-gap-closure/spec.md`

## Summary

Production readiness를 위한 MVP 갭 해소. 현재 구현 상태 분석 결과:
- **AI Worker**: Lambda 코드 100% 완성, S3 권한 설정만 필요
- **Backend RAG/Draft**: 90-95% 완성, 실제 기능 구현됨 (mock 아님)
- **Frontend 에러 처리**: 기본 구조 존재, 일관성 개선 필요
- **CI 테스트**: 실행 중이나 integration 테스트 스킵, 커버리지 65% (목표 80%)

핵심 작업: S3 권한 설정, CI 커버리지 상향, Frontend 에러 처리 통일, 배포 파이프라인 완성

## Technical Context

**Language/Version**: Python 3.11+ (Backend/AI Worker), TypeScript (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, AWS Lambda, OpenAI (GPT-4o, Whisper, Vision), Qdrant, boto3, TipTap/Quill (draft editor)
**Storage**: PostgreSQL (RDS), AWS S3, DynamoDB, Qdrant Cloud
**Testing**: pytest (backend/ai_worker, 65% threshold), Jest (frontend), Playwright (E2E)
**Target Platform**: AWS (Lambda, S3, CloudFront, DynamoDB, ECR)
**Project Type**: Web application (frontend + backend + ai_worker)
**Performance Goals**: 5min AI analysis, 2sec RAG search, 30sec Draft generation
**Constraints**: JWT auth (HTTP-only cookies), RBAC, Case isolation (`case_rag_{case_id}`), 500MB max file size
**Scale/Scope**: MVP with 6 user stories, 22 functional requirements, 3 NFRs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Evidence Integrity (NON-NEGOTIABLE) | ✅ PASS | SHA-256 hash, audit_logs 테이블 존재, 모든 CRUD 로깅 |
| II. Case Isolation (NON-NEGOTIABLE) | ✅ PASS | Qdrant `case_rag_{case_id}` 패턴 사용, cross-case 쿼리 방지 |
| III. No Auto-Submit (NON-NEGOTIABLE) | ✅ PASS | Draft는 "Preview Only", 수동 승인 필요 |
| IV. AWS-Only Data Storage | ✅ PASS | S3, DynamoDB, Qdrant on AWS, 외부 저장소 없음 |
| V. Clean Architecture | ✅ PASS | Routers → Services → Repositories 패턴 준수 |
| VI. Branch Protection | ✅ PASS | PR 기반 워크플로우, main/dev 직접 푸시 금지 |
| VII. TDD Cycle | ⚠️ PARTIAL | 테스트 존재하나 TDD 사이클 문서화 부족 |
| VIII. Semantic Versioning | ✅ PASS | v0.1.0 태그 존재, 배포 파이프라인 구성됨 |

**Gate Result**: PASS (No NON-NEGOTIABLE violations)

## Project Structure

### Documentation (this feature)

```text
specs/009-mvp-gap-closure/
├── plan.md              # This file
├── spec.md              # Feature specification (clarified)
├── research.md          # Phase 0 output - 현재 구현 상태 분석
├── data-model.md        # Phase 1 output - AuditLog, CaseMember 스키마
├── quickstart.md        # Phase 1 output - 로컬 개발 가이드
├── contracts/           # Phase 1 output - API 계약
│   ├── search-api.yaml  # RAG 검색 API
│   ├── draft-api.yaml   # Draft Preview API
│   └── audit-api.yaml   # Audit Log API
├── checklists/          # Requirements quality checklists
│   └── mvp-readiness.md # 63-item checklist
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
# Web application structure (existing)
backend/
├── app/
│   ├── api/             # Route handlers (cases.py, search.py, drafts.py)
│   ├── core/            # Config, security, dependencies
│   ├── db/              # SQLAlchemy models, schemas
│   ├── middleware/      # Security headers, error handlers
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic (draft_service.py, search_service.py)
│   └── utils/           # S3, DynamoDB, Qdrant, OpenAI clients
└── tests/
    ├── contract/        # API contract tests
    ├── integration/     # End-to-end tests (currently skipped in CI)
    └── unit/            # Unit tests

ai_worker/
├── handler.py           # Lambda entry point
├── src/
│   ├── parsers/         # File type parsers (complete)
│   ├── analysis/        # Article 840 tagger, summarizer
│   ├── storage/         # DynamoDB, Qdrant storage
│   └── search/          # Hybrid search
└── tests/               # 48 test files

frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   ├── components/      # React components (ErrorBoundary exists)
│   ├── contexts/        # AuthContext with error handling
│   ├── hooks/           # Custom hooks (need consistency)
│   └── lib/api/         # API client with 401 handling
└── __tests__/           # Jest tests
```

**Structure Decision**: Existing web application structure maintained. No new directories required.

## Complexity Tracking

> No Constitution Check violations requiring justification.

## Current Implementation Analysis

### AI Worker (US1) - 100% Code Complete

| Component | Status | Notes |
|-----------|--------|-------|
| handler.py | ✅ Complete | S3 event routing, idempotency, job tracking |
| Text/PDF Parser | ✅ Complete | UTF-8, CSV, JSON, KakaoTalk auto-detect |
| Audio/Video Parser | ✅ Complete | Whisper STT, ffmpeg extraction |
| Image Parser | ✅ Complete | GPT-4o Vision, OCR, emotion detection |
| DynamoDB Storage | ✅ Complete | Full CRUD, GSI, idempotency |
| Qdrant Storage | ✅ Complete | Case isolation, payload indexes |
| Dockerfile.lambda | ✅ Complete | Python 3.12 base |

**Blocker**: S3 버킷 권한 설정 필요 (IAM role에 s3:GetObject, s3:PutObject)

### Backend RAG/Draft (US2) - 90% Complete

| Component | Status | Notes |
|-----------|--------|-------|
| GET /search | ✅ Complete | Multi-category search with access control |
| POST /cases/{id}/draft-preview | ✅ Complete | RAG + GPT-4o integration |
| GET /cases/{id}/draft-export | ✅ Complete | DOCX/PDF generation |
| DraftService | ✅ Complete | 1,192 lines, full implementation |
| SearchService | ✅ Complete | 349 lines, case/client/evidence/event search |
| Qdrant client | ✅ Complete | 478 lines, semantic search + legal knowledge |
| OpenAI client | ✅ Complete | 150 lines, GPT-4o + embeddings |

**Gap**: Search history storage (returns empty list), Rich text editor integration (FR-007a)

### Frontend Error Handling (US3) - 70% Complete

| Component | Status | Notes |
|-----------|--------|-------|
| 401 handling | ✅ Complete | Redirect to /login, loop prevention |
| Network error | ⚠️ Partial | Returns status 0, no toast notification |
| Loading states | ⚠️ Partial | Inconsistent naming (isLoading vs isPolling) |
| Error boundaries | ✅ Complete | Role-specific error components |
| Retry mechanism | ❌ Missing | No automatic retry, no exponential backoff |
| Toast notifications | ❌ Missing | Inline errors only |

### CI Tests (US4) - 65% Coverage

| Component | Status | Notes |
|-----------|--------|-------|
| Frontend tests | ✅ Running | Jest, no coverage threshold |
| Backend tests | ✅ Running | pytest, 65% threshold (target: 80%) |
| AI Worker tests | ✅ Running | pytest, 65% threshold (target: 80%) |
| Integration tests | ❌ Skipped | `-m "not integration"` in CI |
| E2E tests | ⚠️ Non-blocking | Playwright, `continue-on-error: true` |

### Permissions (US5) - 80% Complete

| Component | Status | Notes |
|-----------|--------|-------|
| case_members table | ✅ Exists | OWNER/MEMBER/VIEWER roles |
| Permission middleware | ✅ Exists | get_current_user_id dependency |
| Audit logging | ⚠️ Partial | Exists but not all APIs use it |
| 403 on unauthorized | ⚠️ Partial | Some APIs may return 404 instead |

### Deployment Pipeline (US6) - 70% Complete

| Component | Status | Notes |
|-----------|--------|-------|
| CI workflow | ✅ Active | ci.yml, tests + lint |
| Backend deploy | ✅ Active | ECR + Lambda update |
| Frontend deploy | ✅ Active | S3 + CloudFront |
| AI Worker deploy | ❌ Disabled | `&& false` condition in workflow |
| Staging environment | ✅ Configured | dev branch → staging |
| Production environment | ✅ Configured | main branch → production |
| Rollback | ❌ Missing | No automated rollback mechanism |

## Implementation Priority

Based on spec priorities and current implementation state:

### P1 - Critical (Must complete for MVP)

1. **S3 IAM Permission Setup** (US1)
   - Create S3 buckets: `leh-evidence-dev`, `leh-evidence-prod`
   - Attach S3 permissions to Lambda execution role
   - Configure S3 event notification for `cases/*/raw/*`
   - **Effort**: Low (AWS Console/CLI, no code)

2. **AI Worker Deploy Enable** (US1/US6)
   - Remove `&& false` from deploy_paralegal.yml
   - Verify Dockerfile.lambda exists
   - **Effort**: Low (1 line change)

### P2 - Important (Quality & UX)

3. **Frontend Error Handling Unification** (US3)
   - Add toast notification system (react-hot-toast)
   - Unify loading state naming
   - Add retry mechanism with exponential backoff
   - **Effort**: Medium

4. **Rich Text Editor Integration** (US2)
   - Add TipTap/Quill editor component
   - Integrate with draft preview page
   - **Effort**: Medium

5. **CI Coverage Increase** (US4)
   - Increase `--cov-fail-under` from 65 to 70 in pytest.ini
   - Add missing unit tests to meet threshold
   - **Effort**: Medium-High

6. **Permission Middleware Audit** (US5)
   - Review all `/cases/*`, `/evidence/*` APIs
   - Ensure 403 (not 404) on unauthorized access
   - Add audit_logs writes for all access attempts
   - **Effort**: Medium

### P3 - Nice to Have

7. **Rollback Mechanism** (US6)
   - Document manual rollback procedure
   - Consider automated rollback on health check failure
   - **Effort**: Medium

8. **Observability Setup** (NFR)
   - Enable CloudWatch structured logging
   - Configure Lambda metrics collection
   - Add API latency tracking
   - **Effort**: Low-Medium

## Generated Artifacts

Phase 0:
- [research.md](./research.md) - Implementation state analysis

Phase 1:
- [data-model.md](./data-model.md) - Entity schemas
- [contracts/](./contracts/) - API contracts
- [quickstart.md](./quickstart.md) - Local development guide

Phase 2:
- [tasks.md](./tasks.md) - Implementation tasks (via /speckit.tasks)

## Next Steps

1. Review generated artifacts
2. Run `/speckit.tasks` to generate actionable task list
3. Begin implementation with P1 items (S3 permissions, AI Worker deploy)

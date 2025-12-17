# Implementation Plan: MVP 구현 갭 해소 (Production Readiness)

**Branch**: `009-mvp-gap-closure` | **Date**: 2025-12-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-mvp-gap-closure/spec.md`

## Summary

Close the implementation gap between enterprise-grade documentation and actual production code. Key deliverables:
1. **AI Worker**: Enable S3 permissions for Lambda trigger (code complete, blocked on IAM)
2. **Backend**: Implement RAG search and Draft Preview APIs with case permission middleware
3. **Frontend**: Unify error handling with react-hot-toast (toast for network errors, inline for validation)
4. **CI**: Fix test skip logic to achieve 65%+ coverage in CI runs

## Technical Context

**Language/Version**: Python 3.11+ (Backend/AI Worker), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, boto3, qdrant-client, openai, react-hot-toast
**Storage**: PostgreSQL (RDS), AWS S3, DynamoDB, Qdrant Cloud
**Testing**: pytest (Backend/AI Worker 80% target), Jest + RTL (Frontend), Playwright (E2E)
**Target Platform**: AWS (Lambda, S3, RDS, CloudFront)
**Project Type**: Web application (frontend + backend + ai_worker)
**Performance Goals**: RAG search <2s, Draft Preview <30s, AI analysis <5min
**Constraints**: 500MB max file upload, JWT 24h expiry, S3 presigned URL 5min expiry
**Scale/Scope**: MVP launch, single AWS region (ap-northeast-2)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Implementation Notes |
|-----------|--------|---------------------|
| I. Evidence Integrity | ✅ PASS | SHA-256 hashing on upload, audit_logs for all CRUD |
| II. Case Isolation | ✅ PASS | `case_rag_{case_id}` collection pattern in Qdrant, FR-014 permission middleware |
| III. No Auto-Submit | ✅ PASS | Draft Preview is "Preview Only", lawyer must manually approve |
| IV. AWS-Only Storage | ✅ PASS | S3, DynamoDB, Qdrant on EC2/Cloud - no external storage |
| V. Clean Architecture | ✅ PASS | Routers→Services→Repositories pattern, dedicated repositories per entity |
| VI. Branch Protection | ✅ PASS | PR workflow required for main/dev, FR-017/FR-018 enforce this |
| VII. TDD Cycle | ✅ PASS | Tests specified in FR-011/12/13, TDD required per constitution |
| VIII. Semantic Versioning | ✅ PASS | Release tags with vX.Y.Z format |

**Gate Result**: ✅ ALL PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/009-mvp-gap-closure/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── search-api.yaml
│   ├── draft-api.yaml
│   └── permission-api.yaml
└── tasks.md             # Phase 2 output (existing, to be updated)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/              # Routers: auth.py, cases.py, evidence.py, search.py, drafts.py
│   ├── core/             # Config, security, dependencies
│   ├── db/               # SQLAlchemy models, schemas
│   ├── middleware/       # Permission check, error handlers
│   ├── repositories/     # case_repository.py, evidence_repository.py, audit_repository.py
│   ├── services/         # case_service.py, search_service.py, draft_service.py
│   └── utils/            # s3.py, dynamo.py, qdrant.py, openai_client.py
└── tests/
    ├── contract/         # API contract tests
    ├── integration/      # Full endpoint tests
    └── unit/             # Service/repository unit tests

frontend/
├── src/
│   ├── app/              # Next.js 14 App Router pages
│   ├── components/       # React components
│   ├── hooks/            # useAuth, useCase, useEvidence, useToast
│   ├── lib/              # API client, error handling
│   └── types/            # TypeScript definitions
└── src/__tests__/        # Jest tests

ai_worker/
├── handler.py            # Lambda entry point
├── src/
│   ├── parsers/          # File type parsers
│   ├── analysis/         # Summarizer, tagger, scorer
│   └── storage/          # DynamoDB, Qdrant storage
└── tests/                # pytest tests
```

**Structure Decision**: Web application with three-tier architecture. AI Worker is deployed as Lambda, Backend as ECS/EC2, Frontend as S3+CloudFront static export.

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Three separate projects | Required | AI Worker (Lambda), Backend (API), Frontend (static) have different deployment targets |
| Manual AWS setup | Chosen | Terraform out of scope per spec assumptions; AWS CLI for S3/IAM |

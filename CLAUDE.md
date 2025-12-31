# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CHAGOK is an AI-powered paralegal system for divorce cases. The platform processes legal evidence (images, audio, video, text, PDFs) using AWS infrastructure, analyzes them with AI, and generates draft legal documents.

**Architecture:** Three-tier AWS system with Next.js frontend, FastAPI backend, and Lambda-based AI Worker pipeline.

**Key Constraint:** All evidence data stays within AWS (S3/DynamoDB/Qdrant). No Google Drive or external storage.

## ABSOLUTE RULES (절대규칙)

These rules must NEVER be violated under any circumstances:

1. **NEVER push directly to main or dev branches**
   - All changes to `main` and `dev` must go through Pull Requests only
   - Direct `git push origin main` or `git push origin p-work:main` is FORBIDDEN
   - Direct `git push origin dev` or `git push origin p-work:dev` is FORBIDDEN

2. **Branch update workflow**
   ```
   p-work → PR → dev (staging deployment)
   dev → PR → main (production deployment)
   ```

3. **Deployment environments**
   - `main` branch → **Production** (CloudFront production)
   - `dev` branch → **Staging** (CloudFront staging)
   - Both environments must be maintained separately

4. **Before any git push, always verify:**
   - You are NOT pushing to main or dev directly
   - You are pushing to your working branch (e.g., p-work, feat/*)

5. **GitHub Issue Assignees (역할별 필수 배정)**
   - 이슈 생성 시 담당 영역에 따라 assignee 지정:
     - **AI Worker** (`ai_worker/`, AWS Lambda, S3, DynamoDB, Qdrant): `vsun410` (L)
     - **Backend** (`backend/`, FastAPI, API, Services): `leaf446` (H)
     - **Frontend** (`frontend/`, Next.js, React, UI): `Prometheus-P` (P)
   - 여러 영역에 걸친 이슈는 해당 담당자 모두 배정
   - gh CLI 예시:
     - AI Worker: `--assignee vsun410`
     - Backend: `--assignee leaf446`
     - Frontend: `--assignee Prometheus-P`

6. **테스트 환경 (Testing Environment)**
   - 사용자가 "테스트"를 요청하면 **항상 Staging 서버**에서 테스트
   - **Staging URL**: `https://dpbf86zqulqfy.cloudfront.net/`
   - 로컬 서버 실행하지 말 것 (uvicorn, npm run dev 등)
   - API 테스트 시 staging API 엔드포인트 사용

7. **커밋 메시지 규칙 (Commit Message Rules)**
   - 커밋 메시지에 다음 내용 절대 포함 금지:
     - `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
     - `Co-Authored-By: Claude` 또는 유사 AI 귀속 문구
   - 커밋 메시지는 순수하게 변경 내용만 기술

## Common Development Commands

### Quick Start (Makefile)
```bash
make setup              # Install all dependencies
make dev-backend        # Run Backend (http://localhost:8000)
make dev-frontend       # Run Frontend (http://localhost:3000)
make test               # Run all tests
make lint               # Run all linters
make clean              # Remove venvs and node_modules
make help               # Show all commands
```

### Backend (FastAPI)
```bash
cd backend
uvicorn app.main:app --reload            # Dev server
pytest                                    # All tests
pytest tests/test_api/                   # API tests only
pytest -m unit                           # Unit tests only
pytest -k test_auth                      # Specific test pattern
pytest --cov=app --cov-report=html       # With coverage

# Database migrations (Alembic)
alembic upgrade head                     # Apply migrations
alembic revision --autogenerate -m "msg" # Create new migration
```

### AI Worker (Lambda/Local)
```bash
cd ai_worker
python -m handler                        # Run locally
pytest                                   # All tests (80% coverage required)
pytest --cov=src --cov-report=term-missing
```

### Frontend (Next.js)
```bash
cd frontend
npm run dev                              # Dev server (http://localhost:3000)
npm run build && npm start               # Production build
npm test                                 # Jest tests
npm run lint                             # ESLint
```

## High-Level Architecture

### Data Flow: Evidence Processing Pipeline
```
1. Frontend → Backend: Request presigned S3 URL
2. Frontend → S3: Direct upload via presigned URL
3. S3 Event → AI Worker (Lambda): Automatic trigger on upload
4. AI Worker → OpenAI: STT/OCR/Vision/Embedding
5. AI Worker → DynamoDB: Store structured evidence metadata
6. AI Worker → Qdrant: Store embeddings for RAG (case_rag_{case_id})
7. Backend → DynamoDB/Qdrant: Query evidence data
8. Backend → Frontend: Return evidence timeline/search results
```

### Draft Preview Generation Flow
```
1. Frontend → Backend: POST /cases/{id}/draft-preview
2. Backend → DynamoDB: Fetch case evidence metadata
3. Backend → Qdrant: RAG search for relevant evidence
4. Backend → GPT-4o: Generate draft with evidence citations
5. Backend → Frontend: Return draft preview (no auto-submit)
```

### Key Architecture Principles
- **Case Isolation:** Each case has isolated RAG index (`case_rag_{case_id}`) in Qdrant
- **Stateless Backend:** All state in RDS/DynamoDB/Qdrant, API is stateless
- **Event-Driven AI:** AI Worker triggered by S3 events, not backend API calls
- **Evidence Integrity:** SHA-256 hashing, Chain of Custody, Audit logs in RDS

## Repository Structure Pattern

### Backend Structure (Clean Architecture)
```
backend/app/
├── api/              # Route handlers (auth.py, cases.py, evidence.py)
├── core/             # Config, security, dependencies
├── db/               # SQLAlchemy models, schemas, session
├── middleware/       # Security headers, error handlers
├── repositories/     # Data access layer (case_repository.py, user_repository.py)
├── services/         # Business logic (case_service.py, evidence_service.py, draft_service.py)
└── utils/            # Helpers (s3.py, dynamo.py, qdrant.py, openai_client.py)
```

**Pattern:** Routers → Services → Repositories → DB/External Services
- Routers handle HTTP concerns only
- Services contain business logic
- Repositories handle data persistence
- Utils are stateless helpers

### AI Worker Structure (Parser Pattern)
```
ai_worker/
├── handler.py              # Lambda entry point (S3 event routing)
├── src/
│   ├── parsers/            # Type-specific parsers (text.py, image_ocr.py, image_vision.py, audio_parser.py, video_parser.py, pdf_parser.py)
│   ├── analysis/           # Analysis engines (summarizer.py, article_840_tagger.py, evidence_scorer.py, risk_analyzer.py)
│   ├── service_rag/        # Legal knowledge RAG (legal_parser.py, legal_vectorizer.py, legal_search.py)
│   ├── user_rag/           # Case-specific RAG (hybrid_search.py)
│   ├── storage/            # Persistence (metadata_store.py → DynamoDB, vector_store.py → Qdrant)
│   └── search/             # Search engines
```

**Pattern:** Strategy Pattern for parsers based on file extension
- `handler.py:route_parser()` selects appropriate parser
- Each parser returns standardized `ParsedMessage` objects
- Analysis engines process parsed results
- Storage layer persists to DynamoDB + Qdrant

### Frontend Structure (Next.js App Router)
```
frontend/src/
├── app/                # Next.js App Router pages
├── components/         # React components (organized by feature)
├── hooks/              # Custom React hooks (useAuth, useCase, useEvidence)
├── lib/                # Utilities and API clients
└── types/              # TypeScript type definitions
```

## Critical Implementation Details

### Authentication (Backend)
- JWT-based authentication with role-based access control (RBAC)
- Tokens stored in HTTP-only cookies (not localStorage)
- All API endpoints require JWT except `/auth/login`, `/health`, `/`
- Case-level permissions in `case_members` table (OWNER/MEMBER/VIEWER)

**Dependency:** Use `get_current_user_id()` from `app/core/dependencies.py`

```python
from app.core.dependencies import get_current_user_id

@router.get("/cases/{case_id}")
async def get_case(case_id: str, user_id: str = Depends(get_current_user_id)):
    # user_id is automatically extracted from JWT
```

### S3 Presigned URLs (Backend)
- Backend generates presigned URLs via `app/utils/s3.py:generate_presigned_upload_url()`
- Frontend uploads directly to S3 (backend never handles file content)
- S3 path pattern: `s3://leh-evidence/cases/{case_id}/raw/{evidence_id}_{filename}`
- Presigned URLs valid for 5 minutes only

### AI Worker Parsers
Each parser must:
1. Inherit from `src/parsers/base.py:BaseParser`
2. Implement `parse(file_path: str) -> List[ParsedMessage]`
3. Return list of `ParsedMessage` with `content`, `sender`, `timestamp`, `metadata`
4. Handle file cleanup in `/tmp` (Lambda environment)

**File Type Routing:**
- Images (.jpg, .png): `ImageVisionParser` (GPT-4o Vision for context/emotion)
- Audio (.mp3, .wav): `AudioParser` (Whisper STT + diarization)
- Video (.mp4, .avi): `VideoParser` (audio extraction → Whisper)
- PDF (.pdf): `PDFParser` (text extraction + OCR fallback)
- Text (.txt, .csv): `TextParser` (KakaoTalk format detection)

### Database Models (Backend)
**Key Tables in RDS PostgreSQL:**
- `users` - User accounts with role (lawyer/staff/admin)
- `cases` - Case metadata (title, status, assigned lawyer)
- `case_members` - Case access permissions
- `audit_logs` - Immutable audit trail

**DynamoDB Schema:**
```json
{
  "case_id": "partition_key",
  "evidence_id": "sort_key",
  "type": "image|audio|video|text|pdf",
  "timestamp": "ISO8601",
  "speaker": "원고|피고|제3자",
  "labels": ["폭언", "불륜", "유책사유"],
  "s3_key": "cases/123/raw/file.jpg",
  "ai_summary": "분석 요약",
  "qdrant_id": "case_123_ev_1"
}
```

### Qdrant Collection Naming
- Pattern: `case_rag_{case_id}` (e.g., `case_rag_123`)
- Each case has isolated collection (deleted on case closure)
- Documents include embedding vector for semantic search
- Backend queries via `app/utils/qdrant.py`

### Error Handling Pattern
Backend uses custom exception handlers in `app/middleware/error_handler.py`:
- `HTTPException` → Standard FastAPI errors
- `ValueError` → 400 Bad Request
- `PermissionError` → 403 Forbidden
- `KeyError` → 404 Not Found
- All errors return JSON: `{"detail": "message", "status_code": 400}`

## Environment Variables

CHAGOK uses a **unified `.env` file** at the project root. Each service directory has a symlink pointing to this root file:

```
project-root/
├── .env                  # Unified environment variables (actual file)
├── .env.example          # Template for new setups
├── backend/.env          # → symlink to ../.env
├── ai_worker/.env        # → symlink to ../.env
└── frontend/.env         # → symlink to ../.env
```

### Setup
```bash
cp .env.example .env
# Edit .env with your values
```

### Key Variables (see `.env.example` for full list):
```bash
# Shared
AWS_REGION=ap-northeast-2
OPENAI_API_KEY=sk-...
S3_EVIDENCE_BUCKET=leh-evidence-dev
QDRANT_HOST=localhost

# Backend specific
DATABASE_URL=sqlite:///./leh_local.db
JWT_SECRET=local-dev-secret-change-in-prod-min-32-chars

# DynamoDB (both names for compatibility)
DDB_EVIDENCE_TABLE=leh_evidence_dev      # Backend
DYNAMODB_TABLE=leh_evidence_dev          # AI Worker

# Frontend (must start with NEXT_PUBLIC_)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Never commit `.env` files to git. See [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) for details.

## Testing Strategy

### Backend Tests
- **Unit tests** (`-m unit`): Test services/repositories with mocked dependencies
- **Integration tests** (`-m integration`): Test full API endpoints with test DB
- Test fixtures in `backend/tests/conftest.py`
- Use `TestClient` from `fastapi.testclient` for API testing

### AI Worker Tests
- **Unit tests**: Test individual parsers with sample files
- **Integration tests**: Test end-to-end pipeline (S3 → DynamoDB → Qdrant)
- Coverage requirement: 80% minimum (`--cov-fail-under=80`)
- Test fixtures in `ai_worker/conftest.py`

### Frontend Tests
- Jest + React Testing Library
- Test components in isolation
- Mock API calls using `jest.mock()`

## Git Workflow

**Branch Strategy:**
```
main ← dev ← feat/*
```

- `main`: Production-ready code, PR required from dev
- `dev`: Active development, H/L/P can push directly (after tests pass)
- `feat/*`: Feature branches, merge to dev when complete

**PR Rules:**
- Direction: Always `dev → main`
- Minimum 1 reviewer (P is primary approver)
- Use PR template from `.github/PULL_REQUEST_TEMPLATE.md`
- Tests must pass before merge

**Documentation-only exception:**
- Changes to `docs/*.md`, `README.md`, `CONTRIBUTING.md` can be pushed directly to main
- Code changes must always go through PR

## Legal/Compliance Considerations

1. **No Auto-Submit:** AI outputs are "Preview Only" - lawyers must manually review/edit
2. **Evidence Integrity:** All uploads get SHA-256 hash, stored in audit logs
3. **Case Isolation:** Each case's RAG index is isolated (no cross-case data leakage)
4. **Data Deletion:** On case closure, delete Qdrant collection, soft-delete DynamoDB records
5. **Audit Trail:** All CRUD operations logged in `audit_logs` table (immutable)

## Common Gotchas

1. **Backend DB Session:** Always use `Depends(get_db)` dependency injection, never create sessions manually
2. **AI Worker /tmp:** Lambda `/tmp` has 512MB limit, clean up files after processing
3. **JWT Expiry:** Access tokens valid 24h, refresh tokens 7 days
4. **CORS:** Frontend must be in `CORS_ORIGINS` env var (comma-separated)
5. **Qdrant Collection:** Create case collection before first evidence upload, delete on case closure
6. **S3 Event:** Lambda triggered on `s3:ObjectCreated:*` only for `cases/*/raw/*` prefix
7. **Alembic Migrations:** Always review auto-generated migrations before applying

## Key Files to Reference

- **Backend API Design:** `docs/specs/BACKEND_DESIGN.md`
- **AI Pipeline Design:** `docs/specs/AI_PIPELINE_DESIGN.md`
- **API Specification:** `docs/specs/API_SPEC.md`
- **System Architecture:** `docs/specs/ARCHITECTURE.md`
- **Collaboration Guide:** `docs/CONTRIBUTING.md`
- **Clean Architecture Guide:** `docs/guides/BACKEND_SERVICE_REPOSITORY_GUIDE.md`
- **Frontend Clean Code:** `docs/guides/FRONTEND_CLEAN_CODE.md`
- **Design Patterns:** `docs/guides/DESIGN_PATTERNS.md`
- **Folder Structure:** `docs/guides/FOLDER_STRUCTURE.md`
- **Testing Strategy:** `docs/guides/TESTING_STRATEGY.md`

## Quick Reference: File Locations

When implementing features, files typically go in:
- **New API endpoint:** `backend/app/api/{resource}.py`
- **Business logic:** `backend/app/services/{resource}_service.py`
- **Database query:** `backend/app/repositories/{resource}_repository.py`
- **New parser:** `ai_worker/src/parsers/{type}_parser.py`
- **Analysis engine:** `ai_worker/src/analysis/{analyzer}.py`
- **React component:** `frontend/src/components/{feature}/{Component}.tsx`
- **API client:** `frontend/src/lib/api/{resource}.ts`
- **Type definition:** `frontend/src/types/{resource}.ts`

## Technology Stack

### Core Technologies
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript 5.x, React 18, Tailwind CSS |
| Backend | FastAPI, Python 3.11+, SQLAlchemy |
| AI Worker | AWS Lambda, Python 3.11+, OpenAI (GPT-4o, Whisper, Vision) |
| Database | PostgreSQL (RDS), DynamoDB, Qdrant Cloud |
| Storage | AWS S3 |
| CDN | CloudFront |

### Key Libraries
- **Frontend**: React Flow (인물관계도), Recharts (차트), react-hot-toast (알림), jose (JWT), Lucide-React (아이콘)
- **Backend**: boto3 (AWS), qdrant-client, openai, python-docx (Word 생성)
- **AI Worker**: openai, boto3, qdrant-client

## Recent Changes

| Feature | Status | Summary |
|---------|--------|---------|
| 015-evidence-speaker-mapping | ✅ COMPLETE | 대화형 증거 화자 매핑 (카톡/문자 → 인물관계도 연결) |
| 012-precedent-integration | ✅ COMPLETE | 판례 검색 + 인물/관계 자동 추출 |
| 011-production-bug-fixes | 🔄 IN PROGRESS | Cookie auth 수정, 로그인 리다이렉트 개선 |
| 009-mvp-gap-closure | 📋 PLANNING | MVP 프로덕션 준비 (AI Worker 배포, 에러 핸들링) |

> Full changelog: See `docs/IMPLEMENTATION_STATUS.md`

## Future Development (추후 개발)
- **WCAG 접근성 지원**: Skip-to-content 링크, 키보드 네비게이션, 스크린 리더 지원 (현재 제거됨, 공공기관 납품 시 필요)

---

## AI Collaboration Guidelines

**Human verification REQUIRED for:**
- Security-related code (auth, permissions)
- Financial transaction logic
- Personal data processing code
- Irreversible operations
- External API integration code

**Before committing:**
- Review generated code personally
- Run tests (`make test`)
- Remove AI mentions from commit messages (see ABSOLUTE RULES #7)


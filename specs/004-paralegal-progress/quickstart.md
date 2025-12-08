# Quickstart: Paralegal Progress Dashboard

**Feature**: 004-paralegal-progress
**Date**: 2025-12-08

---

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL running (local or RDS)
- AWS credentials configured (for DynamoDB access)
- Backend environment configured (`backend/.env`)
- Frontend environment configured (`frontend/.env`)

---

## 1. Backend Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run Migrations (if schema changes)

```bash
alembic upgrade head
```

### Start Development Server

```bash
uvicorn app.main:app --reload
```

### Verify API Endpoint

```bash
# Get JWT token first (login as paralegal/lawyer)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "paralegal@example.com", "password": "password"}'

# Test progress endpoint
curl http://localhost:8000/api/v1/staff/progress \
  -H "Authorization: Bearer <token>"
```

Expected response:
```json
{
  "items": [...],
  "total_count": 5,
  "limit": 20,
  "offset": 0
}
```

---

## 2. Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Start Development Server

```bash
npm run dev
```

### Access Dashboard

Open http://localhost:3000/staff/progress (requires authentication)

---

## 3. Test Data Setup

### Seed Test Cases

```bash
cd backend
python -m scripts.seed_test_data
```

Or manually create via API:
```bash
# Create a case with paralegal assignment
curl -X POST http://localhost:8000/api/v1/cases \
  -H "Authorization: Bearer <lawyer_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Divorce Case",
    "client_name": "Test Client",
    "assigned_paralegal_id": "<paralegal_user_id>"
  }'
```

---

## 4. Key Files

### Backend

| File | Purpose |
|------|---------|
| `backend/app/api/staff_progress.py` | FastAPI router |
| `backend/app/services/progress_service.py` | Business logic |
| `backend/app/schemas/progress.py` | Pydantic DTOs |
| `backend/tests/test_services/test_progress_service.py` | Service tests |
| `backend/tests/test_api/test_staff_progress.py` | API tests |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/app/(dashboard)/staff/progress/page.tsx` | Dashboard page |
| `frontend/src/components/staff/ProgressCard.tsx` | Case card component |
| `frontend/src/components/staff/FeedbackChecklist.tsx` | Checklist component |
| `frontend/src/lib/api/staffProgress.ts` | API client |

---

## 5. Running Tests

### Backend Tests

```bash
cd backend

# Run all progress-related tests
pytest tests/test_services/test_progress_service.py tests/test_api/test_staff_progress.py -v

# With coverage
pytest tests/test_services/test_progress_service.py --cov=app/services/progress_service
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test -- --testPathPattern=staff/progress

# Run E2E tests (optional)
npm run test:e2e -- staff-progress.spec.ts
```

---

## 6. API Reference

### GET /staff/progress

Query Parameters:
- `blocked` (bool): Filter blocked cases only
- `assignee_id` (uuid): Filter by paralegal
- `status` (enum): Filter by case status
- `search` (string): Search title/client name
- `limit` (int): Page size (default 20, max 100)
- `offset` (int): Pagination offset

### GET /staff/progress/{case_id}/feedback

Returns 16 feedback checklist items for the case.

### PATCH /staff/progress/{case_id}/feedback

Update feedback item status.

Request body:
```json
{
  "item_id": "fbk-1",
  "status": "done",
  "notes": "Completed on 2025-12-08"
}
```

---

## 7. Troubleshooting

### API returns 401 Unauthorized
- Ensure JWT token is valid and not expired
- Check that user has paralegal or lawyer role

### API returns 403 Forbidden
- User doesn't have access to the requested cases
- Check case_members table for role assignment

### Evidence counts always show 0
- Verify DynamoDB table name in environment
- Check AWS credentials have read access

### AI status shows PENDING
- Verify Qdrant is running and accessible
- Check case_rag_{case_id} collection exists

---

## 8. Constitution Compliance

This feature adheres to all LEH Constitution principles:

- **I. Evidence Integrity**: Read-only aggregation, no mutations
- **II. Case Isolation**: Queries scoped by case_id
- **III. No Auto-Submit**: Dashboard is informational only
- **IV. AWS-Only Storage**: Uses existing AWS services
- **V. Clean Architecture**: Router → Service → Repository pattern
- **VII. TDD Cycle**: Tests written before implementation

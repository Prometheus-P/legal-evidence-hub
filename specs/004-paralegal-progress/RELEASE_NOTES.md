# Release Notes: Paralegal Progress Dashboard

**Version**: 1.0.0
**Date**: 2025-12-08
**Issue**: #92 - Paralegal progress page and mid-demo feedback

---

## Summary

This release introduces a staff-facing progress dashboard for paralegals and lawyers to monitor case throughput and track mid-demo feedback items. The dashboard aggregates data from PostgreSQL (cases), DynamoDB (evidence), and Qdrant (AI status) to provide a unified view of case progress.

---

## Features

### Case Progress Monitoring (US1)
- **Progress Dashboard** at `/staff/progress`
- Case cards displaying:
  - Case title and client name
  - Assigned paralegal
  - Evidence counts (uploaded, processing, AI-ready)
  - AI status badge (Pending, Processing, Draft Ready, Failed)
  - Last updated timestamp
- Responsive layout (2-column grid on desktop, single column on mobile)
- Manual refresh button for on-demand data updates
- Skeleton loaders during data fetch

### Mid-Demo Feedback Tracking (US2)
- 16 feedback checklist items per case from mid-demo review
- Collapsible accordion UI for checklist
- Pending count displayed as badge on each card
- Owner/team assignment for each item
- "Feedback Complete" banner when all items resolved

### Blocked Case Filter (US3)
- Filter toggle for blocked cases only
- Assignee filter dropdown
- Blocked reason indicators:
  - Missing evidence (>72h gap)
  - AI processing failure
  - Pending critical feedback
- Clear empty state when no blocked cases

---

## Technical Details

### Backend
- **New Router**: `backend/app/api/staff_progress.py`
- **New Service**: `backend/app/services/progress_service.py`
- **New Schemas**: `backend/app/schemas/progress.py`
- **API Endpoint**: `GET /staff/progress` with filter parameters

### Frontend
- **New Page**: `frontend/src/app/staff/progress/page.tsx`
- **New Components**:
  - `ProgressCard.tsx`
  - `FeedbackChecklist.tsx`
  - `ProgressFilters.tsx`
- **New API Client**: `frontend/src/lib/api/staffProgress.ts`

### Observability
- CloudWatch Logs integration for API latency metrics
- Structured JSON logging format
- Fail-fast error handling (0 retries) with manual retry button

---

## Test Coverage

### Backend Tests
- 11 tests in `test_progress_service.py` and `test_staff_progress.py`
- Coverage includes:
  - Happy path with multiple cases
  - Empty assignments
  - Evidence count aggregation
  - AI status fallback
  - Filter validation
  - RBAC enforcement

### Frontend Tests
- 5 tests in `page.test.tsx`
- Coverage includes:
  - Loading state
  - Success state with data
  - Empty state
  - Error handling
  - Filter interactions

---

## Breaking Changes

None. This is a new feature with no impact on existing functionality.

---

## Dependencies

No new dependencies added. Uses existing stack:
- FastAPI (backend)
- React Query (frontend)
- Tailwind CSS (styling)

---

## Related Issues

- **#92**: Paralegal progress page and mid-demo feedback (primary)
- **#91**: Test coverage improvements (related - this feature contributes to overall coverage)

---

## Deployment Notes

1. No database migrations required
2. Checklist data loaded from static JSON (`contracts/checklist.json`)
3. RBAC already configured for paralegal/lawyer roles
4. CloudWatch Logs integration uses existing AWS configuration

---

## Known Limitations

- Checklist persistence is per-session only (static JSON source)
- AI status requires Qdrant collection to exist for the case
- Manual refresh required for real-time updates (no WebSocket)

---

## Next Steps

- [ ] T603: Complete manual QA checklist with seeded data
- [ ] T604: Capture screenshots/video for demo presentation
- Consider: Persistent checklist storage in PostgreSQL (future enhancement)

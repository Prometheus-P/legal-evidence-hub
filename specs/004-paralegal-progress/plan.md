# Implementation Plan: Paralegal Progress Dashboard

**Branch**: `004-paralegal-progress` | **Date**: 2025-12-08 | **Spec**: `/specs/004-paralegal-progress/spec.md`
**Input**: Feature specification describing the paralegal progress dashboard and mid-demo feedback tracking.
**Status**: Phase 1 Complete (ready for tasks.md execution)

## Summary

We will deliver a staff-facing dashboard that aggregates case-progress signals (status, evidence counts, AI processing stage) and visualizes completion of the 16 mid-demo feedback items per case. Backend work introduces a dedicated service + API endpoint returning `CaseProgressSummary` objects with nested `FeedbackChecklistItem`s. Frontend work adds a Next.js App Router page at `/staff/progress`, React Query hook, and UI components (case cards, checklist drawer, filters). Tests cover the new service (FastAPI + pytest) and the UI (React Testing Library + optional Playwright smoke).

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy, boto3, Next.js 14, React Query, Tailwind CSS  
**Storage**: PostgreSQL (cases, users), DynamoDB (evidence metadata), Qdrant (AI status references)  
**Testing**: pytest, pytest-asyncio, Jest + React Testing Library, Playwright (optional)  
**Target Platform**: AWS-backed FastAPI service + CloudFront-hosted Next.js dashboard  
**Project Type**: Web (backend + frontend)  
**Performance Goals**: `/staff/progress` endpoint <400ms P95, page renders <2s with up to 200 cases  
**Constraints**: Respect Clean Architecture (routers→services→repositories), RBAC enforcement, no cross-case leakage (Case Isolation), preserve AWS-only storage  
**Scale/Scope**: Initial release targets paralegals/lawyers (≤50 concurrent users, ≤500 active cases)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | ✅ | Read-only aggregation; does not mutate evidence hashes. |
| II. Case Isolation | ✅ | Service queries remain scoped per case_id; no cross-case AI payload mixing. |
| III. No Auto-Submit | ✅ | Dashboard is informational only. |
| IV. AWS-Only Data Storage | ✅ | Uses existing AWS stores via services. |
| V. Clean Architecture | ✅ | Implemented via new service class + repository joins. |
| VII. TDD Cycle | ✅ | Tests planned before implementation (service tests + UI tests). |

## Project Structure

### Documentation

```text
specs/004-paralegal-progress/
├── spec.md
├── plan.md
├── research.md          # TBD if deeper spikes needed
├── data-model.md        # Outline DTO shapes if schema evolves
├── quickstart.md        # Integration instructions (optional)
└── tasks.md             # Detailed execution plan
```

### Source Code

```text
backend/
├── app/
│   ├── api/staff_progress.py        # new router
│   ├── services/progress_service.py # aggregation logic
│   ├── schemas/progress.py          # DTOs
│   └── repositories/                # reuse case/evidence repos
└── tests/
    ├── test_api/test_staff_progress.py
    └── test_services/test_progress_service.py

frontend/
├── src/
│   ├── app/(dashboard)/staff/progress/page.tsx
│   ├── components/staff/ProgressCard.tsx
│   ├── components/staff/FeedbackChecklist.tsx
│   └── lib/api/staffProgress.ts
└── tests/
    ├── unit/staff/progress-page.test.tsx
    └── e2e/staff-progress.spec.ts  # optional Playwright
```

**Structure Decision**: Use existing backend/frontend mono-repo layout (Option 2). New files plug into FastAPI router/service pattern and Next.js App Router.

## Complexity Tracking

No constitution violations introduced.

---

## Generated Artifacts (2025-12-08)

| Artifact | Path | Status |
|----------|------|--------|
| Research | `specs/004-paralegal-progress/research.md` | ✅ Complete |
| Data Model | `specs/004-paralegal-progress/data-model.md` | ✅ Complete |
| OpenAPI Contract | `specs/004-paralegal-progress/contracts/openapi.yaml` | ✅ Complete |
| Feedback Checklist | `specs/004-paralegal-progress/contracts/checklist.json` | ✅ Complete |
| Quickstart Guide | `specs/004-paralegal-progress/quickstart.md` | ✅ Complete |
| Task List | `specs/004-paralegal-progress/tasks.md` | ✅ Already exists |

### Clarifications Resolved

From `/speckit.clarify` session:
1. **Logging sink**: CloudWatch Logs (AWS native, structured JSON)
2. **SC-001 verification**: Manual QA checklist in T603
3. **Retry behavior**: 0 retries, fail fast with manual retry button

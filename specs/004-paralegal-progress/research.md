# Research: Paralegal Progress Dashboard

**Feature**: 004-paralegal-progress
**Date**: 2025-12-08
**Status**: Complete

---

## 1. Observability Strategy

### Decision
Use **CloudWatch Logs** with structured JSON format for API latency and UI load duration metrics.

### Rationale
- AWS-native solution aligns with Constitution Principle IV (AWS-Only Data Storage)
- No additional infrastructure required
- Integrates with existing backend logging patterns
- Supports CloudWatch Insights for query/analysis

### Alternatives Considered
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| StatsD/DataDog | Rich dashboards, alerting | External service, additional cost | Rejected |
| Console stdout | Simple, no config | Limited query, no retention | Rejected |
| File logging | Portable | Scaling issues, no aggregation | Rejected |

### Implementation Notes
- Backend: Use Python `logging` with JSON formatter
- Frontend: Use `performance.mark()` / `performance.measure()` + send to API endpoint
- Log format: `{"event": "api_latency", "endpoint": "/staff/progress", "duration_ms": 245, "timestamp": "..."}`

---

## 2. Error Handling / Retry Strategy

### Decision
**Fail fast** (0 automatic retries) with immediate error toast and manual retry button.

### Rationale
- Faster user feedback
- Clearer system state indication
- Aligns with edge case spec: "do not leave spinners forever"
- Manual retry empowers user control

### Alternatives Considered
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| 2 retries (1s delay) | Auto-recovery | Hidden delays | Rejected |
| 3 retries (exponential) | Robust | Confusing UX | Rejected |
| Fail fast + retry button | Fast feedback, clear | User effort | **Selected** |

### Implementation Notes
- React Query config: `retry: 0`
- Toast component with "Retry" action button
- Error state persists until user clicks retry

---

## 3. SC-001 Usability Verification

### Decision
Use **manual QA checklist** item in T603 (Phase 6 verification).

### Rationale
- Practical for initial launch
- No test infrastructure overhead
- Aligns with existing verification tasks in tasks.md
- Can upgrade to Playwright timer assertion later if needed

### Alternatives Considered
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Playwright timer | Automated | Complex setup | Deferred |
| User survey | Real-world data | Post-launch only | Deferred |
| Manual QA checklist | Immediate, simple | Manual effort | **Selected** |

---

## 4. Data Aggregation Strategy

### Decision
**Service-layer aggregation** with parallel data fetching from multiple sources.

### Rationale
- PostgreSQL: Cases, users, assignments
- DynamoDB: Evidence metadata, counts by status
- Qdrant: AI processing status (if available)
- Parallel fetching reduces latency (<400ms P95 target)

### Implementation Notes
- Use `asyncio.gather()` for parallel I/O
- Cache static data (checklist definitions) at service startup
- Avoid N+1 queries with batch fetching

---

## 5. Feedback Checklist Data Source

### Decision
**Static JSON file** for PoC, loaded at service initialization.

### Rationale
- 16 items are fixed for mid-demo
- No need for database persistence initially
- Simpler implementation
- Can migrate to Postgres table later if checklist becomes dynamic

### Data Source
- File: `specs/004-paralegal-progress/contracts/checklist.json`
- 16 items with id, title, description, owner

---

## 6. Frontend State Management

### Decision
Use **React Query (TanStack Query)** for server state management.

### Rationale
- Already used in codebase (003-role-based-ui)
- Built-in caching, refetching, error handling
- Optimistic updates if needed later
- Works well with manual refresh pattern

### Configuration
```typescript
const { data, error, refetch, isLoading } = useQuery({
  queryKey: ['staff-progress', filters],
  queryFn: () => fetchStaffProgress(filters),
  retry: 0,  // fail fast
  staleTime: 30_000,  // 30s before refetch
});
```

---

## 7. Pagination Strategy

### Decision
**Server-side pagination** with limit/offset for 50+ cases.

### Rationale
- Performance target: <500ms render per page
- Prevents loading all 500 cases at once
- Default page size: 20 cases
- Supports infinite scroll or traditional pagination

### API Parameters
- `?limit=20&offset=0`
- Response includes `total_count` for pagination UI

---

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Logging sink | CloudWatch Logs (AWS native) |
| Retry behavior | 0 retries, fail fast with manual retry |
| SC-001 verification | Manual QA checklist in T603 |
| Checklist persistence | Static JSON for PoC |

---

## Next Steps

1. Proceed to Phase 1: data-model.md
2. Generate API contracts in /contracts/
3. Create quickstart.md

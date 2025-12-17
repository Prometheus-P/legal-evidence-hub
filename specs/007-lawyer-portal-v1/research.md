# LEH Lawyer Portal v1 Research Notes

**Feature Branch**: `007-lawyer-portal-v1`
**Date**: 2025-12-08
**Purpose**: Document technical research and design decisions for implementation

---

## 1. React Flow Library Selection

### Decision
Use `@xyflow/react` v12.0.0 (formerly react-flow)

### Rationale
- Industry standard for node-based graph visualization in React
- Well-documented with TypeScript support
- Active maintenance (renamed from react-flow to @xyflow/react in v12)
- Built-in features: zoom, pan, minimap, node selection, edge connecting
- Supports custom node and edge components
- Performance: handles 1000+ nodes with virtualization

### Alternatives Considered
| Library | Rejected Because |
|---------|------------------|
| D3.js | Too low-level, requires more code for interactivity |
| vis.js | Less React-native, heavier bundle |
| react-d3-graph | Less customization for legal domain nodes |
| Cytoscape.js | Overkill for 50-node max, steeper learning curve |

### Best Practices for Implementation
1. Use controlled components (`nodes`, `edges` as state)
2. Implement custom nodes with `React.memo` for performance
3. Use `useCallback` for event handlers to prevent re-renders
4. Implement auto-layout using dagre for initial positioning
5. Store positions in database for persistence

---

## 2. Auto-Save Implementation

### Decision
Debounced auto-save with 2-3 second delay after last edit

### Rationale
- Prevents excessive API calls during rapid editing
- User expectation from modern tools (Figma, Notion)
- Reduces data loss risk from browser crashes
- Aligned with clarification session answer

### Implementation Pattern
```typescript
// hooks/useAutoSave.ts
import { useRef, useCallback, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';

interface UseAutoSaveOptions {
  debounceMs?: number;
  onSaveStart?: () => void;
  onSaveSuccess?: () => void;
  onSaveError?: (error: Error) => void;
}

export function useAutoSave<T>(
  saveFn: (data: T) => Promise<void>,
  options: UseAutoSaveOptions = {}
) {
  const { debounceMs = 2500 } = options;
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pendingDataRef = useRef<T | null>(null);

  const mutation = useMutation({
    mutationFn: saveFn,
    onMutate: options.onSaveStart,
    onSuccess: options.onSaveSuccess,
    onError: options.onSaveError,
  });

  const scheduleSave = useCallback((data: T) => {
    pendingDataRef.current = data;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      if (pendingDataRef.current) {
        mutation.mutate(pendingDataRef.current);
        pendingDataRef.current = null;
      }
    }, debounceMs);
  }, [debounceMs, mutation]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    scheduleSave,
    isSaving: mutation.isPending,
    saveError: mutation.error,
  };
}
```

### Save Status UI
```
┌─────────────────────────┐
│ 저장됨 ✓               │  (idle)
│ 저장 중... ⏳          │  (saving)
│ 저장 실패 ⚠️ [재시도]  │  (error)
└─────────────────────────┘
```

---

## 3. Authorization Model

### Decision
Reuse existing `case_members` table for party/asset/procedure authorization

### Rationale
- Consistency with existing APIs
- No new permission tables needed
- Lawyers familiar with OWNER/MEMBER/VIEWER model
- Aligned with clarification session answer

### Implementation
```python
# backend/app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from app.db.session import get_db
from sqlalchemy.orm import Session

async def verify_case_write_access(
    case_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> str:
    """Verify user has write access (OWNER or MEMBER) to case."""
    member = db.query(CaseMember).filter(
        CaseMember.case_id == case_id,
        CaseMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this case"
        )

    if member.role == 'VIEWER':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot modify party data"
        )

    return user_id

async def verify_case_read_access(
    case_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> str:
    """Verify user has any access to case."""
    member = db.query(CaseMember).filter(
        CaseMember.case_id == case_id,
        CaseMember.user_id == user_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this case"
        )

    return user_id
```

### Permission Matrix
| Role | Read | Create | Update | Delete |
|------|------|--------|--------|--------|
| OWNER | ✅ | ✅ | ✅ | ✅ |
| MEMBER | ✅ | ✅ | ✅ | ✅ |
| VIEWER | ✅ | ❌ | ❌ | ❌ |

---

## 4. Korean Property Division Legal Constraints

### Decision
Implement calculation as advisory only, never auto-submit

### Rationale
- Korean Civil Code Article 839-2 governs property division
- Courts have discretion; no fixed formula
- Calculation serves as starting point for lawyer analysis
- Aligned with Constitution Principle III (No Auto-Submit)

### Key Legal Concepts
| Concept | Korean Term | Implementation |
|---------|-------------|----------------|
| Separate Property | 특유재산 | `is_separate_property: boolean` |
| Joint Property | 공동재산 | `owner: 'joint'` |
| Contribution Rate | 기여율 | `contribution_plaintiff/defendant: 0-100` |
| Settlement Amount | 정산금 | Calculated field |
| Marriage Period | 혼인기간 | `start_date` on marriage relationship |

### Calculation Notes
- Default 50:50 split as starting point
- Contribution adjustment requires lawyer input
- Settlement = plaintiff_share - plaintiff_already_owns
- Negative settlement means defendant pays plaintiff

### Disclaimer Text (Required)
```
이 계산 결과는 참고용이며, 실제 재산분할 금액은 법원의 판단에 따라 달라질 수 있습니다.
변호사의 검토 없이 의뢰인에게 직접 전달하지 마십시오.
```

---

## 5. Concurrency Strategy

### Decision
Last-Write-Wins (LWW) with no conflict detection in v1

### Rationale
- Simplicity for MVP
- Typical use: single editor per case at a time
- Lawyers and paralegals work in shifts, not simultaneously
- Aligned with clarification session answer

### Future Consideration (v2)
- Add `updated_at` version check on save
- Show warning if server version newer than client
- Implement Operational Transform (OT) for real-time collaboration

---

## 6. Empty State UX

### Decision
Empty canvas with centered CTA button and instruction text

### Rationale
- Clear guidance for first-time users
- Reduces cognitive load
- Aligned with clarification session answer

### Design
```
┌────────────────────────────────────────────────┐
│                                                │
│                                                │
│      ┌──────────────────────────────┐         │
│      │                              │         │
│      │   📊 관계도가 비어 있습니다    │         │
│      │                              │         │
│      │  당사자를 추가하여 관계도를   │         │
│      │  시작하세요.                 │         │
│      │                              │         │
│      │  [+ 원고/피고 추가하기]       │         │
│      │                              │         │
│      └──────────────────────────────┘         │
│                                                │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 7. Node Performance Benchmark

### Requirement
Support up to 50 nodes with smooth rendering (SC-002)

### Research Findings
- React Flow handles 1000+ nodes with virtualization
- 50 nodes is well within comfortable range
- No special optimization needed for MVP

### Performance Checklist
- [ ] Use `React.memo` for custom node components
- [ ] Use `useCallback` for event handlers
- [ ] Avoid inline object creation in renders
- [ ] Test with 50 nodes before release

---

## 8. API Response Format

### Decision
Follow existing LEH API patterns

### Standard Response
```json
// Success (list)
{
  "items": [...],
  "total": 10
}

// Success (single)
{
  "id": "uuid",
  "case_id": "uuid",
  ...
}

// Error
{
  "detail": "Error message",
  "status_code": 400
}
```

### Pagination (if needed)
```
GET /cases/{id}/parties?limit=50&offset=0
```

---

## 9. Database Migration Strategy

### Decision
Single migration file per table, applied in dependency order

### Order
1. `party_nodes` (depends on `cases`)
2. `party_relationships` (depends on `party_nodes`)
3. `assets` (depends on `cases`) - v1 optional
4. `procedure_stages` (depends on `cases`) - v1 optional
5. `evidence_party_links` (depends on all above)

### Rollback Plan
```bash
# If issues during deployment
alembic downgrade -1  # Rollback last migration

# Or disable feature via flag
FEATURES.PARTY_GRAPH = false
```

---

## 10. Testing Strategy

### Backend Tests
| Type | Coverage Target | Focus |
|------|-----------------|-------|
| Unit | 90% | Service logic, calculator |
| Contract | 100% | API schemas |
| Integration | 80% | E2E API flows |

### Frontend Tests
| Type | Coverage Target | Focus |
|------|-----------------|-------|
| Unit | 80% | Hooks, utilities |
| Component | 70% | React components |
| E2E | Core flows | Happy path scenarios |

### TDD Approach (per Constitution VII)
1. Write failing test for API endpoint
2. Implement minimal code to pass
3. Refactor and add edge cases
4. Repeat for each endpoint

---

**END OF RESEARCH.md**

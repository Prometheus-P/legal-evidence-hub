# Data Model: Paralegal Progress Dashboard

**Feature**: 004-paralegal-progress
**Date**: 2025-12-08

---

## Entity Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CaseProgressSummary                            │
├─────────────────────────────────────────────────────────────────────────┤
│  case_id: str (PK)                                                      │
│  title: str                                                             │
│  client_name: str                                                       │
│  status: CaseStatus                                                     │
│  assigned_paralegal_id: str (FK → users.id)                             │
│  assigned_paralegal_name: str                                           │
│  evidence_counts: EvidenceCounts                                        │
│  ai_status: AIStatus                                                    │
│  is_blocked: bool                                                       │
│  blocked_reason: BlockedReason | None                                   │
│  outstanding_feedback_count: int                                        │
│  feedback_last_updated: datetime | None                                 │
│  last_updated_at: datetime                                              │
│  feedback_items: List[FeedbackChecklistItem] (lazy load)                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:N
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FeedbackChecklistItem                           │
├─────────────────────────────────────────────────────────────────────────┤
│  item_id: str (e.g., "fbk-1")                                           │
│  case_id: str (FK → cases.id)                                           │
│  title: str                                                             │
│  description: str                                                       │
│  status: ChecklistStatus (pending | done)                               │
│  owner: str (team/role)                                                 │
│  updated_at: datetime | None                                            │
│  notes: str | None                                                      │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           ProgressFilter                                │
├─────────────────────────────────────────────────────────────────────────┤
│  blocked: bool | None                                                   │
│  assignee_id: str | None                                                │
│  status: CaseStatus | None                                              │
│  search: str | None                                                     │
│  limit: int (default 20, max 100)                                       │
│  offset: int (default 0)                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Enumerations

### CaseStatus
```python
class CaseStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    CLOSED = "CLOSED"
```

### AIStatus
```python
class AIStatus(str, Enum):
    PENDING = "PENDING"          # No AI processing yet
    PROCESSING = "PROCESSING"    # AI Worker active
    DRAFT_READY = "DRAFT_READY"  # Draft preview available
    FAILED = "FAILED"            # AI processing error
```

### BlockedReason
```python
class BlockedReason(str, Enum):
    MISSING_EVIDENCE = "MISSING_EVIDENCE"      # Evidence gap >72h
    AI_FAILURE = "AI_FAILURE"                  # AI Worker error
    PENDING_FEEDBACK = "PENDING_FEEDBACK"      # Critical feedback incomplete
    CLIENT_WAITING = "CLIENT_WAITING"          # Awaiting client response
```

### ChecklistStatus
```python
class ChecklistStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
```

---

## Value Objects

### EvidenceCounts
```python
class EvidenceCounts(BaseModel):
    uploaded: int          # Total uploaded files
    in_processing: int     # Being processed by AI Worker
    ai_ready: int          # AI analysis complete
```

---

## Entity Details

### CaseProgressSummary

**Source**: Aggregated from PostgreSQL (cases, users) + DynamoDB (evidence) + Qdrant (AI status)

| Field | Type | Source | Constraints |
|-------|------|--------|-------------|
| case_id | str | cases.id | UUID format |
| title | str | cases.title | Max 200 chars |
| client_name | str | users.name (via client_id) | Max 100 chars |
| status | CaseStatus | cases.status | Enum value |
| assigned_paralegal_id | str | case_members.user_id | UUID, role=paralegal |
| assigned_paralegal_name | str | users.name | Denormalized for display |
| evidence_counts | EvidenceCounts | DynamoDB aggregation | Non-negative ints |
| ai_status | AIStatus | Qdrant collection status | Derived from latest record |
| is_blocked | bool | Computed | True if blocked_reason set |
| blocked_reason | BlockedReason? | Computed | See blocking logic |
| outstanding_feedback_count | int | Computed | Count of pending items |
| feedback_last_updated | datetime? | Max of item.updated_at | ISO8601 |
| last_updated_at | datetime | cases.updated_at | ISO8601 |
| feedback_items | List[FeedbackChecklistItem] | Loaded on demand | Max 16 items |

**Blocking Logic**:
```python
def compute_blocked_reason(case, evidence_counts, ai_status, feedback) -> BlockedReason | None:
    # 1. Evidence gap >72h
    if evidence_counts.uploaded == 0 and case.created_at < now() - 72h:
        return BlockedReason.MISSING_EVIDENCE

    # 2. AI failure
    if ai_status == AIStatus.FAILED:
        return BlockedReason.AI_FAILURE

    # 3. Critical feedback incomplete (owner=Eng or AI)
    critical_pending = [f for f in feedback if f.status == "pending" and f.owner in ("Eng", "AI")]
    if critical_pending:
        return BlockedReason.PENDING_FEEDBACK

    return None
```

### FeedbackChecklistItem

**Source**: Static JSON (contracts/checklist.json) + per-case completion state

| Field | Type | Source | Constraints |
|-------|------|--------|-------------|
| item_id | str | checklist.json | Format: "fbk-{n}" |
| case_id | str | Request context | UUID |
| title | str | checklist.json | Max 50 chars |
| description | str | checklist.json | Max 200 chars |
| status | ChecklistStatus | Database or computed | pending/done |
| owner | str | checklist.json | Team name (Eng, AI, Ops, etc.) |
| updated_at | datetime? | Database | When marked done |
| notes | str? | Database | User notes |

---

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  PostgreSQL │     │  DynamoDB   │     │   Qdrant    │
│   (cases)   │     │ (evidence)  │     │ (AI status) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────┬───────┴───────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │ ProgressService│
          │  (aggregation) │
          └────────┬───────┘
                   │
                   ▼
          ┌────────────────┐
          │   API Router   │
          │ /staff/progress│
          └────────┬───────┘
                   │
                   ▼
          ┌────────────────┐
          │    Frontend    │
          │  ProgressCard  │
          └────────────────┘
```

---

## Validation Rules

1. **case_id**: Must be valid UUID and user must have access (RBAC)
2. **evidence_counts**: All values >= 0
3. **outstanding_feedback_count**: 0-16 range
4. **limit**: 1-100, default 20
5. **offset**: >= 0

---

## State Transitions

### FeedbackChecklistItem Status
```
pending → done (user marks complete)
done → pending (user reopens)
```

Note: No automated state changes; all transitions are user-initiated.

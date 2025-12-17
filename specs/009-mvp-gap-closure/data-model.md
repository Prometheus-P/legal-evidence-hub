# Data Model: MVP 구현 갭 해소

**Date**: 2025-12-11
**Feature**: 009-mvp-gap-closure

## Overview

This document defines the data entities required for MVP production readiness. Entities are grouped by storage layer.

---

## PostgreSQL (RDS) Entities

### AuditLog

Immutable audit trail for all system actions (Constitution Principle I).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Unique identifier |
| user_id | UUID | FK → users, NOT NULL | Acting user |
| action | VARCHAR(50) | NOT NULL | Action type: CREATE, READ, UPDATE, DELETE, ACCESS_DENIED |
| resource_type | VARCHAR(50) | NOT NULL | Entity type: case, evidence, draft, user |
| resource_id | UUID | NOT NULL | Target entity ID |
| ip_address | VARCHAR(45) | NULLABLE | Client IP (IPv4/IPv6) |
| user_agent | VARCHAR(255) | NULLABLE | Browser/client info |
| metadata | JSONB | NULLABLE | Additional context (e.g., old values on UPDATE) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Action timestamp |

**Indexes**:
- `idx_audit_user_id` on (user_id)
- `idx_audit_resource` on (resource_type, resource_id)
- `idx_audit_created_at` on (created_at DESC)

**Validation Rules**:
- action must be one of: CREATE, READ, UPDATE, DELETE, ACCESS_DENIED
- resource_type must be one of: case, evidence, draft, user, case_member
- created_at is immutable (no updates allowed)

---

### CaseMember

Maps users to cases with role-based permissions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto | Unique identifier |
| case_id | UUID | FK → cases, NOT NULL | Case reference |
| user_id | UUID | FK → users, NOT NULL | User reference |
| role | ENUM | NOT NULL | OWNER (full access), MEMBER (read/write), VIEWER (read only) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Membership start |
| updated_at | TIMESTAMP | NOT NULL | Last modification |

**Indexes**:
- `idx_case_member_unique` UNIQUE on (case_id, user_id)
- `idx_case_member_user` on (user_id)

**Validation Rules**:
- Each case MUST have at least one OWNER
- role hierarchy: OWNER > MEMBER > VIEWER
- user_id + case_id must be unique (no duplicate memberships)

**State Transitions**:
```
VIEWER → MEMBER → OWNER (promotion)
OWNER → MEMBER → VIEWER (demotion)
Any → (deleted) (removal from case)
```

---

## DynamoDB Entities

### Evidence (leh_evidence table)

Stores evidence metadata after AI Worker analysis.

| Field | Type | Key | Description |
|-------|------|-----|-------------|
| case_id | String | PK (Partition) | Case identifier |
| evidence_id | String | SK (Sort) | Unique evidence ID, format: `EV-{uuid[:8]}` |
| type | String | - | File type: image, audio, video, text, pdf |
| original_filename | String | - | Original uploaded filename |
| s3_key | String | - | S3 object key: `cases/{case_id}/raw/{evidence_id}_{filename}` |
| file_size | Number | - | File size in bytes |
| sha256_hash | String | - | SHA-256 hash for integrity verification |
| timestamp | String | GSI | ISO8601 timestamp of evidence (from content or upload) |
| speaker | String | - | 원고, 피고, 제3자, 불명 |
| ai_summary | String | - | AI-generated summary (max 500 chars) |
| labels | List[String] | - | Article 840 tags: 폭언, 불륜, 유책사유, etc. |
| evidence_score | Number | - | AI confidence score (0-100) |
| qdrant_id | String | - | Qdrant point ID for RAG search |
| status | String | GSI | pending, processing, completed, failed |
| created_at | String | - | ISO8601 upload timestamp |
| updated_at | String | - | ISO8601 last update timestamp |

**GSI**:
- `case_status_index`: PK=case_id, SK=status (filter by status)
- `case_timestamp_index`: PK=case_id, SK=timestamp (timeline view)

**Validation Rules**:
- evidence_id format: `EV-` prefix + 8 hex chars
- type must be one of: image, audio, video, text, pdf
- status must be one of: pending, processing, completed, failed
- sha256_hash must be 64 hex characters

---

## Qdrant Collections

### case_rag_{case_id}

Per-case vector collection for RAG search (Constitution Principle II).

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Qdrant point ID (matches DynamoDB qdrant_id) |
| vector | Float[1536] | OpenAI text-embedding-3-small output |
| payload.evidence_id | String | Reference to DynamoDB evidence |
| payload.case_id | String | Case identifier for validation |
| payload.content_chunk | String | Text chunk (max 1000 tokens) |
| payload.chunk_index | Number | Position in document (0-indexed) |
| payload.timestamp | String | Evidence timestamp for filtering |
| payload.speaker | String | Speaker attribution |
| payload.labels | List[String] | Article 840 tags |

**Collection Settings**:
- Distance: Cosine
- Vector size: 1536
- On-disk: true (for cost efficiency)

**Lifecycle**:
- Created: When first evidence uploaded to case
- Deleted: When case is closed (soft-delete in DynamoDB, hard-delete in Qdrant)

---

## API Response Models

### EvidenceSearchResult

Returned from RAG search endpoint.

```python
class EvidenceSearchResult(BaseModel):
    evidence_id: str           # EV-xxxxxxxx
    score: float               # Relevance score (0-1)
    content_preview: str       # First 200 chars of matching chunk
    timestamp: datetime
    speaker: str
    labels: List[str]
    s3_url: Optional[str]      # Presigned URL if requested
```

### DraftPreviewResponse

Returned from draft generation endpoint.

```python
class DraftPreviewResponse(BaseModel):
    draft_id: str              # Temporary ID for this preview
    content: str               # Markdown draft with [EV-xxx] citations
    citations: List[Citation]  # Structured citation references
    generated_at: datetime
    model: str                 # gpt-4o
    token_count: int

class Citation(BaseModel):
    evidence_id: str           # EV-xxxxxxxx
    quote: str                 # Cited text snippet
    relevance: str             # How it supports the argument
```

---

## Entity Relationships

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│    User     │──1:N──│ CaseMember  │──N:1──│    Case     │
└─────────────┘      └─────────────┘      └─────────────┘
                                                 │
                                                1:N
                                                 │
                                          ┌─────────────┐
                                          │  Evidence   │
                                          │ (DynamoDB)  │
                                          └─────────────┘
                                                 │
                                                1:N
                                                 │
                                          ┌─────────────┐
                                          │   Qdrant    │
                                          │   Vectors   │
                                          └─────────────┘
                                          
┌─────────────┐
│  AuditLog   │  (references all entities via resource_type + resource_id)
└─────────────┘
```

---

## Migration Notes

### New Tables (Alembic)
1. `audit_logs` - Create if not exists
2. `case_members` - Already exists, verify role enum includes OWNER/MEMBER/VIEWER

### DynamoDB
- Table `leh_evidence` - Already exists
- Add GSI `case_status_index` if not present
- Add GSI `case_timestamp_index` if not present

### Qdrant
- Collections created dynamically per case
- No migration needed

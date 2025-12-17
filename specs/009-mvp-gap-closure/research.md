# Research: MVP 구현 갭 해소

**Date**: 2025-12-11
**Feature**: 009-mvp-gap-closure

## Overview

This research consolidates decisions for implementing production readiness features. Since the tech stack is well-established (Python/FastAPI, Next.js, AWS), research focuses on specific implementation patterns.

---

## 1. Error Handling Pattern (Frontend)

### Decision
Use **react-hot-toast** for transient errors (network, timeout) and **inline validation** for form field errors.

### Rationale
- react-hot-toast is lightweight (5KB), actively maintained, and supports promise-based toasts
- Inline validation provides immediate feedback without modal interruption
- Consistent with clarified FR-009 requirements

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| react-toastify | Larger bundle size (10KB+), more features than needed |
| Chakra UI Toast | Would require full Chakra dependency |
| Custom toast | Unnecessary development overhead |

### Implementation Pattern
```typescript
// lib/api/client.ts - centralized error handling
import toast from 'react-hot-toast';

export async function apiCall<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (error.status === 401) {
      toast.error('세션이 만료되었습니다');
      redirect('/login');
    } else if (error.status >= 500) {
      toast.error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    } else {
      toast.error(error.message || '요청 처리 중 오류가 발생했습니다.');
    }
    throw error;
  }
}
```

---

## 2. RAG Search Implementation (Backend)

### Decision
Use **Qdrant hybrid search** (vector + keyword) with case-scoped collections.

### Rationale
- Qdrant already deployed and integrated
- Hybrid search combines semantic similarity with exact keyword matching
- Collection pattern `case_rag_{case_id}` ensures case isolation per Constitution Principle II

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| OpenAI embeddings only | Misses exact keyword matches |
| PostgreSQL pg_vector | Additional setup, Qdrant already in use |
| Elasticsearch | Additional infrastructure, overkill for MVP |

### Implementation Pattern
```python
# services/search_service.py
class SearchService:
    async def search_evidence(
        self, case_id: str, query: str, limit: int = 10
    ) -> List[EvidenceSearchResult]:
        collection = f"case_rag_{case_id}"
        embedding = await self.openai_client.embed(query)

        results = await self.qdrant.search(
            collection_name=collection,
            query_vector=embedding,
            limit=limit,
            with_payload=True
        )
        return [EvidenceSearchResult.from_qdrant(r) for r in results]
```

---

## 3. Draft Preview with Citations (Backend)

### Decision
Use **GPT-4o** with structured prompt template, returning inline citations `[EV-XXX]`.

### Rationale
- GPT-4o has best performance for Korean legal text
- Inline citations match clarified FR-007 format
- 30-second timeout aligns with SC-003

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| GPT-4 Turbo | Slower for same task |
| Claude 3 | Requires API key change, less tested for Korean legal |
| Local LLM | Insufficient quality for legal documents |

### Implementation Pattern
```python
# services/draft_service.py
DRAFT_PROMPT = """
당신은 이혼 전문 법률 문서 작성 보조원입니다.
다음 증거 자료를 기반으로 준비서면 초안을 작성하세요.

증거 목록:
{evidence_list}

작성 규칙:
1. 각 주장에 증거 ID를 [EV-XXX] 형식으로 인용하세요
2. 민법 제840조(이혼사유) 조항을 참조하세요
3. 객관적이고 법률적인 문체를 사용하세요

출력 형식: 준비서면 초안 (마크다운)
"""
```

---

## 4. Case Permission Middleware (Backend)

### Decision
Use **FastAPI dependency injection** with `CasePermissionChecker` class.

### Rationale
- Dependency injection is idiomatic FastAPI pattern
- Reusable across all case-related endpoints
- Enables audit logging per FR-015/FR-016

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| Middleware (global) | Can't access route parameters easily |
| Decorator pattern | Less integration with FastAPI DI |
| Per-route checks | Code duplication, error-prone |

### Implementation Pattern
```python
# core/dependencies.py
class CasePermissionChecker:
    def __init__(self, required_role: CaseRole = CaseRole.VIEWER):
        self.required_role = required_role

    async def __call__(
        self,
        case_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ):
        member = await case_member_repo.get(db, case_id, user_id)
        if not member or member.role < self.required_role:
            await audit_service.log_access_denied(user_id, case_id)
            raise HTTPException(403, "사건 접근 권한이 없습니다")
        return member

# Usage in router
@router.get("/cases/{case_id}/evidence")
async def get_evidence(
    case_id: str,
    permission: CaseMember = Depends(CasePermissionChecker())
):
    ...
```

---

## 5. CI Test Coverage Fix (AI Worker)

### Decision
Modify `conftest.py` to skip only **integration tests** when AWS credentials missing, not all tests.

### Rationale
- Unit tests (300+) should always run
- Integration tests require AWS services (S3, DynamoDB, Qdrant)
- pytest markers can selectively skip

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| Mock all AWS | Integration tests lose value |
| LocalStack | Additional CI complexity |
| Skip all on missing env | Defeats CI purpose (current problem) |

### Implementation Pattern
```python
# conftest.py
import pytest
import os

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: marks tests as integration (require AWS)"
    )

@pytest.fixture(scope="session", autouse=True)
def check_aws_credentials():
    """Skip integration tests if AWS not configured."""
    pass  # No longer skip all tests

def pytest_collection_modifyitems(config, items):
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        skip_aws = pytest.mark.skip(reason="AWS credentials not configured")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_aws)
```

---

## 6. S3 Multipart Upload (Frontend)

### Decision
Use **AWS SDK v3** multipart upload for files >5MB, presigned URL for smaller files.

### Rationale
- 500MB file limit (per clarification) requires chunked upload
- AWS SDK v3 handles multipart automatically
- Presigned URLs still work for most uploads (<5MB)

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| Single PUT always | Fails for large files, timeout issues |
| tus-js-client | Additional dependency, AWS S3 native is sufficient |
| Backend proxy | Violates architecture (direct S3 upload) |

### Implementation Pattern
```typescript
// lib/upload.ts
import { S3Client, CreateMultipartUploadCommand } from '@aws-sdk/client-s3';
import { Upload } from '@aws-sdk/lib-storage';

export async function uploadEvidence(file: File, presignedUrl: string) {
  if (file.size > 5 * 1024 * 1024) {
    // Use multipart for files > 5MB
    const upload = new Upload({
      client: s3Client,
      params: { Bucket, Key, Body: file }
    });
    return await upload.done();
  } else {
    // Use presigned URL for small files
    return await fetch(presignedUrl, { method: 'PUT', body: file });
  }
}
```

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Frontend Error | react-hot-toast + inline | Lightweight, matches UX pattern |
| RAG Search | Qdrant hybrid | Already integrated, case isolation |
| Draft Generation | GPT-4o + inline citations | Best Korean legal quality |
| Permission Check | FastAPI DI | Idiomatic, enables audit |
| CI Tests | Skip only integration | Unit tests always run |
| Large Upload | S3 multipart | 500MB file support |

All decisions align with Constitution principles and spec requirements. No NEEDS CLARIFICATION items remain.

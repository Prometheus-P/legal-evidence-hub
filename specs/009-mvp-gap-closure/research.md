# Research: MVP 구현 갭 해소

**Feature**: 009-mvp-gap-closure
**Date**: 2025-12-09
**Status**: Complete

## Executive Summary

현재 LEH 프로젝트는 설계 문서 대비 실제 구현이 **예상보다 훨씬 완성도가 높음**.

| 영역 | 예상 | 실제 | 갭 |
|------|------|------|-----|
| AI Worker | 코드 완성, S3 권한 미비 | ✅ 100% 완성 | S3 권한 설정만 필요 |
| Backend RAG/Draft | 미구현 추정 | ✅ 90-95% 완성 | Search history만 stub |
| Frontend 에러 | 산발적 | ✅ 70% 완성 | Toast, retry 추가 필요 |
| CI 테스트 | 스킵 추정 | ✅ 실행 중 (65%) | 80% 목표 미달 |

---

## 1. AI Worker 실서비스 연동 (US1)

### Decision: S3 권한 설정으로 배포 가능

### Rationale
코드는 100% 완성됨. 7개 메인 파서 + 4개 V2 파서, DynamoDB/Qdrant 저장소, 48개 테스트 파일.
Lambda Dockerfile.lambda도 준비됨 (Python 3.12 base).

**Blocker**: IAM 역할에 S3 권한 부재

### Alternatives Considered
1. ~~새로 코드 작성~~ - 불필요 (이미 완성)
2. ~~LocalStack 에뮬레이션~~ - 실환경 테스트 필요

### Required Actions
```bash
# 1. S3 버킷 생성
aws s3 mb s3://leh-evidence-dev --region ap-northeast-2
aws s3 mb s3://leh-evidence-prod --region ap-northeast-2

# 2. Lambda 실행 역할에 S3 정책 연결
aws iam attach-role-policy \
  --role-name leh-ai-worker-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# 3. S3 이벤트 알림 설정
aws s3api put-bucket-notification-configuration \
  --bucket leh-evidence-dev \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [{
      "LambdaFunctionArn": "arn:aws:lambda:ap-northeast-2:ACCOUNT:function:leh-ai-worker",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "cases/"}]}}
    }]
  }'
```

---

## 2. Backend RAG 검색 및 Draft 생성 (US2)

### Decision: 이미 구현 완료, 추가 작업 불필요

### Rationale
연구 결과 발견:
- `DraftService` (1,192 lines): RAG + GPT-4o 통합 완료
- `SearchService` (349 lines): 멀티 카테고리 검색 완료
- `qdrant.py` (478 lines): Semantic search + Legal knowledge
- `openai_client.py` (150 lines): GPT-4o, embeddings, token counting

**실제 동작하는 기능:**
- POST `/cases/{id}/draft-preview` - RAG 기반 초안 생성
- GET `/cases/{id}/draft-export` - DOCX/PDF 내보내기
- GET `/search` - 통합 검색 (cases, clients, evidence, events)

### Alternatives Considered
1. ~~신규 구현~~ - 이미 존재
2. ~~Mock 서비스 교체~~ - Mock이 아님

### Known Gap
- `get_recent_searches()` 메서드가 빈 리스트 반환 (TODO 상태)
- **해결**: 별도 테이블 필요 시 향후 구현, MVP에서 스킵 가능

---

## 3. Frontend 에러 처리 통일 (US3)

### Decision: react-hot-toast 도입 + 공통 패턴 적용

### Rationale
현재 구현:
- ✅ 401 처리: `client.ts`에서 `/login` 리다이렉트 (루프 방지 로직 포함)
- ✅ Error boundaries: 역할별 에러 컴포넌트 (Lawyer/Client/Detective)
- ⚠️ 에러 표시: 인라인 텍스트만 (toast 없음)
- ❌ 자동 재시도: 미구현

### Alternatives Considered
1. **react-hot-toast** ← 선택: 경량, 설정 간단, Next.js 호환
2. ~~sonner~~ - 더 무거움
3. ~~커스텀 구현~~ - 시간 소요

### Implementation Pattern
```typescript
// lib/api/client.ts 수정
import toast from 'react-hot-toast';

// Network error 시 toast 표시
catch (error) {
  toast.error('네트워크 오류가 발생했습니다. 다시 시도해주세요.');
  return { error: 'Network error', status: 0 };
}

// hooks/useRetry.ts 신규
export function useRetry<T>(
  fn: () => Promise<T>,
  options: { maxRetries: number; backoff: number }
) {
  // Exponential backoff 구현
}
```

---

## 4. CI 테스트 커버리지 정상화 (US4)

### Decision: 커버리지 임계값 80%로 상향, 누락 테스트 추가

### Rationale
현재 상태:
- Backend: `--cov-fail-under=65` (pytest.ini)
- AI Worker: `--cov-fail-under=65` (pytest.ini)
- CLAUDE.md 요구사항: 80% minimum
- 15%p 갭 존재

### Alternatives Considered
1. **단계적 상향** ← 선택: 65% → 70% → 75% → 80%
2. ~~즉시 80%~~ - 테스트 대량 추가 필요
3. ~~현행 유지~~ - 품질 기준 미달

### Test Files Needing Coverage
```
backend/
├── app/services/draft_service.py  # 1,192 lines, 추가 테스트 필요
├── app/services/search_service.py # 349 lines
└── app/utils/qdrant.py            # 478 lines

ai_worker/
├── src/parsers/image_vision.py    # GPT-4o Vision 테스트
└── src/analysis/article_840_tagger.py
```

---

## 5. 사건별 권한 제어 (US5)

### Decision: 기존 미들웨어 강화 + audit_logs 일관 적용

### Rationale
현재 구현:
- `case_members` 테이블 존재 (OWNER/MEMBER/VIEWER)
- `get_current_user_id()` 의존성 주입 패턴
- 일부 API에서 권한 검증 누락 가능성

### Actions
1. 모든 `/cases/*`, `/evidence/*`, `/draft/*` 엔드포인트 감사
2. 404 대신 403 반환 통일
3. `audit_service.log_access()` 호출 추가

### Audit Log Schema (기존)
```python
# backend/app/db/models.py
class AuditLog(Base):
    id: int
    user_id: int
    action: str  # "read", "create", "update", "delete", "access_denied"
    resource_type: str  # "case", "evidence", "draft"
    resource_id: str
    ip_address: str
    created_at: datetime
```

---

## 6. 기본 배포 파이프라인 (US6)

### Decision: AI Worker 배포 활성화 + 롤백 문서화

### Rationale
현재 상태:
- Backend deploy: ✅ 활성
- Frontend deploy: ✅ 활성
- AI Worker deploy: ❌ `&& false` 조건으로 비활성

### Fix Required
```yaml
# .github/workflows/deploy_paralegal.yml
# Line 95 변경:
# Before: if: github.ref == 'refs/heads/main' && false
# After:  if: github.ref == 'refs/heads/main'
```

### Rollback Procedure (문서화)
```bash
# Backend Lambda 롤백
aws lambda update-function-code \
  --function-name leh-backend \
  --image-uri $ECR_REGISTRY/leh-backend:$PREVIOUS_SHA

# Frontend 롤백 (S3)
aws s3 sync s3://leh-frontend-backup/$PREVIOUS_SHA s3://leh-frontend --delete
aws cloudfront create-invalidation --distribution-id $CF_DIST --paths "/*"
```

---

## Technology Best Practices Applied

### FastAPI + Qdrant RAG
- Singleton pattern for Qdrant client (connection pooling)
- Case-isolated collections (`case_rag_{case_id}`)
- Graceful degradation on missing collections (empty list return)

### Next.js Error Handling
- Error boundaries per route segment
- HTTP-only cookie auth (no localStorage)
- Smart 401 redirect with loop prevention

### AWS Lambda Best Practices
- Idempotency keys (evidence_id, file hash, S3 key)
- Job tracking with ProcessingStage
- /tmp cleanup for file processing
- Cost guard validation

---

## Unresolved Questions

1. **Qdrant Cloud 프로비저닝**: 이미 완료 가정 (spec Assumptions)
2. **OpenAI API 키 설정**: 환경변수 설정 확인 필요
3. **GitHub Secrets 설정**: AWS credentials 확인 필요

---

## References

- [spec.md](./spec.md) - Feature specification
- [CLAUDE.md](../../CLAUDE.md) - Project guidelines
- [constitution.md](../../.specify/memory/constitution.md) - Architecture principles

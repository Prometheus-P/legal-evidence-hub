# Quickstart: MVP 구현 갭 해소

**Feature**: 009-mvp-gap-closure
**Date**: 2025-12-11

## Prerequisites

Before starting implementation, verify these are in place:

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-2
S3_EVIDENCE_BUCKET=leh-evidence-dev
DYNAMODB_TABLE=leh_evidence_dev
QDRANT_HOST=your-qdrant-host
QDRANT_API_KEY=your-qdrant-key
OPENAI_API_KEY=sk-...

# Frontend (.env.local)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### AWS Resources
- [ ] S3 bucket `leh-evidence-dev` exists
- [ ] Lambda execution role has S3:GetObject, S3:PutObject permissions
- [ ] DynamoDB table `leh_evidence_dev` exists with GSIs
- [ ] Qdrant Cloud cluster accessible

### Dependencies
```bash
# Backend
pip install qdrant-client openai boto3

# Frontend
npm install react-hot-toast @aws-sdk/client-s3 @aws-sdk/lib-storage
```

---

## Verification Steps

### US1: AI Worker Pipeline

1. **Upload test file**
```bash
aws s3 cp test-evidence.pdf s3://leh-evidence-dev/cases/test-case-id/raw/EV-test1234_test.pdf
```

2. **Check Lambda trigger** (wait 1-2 minutes)
```bash
aws logs tail /aws/lambda/leh-ai-worker --follow
```

3. **Verify DynamoDB entry**
```bash
aws dynamodb get-item \
  --table-name leh_evidence_dev \
  --key '{"case_id": {"S": "test-case-id"}, "evidence_id": {"S": "EV-test1234"}}'
```

4. **Verify Qdrant vectors**
```python
from qdrant_client import QdrantClient
client = QdrantClient(host="...", api_key="...")
client.get_collection("case_rag_test-case-id")
```

**Expected**: Entry in DynamoDB with ai_summary, labels; vectors in Qdrant

---

### US2: RAG Search & Draft

1. **Test search endpoint**
```bash
curl -X GET "http://localhost:8000/v1/search?q=폭언&case_id=<case_id>" \
  -H "Authorization: Bearer <token>"
```

**Expected**: JSON with results array, each containing evidence_id, score, content_preview

2. **Test draft preview**
```bash
curl -X POST "http://localhost:8000/v1/cases/<case_id>/draft-preview" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"document_type": "준비서면"}'
```

**Expected**: JSON with content containing `[EV-xxx]` inline citations, citations array

---

### US3: Error Handling

1. **Test 401 redirect** (frontend)
   - Clear cookies/token
   - Navigate to `/lawyer/dashboard`
   - **Expected**: Redirect to `/login` with toast "세션이 만료되었습니다"

2. **Test network error** (frontend)
   - Stop backend server
   - Click any API action button
   - **Expected**: Toast "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

3. **Test loading state**
   - Click form submit button
   - **Expected**: Button disabled with loading spinner during API call

---

### US4: CI Tests

1. **Run AI Worker tests locally**
```bash
cd ai_worker
pytest -v --tb=short
```
**Expected**: 300+ tests pass (integration tests may skip without AWS)

2. **Run Backend tests with coverage**
```bash
cd backend
pytest --cov=app --cov-report=term-missing
```
**Expected**: 65%+ coverage

3. **Verify CI workflow**
   - Create PR with code changes
   - Check GitHub Actions
   - **Expected**: Tests run (not skipped), coverage reported

---

### US5: Permission Check

1. **Create test users and case**
```python
# User A is OWNER of case-1
# User B has no access to case-1
```

2. **Test unauthorized access**
```bash
curl -X GET "http://localhost:8000/v1/cases/<case-1>/evidence" \
  -H "Authorization: Bearer <user-b-token>"
```
**Expected**: 403 Forbidden

3. **Verify audit log**
```sql
SELECT * FROM audit_logs 
WHERE action = 'ACCESS_DENIED' 
AND resource_id = '<case-1>'
ORDER BY created_at DESC LIMIT 1;
```
**Expected**: Entry with user_id = User B

---

### US6: Deployment Pipeline

1. **Verify staging deployment**
   - Merge PR to `dev` branch
   - Wait for CI to complete
   - **Expected**: Changes visible at staging CloudFront URL within 10 minutes

2. **Verify production deployment**
   - Create PR from `dev` to `main`
   - Merge with approval
   - **Expected**: GitHub Actions shows manual approval step, then deploys

---

## Troubleshooting

### AI Worker not triggering
- Check S3 event notification is configured
- Verify Lambda has correct execution role
- Check CloudWatch logs for errors

### RAG search returns empty
- Verify Qdrant collection exists: `case_rag_{case_id}`
- Check OpenAI API key is valid
- Verify evidence has status=completed in DynamoDB

### Draft generation timeout
- Increase OpenAI API timeout to 30s
- Check for rate limiting (429 errors)
- Verify case has sufficient evidence (minimum 1)

### Permission check bypassed
- Verify `CasePermissionChecker` dependency is in route
- Check JWT token contains valid user_id
- Verify case_members table has correct entries

### CI tests skipping
- Check conftest.py skip logic
- Verify pytest markers are correct (`@pytest.mark.integration`)
- Ensure AWS credentials are NOT in CI environment (intentional)

---

## Success Criteria Checklist

| ID | Criteria | Test Method |
|----|----------|-------------|
| SC-001 | AI analysis <5min | Upload file, time until DynamoDB entry |
| SC-002 | RAG search <2s | Measure /search response time |
| SC-003 | Draft Preview <30s | Measure /draft-preview response time |
| SC-004 | AI Worker tests 300+ | `pytest --collect-only \| wc -l` |
| SC-005 | Backend coverage 65%+ | `pytest --cov` report |
| SC-006 | 403 on unauthorized | Test with wrong user token |
| SC-007 | Staging deploy <10min | Time from merge to live |
| SC-008 | Error messages 100% | Manual UI testing |

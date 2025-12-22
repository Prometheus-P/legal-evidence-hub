# Quickstart: 사건 전체 사실관계 요약

**Feature**: 014-case-fact-summary
**Date**: 2025-12-22

## 개발 환경 설정

### 필수 환경 변수

```bash
# .env 파일에 추가 (이미 존재해야 함)
AWS_REGION=ap-northeast-2
DDB_CASE_SUMMARY_TABLE=leh_case_summary  # 기존 테이블 활용
OPENAI_API_KEY=sk-...
OPENAI_MODEL_CHAT=gpt-4o-mini
```

### Backend 로컬 실행

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend 로컬 실행

```bash
cd frontend
npm install
npm run dev
```

---

## API 사용 예시

### 1. 사실관계 생성

```bash
# 최초 생성
curl -X POST "http://localhost:8000/api/cases/case_abc123/fact-summary/generate" \
  -H "Cookie: access_token=YOUR_JWT" \
  -H "Content-Type: application/json"

# 응답
{
  "case_id": "case_abc123",
  "ai_summary": "### 사건 개요\n혼인기간 8년...",
  "evidence_count": 5,
  "fault_types": ["부정행위", "가정폭력"],
  "generated_at": "2025-12-22T10:00:00Z"
}
```

### 2. 사실관계 조회

```bash
curl "http://localhost:8000/api/cases/case_abc123/fact-summary" \
  -H "Cookie: access_token=YOUR_JWT"

# 응답
{
  "case_id": "case_abc123",
  "ai_summary": "### 사건 개요\n...",
  "modified_summary": null,
  "evidence_ids": ["evt_001", "evt_002"],
  "fault_types": ["부정행위"],
  "created_at": "2025-12-22T10:00:00Z",
  "modified_at": null,
  "modified_by": null,
  "has_previous_version": false
}
```

### 3. 사실관계 수정

```bash
curl -X PATCH "http://localhost:8000/api/cases/case_abc123/fact-summary" \
  -H "Cookie: access_token=YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"modified_summary": "### 사건 개요\n혼인기간 8년 (2015.03 ~ 2023.11)..."}'

# 응답
{
  "case_id": "case_abc123",
  "modified_summary": "### 사건 개요\n...",
  "modified_at": "2025-12-22T11:30:00Z",
  "modified_by": "user_lawyer123"
}
```

### 4. 사실관계 재생성 (기존 수정본 백업)

```bash
curl -X POST "http://localhost:8000/api/cases/case_abc123/fact-summary/generate" \
  -H "Cookie: access_token=YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"force_regenerate": true}'
```

---

## 테스트 실행

### Backend 단위 테스트

```bash
cd backend
pytest tests/unit/test_fact_summary_service.py -v
```

### Backend 통합 테스트

```bash
cd backend
pytest tests/integration/test_fact_summary_api.py -v
```

### Frontend 컴포넌트 테스트

```bash
cd frontend
npm test -- --testPathPattern=fact-summary
```

---

## 주요 파일 위치

| 파일 | 용도 |
|------|------|
| `backend/app/api/fact_summary.py` | API 라우터 |
| `backend/app/schemas/fact_summary.py` | Pydantic 스키마 |
| `backend/app/services/fact_summary_service.py` | 비즈니스 로직 |
| `backend/app/utils/dynamo.py` | DynamoDB CRUD 함수 |
| `frontend/src/lib/api/fact-summary.ts` | API 클라이언트 |
| `frontend/src/types/fact-summary.ts` | TypeScript 타입 |
| `frontend/src/components/fact-summary/FactSummaryPanel.tsx` | UI 컴포넌트 |

---

## 디버깅 팁

### DynamoDB 데이터 확인

```bash
aws dynamodb get-item \
  --table-name leh_case_summary \
  --key '{"case_id": {"S": "case_abc123"}}' \
  --region ap-northeast-2
```

### 로그 확인

```bash
# Lambda 로그 (배포 후)
aws logs tail /aws/lambda/leh-backend --follow

# 로컬 개발 시 uvicorn 로그에서 확인
```

---

## 다음 단계

1. `/speckit.tasks` 실행하여 상세 태스크 생성
2. TDD 사이클에 따라 테스트 먼저 작성
3. Backend 서비스 구현 → API 구현 → Frontend 구현 순서

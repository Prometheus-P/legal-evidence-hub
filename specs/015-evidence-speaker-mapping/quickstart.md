# Quickstart: 증거 화자 매핑

**Feature**: 015-evidence-speaker-mapping
**Date**: 2025-12-22

## 개발 환경 설정

### 필수 환경 변수

```bash
# .env 파일 (프로젝트 루트)
AWS_REGION=ap-northeast-2
DDB_EVIDENCE_TABLE=leh_evidence
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
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

### 1. 화자 매핑 저장

```bash
# 증거에 화자 매핑 설정
curl -X PATCH "http://localhost:8000/api/evidence/evt_abc123/speaker-mapping" \
  -H "Cookie: access_token=YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "speaker_mapping": {
      "나": {"party_id": "party_001", "party_name": "김동우"},
      "상대방": {"party_id": "party_002", "party_name": "김도연"}
    }
  }'

# 응답
{
  "evidence_id": "evt_abc123",
  "speaker_mapping": {
    "나": {"party_id": "party_001", "party_name": "김동우"},
    "상대방": {"party_id": "party_002", "party_name": "김도연"}
  },
  "updated_at": "2025-12-22T14:30:00Z",
  "updated_by": "user_lawyer123"
}
```

### 2. 화자 매핑 삭제

```bash
# 빈 객체로 매핑 삭제
curl -X PATCH "http://localhost:8000/api/evidence/evt_abc123/speaker-mapping" \
  -H "Cookie: access_token=YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"speaker_mapping": {}}'

# 응답
{
  "evidence_id": "evt_abc123",
  "speaker_mapping": null,
  "updated_at": "2025-12-22T14:35:00Z",
  "updated_by": "user_lawyer123"
}
```

### 3. 증거 상세 조회 (매핑 포함)

```bash
curl "http://localhost:8000/api/evidence/evt_abc123" \
  -H "Cookie: access_token=YOUR_JWT"

# 응답
{
  "id": "evt_abc123",
  "case_id": "case_xyz789",
  "type": "image",
  "filename": "kakaotalk_capture.jpg",
  "status": "completed",
  "ai_summary": "카카오톡 대화에서...",
  "content": "나: 왜 그랬어?\n상대방: 미안해...",
  "speaker_mapping": {
    "나": {"party_id": "party_001", "party_name": "김동우"},
    "상대방": {"party_id": "party_002", "party_name": "김도연"}
  },
  "speaker_mapping_updated_at": "2025-12-22T14:30:00Z",
  "created_at": "2025-12-20T10:00:00Z"
}
```

### 4. 사실관계 생성 (매핑 자동 반영)

```bash
# 화자 매핑이 설정된 증거가 있으면 AI가 실제 인물명으로 해석
curl -X POST "http://localhost:8000/api/cases/case_xyz789/fact-summary/generate" \
  -H "Cookie: access_token=YOUR_JWT"

# AI 생성 결과 예시
{
  "case_id": "case_xyz789",
  "ai_summary": "### 사건 개요\n\n### 사실관계\n1. [증거1] 2024년 1월 - 김동우가 김도연에게 폭언을 함...",
  "evidence_count": 3,
  "fault_types": ["폭언"],
  "generated_at": "2025-12-22T15:00:00Z"
}
```

---

## 테스트 실행

### Backend 단위 테스트

```bash
cd backend

# 화자 매핑 서비스 테스트
pytest tests/unit/test_speaker_mapping_service.py -v

# DynamoDB 화자 매핑 함수 테스트
pytest tests/unit/test_dynamo_speaker_mapping.py -v

# 사실관계 프롬프트 화자 매핑 테스트
pytest tests/unit/test_fact_summary_speaker_mapping.py -v

# 증거 목록 화자 매핑 필드 테스트
pytest tests/unit/test_evidence_list_speaker_mapping.py -v
```

### Backend API 테스트

```bash
cd backend
pytest tests/integration/test_speaker_mapping_api.py -v
```

### Frontend 컴포넌트 테스트

```bash
cd frontend
npm test -- --testPathPattern=SpeakerMapping
```

---

## 주요 파일 위치

| 파일 | 용도 |
|------|------|
| `backend/app/api/evidence.py` | API 라우터 (PATCH /speaker-mapping) |
| `backend/app/db/schemas/evidence.py` | Pydantic 스키마 (SpeakerMappingItem, SpeakerMappingUpdateRequest) |
| `backend/app/db/schemas/audit.py` | AuditAction.SPEAKER_MAPPING_UPDATE |
| `backend/app/services/evidence_service.py` | 화자 매핑 CRUD 로직, 감사 로그 |
| `backend/app/services/fact_summary_service.py` | 프롬프트 매핑 주입 (_build_generation_prompt) |
| `backend/app/utils/dynamo.py` | DynamoDB 업데이트 함수 (update_evidence_speaker_mapping) |
| `frontend/src/lib/api/evidence.ts` | API 클라이언트 |
| `frontend/src/types/evidence.ts` | TypeScript 타입 |
| `frontend/src/hooks/useSpeakerMapping.ts` | 화자 매핑 React Hook |
| `frontend/src/components/evidence/SpeakerMappingModal.tsx` | 매핑 설정 모달 |
| `frontend/src/components/evidence/SpeakerMappingBadge.tsx` | 목록 뱃지 |

---

## 디버깅 팁

### DynamoDB 데이터 확인

```bash
# 증거의 화자 매핑 확인
aws dynamodb get-item \
  --table-name leh_evidence \
  --key '{"evidence_id": {"S": "evt_abc123"}}' \
  --projection-expression "speaker_mapping" \
  --region ap-northeast-2
```

### 인물 목록 확인

```bash
# 해당 케이스의 인물 목록 (매핑 UI 드롭다운용)
curl "http://localhost:8000/api/cases/case_xyz789/parties" \
  -H "Cookie: access_token=YOUR_JWT"
```

### 로그 확인

```bash
# 로컬 개발 시 uvicorn 로그
# "speaker_mapping" 관련 로그 확인

# Lambda 로그 (배포 후)
aws logs tail /aws/lambda/leh-backend --follow --filter-pattern "speaker_mapping"
```

---

## 다음 단계

1. `/speckit.tasks` 실행하여 상세 태스크 생성
2. TDD 사이클에 따라 테스트 먼저 작성
3. 구현 순서:
   - Backend: Schema → Service → API → Tests
   - Frontend: Types → API Client → Modal → Badge → Integration

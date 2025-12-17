# Quickstart: 판례 검색 시스템

## 사전 요구사항

- Python 3.11+
- Node.js 18+
- PostgreSQL (로컬 또는 RDS)
- Qdrant (로컬 또는 Cloud)
- OpenAI API 키

## 환경 설정

1. **환경 변수 설정** (`.env` 파일)

```bash
# 프로젝트 루트에서
cp .env.example .env

# 필수 변수 확인
OPENAI_API_KEY=sk-...
QDRANT_HOST=localhost  # 또는 Qdrant Cloud URL
QDRANT_API_KEY=...     # Cloud 사용 시
DATABASE_URL=postgresql://...
```

2. **의존성 설치**

```bash
# Backend
cd backend && pip install -r requirements.txt

# AI Worker
cd ../ai_worker && pip install -r requirements.txt

# Frontend
cd ../frontend && npm install
```

## 판례 데이터 초기화

### Option A: Sample 데이터 로드 (권장 - 테스트용)

```bash
cd ai_worker/scripts
python load_sample_precedents.py
```

예상 출력:
```
Loading sample precedents from sample_precedents.json...
Loaded 10 precedents
Creating embeddings...
Storing in Qdrant collection: leh_legal_knowledge
Done! 10 precedents stored.
```

### Option B: 국가법령정보 API에서 수집 (프로덕션용)

```bash
cd ai_worker/scripts
python fetch_and_store_legal_data.py --count 100
```

**참고**: API 키가 필요합니다. 발급: https://www.law.go.kr/LSW/openApi.do

## 서비스 실행

### 1. Backend 실행

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend 실행

```bash
cd frontend
npm run dev
```

### 3. (Optional) AI Worker 로컬 테스트

```bash
cd ai_worker
python -m handler
```

## 기능 검증

### 1. 판례 검색 API 테스트

```bash
curl -X GET "http://localhost:8000/api/cases/test-case-001/similar-precedents?limit=5" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

예상 응답:
```json
{
  "precedents": [
    {
      "case_ref": "2020므12345",
      "court": "서울가정법원",
      "decision_date": "2020-06-15",
      "summary": "외도로 인한 혼인파탄...",
      "similarity_score": 0.87
    }
  ],
  "query_context": {
    "fault_types": ["외도"],
    "total_found": 5
  }
}
```

### 2. Frontend 확인

1. http://localhost:3000/lawyer/cases/test-case-001 접속
2. "유사 판례 검색" 버튼 클릭
3. 판례 카드 목록 확인
4. 카드 클릭 → 상세 모달 확인

### 3. Qdrant 데이터 확인

```bash
# Qdrant REST API로 확인
curl "http://localhost:6333/collections/leh_legal_knowledge"
```

## 트러블슈팅

### Qdrant 연결 실패

```
Error: Connection refused to localhost:6333
```

해결: Qdrant Docker 실행
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### OpenAI API 오류

```
Error: Invalid API key
```

해결: `.env` 파일의 `OPENAI_API_KEY` 확인

### 판례 검색 결과 없음

```json
{"precedents": [], "query_context": {"total_found": 0}}
```

해결: 
1. `python load_sample_precedents.py` 실행
2. Qdrant 컬렉션 데이터 확인

## 다음 단계

1. **초안 생성 테스트** (US2)
   - POST /cases/{id}/draft-preview 호출
   - 응답에 citations 필드 확인

2. **인물 자동 추출 테스트** (US3)
   - 카카오톡 증거 업로드
   - 관계도에서 자동 추출된 인물 확인

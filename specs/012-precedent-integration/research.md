# Research: 판례 검색 시스템 기술 결정

**Feature**: 012-precedent-integration
**Date**: 2025-12-12

## 1. 판례 데이터 소스

### Decision: 국가법령정보센터 Open API (law.go.kr)

**Rationale**:
- 공식 정부 API로 데이터 신뢰성 보장
- 무료 사용 가능 (API 키 필요)
- 판례 검색, 상세 조회 API 제공
- 기존 코드베이스 (`ai_worker/scripts/fetch_and_store_legal_data.py`)에서 이미 사용

**Alternatives Considered**:
- 대법원 종합법률정보 (glaw.scourt.go.kr): API 제한적, 크롤링 필요
- 빅카인즈 법률 DB: 유료, 예산 초과
- 수동 데이터 입력: 확장성 없음

**Fallback Strategy**:
- API 실패 시 `ai_worker/scripts/sample_precedents.json`에서 로드
- 10건의 이혼 판례 샘플 포함

## 2. 벡터 저장소

### Decision: Qdrant Cloud (leh_legal_knowledge collection)

**Rationale**:
- 기존 케이스별 RAG (`case_rag_{case_id}`)와 분리된 공유 컬렉션
- 1536차원 벡터 (text-embedding-3-small)
- 빠른 유사도 검색 (<100ms)

**Alternatives Considered**:
- PostgreSQL pgvector: 설정 복잡, 별도 인덱스 필요
- Pinecone: 유료, 기존 Qdrant와 중복
- ChromaDB: 프로덕션 안정성 부족

**Collection Schema**:
```json
{
  "name": "leh_legal_knowledge",
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload": {
    "case_ref": "string",
    "court": "string",
    "decision_date": "string",
    "summary": "string",
    "key_factors": "string[]",
    "division_ratio": "object"
  }
}
```

## 3. 임베딩 모델

### Decision: OpenAI text-embedding-3-small

**Rationale**:
- 1536차원으로 기존 Qdrant 설정과 호환
- 비용 효율적 ($0.02/1M tokens)
- 한국어 지원 우수

**Alternatives Considered**:
- text-embedding-3-large: 비용 2배, 성능 향상 미미
- Cohere multilingual: 추가 API 키 필요
- 로컬 모델 (sentence-transformers): 배포 복잡성 증가

## 4. 초안 판례 인용 구현

### Decision: DraftService에서 PrecedentService 호출

**Rationale**:
- 기존 DraftService 구조 활용
- 초안 생성 시 관련 판례 자동 검색
- GPT-4o 프롬프트에 판례 컨텍스트 추가

**Implementation Pattern**:
```python
# backend/app/services/draft_service.py
class DraftService:
    async def generate_draft(self, case_id: str) -> DraftPreview:
        # 1. 케이스 증거 조회
        evidence = await self.get_case_evidence(case_id)
        
        # 2. 유사 판례 검색 (NEW)
        precedents = await self.precedent_service.search_similar_precedents(
            case_id=case_id, 
            limit=5, 
            min_score=0.6
        )
        
        # 3. GPT-4o 프롬프트에 판례 컨텍스트 포함
        prompt = self._build_prompt_with_precedents(evidence, precedents)
        
        # 4. 초안 생성
        draft = await self.generate_with_citations(prompt)
        return draft
```

## 5. 인물 자동 추출 통합

### Decision: AI Worker → Backend API 호출

**Rationale**:
- AI Worker에서 추출한 인물/관계를 Backend에 저장
- 기존 PartyNode/PartyRelationship 테이블 활용
- 중복 감지는 Backend에서 처리

**API Endpoints**:
- `POST /cases/{case_id}/parties/auto-extract`: 인물 자동 저장
- `POST /cases/{case_id}/relationships/auto-extract`: 관계 자동 저장

**Confidence Threshold**: 0.7 (70% 이상 신뢰도만 저장)

## 6. 성능 최적화

### Decision: 캐싱 + 비동기 처리

**Rationale**:
- 판례 검색 5초 이내 목표 (SC-001)
- Qdrant 쿼리 자체는 <100ms
- 임베딩 생성이 병목 → 사전 임베딩 저장

**Optimization Strategies**:
1. 판례 데이터 사전 임베딩 (로딩 스크립트에서)
2. 검색 결과 메모리 캐시 (5분 TTL)
3. 비동기 API 호출 (asyncio)

## Summary Table

| Area | Decision | Key Factor |
|------|----------|------------|
| Data Source | 국가법령정보센터 API | 공식 + 무료 |
| Vector Store | Qdrant (leh_legal_knowledge) | 기존 인프라 활용 |
| Embedding | text-embedding-3-small | 비용 효율 |
| Draft Citation | DraftService 통합 | Clean Architecture |
| Auto-Extract | Backend API 호출 | 중앙집중 관리 |
| Performance | 사전 임베딩 + 캐시 | 5초 목표 달성 |

## 7. 판례 딥링크 URL 생성 (NEW)

### Decision: 국가법령정보센터 법령한글주소 규칙 적용

**참고 문서**: `docs/LAW_HAGUL_ADDRESS_API.md`

**Rationale**:
- 국가법령정보센터 공식 URL 규칙 준수
- 사건번호만으로 판례 원문 직접 접근 가능
- 외부 링크로 판례 전문 열람 기능 대체

**URL 패턴**:

| 유형 | 패턴 | 예시 |
|------|------|------|
| 사건번호 기반 | `/판례/({identifier})` | `/판례/(2020다12345)` |
| 사건번호+판결일 | `/판례/({identifier},{date_val})` | `/판례/(2020다12345,20200315)` |
| 제목+사건번호+판결일 | `/판례/{title}/({identifier},{date_val})` | `/판례/이혼등/(2020므1234,20200601)` |

**Implementation**:
```python
from urllib.parse import quote

BASE_URL = "https://www.law.go.kr"

def generate_precedent_url(case_ref: str, decision_date: str = None) -> str:
    """
    판례 딥링크 URL 생성
    
    Args:
        case_ref: 사건번호 (예: "2020다12345")
        decision_date: 판결일자 YYYYMMDD (예: "20200315")
    
    Returns:
        국가법령정보센터 판례 URL
    """
    # 날짜 형식 변환 (ISO -> YYYYMMDD)
    if decision_date and "-" in decision_date:
        decision_date = decision_date.replace("-", "")
    
    if decision_date:
        params = f"{case_ref},{decision_date}"
    else:
        params = case_ref
    
    encoded_params = quote(params, safe="")
    return f"{BASE_URL}/판례/({encoded_params})"

# 예시
# generate_precedent_url("2020다12345", "20200315")
# → "https://www.law.go.kr/판례/(2020%EB%8B%A412345%2C20200315)"
```

**PrecedentCase.source_url 생성 규칙**:
- 저장 시 `case_ref`와 `decision_date`로 URL 자동 생성
- Frontend에서 "원문 보기" 링크로 사용

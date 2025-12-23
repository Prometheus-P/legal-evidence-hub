# Legal Evidence Hub - 초안 생성 데이터 파이프라인 분석 보고서

> 작성일: 2024-12-23
> 분석자: AI Assistant
> 관련 이슈: #403 (상담내역 통합)

## 1. Executive Summary

LEH의 초안 생성 파이프라인은 **3계층 아키텍처**로 구성된 RAG(Retrieval-Augmented Generation) 기반 시스템입니다:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                               │
│                 POST /cases/{id}/draft-preview                      │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                    Backend (FastAPI)                                │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐            │
│  │DraftService │→ │RAGOrchestrator│→ │PromptBuilder   │            │
│  └─────────────┘  └──────────────┘  └─────────────────┘            │
│         ↓                ↓                   ↓                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐            │
│  │DynamoDB    │  │Qdrant       │  │OpenAI GPT-4o   │            │
│  └─────────────┘  └──────────────┘  └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
                              ↑
                    (증거 데이터 공급)
┌─────────────────────────────┴───────────────────────────────────────┐
│                    AI Worker (Lambda)                               │
│  S3 Upload → Parser → Analysis → Embedding → Storage               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 전체 데이터 흐름

### 2.1 증거 업로드 → 처리 파이프라인 (AI Worker)

```
[사용자: 증거 파일 업로드]
        ↓
[Frontend] → Backend: presigned URL 요청
        ↓
[Frontend] → S3: 직접 업로드
        ↓
[S3 Event] → Lambda Trigger (ObjectCreated)
        ↓
┌─────────────────────────────────────────┐
│ AI Worker Pipeline (7 Stages)           │
├─────────────────────────────────────────┤
│ 1. DOWNLOAD: S3 → /tmp                  │
│ 2. VALIDATE: 파일 크기 (CostGuard)      │
│ 3. HASH: SHA-256 중복 감지              │
│ 4. PARSE: 파일 타입별 파서              │
│    ├─ Image → ImageVisionParser (GPT-4o)│
│    ├─ Audio → AudioParser (Whisper)     │
│    ├─ Video → VideoParser               │
│    ├─ PDF → PDFParser                   │
│    └─ Text → TextParser/KakaoTalkParser │
│ 5. ANALYZE: 법률 분석                   │
│    ├─ Article840Tagger (이혼 사유 분류) │
│    ├─ EvidenceSummarizer (GPT-4o 요약)  │
│    ├─ PersonExtractor (인물 추출)       │
│    └─ RelationshipInferrer (관계 추론)  │
│ 6. EMBED: OpenAI text-embedding-3-small │
│ 7. STORE: DynamoDB + Qdrant             │
└─────────────────────────────────────────┘
```

### 2.2 초안 생성 파이프라인 (Backend)

```
[사용자: 초안 미리보기 요청]
        ↓
POST /cases/{case_id}/draft-preview
        ↓
┌─────────────────────────────────────────────────────────┐
│ DraftService.generate_draft_preview()                   │
├─────────────────────────────────────────────────────────┤
│ Step 1: 권한 검증                                       │
│    └─ CaseMemberRepository.has_access()                 │
│                                                         │
│ Step 2: 증거 메타데이터 조회                            │
│    └─ DynamoDB: get_evidence_by_case(case_id)          │
│    └─ Output: List[EvidenceMetadata]                    │
│                                                         │
│ Step 3: RAG 검색 (RAGOrchestrator)                     │
│    ├─ 3a. 증거 검색 (Qdrant)                           │
│    │   └─ search_evidence_by_semantic()                │
│    │   └─ Collection: case_rag_{case_id}               │
│    │   └─ top_k=5, score_threshold=0.5                 │
│    │                                                    │
│    ├─ 3b. 법률 조문 검색 (Qdrant)                      │
│    │   └─ search_legal_knowledge()                     │
│    │   └─ Collection: leh_legal_knowledge              │
│    │   └─ top_k=3                                      │
│    │                                                    │
│    └─ 3c. 유사 판례 검색 (PrecedentService)            │
│        └─ get_fault_types() → DynamoDB                 │
│        └─ search_similar_precedents() → Qdrant         │
│        └─ Fallback: 8개 Mock 판례 데이터               │
│                                                         │
│ Step 4: 프롬프트 구성 (PromptBuilder)                  │
│    ├─ System Message: 법률 문서 작성 지침              │
│    ├─ User Message:                                    │
│    │   ├─ 사건 정보                                    │
│    │   ├─ 생성할 섹션 (청구취지, 청구원인 등)         │
│    │   ├─ 법률 컨텍스트 (민법 제840조 등)             │
│    │   ├─ 판례 컨텍스트                               │
│    │   └─ 증거 컨텍스트                               │
│    └─ JSON 모드 또는 텍스트 모드                       │
│                                                         │
│ Step 5: GPT-4o 초안 생성                               │
│    └─ generate_chat_completion()                       │
│    └─ Model: gpt-4o-mini (30초 제한 대응)             │
│    └─ Temperature: 0.3 (일관성 우선)                   │
│    └─ max_tokens: 2000                                 │
│                                                         │
│ Step 6: 인용 추출 (CitationExtractor)                  │
│    ├─ extract_evidence_citations()                     │
│    └─ extract_precedent_citations()                    │
│                                                         │
│ Step 7: 응답 반환                                       │
│    └─ DraftPreviewResponse                             │
│        ├─ draft_text: str                              │
│        ├─ citations: List[DraftCitation]               │
│        ├─ precedent_citations: List[PrecedentCitation] │
│        └─ preview_disclaimer: str                      │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 핵심 데이터 구조

### 3.1 DynamoDB - 증거 메타데이터

**테이블:** `leh_evidence`
```json
{
  "evidence_id": "ev_abc123",           // PK
  "case_id": "case_001",                // GSI
  "filename": "chat_log.txt",
  "file_type": "text",
  "file_hash": "sha256:...",
  "s3_key": "cases/001/raw/ev_abc123_chat.txt",
  "status": "completed",

  // AI Worker 분석 결과
  "ai_summary": "2024년 1월 카카오톡 대화에서...",
  "article_840_tags": {
    "categories": ["adultery", "domestic_violence"],
    "confidence": 0.87,
    "matched_keywords": ["외도", "바람"]
  },

  // Qdrant 연결
  "qdrant_id": "chunk_xyz789",
  "chunks_indexed": 42
}
```

### 3.2 Qdrant - 벡터 저장

**컬렉션 패턴:** `case_rag_{case_id}`
```json
{
  "id": "chunk_xyz789",
  "vector": [0.123, 0.456, ...],  // 1536차원
  "payload": {
    "evidence_id": "ev_abc123",
    "case_id": "case_001",
    "content": "피고가 원고에게 '이혼하자'고 발언",
    "sender": "피고",
    "timestamp": "2024-01-15T10:30:00Z",
    "legal_categories": ["irreconcilable_differences"],
    "labels": ["폭언", "불화"]
  }
}
```

### 3.3 API 응답 - DraftPreviewResponse

```json
{
  "case_id": "case_001",
  "draft_text": "소장\n\n당사자\n원고: 김철수\n피고: 이영희\n\n청구취지\n...",
  "citations": [
    {
      "evidence_id": "ev_abc123",
      "snippet": "피고가 '너는 능없다'고 폭언...",
      "labels": ["폭언", "부정행위"]
    }
  ],
  "precedent_citations": [
    {
      "case_ref": "2020다12345",
      "court": "서울가정법원",
      "decision_date": "2020-06-15",
      "summary": "부정행위를 이유로 이혼을 청구한 사건...",
      "similarity_score": 0.85,
      "source_url": "https://www.law.go.kr/판례/..."
    }
  ],
  "generated_at": "2024-12-22T15:30:00Z",
  "preview_disclaimer": "본 문서는 AI가 생성한 미리보기입니다..."
}
```

---

## 4. 핵심 컴포넌트 위치

| 컴포넌트 | 파일 경로 | 역할 |
|----------|----------|------|
| **DraftService** | `backend/app/services/draft_service.py` | 초안 생성 오케스트레이션 |
| **RAGOrchestrator** | `backend/app/services/draft/rag_orchestrator.py` | RAG 검색 조율 |
| **PromptBuilder** | `backend/app/services/draft/prompt_builder.py` | GPT-4o 프롬프트 구성 |
| **CitationExtractor** | `backend/app/services/draft/citation_extractor.py` | 인용 추출 |
| **PrecedentService** | `backend/app/services/precedent_service.py` | 판례 검색 |
| **Qdrant Utils** | `backend/app/utils/qdrant.py` | 벡터 검색 |
| **OpenAI Client** | `backend/app/utils/openai_client.py` | GPT-4o/임베딩 호출 |
| **DynamoDB Utils** | `backend/app/utils/dynamo.py` | 증거 메타데이터 조회 |
| **Lambda Handler** | `ai_worker/handler.py` | AI Worker 진입점 |
| **Parsers** | `ai_worker/src/parsers/` | 파일 타입별 파서 |
| **Analysis** | `ai_worker/src/analysis/` | 분석 엔진들 |
| **Storage** | `ai_worker/src/storage/` | DynamoDB/Qdrant 저장 |

---

## 5. 성능 최적화 설정

| 항목 | 설정값 | 사유 |
|------|--------|------|
| LLM Model | `gpt-4o-mini` | API Gateway 30초 제한 대응 |
| Temperature | `0.3` | 법률 문서 일관성 우선 |
| max_tokens | `2000` | 적절한 초안 길이 |
| Embedding Model | `text-embedding-3-small` | 1536차원, 저비용 |
| Evidence top_k | `5` | 응답 시간 최적화 |
| Legal top_k | `3` | 컨텍스트 최소화 |
| Precedent top_k | `5` | 충분한 참조 제공 |
| score_threshold | `0.5` | 품질 필터링 |
| Timeout | `25초` | API Gateway 여유 확보 |

---

## 6. 데이터 파이프라인 특징

### 6.1 강점
- **End-to-End 자동화**: 증거 업로드부터 초안 생성까지 완전 자동화
- **멱등성 보장**: 3단계 중복 검사 (evidence_id, hash, s3_key)
- **케이스 격리**: `case_rag_{case_id}` 패턴으로 데이터 격리
- **다중 소스 통합**: 증거 + 법률 조문 + 판례 통합 검색
- **Fallback 메커니즘**: 판례 검색 실패 시 Mock 데이터 제공
- **법적 근거 강화**: 민법 제840조 자동 인용, 판례 참조

### 6.2 제약사항
- **Lambda 제한**: /tmp 512MB, 실행 시간 15분
- **API Gateway**: 30초 타임아웃 → gpt-4o-mini 사용
- **Qdrant 의존**: 컬렉션 사전 생성 필요
- **OpenAI 비용**: Vision, Whisper, Embedding 호출 비용

### 6.3 품질 관리
- **증거 기반 생성**: System Message에서 "증거에만 기반" 강제
- **인용 추적**: 모든 주장에 [갑 제N호증] 형식 명시
- **변호사 검토**: "Preview Only" - 자동 제출 없음
- **SHA-256 해싱**: 증거 무결성 검증

---

## 7. 시각화: 전체 데이터 흐름

```
                    ┌───────────────────────────────────────┐
                    │           사용자 (Frontend)           │
                    └─────────────┬─────────────────────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
    ┌─────────────┐      ┌─────────────┐       ┌─────────────┐
    │ 증거 업로드  │      │ 초안 미리보기│       │ 판례 검색   │
    └──────┬──────┘      └──────┬──────┘       └──────┬──────┘
           │                    │                     │
           ▼                    │                     │
    ┌─────────────┐             │                     │
    │    S3       │             │                     │
    └──────┬──────┘             │                     │
           │                    │                     │
           ▼                    │                     │
    ┌─────────────┐             │                     │
    │ AI Worker   │             │                     │
    │  (Lambda)   │             │                     │
    │ ┌─────────┐ │             │                     │
    │ │ Parser  │ │             │                     │
    │ └────┬────┘ │             │                     │
    │      ▼      │             │                     │
    │ ┌─────────┐ │             │                     │
    │ │Analysis │ │             │                     │
    │ └────┬────┘ │             │                     │
    │      ▼      │             │                     │
    │ ┌─────────┐ │             │                     │
    │ │Embedding│ │             │                     │
    │ └────┬────┘ │             │                     │
    └──────┼──────┘             │                     │
           │                    │                     │
           ├────────────────────┼─────────────────────┤
           ▼                    ▼                     ▼
    ┌─────────────┐      ┌─────────────┐       ┌─────────────┐
    │  DynamoDB   │◄─────│   Backend   │──────►│   Qdrant    │
    │  (메타데이터)│      │  (FastAPI)  │       │  (벡터DB)   │
    └─────────────┘      └──────┬──────┘       └─────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │  OpenAI API │
                         │ (GPT-4o)    │
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │ 초안 + 인용  │
                         └─────────────┘
```

---

## 8. 결론

LEH의 초안 생성 파이프라인은 **RAG 기반의 멀티 소스 검색**과 **GPT-4o 생성**을 결합하여:

1. **증거 기반의 법적 문서 생성** - 모든 주장에 증거 인용 필수
2. **법률 지식 통합** - 민법 840조 등 관련 법률 자동 참조
3. **판례 인용** - 유사 사건 검색으로 논리 강화
4. **변호사 검토 필수** - AI 미리보기만 제공, 자동 제출 없음

이 파이프라인은 **변호사의 업무 효율화**를 목표로 하며, 최종 법적 판단은 항상 전문가의 검토를 거칩니다.

---

## 9. 상세 데이터 스키마

### 9.1 DynamoDB - `leh_evidence` 테이블

**키 구조:**
| 키 타입 | 필드 | 설명 |
|--------|------|------|
| **PK (Hash)** | `evidence_id` | 증거 고유 ID (ev_xxx) |
| **GSI-1** | `case_id-index` | 케이스별 조회 |
| **GSI-2** | `file_hash-index` | 중복 검사 |
| **GSI-3** | `s3_key-index` | S3 키 기반 조회 |

**필드 정의:**
```
┌─────────────────────┬──────────┬──────────────────────────────────┐
│ 필드명              │ 타입     │ 설명                             │
├─────────────────────┼──────────┼──────────────────────────────────┤
│ evidence_id         │ String   │ PK - ev_{uuid}                   │
│ case_id             │ String   │ GSI - 사건 ID                    │
│ filename            │ String   │ 원본 파일명                      │
│ file_type           │ String   │ kakaotalk|pdf|image|audio|video  │
│ file_hash           │ String   │ SHA-256 (중복 검사)              │
│ s3_key              │ String   │ cases/{case_id}/raw/{ev_id}_{fn} │
│ status              │ String   │ pending→processing→completed    │
├─────────────────────┼──────────┼──────────────────────────────────┤
│ content             │ String   │ 파싱된 텍스트 (50KB 제한)        │
│ ai_summary          │ String   │ GPT-4o 생성 요약                 │
│ article_840_tags    │ Map      │ {categories, confidence, keywords}│
│ qdrant_id           │ String   │ Qdrant 벡터 ID                   │
│ total_messages      │ Number   │ 파싱된 메시지 수                 │
├─────────────────────┼──────────┼──────────────────────────────────┤
│ created_at          │ String   │ ISO8601 생성 시간                │
│ processed_at        │ String   │ ISO8601 처리 완료 시간           │
│ error_message       │ String   │ 오류 메시지 (failed 시)          │
└─────────────────────┴──────────┴──────────────────────────────────┘
```

**article_840_tags 구조:**
```json
{
  "categories": ["adultery", "domestic_violence"],
  "confidence": 0.87,
  "matched_keywords": ["외도", "바람", "폭력"]
}
```

### 9.2 Qdrant - 벡터 컬렉션

**컬렉션 패턴:**
| 컬렉션명 | 용도 | 격리 수준 |
|---------|------|----------|
| `case_rag_{case_id}` | 케이스별 증거 | 케이스별 완전 격리 |
| `leh_legal_knowledge` | 법률 조문/판례 | 전역 (공유) |
| `legal_templates` | 문서 템플릿 | 전역 (공유) |

**벡터 설정:**
```
Size: 1536 (text-embedding-3-small)
Distance: COSINE
```

**Payload 필드:**
```
┌─────────────────────┬──────────┬───────────┬──────────────────────┐
│ 필드명              │ 타입     │ 인덱스    │ 설명                 │
├─────────────────────┼──────────┼───────────┼──────────────────────┤
│ case_id             │ String   │ KEYWORD   │ 필터링용             │
│ evidence_id         │ String   │ KEYWORD   │ 증거 ID              │
│ chunk_id            │ String   │ KEYWORD   │ 청크 ID              │
│ document            │ String   │ -         │ 원본 텍스트          │
│ sender              │ String   │ KEYWORD   │ 발신자               │
│ timestamp           │ String   │ -         │ ISO8601              │
├─────────────────────┼──────────┼───────────┼──────────────────────┤
│ file_type           │ String   │ KEYWORD   │ 파일 타입            │
│ legal_categories    │ List     │ -         │ 법적 분류            │
│ confidence_level    │ Integer  │ INTEGER   │ 신뢰도 1-5           │
├─────────────────────┼──────────┼───────────┼──────────────────────┤
│ line_number         │ Integer  │ INTEGER   │ 텍스트 라인 (txt)    │
│ page_number         │ Integer  │ INTEGER   │ 페이지 번호 (pdf)    │
│ segment_start_sec   │ Float    │ -         │ 시작 시간 (audio)    │
│ segment_end_sec     │ Float    │ -         │ 끝 시간 (audio)      │
└─────────────────────┴──────────┴───────────┴──────────────────────┘
```

### 9.3 PostgreSQL (RDS) - 핵심 테이블

**ERD 관계:**
```
users ─┬─< cases (created_by)
       │
       └─< case_members >─ cases

cases ─< evidence (case_id)
      │
      └─< audit_logs (object_id)
```

**테이블: `users`**
```sql
id              VARCHAR PK      -- user_{uuid[:12]}
email           VARCHAR UNIQUE NOT NULL
hashed_password VARCHAR NOT NULL
name            VARCHAR NOT NULL
role            ENUM(LAWYER|STAFF|ADMIN|CLIENT|DETECTIVE)
status          ENUM(ACTIVE|INACTIVE)
created_at      TIMESTAMP NOT NULL
```

**테이블: `cases`**
```sql
id          VARCHAR PK      -- case_{uuid[:12]}
title       VARCHAR NOT NULL
client_name VARCHAR
description TEXT
status      ENUM(ACTIVE|OPEN|IN_PROGRESS|REVIEW|CLOSED)
created_by  VARCHAR FK → users.id
created_at  TIMESTAMP NOT NULL
updated_at  TIMESTAMP NOT NULL
deleted_at  TIMESTAMP       -- Soft delete
```

**테이블: `case_members`**
```sql
case_id     VARCHAR PK/FK → cases.id
user_id     VARCHAR PK/FK → users.id
role        ENUM(OWNER|MEMBER|VIEWER)
```

**테이블: `evidence`**
```sql
id          VARCHAR PK      -- UUID
case_id     VARCHAR FK → cases.id (indexed)
file_name   VARCHAR NOT NULL
s3_key      VARCHAR NOT NULL
file_type   VARCHAR         -- MIME type
status      VARCHAR         -- pending|completed|failed
ai_labels   TEXT            -- JSON array
ai_summary  TEXT
uploaded_by VARCHAR FK → users.id (indexed)
created_at  TIMESTAMP NOT NULL
```

**테이블: `audit_logs`**
```sql
id          VARCHAR PK      -- audit_{uuid[:12]}
user_id     VARCHAR FK → users.id
action      VARCHAR         -- VIEW_EVIDENCE|CREATE_CASE|...
object_id   VARCHAR         -- evidence_id or case_id
timestamp   TIMESTAMP NOT NULL
-- INDEX: (user_id, timestamp)
```

### 9.4 데이터 흐름별 매핑

**증거 업로드 → 저장:**
```
Frontend Upload
    │
    ▼
PostgreSQL.evidence: INSERT {case_id, file_name, status='pending'}
    │
    ▼
S3: PUT cases/{case_id}/raw/{evidence_id}_{filename}
    │
    ▼ (Lambda Trigger)
    │
AI Worker Pipeline
    │
    ├─→ DynamoDB: UPDATE {
    │       evidence_id, case_id, content, ai_summary,
    │       article_840_tags, status='completed'
    │   }
    │
    └─→ Qdrant: UPSERT {
            vector: [1536 floats],
            payload: {case_id, document, sender, timestamp, ...}
        }
```

**초안 생성 조회:**
```
Draft Request
    │
    ├─→ DynamoDB: QUERY case_id-index
    │       → 증거 메타데이터 (article_840_tags)
    │
    ├─→ Qdrant: SEARCH case_rag_{case_id}
    │       → 유사 증거 청크 (top_k=5)
    │
    ├─→ Qdrant: SEARCH leh_legal_knowledge
    │       → 관련 법률 조문 (top_k=3)
    │
    └─→ GPT-4o: generate_chat_completion
            → 초안 텍스트 + 인용
```

### 9.5 인덱스 전략 요약

| DB | 인덱스 | 용도 |
|----|--------|------|
| **DynamoDB** | evidence_id (PK) | 단건 조회 |
| | case_id-index (GSI) | 케이스별 증거 목록 |
| | file_hash-index (GSI) | 중복 검사 |
| **Qdrant** | case_id (KEYWORD) | 케이스 필터링 |
| | sender (KEYWORD) | 발신자 필터링 |
| | confidence_level (INTEGER) | 신뢰도 필터링 |
| **PostgreSQL** | cases.deleted_at | 소프트 삭제 제외 |
| | evidence.case_id | 케이스별 증거 |
| | audit_logs.(user_id, timestamp) | 감사 추적 |

### 9.6 데이터 무결성 제약

| 제약 | 구현 | 설명 |
|-----|------|------|
| **케이스 격리** | Qdrant 컬렉션/필터 | 케이스 간 데이터 접근 차단 |
| **중복 방지** | DynamoDB file_hash-index | 동일 파일 재처리 방지 |
| **멱등성** | ConditionExpression | 중복 Lambda 실행 방지 |
| **감사 추적** | audit_logs 불변 INSERT | 모든 액션 기록 |
| **Soft Delete** | deleted_at 필드 | 물리 삭제 없음 |

---

## 10. 테스트 전략 및 모니터링

### 10.1 테스트 계층 구조

| 계층 | 위치 | 커버리지 목표 | 실행 방법 |
|------|------|--------------|----------|
| **Backend Unit** | `backend/tests/unit/` | 70% (목표 80%) | `pytest -m unit` |
| **Backend Integration** | `backend/tests/test_integration/` | - | `pytest -m integration` |
| **AI Worker Unit** | `ai_worker/tests/` | 70% (목표 80%) | `pytest -m unit` |
| **Frontend** | `frontend/src/__tests__/` | 35% (목표 50%) | `npm test` |

### 10.2 Mock 전략

**Backend (`conftest.py` 850줄):**
```
┌───────────────┬─────────────────┬─────────────────────────────┐
│ 대상          │ Mock 방식       │ 스코프                      │
├───────────────┼─────────────────┼─────────────────────────────┤
│ Database      │ SQLite in-memory│ Session                     │
│ DynamoDB      │ boto3 patch     │ Session + Function reset    │
│ S3            │ boto3 patch     │ Session                     │
│ OpenAI        │ patch decorator │ Function                    │
│ Qdrant        │ patch decorator │ Function                    │
└───────────────┴─────────────────┴─────────────────────────────┘
```

**AI Worker (`conftest.py` 287줄):**
```python
class MockDynamoDBTable:
    def put_item(self, Item): ...
    def get_item(self, Key): ...
    def query(self, **kwargs): ...  # case_id 필터링

class MockQdrantClient:
    def upsert(self, collection_name, points): ...
    def search(self, collection_name, query_vector, ...): ...
```

**Frontend (`jest.setup.js`):**
```javascript
jest.mock('@/lib/api/evidence', () => ({
    getEvidence: jest.fn(async () => ({ data: mockData })),
    uploadToS3: jest.fn(async () => true),
}));
```

### 10.3 DraftService 테스트 패턴

**파일:** `backend/tests/unit/test_draft_service.py` (1018줄)

```python
# RAG 검색 테스트
@patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic')
@patch('app.services.draft.rag_orchestrator.search_legal_knowledge')
def test_perform_rag_search(mock_legal, mock_evidence):
    # 검색 호출 검증
    # 결과 포맷 검증

# 초안 생성 전체 파이프라인
@patch('app.services.draft_service.generate_chat_completion')
def test_generate_draft_preview_success():
    # 권한 검증 → RAG 검색 → GPT 호출 → 인용 추출
```

### 10.4 모니터링 (JobTracker)

**파일:** `ai_worker/src/utils/observability.py`

```python
tracker = JobTracker.from_s3_event(bucket_name, object_key)

# Stage별 추적
with tracker.stage(ProcessingStage.PARSE) as stage:
    parsed = parser.parse(file_path)
    stage.log("완료", extra={"count": len(parsed)})

# 에러 기록
tracker.record_error(ErrorType.RATE_LIMIT, str(e))

# CloudWatch 메트릭
tracker.to_cloudwatch_metrics()
```

**ProcessingStage:**
```
DOWNLOAD → HASH → PARSE → ANALYZE → EMBED → STORE → COMPLETE
```

**ErrorType 분류:**
```
TIMEOUT | API_ERROR | PARSE_ERROR | STORAGE_ERROR
VALIDATION_ERROR | RATE_LIMIT | DUPLICATE | PERMISSION_ERROR
```

### 10.5 JSON 로깅 (CloudWatch 호환)

```python
# 출력 형식
{
  "level": "INFO",
  "logger": "parser.kakaotalk",
  "message": "파싱 완료",
  "timestamp": "2024-12-22T15:30:00Z",
  "case_id": "case123",
  "duration_ms": 1234
}
```

**CloudWatch Logs Insights 쿼리:**
```sql
# Stage별 처리 시간
fields stage, duration_ms
| filter case_id = "case123"
| stats avg(duration_ms) by stage

# 에러 분류별 집계
fields error_type
| stats count() by error_type
```

### 10.6 E2E 테스트 체크리스트

```
□ S3 증거 업로드 (PDF, MP3, PNG, TXT)
□ Lambda 자동 트리거 (CloudWatch Logs)
□ Parser 출력 검증 (ParsedMessage)
□ DynamoDB 메타데이터 저장
□ Qdrant 벡터 저장 (1536차원)
□ Article 840 태깅
□ Backend RAG 검색
□ 초안 생성 + 인용
□ Frontend 표시
```

### 10.7 CI/CD 테스트 게이트

```yaml
# GitHub Actions
Backend:  pytest --cov=app --cov-fail-under=70
AI Worker: pytest --cov=src --cov-fail-under=70
Frontend: npm test -- --coverage
```

### 10.8 테스트 실행 명령어

```bash
# Backend
cd backend
pytest                           # 전체
pytest -m unit                   # 단위만
pytest --cov=app --cov-report=html  # 커버리지

# AI Worker
cd ai_worker
pytest                           # 전체
pytest -m unit                   # 단위만
RUN_INTEGRATION_TESTS=1 pytest -m integration  # 통합

# Frontend
cd frontend
npm test                         # 전체
npm test -- --coverage           # 커버리지
```

---

## 11. 법률 절차 기반 논리적 흐름 (UI 시각화 권장)

### 11.1 4단계 데이터 파이프라인

```
┌─────────────────────────────────────────────────────────────────────┐
│                    1️⃣ 데이터 수집 (Input Layer)                      │
│  ┌─────────────────┐    ┌─────────────────┐                         │
│  │   증거자료       │    │   상담내역       │                         │
│  │ (Evidence)      │    │ (Consultation)  │                         │
│  │ • 파일 업로드    │    │ • 의뢰인 진술    │                         │
│  │ • STT/OCR/Vision│    │ • 변호사 메모    │                         │
│  └────────┬────────┘    └────────┬────────┘                         │
└───────────┼──────────────────────┼──────────────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    2️⃣ AI 분석 (Processing Layer)                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     법률분석 (Legal Analysis)                  │   │
│  │  • Article 840 태깅 (이혼 사유 분류)                          │   │
│  │  • 키포인트 추출                                              │   │
│  │  • 유사 판례 검색 (Qdrant RAG)                               │   │
│  │  • 법적 근거 식별                                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    3️⃣ 구조화 (Structuring Layer)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │   타임라인       │  │   관계도        │  │   재산분할      │      │
│  │ (Timeline)      │  │ (Relations)     │  │ (Assets)       │      │
│  │ • 사건 시간순    │  │ • 당사자 식별   │  │ • 자산 목록    │      │
│  │ • 절차 진행상황  │  │ • 관계 연결     │  │ • 분할 비율    │      │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │
└───────────┼────────────────────┼────────────────────┼───────────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    4️⃣ 문서 생성 (Output Layer)                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     초안생성 (Draft Generation)               │   │
│  │  • RAG: 증거 + 법률조문 + 판례 + 상담내역 통합               │   │
│  │  • GPT-4o: 법률 문서 생성                                    │   │
│  │  • 인용 자동 추출 [갑 제N호증]                               │   │
│  │  • DOCX/PDF 내보내기                                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.2 계층별 데이터 의존성

| 단계 | 계층 | 입력 데이터 | 출력 데이터 |
|:---:|------|------------|------------|
| **1** | 증거자료 | 원본 파일 | AI 요약, 라벨, Article840 태그 |
| **1** | 상담내역 | 의뢰인 진술 | 변호사 메모, 핵심 정보 |
| **2** | 법률분석 | 증거 + 상담 | 키포인트, 판례, 법적 근거 |
| **3** | 타임라인 | 증거(시간), 분석결과 | 사건 흐름도 |
| **3** | 관계도 | 분석결과(인물추출) | 당사자 관계 그래프 |
| **3** | 재산분할 | 증거(금융), 분석결과 | 분할 계산서 |
| **4** | 초안생성 | **1~3 모든 데이터** | 법률 문서 |

### 11.3 권장 UI 탭 순서 (논리적 흐름 기준)

| 현재 순서 | 권장 순서 | 단계 |
|:---------:|:---------:|:----:|
| 1. 증거자료 | 1. 증거자료 | 수집 |
| 2. 타임라인 | **2. 상담내역** | 수집 |
| 3. 상담내역 | **3. 법률분석** | 분석 |
| 4. 법률분석 | **4. 타임라인** | 구조화 |
| 5. 관계도 | 5. 관계도 | 구조화 |
| 6. 재산분할 | 6. 재산분할 | 구조화 |
| 7. 초안생성 | 7. 초안생성 | 생성 |

### 11.4 시각화 UI 제안

**파이프라인 진행 상황 표시 (케이스 상세 페이지 상단)**
```
[수집] ━━━━▶ [분석] ━━━━▶ [구조화] ━━━━▶ [생성]
  ●           ○           ○            ○
 완료        진행중       대기          대기

● 완료 (녹색)  ○ 진행중 (파랑)  ○ 대기 (회색)
```

**각 단계 완료 조건:**
- **수집**: 증거 1개 이상 + 상담내역 1개 이상
- **분석**: 모든 증거 분석 완료 (status='completed')
- **구조화**: 타임라인/관계도/재산분할 중 1개 이상 데이터 존재
- **생성**: 초안 생성 완료

---

## 12. 데이터 소스 통합 현황

### 12.1 현재 통합된 데이터 소스

| 데이터 소스 | 저장소 | RAG 통합 | 초안 생성 반영 |
|------------|--------|----------|---------------|
| **증거자료** | DynamoDB + Qdrant | ✅ | ✅ |
| **법률 조문** | Qdrant (`leh_legal_knowledge`) | ✅ | ✅ |
| **판례** | Qdrant + Mock 데이터 | ✅ | ✅ |

### 12.2 미통합 데이터 소스 (개선 필요)

| 데이터 소스 | 현재 상태 | 우선순위 | 담당자 | 이슈 |
|------------|----------|---------|--------|------|
| **상담내역** | Frontend만 존재 (Backend 없음) | 1차 | @vsun410 | #403 |
| **채팅** | 미구현 | 2차 | TBD | - |
| **캘린더** | 미구현 | 2차 | TBD | - |

### 12.3 상담내역 통합 상세 (Issue #403)

**현재 문제점:**
- `ConsultationHistoryTab.tsx`가 존재하지만 Backend 연동 없음
- PostgreSQL에 `consultations` 테이블 없음
- RAG 파이프라인에 상담 데이터 미포함
- 초안 생성 시 변호사 메모/의뢰인 진술 미반영

**필요 작업:**
1. Backend: `consultations` DB 모델 생성
2. Backend: ConsultationRepository + ConsultationService
3. Backend: `/cases/{id}/consultations` API 엔드포인트
4. AI Worker: 상담 텍스트 임베딩 + Qdrant 저장
5. Backend: DraftService의 RAG 검색에 상담 데이터 통합
6. Backend: PromptBuilder에 상담 컨텍스트 추가

---

## 13. 관련 이슈

| 이슈 번호 | 제목 | 담당자 | 우선순위 |
|----------|------|--------|---------|
| #403 | 상담내역 데이터 소스를 초안 생성 RAG 파이프라인에 통합 | @vsun410 | 1차 |
| TBD | UI 탭 순서 논리적 흐름 기준 변경 | @Prometheus-P | - |
| TBD | 파이프라인 진행 상황 시각화 UI | @Prometheus-P | - |

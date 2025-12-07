# AI_PIPELINE_DESIGN.md

### *증거 분석·요약·라벨링·RAG 구축 파이프라인*

**버전:** v2.1
**작성일:** 2025-11-18
**최종 수정:** 2025-12-03
**작성자:** Team L(AI)
**참고 문서:**

* `PRD.md`
* `ARCHITECTURE.md`
* `json_template_implementation_plan.md` (신규)

---

## 변경 이력 (Change Log)

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| v2.0 | 2025-11-18 | Team L | 최초 작성 |
| v2.1 | 2025-12-03 | L-work | TemplateStore 추가, JSON 템플릿 시스템 문서화 |

---

# 📌 0. 문서 목적

본 문서는 LEH(Legal Evidence Hub)에서 사용되는
**전체 AI 파이프라인 구조**를 정의한다.

AI Worker(L)가 수행하는:

* 증거 ingest
* 파일 타입 자동 판별
* STT/OCR/Parsing
* 요약(Summarization)
* 의미 분석(유책사유/화자/감정/시점 등)
* Embedding 생성
* 사건별 RAG Index 구축(Qdrant)

전 과정을 상세히 기술한다.

백엔드 및 프론트엔드 개발자는 AI Worker가 **어떤 결과를 생성하며**,
그 결과가 **DynamoDB/Qdrant**에서 어떻게 활용되는지 이 문서를 참고한다.

---

# 🧭 1. AI 파이프라인 전체 개요

LEH AI 파이프라인은 다음 특징을 가진다:

### ✔ 100% 자동화

S3 업로드 → S3 Event → AI Worker 실행 → DynamoDB / Qdrant 업데이트

### ✔ 증거 타입별 맞춤 처리

* Text → 구조화 파싱
* Image → Vision OCR + 상황/감정 설명
* Audio → Whisper STT + diarization
* Video → 음성 추출 후 STT + frame 분석(선택)
* PDF → Text Extract + OCR fallback

### ✔ 사건 단위 RAG 구축

각 사건은 독립된 embedding index(`case_rag_<case_id>`)로 관리된다.

### ✔ 법률 도메인 최적화

민법 제840 기준 자동 라벨링
유책사유 기반 필터링
타임라인 생성

---

# 🏗 2. 파이프라인 전체 다이어그램

               ┌───────────────────────┐
               │   S3 Evidence Upload  │
               └─────────┬─────────────┘
                         ▼ (Event)
                ┌──────────────────┐
                │ AI Worker (L)    │
                │ Lambda/ECS       │
                └───────┬──────────┘
      ┌──────────────────┼────────────────────┐
      ▼                  ▼                    ▼
┌─────────────┐   ┌───────────────┐   ┌────────────────┐
│ Preprocess  │   │ Content       │   │ Semantic       │
│ File Type   │   │ Extraction    │   │ Analysis       │
└──────┬──────┘   └──────┬────────┘   └────────┬───────┘
       ▼                 ▼                    ▼
┌─────────────┐   ┌───────────────┐   ┌────────────────┐
│ OCR / STT   │   │ Summarization │   │ Labeling       │
│ Parsing     │   │ (GPT-4o)      │   │ (유책사유 등)  │
└──────┬──────┘   └──────┬────────┘   └────────┬───────┘
       ▼                 ▼                    ▼
┌────────────────────────────────────────────────────────┐
│                Embedding Generation                    │
│             (OpenAI / Voyage / Local)                  │
└───────────────────────┬────────────────────────────────┘
                        ▼
                ┌───────────────┐
                │ Qdrant RAG │
                │ 사건별 index   │
                └──────┬────────┘
                        ▼
                ┌───────────────┐
                │ DynamoDB JSON │
                │ Evidence Meta │
                └───────────────┘

---

# 🧩 3. 파이프라인 단계 상세

## 3.1 Step 1 — 파일 타입 자동 판별

S3에서 파일을 임시 다운로드 후 확장자·헤더 기반으로 판별:

| 타입    | 판별 방식                        |
| ----- | ---------------------------- |
| text  | `.txt`, MIME=text/plain      |
| image | `.jpg`, `.png`, Vision check |
| audio | `.mp3`, `.m4a`               |
| video | `.mp4`                       |
| pdf   | `.pdf`                       |

PDF의 초기 Paralegal 설계에서도 동일하게 파일 타입 기반 분기 흐름을 사용했다.

---

## 3.2 Step 2 — Content Extraction

### 3.2.1 Text File Parsing

**카카오톡 형태가 아니어도 아무 텍스트나 자동 정규화 처리**

* 날짜/시간 감지 (`regex + GPT assist`)
* 대화 구조 추출:

  json
  { "speaker": "", "timestamp": "", "message": "" }
  
* 시스템 메시지/이모지 제거
* 중복 메시지 제거

---

### 3.2.2 Image → OCR + Vision 분석

(PDF에서도 OCR + Vision 정보 추출 구조를 명확히 언급함 )

사용 모델:

* **GPT-4o Vision(우선)**
* Tesseract(백업)

추출 정보:

* 텍스트 내용
* 장면 요약
* 인물/사람 여부
* 감정/톤
* 법률적으로 중요한 표현 감지

---

### 3.2.3 Audio → STT + Diarization

**Whisper 기반**, PDF의 기존 설계와 동일.

추출 결과:

json
[
  {
    "speaker": "S1",
    "timestamp": "00:01:23",
    "text": "그만 좀 소리 질러!"
  }
]

필요 기능:

* 화자 분리
* 욕설/폭언 감지
* 타임스탬프 포함

---

### 3.2.4 Video → Audio + Frame 분석

필수는 아님(MVP 옵션), 구조만 정의:

* ffmpeg로 audio 추출 → STT 처리
* 프레임 기반 OCR (폭행 장면 여부 감지 가능)

---

### 3.2.5 PDF → Text Extract → OCR fallback

* 텍스트 PDF → PyPDF2
* 스캔본 PDF → OCR → Vision 분석

---

# 🧠 4. Step 3 — Summarization (요약)

요약은 기존 Paralegal 시스템에서 핵심 기능이었다.
PDF 설계에서 GPT 기반 요약 프로세스를 도입했으며, LEH에서 이를 확장한다.

### 요약 규칙

1. **법률적 사건 흐름 중심**
2. **날짜 / 화자 / 행위 / 감정 포함**
3. **유책사유 관련 내용은 강조**
4. **증거 번호 자동 표시 가능**

### 출력 예시

json
"2021-03-22 새벽, 피고가 고성을 지르며 폭언하였고 원고는 공포감을 느꼈다."

---

# ⚖️ 5. Step 4 — Semantic Analysis (의미 분석)

### 5.1 유책사유 자동 라벨링 (민법 제840 기준)

* 부정행위
* 악의의 유기
* 학대
* 유기
* 계속적 불화
* 3년 실종
* 기타 중대한 사유

### 5.2 기타 Legal Features

* 감정 분석
* 위험 표현(협박, 위협, 통제)
* 관계 패턴
* 사실관계 핵심 포인트(인정/부정 문장)

---

# 🔍 6. Step 5 — Embedding 생성

### Embedding 모델

* OpenAI text-embedding-3-large
* 또는 Voyage 등 사건 특화 모델
* Qdrant와 호환되는 1536~3072 dimension

### Embedding 대상

* OCR/STT 전체 텍스트
* 요약
* 파싱된 대화 message
* 사건 핵심 포인트

---

# 🔎 7. Step 6 — 사건별 RAG Index 구축 (Qdrant)

PDF에서도 RAG 기반 Draft 생성이 핵심 기능으로 강조됨.
LEH에서는 이를 사건 단위로 완전히 분리한다.

### 인덱스 이름

case_rag_{case_id}

### 문서 구조

json
{
  "id": "case_123_ev_3",
  "case_id": "case_123",
  "evidence_id": "ev_3",
  "content": "전체 텍스트",
  "summary": "...",
  "labels": ["폭언"],
  "timestamp": "2024-12-21",
  "vector": [0.12, ...]
}

---

# 🗂 8. Step 7 — DynamoDB 저장 구조

Worker는 최종 JSON을 DynamoDB에 저장한다:

json
{
  "case_id": "case_123",
  "evidence_id": "ev_3",
  "type": "audio",
  "timestamp": "2024-12-25",
  "speaker": "S1",
  "labels": ["폭언"],
  "ai_summary": "...",
  "insights": ["지속적 고성"],
  "content": "STT 결과 전문",
  "s3_key": "cases/123/raw/xx.m4a",
  "qdrant_id": "case_123_ev_3"
}

---

# 🧩 9. Step 8 — 타임라인 데이터 생성

타임라인 구성 요소:

* timestamp
* speaker
* main_event (요약 기반)
* evidence_id

타임라인은 FE에서 그대로 렌더링할 수 있도록 다음 형태로 저장:

json
{
  "timeline_event": {
    "evidence_id": "ev_3",
    "timestamp": "2024-12-25T10:20:00Z",
    "description": "피고가 고성을 지르며 폭언함",
    "labels": ["폭언"]
  }
}

---

# 🛠 10. Worker 내부 설계

### 필수 파이썬 모듈

* boto3 (S3, DynamoDB)
* Qdrant client
* openai (4o / Whisper)
* ffmpeg/ffprobe
* regex/mecab(선택)
* pydantic

---

### Worker 구조

ai_worker/
├── handler.py          # Lambda 핸들러
├── processor/
│   ├── router.py       # 타입별 분기
│   ├── text_parser.py
│   ├── ocr.py
│   ├── stt.py
│   ├── semantic.py
│   ├── embed.py
│   └── timeline.py
└── utils/
    ├── s3.py
    ├── qdrant.py
    ├── dynamo.py
    └── ffmpeg.py

---

# 🚨 11. 에러 핸들링 & 재처리

### Worker 실패 시

* 실패 사유 로그 기록
* DynamoDB에 `"status": "failed"` 저장
* S3 → DLQ(SQS Dead Letter Queue) 연동 가능

### 재처리

POST /admin/reprocess-evidence

---

# 🧪 12. 테스트 전략

### Unit Test

* 타입별 parser 테스트
* OCR mock test
* STT mock test
* 유책사유 라벨링 테스트
* embedding 사이즈 검증

### Integration Test

* S3 → Worker → DynamoDB 전체 플로우
* Qdrant RAG 쿼리

---

# 🤝 13. 백엔드/프론트 연동 인터페이스

| 목적            | 출처          | 목적지      |
| ------------- | ----------- | -------- |
| 증거 metadata   | AI Worker   | DynamoDB |
| 증거 검색         | Qdrant  | Backend  |
| Draft Preview | BE → GPT-4o | FE       |
| Timeline      | DynamoDB    | FE       |

---

# 📄 14. 법률 문서 템플릿 시스템 (v2.1 신규)

> **12/3 추가**: 컨퍼런스 인사이트 기반 - JSON 템플릿으로 문서 품질 향상

## 14.1 개요

법률 문서 템플릿을 **JSON 형식(문서 형식 메타데이터 포함)**으로 저장하여
GPT-4o가 구조화된 출력을 생성하도록 유도한다.

### 핵심 인사이트
- 단순 텍스트 대신 **JSON 스키마 + 포맷 정보**를 제공하면 출력 품질 향상
- 들여쓰기, 정렬, 줄간격 등 문서 형식까지 스키마에 포함

## 14.2 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                      Qdrant Collections                         │
├─────────────────────────────────────────────────────────────────┤
│  case_rag_{case_id}    │ 증거 임베딩 (사건별)                    │
│  leh_legal_knowledge   │ 법률 조문/판례                          │
│  legal_templates       │ 문서 템플릿 JSON 스키마 (신규)          │
└─────────────────────────────────────────────────────────────────┘
```

## 14.3 TemplateStore 클래스

**위치**: `ai_worker/src/storage/template_store.py`

```python
class TemplateStore:
    """법률 문서 템플릿 저장소"""

    def get_template(template_type: str) -> dict
        # 템플릿 타입으로 JSON 스키마 조회

    def search_templates(query: str) -> list[dict]
        # 쿼리로 적합한 템플릿 검색 (벡터 유사도)

    def upload_template(template_type, schema, example, ...) -> str
        # 새 템플릿 업로드

    def get_schema_for_generation(template_type: str) -> str
        # GPT 프롬프트용 JSON 스키마 문자열 반환
```

## 14.4 JSON 스키마 구조

**예시**: `docs/divorce_complaint_schema.json`

```json
{
  "document_type": "이혼소장",
  "header": {
    "title": {
      "text": "소    장",
      "format": {
        "alignment": "center",
        "font_size": 18,
        "bold": true,
        "spacing_after": 2
      }
    }
  },
  "parties": { ... },
  "claims": { ... },
  "grounds": {
    "sections": [
      {
        "title": { "text": "1. 당사자들의 관계" },
        "paragraphs": [
          {
            "text": "원고와 피고는 ...",
            "format": { "indent_level": 1 },
            "evidence_refs": ["갑 제1호증"]
          }
        ]
      }
    ]
  }
}
```

## 14.5 Draft 생성 흐름 통합

```
사용자 "Draft 생성" 클릭
         │
         ▼
┌─────────────────────────────────┐
│ 1. get_template_by_type("이혼소장") │
│    → Qdrant legal_templates 조회   │
└─────────────────────────────────┘
         │
         ▼ (템플릿 있음)
┌─────────────────────────────────┐
│ 2. GPT-4o 프롬프트에 스키마 포함   │
│    "다음 JSON 스키마에 맞춰 출력"  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 3. GPT-4o JSON 응답 생성          │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 4. DocumentRenderer.render_to_text() │
│    → 포맷팅된 소장 텍스트 생성     │
└─────────────────────────────────┘
```

## 14.6 관련 파일

| 파일 | 위치 | 설명 |
|------|------|------|
| `template_store.py` | ai_worker/src/storage/ | 템플릿 저장소 클래스 |
| `upload_templates.py` | ai_worker/scripts/ | 템플릿 업로드 스크립트 |
| `document_renderer.py` | backend/app/services/ | JSON→텍스트 렌더러 |
| `qdrant.py` | backend/app/utils/ | 템플릿 조회 함수 추가 |
| `divorce_complaint_schema.json` | docs/ | 이혼소장 스키마 |
| `divorce_complaint_example.json` | docs/ | 이혼소장 예시 |

## 14.7 향후 확장

- [ ] 답변서 템플릿 추가
- [ ] 준비서면 템플릿 추가
- [ ] 프론트엔드 템플릿 선택 UI
- [ ] 템플릿 관리 API (Phase 5)

---

# ✔️ 15. 최종 산출물

AI 파이프라인이 최종적으로 제공하는 데이터들은:

1. **증거 raw → 정제된 content**
2. **요약(ai_summary)**
3. **유책사유(labels)**
4. **임베딩(vector)**
5. **증거 인사이트(insights)**
6. **타임라인 데이터**
7. **RAG Index 문서**
8. **법률 문서 템플릿 (v2.1 추가)**

이 8개가 LEH 전체 기능의 기반이 된다.

---

# 🔚 END OF AI_PIPELINE_DESIGN.md

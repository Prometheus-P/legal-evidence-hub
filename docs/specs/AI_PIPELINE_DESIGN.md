# AI_PIPELINE_DESIGN.md

### *증거 분석·요약·라벨링·RAG 구축 파이프라인*

**버전:** v3.1
**작성일:** 2025-11-18
**최종 수정:** 2025-12-23
**작성자:** Team L(AI)
**참고 문서:**

* `PRD.md`
* `ARCHITECTURE.md`
* `json_template_implementation_plan.md`
* `lssp_divorce_module_pack_v2_01 ~ v2_15` (draft_upgrade)

---

## 변경 이력 (Change Log)

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| v2.0 | 2025-11-18 | Team L | 최초 작성 |
| v2.1 | 2025-12-03 | L-work | TemplateStore 추가, JSON 템플릿 시스템 문서화 |
| v3.0 | 2025-12-23 | L-work | 전면 재작성: 실제 구현 반영, 16개 분석기 문서화, YAML 설정 시스템, draft_upgrade 로드맵 추가 |
| v3.1 | 2025-12-23 | L-work | 통합 검증 결과 추가 (섹션 15), Phase 3-5 완료 상태 업데이트, Module Pack 테이블 갱신 |

---

# 📌 0. 문서 목적

본 문서는 LEH(Legal Evidence Hub)에서 사용되는
**전체 AI 파이프라인 구조**를 정의한다.

AI Worker(L)가 수행하는:

* 증거 ingest
* 파일 타입 자동 판별
* STT/OCR/Parsing (8개 파서)
* 요약(Summarization)
* 의미 분석 (16개 분석기)
* 인물 추출 / 관계 추론
* Keypoint 추출
* Embedding 생성
* 사건별 RAG Index 구축(Qdrant)
* 비용/용량 제어(Cost Guard)
* 모니터링(Observability)

전 과정을 상세히 기술한다.

백엔드 및 프론트엔드 개발자는 AI Worker가 **어떤 결과를 생성하며**,
그 결과가 **DynamoDB/Qdrant**에서 어떻게 활용되는지 이 문서를 참고한다.

---

# 🧭 1. AI 파이프라인 전체 개요

LEH AI 파이프라인은 다음 특징을 가진다:

### ✔ 100% 자동화

S3 업로드 → S3 Event → AI Worker 실행 → DynamoDB / Qdrant 업데이트

### ✔ 증거 타입별 맞춤 처리 (8개 파서)

* Text → 구조화 파싱 (카카오톡 포맷 자동 감지)
* Image OCR → Tesseract 기반 텍스트 추출
* Image Vision → GPT-4o Vision 상황/감정 설명
* Audio → Whisper STT + diarization
* Video → 음성 추출 후 STT
* PDF → Text Extract + OCR fallback

### ✔ 고도화된 분석 (16개 분석기)

* Article 840 Tagger (민법 840조 기반)
* Person Extractor (인물 추출)
* Relationship Inferrer (관계 추론)
* Keypoint Extractor (핵심 사실 추출)
* Evidence Scorer (증거 스코어링)
* Risk Analyzer (리스크 평가)
* (+ 10개 추가 분석기)

### ✔ 사건 단위 RAG 구축

각 사건은 독립된 embedding index(`case_rag_<case_id>`)로 관리된다.

### ✔ YAML 기반 설정 시스템

모든 키워드, 프롬프트, 규칙을 YAML로 외부화하여 관리

### ✔ 비용/용량 제어

Cost Guard로 파일 크기, API 비용, 토큰 사용량 관리

---

# 🏗 2. 파이프라인 전체 다이어그램

```
               ┌───────────────────────┐
               │   S3 Evidence Upload  │
               └─────────┬─────────────┘
                         ▼ (Event)
                ┌──────────────────┐
                │ AI Worker (L)    │
                │ Lambda/ECS       │
                └───────┬──────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌─────────────┐ ┌─────────┐ ┌─────────────┐
   │ Cost Guard  │ │ Parser  │ │ Observ-     │
   │ (용량 검증)  │ │ Router  │ │ ability     │
   └──────┬──────┘ └────┬────┘ └──────┬──────┘
          │             │             │
          └─────────────┼─────────────┘
                        ▼
     ┌──────────────────────────────────────┐
     │         8개 Parser Layer             │
     ├──────────────────────────────────────┤
     │ text │ image_ocr │ image_vision │    │
     │ audio │ video │ pdf │ csv │ json    │
     └──────────────────┬───────────────────┘
                        ▼
     ┌──────────────────────────────────────┐
     │        16개 Analysis Layer           │
     ├──────────────────────────────────────┤
     │ Article840Tagger │ Summarizer │      │
     │ PersonExtractor │ RelationshipInfer │
     │ KeypointExtractor │ EvidenceScorer │ │
     │ RiskAnalyzer │ ImpactRules │ ...    │
     └──────────────────┬───────────────────┘
                        ▼
     ┌──────────────────────────────────────┐
     │        Embedding Generation          │
     │     (OpenAI text-embedding-3-large)  │
     └──────────────────┬───────────────────┘
                        ▼
          ┌─────────────┴─────────────┐
          ▼                           ▼
   ┌───────────────┐         ┌───────────────┐
   │ Qdrant RAG    │         │ DynamoDB JSON │
   │ case_rag_{id} │         │ Evidence Meta │
   └───────────────┘         └───────────────┘
```

---

# 🧩 3. Parser Layer (8개 파서)

## 3.1 파서 라우팅 (handler.py:route_parser)

S3에서 파일을 임시 다운로드 후 확장자·헤더 기반으로 적절한 파서 선택:

| 파서 | 파일 타입 | 설명 |
|------|-----------|------|
| `TextParser` | `.txt` | 카카오톡/일반 텍스트 구조화 |
| `ImageOCRParser` | `.jpg`, `.png` | Tesseract OCR 텍스트 추출 |
| `ImageVisionParser` | `.jpg`, `.png` | GPT-4o Vision 상황/감정 분석 |
| `AudioParser` | `.mp3`, `.m4a`, `.wav` | Whisper STT + diarization |
| `VideoParser` | `.mp4`, `.avi` | FFmpeg 음성 추출 → STT |
| `PDFParser` | `.pdf` | PyPDF2 + OCR fallback |
| `CSVParser` | `.csv` | 구조화된 데이터 파싱 |
| `JSONParser` | `.json` | JSON 구조 파싱 |

**위치**: `ai_worker/src/parsers/`

```
parsers/
├── base.py              # BaseParser 추상 클래스
├── text.py              # TextParser (카카오톡 포맷 감지)
├── image_ocr.py         # ImageOCRParser (Tesseract)
├── image_vision.py      # ImageVisionParser (GPT-4o Vision)
├── audio_parser.py      # AudioParser (Whisper STT)
├── video_parser.py      # VideoParser (FFmpeg + Whisper)
├── pdf_parser.py        # PDFParser (PyPDF2 + OCR)
├── csv_parser.py        # CSVParser
└── json_parser.py       # JSONParser
```

## 3.2 파서 출력 구조 (ParsedMessage)

모든 파서는 통일된 `ParsedMessage` 구조로 출력:

```python
@dataclass
class ParsedMessage:
    content: str              # 추출된 텍스트
    sender: Optional[str]     # 발신자 (대화형 증거)
    timestamp: Optional[str]  # ISO8601 타임스탬프
    metadata: Dict[str, Any]  # 추가 메타데이터
```

## 3.3 TextParser - 카카오톡 포맷 자동 감지

```python
# 카카오톡 내보내기 형식 자동 감지
# "2024년 1월 15일 오후 3:45, 홍길동 : 안녕하세요"
KAKAO_PATTERN = r"(\d{4}년 \d{1,2}월 \d{1,2}일.*?),?\s*(.+?)\s*:\s*(.+)"
```

## 3.4 AudioParser - Whisper STT + Diarization

```python
# Whisper 모델 설정 (config/models.yaml)
whisper:
  model_name: "whisper-1"
  language: "ko"
  response_format: "verbose_json"  # 타임스탬프 포함
```

---

# 🧠 4. Analysis Layer (16개 분석기)

## 4.1 분석기 목록

| 분석기 | 파일 | 기능 |
|--------|------|------|
| `Article840Tagger` | `article_840_tagger.py` | 민법 840조 유책사유 라벨링 |
| `Summarizer` | `summarizer.py` | 증거 요약 생성 |
| `StreamingAnalyzer` | `streaming_analyzer.py` | 스트리밍 분석 |
| `AIAnalyzer` | `ai_analyzer.py` | GPT 기반 심층 분석 |
| `PersonExtractor` | `person_extractor.py` | 인물 추출 |
| `RelationshipInferrer` | `relationship_inferrer.py` | 관계 추론 |
| `KeypointExtractor` | `keypoint_extractor.py` | 핵심 사실 추출 |
| `EvidenceScorer` | `evidence_scorer.py` | 증거 스코어링 |
| `RiskAnalyzer` | `risk_analyzer.py` | 리스크 평가 |
| `ImpactRules` | `impact_rules.py` | 재산분할 영향도 계산 |
| `EventSummarizer` | `event_summarizer.py` | 이벤트별 요약 |
| `TimelineGenerator` | `timeline_generator.py` | 타임라인 생성 |
| `LegalReferencer` | `legal_referencer.py` | 법조문 인용 |
| `SentimentAnalyzer` | `sentiment_analyzer.py` | 감정 분석 |
| `ThreatDetector` | `threat_detector.py` | 협박/위협 감지 |
| `PatternAnalyzer` | `pattern_analyzer.py` | 행동 패턴 분석 |

**위치**: `ai_worker/src/analysis/`

## 4.2 Article840Tagger (민법 840조 태거)

**기능**: 증거 텍스트에서 민법 840조 이혼 사유 자동 라벨링

**법률 근거 코드 (G1-G6)**:

| 코드 | 사유 | 민법 조항 |
|------|------|-----------|
| G1 | 부정한 행위(외도) | 제840조 제1호 |
| G2 | 악의의 유기 | 제840조 제2호 |
| G3 | 배우자/직계존속의 부당 대우 | 제840조 제3호 |
| G4 | 자기 직계존속에 대한 부당 대우 | 제840조 제4호 |
| G5 | 3년 이상 생사 불명 | 제840조 제5호 |
| G6 | 기타 중대 사유 | 제840조 제6호 |

**설정 파일**: `config/legal_keywords.yaml`, `config/legal_grounds.yaml`

```yaml
# legal_keywords.yaml 예시
adultery:
  weight: 3
  keywords:
    - 외도
    - 바람
    - 불륜
    - 상간녀
    - 상간남
```

## 4.3 PersonExtractor (인물 추출)

**기능**: 대화/문서에서 인물 이름, 역할, 진영 추출

**설정 파일**: `config/role_keywords.yaml`

```yaml
# role_keywords.yaml
spouse_keywords:
  남편:
    role: "배우자"
    side: "defendant"
  아내:
    role: "배우자"
    side: "plaintiff"
```

**출력 구조**:
```python
@dataclass
class ExtractedPerson:
    name: str                    # 추출된 이름
    role: Optional[str]          # 역할 (배우자, 부모, 자녀 등)
    side: Optional[str]          # 진영 (plaintiff/defendant)
    mention_count: int           # 언급 횟수
    context_snippets: List[str]  # 맥락 스니펫
```

## 4.4 RelationshipInferrer (관계 추론)

**기능**: 추출된 인물 간 관계 유형 추론

**관계 유형**:

| 타입 | 라벨 | 색상 |
|------|------|------|
| `SPOUSE` | 배우자 | #FF6B6B |
| `PARENT` | 부모 | #4ECDC4 |
| `CHILD` | 자녀 | #45B7D1 |
| `AFFAIR_PARTNER` | 외도 상대 | #F39C12 |
| `IN_LAW` | 시/처가 | #9B59B6 |
| `SIBLING` | 형제자매 | #3498DB |
| `FRIEND` | 친구 | #2ECC71 |
| `COLLEAGUE` | 직장동료 | #95A5A6 |
| `OTHER` | 기타 | #BDC3C7 |

**설정 파일**: `config/relationship_keywords.yaml`

## 4.5 KeypointExtractor (핵심 사실 추출)

**기능**: 법적으로 중요한 핵심 사실(Keypoint) 추출

**Keypoint 타입** (config/keypoint_taxonomy.yaml):

| 타입 | 라벨 | 관련 사유 |
|------|------|-----------|
| `COMMUNICATION_ADMISSION` | 자백/인정 발언 | G1, G3, G6 |
| `COMMUNICATION_THREAT` | 협박/모욕 발언 | G3, G6 |
| `VIOLENCE_INJURY` | 폭행/상해 | G3 |
| `FINANCE_SPEND` | 결제 내역 | G1, G6 |
| `SEPARATION_LEAVE_HOME` | 가출/별거 | G2, G6 |
| `AFFAIR_EVIDENCE` | 외도 증거 | G1 |
| `ECONOMIC_ABUSE` | 경제적 학대 | G2, G6 |

**출력 구조**:
```python
@dataclass
class Keypoint:
    keypoint_type: str           # COMMUNICATION_ADMISSION 등
    statement: str               # 핵심 문장
    occurred_at: Optional[str]   # 발생 시점
    actors: List[str]            # 관련 인물
    confidence: float            # 신뢰도 (0.0-1.0)
    ground_codes: List[str]      # 관련 법률 근거 (G1-G6)
    extract_link: Optional[str]  # 원본 증거 링크
```

## 4.6 EvidenceScorer (증거 스코어링)

**기능**: 증거의 법적 증명력 점수 계산

**설정 파일**: `config/scoring_keywords.yaml`

```yaml
categories:
  violence:
    base_score: 8.0
    keywords:
      - 폭행
      - 폭력
      - 상해
      - 진단서
```

**점수 계산 규칙**:
- 키워드 매칭 점수 합산
- 카테고리 중첩 시 감쇠 계수 적용 (0.7)
- 키워드 반복 시 보너스 (0.5)
- 최종 점수: 0-10 범위

## 4.7 ImpactRules (재산분할 영향도)

**기능**: 유책사유별 재산분할 비율 영향 계산

**설정 파일**: `config/impact_rules.yaml`

```yaml
fault_types:
  adultery:
    base_impact: 5.0
    max_impact: 10.0
    evidence_weights:
      photo: 1.5
      video: 1.8
      chat_log: 1.2
```

**계산 공식**:
```
final_impact = base_impact × Σ(evidence_weight × evidence_count)
최대값: max_impact 제한
복합 유책: multiple_fault_decay (0.8) 적용
```

## 4.8 RiskAnalyzer (리스크 평가)

**기능**: 사건 리스크 레벨 평가 및 경고

**평가 항목**:
- 증거 완성도
- 법적 근거 강도
- 상대방 반박 가능성
- 시효 위험

---

# ⚙️ 5. Configuration System (YAML 설정)

## 5.1 설정 디렉토리 구조

```
ai_worker/
├── config/
│   ├── __init__.py              # ConfigLoader 클래스
│   ├── legal_keywords.yaml      # Article 840 키워드 (240+)
│   ├── legal_grounds.yaml       # G1-G6 법률 근거 정의
│   ├── role_keywords.yaml       # 인물 역할 매핑 (100+)
│   ├── relationship_keywords.yaml # 관계 유형 매핑 (60+)
│   ├── keypoint_taxonomy.yaml   # Keypoint 분류 체계
│   ├── scoring_keywords.yaml    # 증거 스코어링 키워드
│   ├── impact_rules.yaml        # 재산분할 영향 규칙
│   ├── limits.yaml              # 파일/비용 제한
│   ├── models.yaml              # AI 모델 설정
│   └── prompts/
│       ├── ai_system.yaml       # AI Analyzer 프롬프트
│       ├── keypoint.yaml        # Keypoint 추출 프롬프트
│       ├── summarizer.yaml      # 요약 프롬프트
│       └── tone_guidelines.yaml # 톤 가이드라인
```

## 5.2 ConfigLoader 클래스

```python
from config import ConfigLoader

# 설정 파일 로드
legal_keywords = ConfigLoader.load("legal_keywords")

# 프롬프트 로드
system_prompt = ConfigLoader.get_prompt("ai_system", "system_prompt")

# 법률 근거 조회
g1_info = ConfigLoader.get_legal_ground("G1")

# Keypoint 타입 조회
kp_type = ConfigLoader.get_keypoint_type("VIOLENCE_INJURY")
```

## 5.3 legal_grounds.yaml 구조

```yaml
version: "2.01"

grounds:
  G1:
    code: "G1"
    name_ko: "부정한 행위(외도)"
    civil_code_ref: "민법 제840조 제1호"
    elements:
      - "정조의무 위반에 해당하는 행위"
      - "혼인 파탄과의 관련성(정황)"
    typical_evidence_types:
      - "문자메시지/카카오톡"
      - "녹음파일"
      - "사진/동영상"
    limitation:
      type: "제척기간(서비스가정)"
      known_within_months: 6
      occurred_within_years: 2
    legal_category: "adultery"
    article_840_code: "840-1"

code_mappings:
  article_840_to_ground:
    "840-1": "G1"
    "840-2": "G2"
    ...
```

## 5.4 keypoint_taxonomy.yaml 구조

```yaml
version: "2.03"

keypoint_types:
  COMMUNICATION_ADMISSION:
    code: "COMMUNICATION_ADMISSION"
    label: "자백/인정 발언"
    required_fields:
      - statement
      - occurred_at
      - actors
    auto_timeline_event: true
    ground_relevance:
      - "G1"
      - "G3"
      - "G6"
    evidence_weight: 1.8

categories:
  communication:
    - "COMMUNICATION_ADMISSION"
    - "COMMUNICATION_THREAT"
    - "VERBAL_ABUSE"

extraction_rules:
  confidence_thresholds:
    min_extraction: 0.3
    auto_timeline: 0.5
    high_confidence: 0.7
```

---

# 💰 6. Cost & Rate Limiting

## 6.1 Cost Guard (cost_guard.py)

**기능**: 파일 크기, API 비용, 토큰 사용량 제어

**설정 파일**: `config/limits.yaml`

```yaml
file_limits:
  image:
    max_size_mb: 10
    allowed_extensions: [".jpg", ".jpeg", ".png", ".gif", ".webp"]
  audio:
    max_size_mb: 100
    max_duration_minutes: 60
    allowed_extensions: [".mp3", ".m4a", ".wav", ".ogg"]
  video:
    max_size_mb: 500
    max_duration_minutes: 30
    allowed_extensions: [".mp4", ".avi", ".mov", ".mkv"]

cost_limits:
  max_daily_tokens_per_case: 100000
  max_daily_cost_per_case: 5.0
  max_single_request_tokens: 10000
  warn_threshold_percent: 80

model_costs:
  gpt-4o-mini:
    input_per_1k: 0.00015
    output_per_1k: 0.0006
  whisper-1:
    per_minute: 0.006
```

## 6.2 비용 계산

```python
class CostGuard:
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """API 호출 예상 비용 계산"""

    def check_limit(self, case_id: str, estimated_cost: float) -> bool:
        """일일 한도 확인"""

    def record_usage(self, case_id: str, actual_cost: float) -> None:
        """사용량 기록"""
```

---

# 📊 7. Observability & Monitoring

## 7.1 observability.py

**기능**: 파이프라인 실행 추적, 메트릭 수집, 에러 로깅

```python
class PipelineObserver:
    def start_trace(self, evidence_id: str, operation: str) -> str:
        """트레이스 시작"""

    def end_trace(self, trace_id: str, status: str, metadata: dict) -> None:
        """트레이스 종료"""

    def record_metric(self, name: str, value: float, tags: dict) -> None:
        """메트릭 기록"""

    def log_error(self, error: Exception, context: dict) -> None:
        """에러 로깅"""
```

## 7.2 수집 메트릭

| 메트릭 | 설명 |
|--------|------|
| `parser.duration` | 파서 실행 시간 |
| `analyzer.duration` | 분석기 실행 시간 |
| `embedding.duration` | 임베딩 생성 시간 |
| `api.tokens_used` | API 토큰 사용량 |
| `api.cost` | API 비용 |
| `error.count` | 에러 발생 수 |

---

# 🗂 8. Storage Layer

## 8.1 DynamoDB 스키마

```json
{
  "case_id": "case_123",          // Partition Key
  "evidence_id": "ev_3",          // Sort Key
  "type": "audio",
  "timestamp": "2024-12-25T10:20:00Z",
  "speaker": "S1",
  "labels": ["폭언", "G3"],
  "ai_summary": "피고가 고성으로 폭언...",
  "insights": ["지속적 고성", "협박성 발언"],
  "content": "STT 결과 전문",
  "s3_key": "cases/123/raw/xx.m4a",
  "qdrant_id": "case_123_ev_3",
  "persons": [
    {"name": "김OO", "role": "배우자", "side": "defendant"}
  ],
  "keypoints": [
    {
      "type": "COMMUNICATION_THREAT",
      "statement": "죽여버리겠다",
      "confidence": 0.95
    }
  ],
  "evidence_score": 8.5,
  "impact_assessment": {
    "property_division_impact": 4.0,
    "favorable_to": "plaintiff"
  }
}
```

## 8.2 Qdrant Collection

**컬렉션 이름**: `case_rag_{case_id}`

**문서 구조**:
```json
{
  "id": "case_123_ev_3",
  "vector": [0.12, ...],  // 1536 dimensions
  "payload": {
    "case_id": "case_123",
    "evidence_id": "ev_3",
    "content": "전체 텍스트",
    "summary": "요약 텍스트",
    "labels": ["폭언"],
    "timestamp": "2024-12-21",
    "keypoints": [...],
    "ground_codes": ["G3"]
  }
}
```

---

# 🔄 9. draft_upgrade 통합 로드맵

## 9.1 Module Pack 개요

| 버전 | 모듈명 | 상태 | 통합 포인트 |
|------|--------|------|-------------|
| v2.01 | Foundation | ✅ 완료 | legal_grounds.yaml |
| v2.02 | Draft Mapping | ✅ 완료 | draft_blocks.yaml ground_to_blocks |
| v2.03 | Keypoint Tracking | ✅ 완료 | keypoint_taxonomy.yaml |
| v2.04 | Draft Engine | ✅ 완료 | draft_blocks.yaml 템플릿 |
| v2.05 | Document Gen | ⬜ N/A | Backend 영역 (python-docx) |
| v2.06 | Draft Engine Impl | ⬜ N/A | 참조용 stub |
| v2.07 | Consultation | ⚠️ 미반영 | consultation_taxonomy 추가 필요 |
| v2.08 | Issues Dashboard | ✅ 완료 | issue_taxonomy.yaml |
| v2.09 | Evidence Checklist | ⚠️ 부분 | requirement_sets 일부 |
| v2.10 | Keypoint Pipeline | ✅ 완료 | extraction_rules |
| v2.11 | Legal Authority | ✅ 완료 | legal_authorities.yaml |
| v2.12 | Precedent Recommender | ⬜ N/A | 데이터 미생성 |
| v2.13 | Timeline | ⬜ N/A | 스펙만 존재 |
| v2.14 | Process State Machine | ⬜ N/A | 스펙만 존재 |
| v2.15 | Recompute Pipeline | ⬜ N/A | Backend 영역 (DAG)

## 9.2 Phase 1 (완료): Foundation

- `legal_grounds.v2_01.json` → `config/legal_grounds.yaml`
- G1-G6 코드 체계 Article840Tagger 통합
- 증거 유형 힌트 제공

## 9.3 Phase 2 (완료): Keypoint System

- `keypoint_types.v2_03.json` → `config/keypoint_taxonomy.yaml`
- KeypointExtractor 출력 스키마 확장
- Ground Relevance 매핑 구현

## 9.4 Phase 3 (완료): Draft & Evidence

- `draft_blocks.v2_04.json` → `config/draft_blocks.yaml`
- 10개 블록 템플릿 (COMMON_HEADER, FACTS_G1_AFFAIR 등)
- Ground → Block 매핑 구현

## 9.5 Phase 4 (완료): Legal Authority

- `law_articles.v2_11.json` → `config/legal_authorities.yaml`
- 11개 법조문 (민법/가사소송법/가정폭력법 등)
- Ground → Authority 매핑 구현

## 9.6 Phase 5 (완료): Risk & Scoring

- `issue_taxonomy.v2_08.json` → `config/issue_taxonomy.yaml`
- 25개 이슈, 6개 그룹 (DEADLINE, PROCEDURE, EVIDENCE, DRAFT, CHILD, PROPERTY)
- Scoring Rules 및 Risk Levels 통합

---

# 🚨 10. 에러 핸들링 & 재처리

## 10.1 에러 유형

| 에러 타입 | 처리 방식 |
|-----------|-----------|
| 파일 크기 초과 | 즉시 거부 + 사용자 알림 |
| API 비용 한도 | 대기열 이동 + 익일 재처리 |
| 파서 실패 | DLQ 이동 + 수동 검토 |
| 분석기 실패 | 기본값 저장 + 재분석 예약 |

## 10.2 재처리 API

```
POST /admin/reprocess-evidence
{
  "case_id": "case_123",
  "evidence_id": "ev_3",
  "force": true
}
```

## 10.3 DLQ (Dead Letter Queue)

실패한 처리 작업은 SQS Dead Letter Queue로 이동:
- 최대 재시도: 3회
- 재시도 간격: 지수 백오프 (1분, 5분, 15분)

---

# 🧪 11. 테스트 전략

## 11.1 Unit Test

- 타입별 parser 테스트
- 분석기별 로직 테스트
- ConfigLoader 테스트
- Cost Guard 계산 테스트

## 11.2 Integration Test

- S3 → Worker → DynamoDB 전체 플로우
- Qdrant RAG 쿼리
- 다중 분석기 파이프라인

## 11.3 Coverage 요구사항

- 최소 커버리지: 80%
- 핵심 분석기: 90% 이상

---

# 🛠 12. Worker 내부 구조

## 12.1 디렉토리 구조

```
ai_worker/
├── handler.py                 # Lambda 핸들러 (진입점)
├── config/                    # YAML 설정 시스템
│   ├── __init__.py           # ConfigLoader
│   ├── legal_keywords.yaml
│   ├── legal_grounds.yaml
│   ├── keypoint_taxonomy.yaml
│   └── ...
├── src/
│   ├── parsers/              # 8개 파서
│   │   ├── base.py
│   │   ├── text.py
│   │   ├── image_ocr.py
│   │   ├── image_vision.py
│   │   ├── audio_parser.py
│   │   ├── video_parser.py
│   │   └── pdf_parser.py
│   ├── analysis/             # 16개 분석기
│   │   ├── article_840_tagger.py
│   │   ├── summarizer.py
│   │   ├── person_extractor.py
│   │   ├── relationship_inferrer.py
│   │   ├── keypoint_extractor.py
│   │   ├── evidence_scorer.py
│   │   ├── impact_rules.py
│   │   └── risk_analyzer.py
│   ├── storage/
│   │   ├── metadata_store.py  # DynamoDB
│   │   ├── vector_store.py    # Qdrant
│   │   └── template_store.py  # 템플릿
│   ├── service_rag/           # 법률 지식 RAG
│   ├── user_rag/              # 사건별 RAG
│   └── search/
├── utils/
│   ├── cost_guard.py          # 비용 관리
│   ├── observability.py       # 모니터링
│   ├── s3.py
│   └── ffmpeg.py
└── tests/
```

## 12.2 필수 의존성

```
boto3           # AWS SDK
qdrant-client   # Qdrant 클라이언트
openai          # OpenAI API
ffmpeg-python   # 미디어 처리
pydantic        # 데이터 검증
PyYAML          # YAML 파싱
pytesseract     # OCR
PyPDF2          # PDF 처리
```

---

# 📄 13. 법률 문서 템플릿 시스템

## 13.1 TemplateStore 클래스

**위치**: `ai_worker/src/storage/template_store.py`

```python
class TemplateStore:
    def get_template(template_type: str) -> dict
    def search_templates(query: str) -> list[dict]
    def upload_template(template_type, schema, example, ...) -> str
    def get_schema_for_generation(template_type: str) -> str
```

## 13.2 Draft 생성 흐름

```
1. get_template_by_type("이혼소장")
   → Qdrant legal_templates 조회

2. GPT-4o 프롬프트에 스키마 포함
   "다음 JSON 스키마에 맞춰 출력"

3. GPT-4o JSON 응답 생성

4. DocumentRenderer.render_to_text()
   → 포맷팅된 소장 텍스트 생성
```

---

# ✔️ 14. 최종 산출물

AI 파이프라인이 최종적으로 제공하는 데이터:

1. **증거 raw → 정제된 content**
2. **요약(ai_summary)**
3. **유책사유(labels + ground_codes)**
4. **임베딩(vector)**
5. **증거 인사이트(insights)**
6. **타임라인 데이터**
7. **RAG Index 문서**
8. **인물 추출(persons)**
9. **관계 추론(relationships)**
10. **핵심 사실(keypoints)**
11. **증거 점수(evidence_score)**
12. **영향 평가(impact_assessment)**
13. **리스크 레벨(risk_level)**
14. **법률 문서 템플릿**

이 14개가 LEH 전체 기능의 기반이 된다.

---

# 📊 15. 통합 검증 결과 (2025-12-23)

## 15.1 draft_upgrade 반영률

| 구분 | 모듈 수 | 비율 |
|------|---------|------|
| ✅ 완전 반영 | 8개 | 53% |
| ⚠️ 부분 반영 | 1개 | 7% |
| ⬜ 미반영/범위외 | 6개 | 40% |

**완전 반영 모듈**: v2.01 (Foundation), v2.02 (Draft Mapping), v2.03 (Keypoint), v2.04 (Draft Engine), v2.08 (Issues), v2.10 (Keypoint Pipeline), v2.11 (Legal Authority)

**범위 외**: v2.05/v2.06/v2.15 (Backend 영역), v2.12-v2.14 (스펙만 존재)

## 15.2 Config 아키텍처 검증

| 항목 | 상태 | 비고 |
|------|------|------|
| ConfigLoader 캐싱 | ✅ 정상 | 클래스 변수 기반 싱글톤 |
| Fallback 패턴 | ✅ 구현됨 | `CONSTANT = _load() or {fallback}` |
| 경로 탐색 | ✅ 정상 | `config/` → `config/prompts/` 자동 |
| 타입 힌트 | ✅ 완전 | Dict, List, Optional 명시 |
| 테스트 커버리지 | ✅ 76.04% | 70% 요구사항 충족 |

**생성된 YAML 파일** (16개):
- `legal_grounds.yaml`, `keypoint_taxonomy.yaml`, `draft_blocks.yaml`
- `legal_authorities.yaml`, `issue_taxonomy.yaml`
- `legal_keywords.yaml`, `role_keywords.yaml`, `relationship_keywords.yaml`
- `event_templates.yaml`, `impact_rules.yaml`, `scoring_keywords.yaml`, `limits.yaml`
- `prompts/ai_system.yaml`, `prompts/streaming.yaml`, `prompts/summarizer.yaml`, `prompts/keypoint.yaml`

## 15.3 스키마 일관성 검증

| 저장소 | 일관성 | 비고 |
|--------|--------|------|
| DynamoDB | 70% | 핵심 필드 저장, 확장 필드 일부 누락 |
| Qdrant | 85% | 대부분 필드 저장 |
| Cross-storage | 60% | `content`/`document` 필드명 불일치 |

## 15.4 발견된 GAP 및 권장 조치

### 🔴 Critical (즉시 조치)
| GAP | 권장 조치 |
|-----|-----------|
| keypoints/persons/relationships DynamoDB 저장 검증 | `metadata_store.py` 확인 |

### 🟡 Important (Phase 2)
| GAP | 권장 조치 |
|-----|-----------|
| v2.07 consultation_taxonomy 미반영 | `config/consultation_taxonomy.yaml` 추가 |
| v2.09 requirement_sets 완전 통합 | Evidence Scorer 강화 |
| risk_level/issue_list DynamoDB 필드 | `metadata_store.py` 확장 |

### 🟢 Nice to Have (추후)
| GAP | 설명 |
|-----|------|
| v2.12-v2.14 통합 | 스펙만 존재, 데이터 생성 후 |
| content/document 필드명 통일 | 전체 코드베이스 리팩토링 |
| ConfigLoader Thread Safety | Lambda 외 환경 지원 시 |

---

# 🔚 END OF AI_PIPELINE_DESIGN.md

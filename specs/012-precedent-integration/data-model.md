# Data Model: 판례 검색 시스템

**Feature**: 012-precedent-integration
**Date**: 2025-12-12

## Entities

### 1. PrecedentCase (Qdrant Payload)

판례 정보를 저장하는 벡터 저장소 페이로드입니다.

```typescript
interface PrecedentCase {
  // 식별자
  case_ref: string;           // 사건번호 (예: "2020다12345")
  
  // 기본 정보
  court: string;              // 법원 (예: "대법원", "서울가정법원")
  decision_date: string;      // 선고일 (ISO 8601: "2020-03-15")
  case_type: string;          // 사건 유형 (예: "이혼", "재산분할")
  
  // 내용
  summary: string;            // 판결 요지 (200-500자)
  key_factors: string[];      // 주요 요인 (예: ["외도", "가정폭력", "경제적 기여도"])
  
  // 재산분할 (optional)
  division_ratio?: {
    plaintiff: number;        // 원고 비율 (0-100)
    defendant: number;        // 피고 비율 (0-100)
  };
  
  // 메타데이터
  similarity_score?: number;  // 검색 시 유사도 점수 (0.0-1.0)
  source_url?: string;        // 원문 링크 (법령정보센터)
}
```

### 2. PartyNode (PostgreSQL - 확장)

기존 PartyNode 테이블에 자동 추출 관련 필드를 추가합니다.

```sql
-- 기존 party_nodes 테이블 확장
ALTER TABLE party_nodes ADD COLUMN IF NOT EXISTS
  is_auto_extracted BOOLEAN DEFAULT FALSE;
  
ALTER TABLE party_nodes ADD COLUMN IF NOT EXISTS
  extraction_confidence FLOAT CHECK (extraction_confidence >= 0 AND extraction_confidence <= 1);
  
ALTER TABLE party_nodes ADD COLUMN IF NOT EXISTS
  source_evidence_id VARCHAR(255) REFERENCES evidences(id);
```

```typescript
interface PartyNode {
  // 기존 필드
  id: string;
  case_id: string;
  name: string;
  role: 'plaintiff' | 'defendant' | 'witness' | 'other';
  side: 'plaintiff_side' | 'defendant_side' | 'neutral';
  position_x: number;
  position_y: number;
  
  // 자동 추출 필드 (NEW)
  is_auto_extracted: boolean;         // AI가 추출했는지 여부
  extraction_confidence?: number;     // 추출 신뢰도 (0.0-1.0)
  source_evidence_id?: string;        // 추출 근거 증거 ID
}
```

### 3. PartyRelationship (PostgreSQL - 확장)

기존 PartyRelationship 테이블에 자동 추출 관련 필드를 추가합니다.

```sql
-- 기존 party_relationships 테이블 확장
ALTER TABLE party_relationships ADD COLUMN IF NOT EXISTS
  is_auto_extracted BOOLEAN DEFAULT FALSE;
  
ALTER TABLE party_relationships ADD COLUMN IF NOT EXISTS
  extraction_confidence FLOAT CHECK (extraction_confidence >= 0 AND extraction_confidence <= 1);
  
ALTER TABLE party_relationships ADD COLUMN IF NOT EXISTS
  evidence_text TEXT;
```

```typescript
interface PartyRelationship {
  // 기존 필드
  id: string;
  case_id: string;
  from_party_id: string;
  to_party_id: string;
  relationship_type: string;          // 예: "spouse", "parent", "sibling"
  start_date?: string;
  end_date?: string;
  
  // 자동 추출 필드 (NEW)
  is_auto_extracted: boolean;         // AI가 추출했는지 여부
  extraction_confidence?: number;     // 추출 신뢰도 (0.0-1.0)
  evidence_text?: string;             // 관계 추론 근거 텍스트
}
```

## Relationships

```
┌─────────────────┐
│  PrecedentCase  │ (Qdrant - 공유 컬렉션)
│  leh_legal_     │
│  knowledge      │
└─────────────────┘
        ↓ 검색
┌─────────────────┐     ┌─────────────────┐
│     Case        │ 1:N │   Evidence      │
│  (PostgreSQL)   │────→│  (DynamoDB)     │
└─────────────────┘     └─────────────────┘
        │                      ↓ 추출
        │ 1:N            ┌─────────────────┐
        ↓                │   AI Worker     │
┌─────────────────┐      │ (PersonExtractor│
│   PartyNode     │ ←────│ Relationship    │
│  (PostgreSQL)   │      │ Inferrer)       │
└─────────────────┘      └─────────────────┘
        │ N:M
        ↓
┌─────────────────┐
│PartyRelationship│
│  (PostgreSQL)   │
└─────────────────┘
```

## Validation Rules

### PrecedentCase
- `case_ref`: 필수, 형식 "연도+사건종류+번호" (예: "2020다12345")
- `court`: 필수, 알려진 법원 목록에 포함
- `decision_date`: 필수, ISO 8601 형식
- `summary`: 필수, 최소 50자
- `key_factors`: 최소 1개 이상
- `division_ratio`: 존재 시 plaintiff + defendant = 100

### PartyNode (자동 추출)
- `extraction_confidence`: 0.7 이상만 저장
- `source_evidence_id`: 자동 추출 시 필수

### PartyRelationship (자동 추출)
- `extraction_confidence`: 0.7 이상만 저장
- `evidence_text`: 최대 500자

## State Transitions

### PartyNode 상태

```
[생성 요청] → is_auto_extracted=true → [저장됨]
                                            ↓
                                    사용자 편집 시
                                            ↓
                                    is_auto_extracted=false
```

### 중복 감지 로직

```python
# 이름 기반 중복 감지
def detect_duplicate(new_party: PartyNode, existing_parties: List[PartyNode]) -> Optional[PartyNode]:
    for existing in existing_parties:
        if similar_name(new_party.name, existing.name, threshold=0.8):
            return existing
    return None
```

## Indexes

```sql
-- 자동 추출 인물 빠른 조회
CREATE INDEX idx_party_nodes_auto_extracted 
ON party_nodes(is_auto_extracted) 
WHERE is_auto_extracted = TRUE;

-- 자동 추출 관계 빠른 조회
CREATE INDEX idx_party_relationships_auto_extracted 
ON party_relationships(is_auto_extracted) 
WHERE is_auto_extracted = TRUE;

-- 증거별 추출 인물 조회
CREATE INDEX idx_party_nodes_source_evidence 
ON party_nodes(source_evidence_id);
```

## URL Generation

### source_url 생성 규칙 (국가법령정보센터 법령한글주소)

**참고**: `docs/LAW_HAGUL_ADDRESS_API.md`

```typescript
// PrecedentCase.source_url 생성
function generateSourceUrl(case_ref: string, decision_date: string): string {
  const BASE_URL = "https://www.law.go.kr";
  
  // ISO 날짜 → YYYYMMDD 변환
  const dateVal = decision_date.replace(/-/g, "");
  
  // URL 인코딩
  const params = encodeURIComponent(`${case_ref},${dateVal}`);
  
  return `${BASE_URL}/판례/(${params})`;
}

// 예시
generateSourceUrl("2020므12345", "2020-06-15")
// → "https://www.law.go.kr/판례/(2020%EB%AF%8012345%2C20200615)"
```

### URL 패턴 요약

| 유형 | URL 패턴 | 용도 |
|------|----------|------|
| 판례 상세 | `/판례/({case_ref},{date_val})` | 원문 열람 링크 |
| 법령 조문 | `/법령/{법령명}/제{N}조` | 관련 법령 참조 |

### Qdrant Payload 저장 시 URL 생성

```python
# ai_worker/scripts/load_sample_precedents.py
def create_payload(precedent: dict) -> dict:
    return {
        "case_ref": precedent["case_ref"],
        "court": precedent["court"],
        "decision_date": precedent["decision_date"],
        "summary": precedent["summary"],
        "key_factors": precedent["key_factors"],
        "division_ratio": precedent.get("division_ratio"),
        # URL 자동 생성
        "source_url": generate_precedent_url(
            precedent["case_ref"],
            precedent["decision_date"]
        )
    }
```

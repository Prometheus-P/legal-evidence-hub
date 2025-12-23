# Data Model: 증거 화자 매핑

**Feature**: 015-evidence-speaker-mapping
**Date**: 2025-12-22
**Phase**: 1 (Design)

## 1. Schema Changes

### 1.1 DynamoDB - leh_evidence 테이블 확장

**기존 스키마**:
```json
{
  "evidence_id": "evt_abc123",
  "case_id": "case_xyz789",
  "type": "image",
  "filename": "kakaotalk_capture.jpg",
  "status": "completed",
  "speaker": "원고",
  "ai_summary": "카카오톡 대화 내용...",
  "labels": ["폭언", "협박"],
  "content": "나: 왜 그랬어?\n상대방: 미안해...",
  "created_at": "2025-12-20T10:00:00Z",
  "updated_at": "2025-12-20T10:05:00Z"
}
```

**확장 스키마** (신규 필드):
```json
{
  "evidence_id": "evt_abc123",
  "case_id": "case_xyz789",
  "type": "image",
  "filename": "kakaotalk_capture.jpg",
  "status": "completed",
  "speaker": "원고",
  "ai_summary": "카카오톡 대화 내용...",
  "labels": ["폭언", "협박"],
  "content": "나: 왜 그랬어?\n상대방: 미안해...",

  "speaker_mapping": {
    "나": {
      "party_id": "party_001",
      "party_name": "김동우"
    },
    "상대방": {
      "party_id": "party_002",
      "party_name": "김도연"
    }
  },
  "speaker_mapping_updated_at": "2025-12-22T14:30:00Z",
  "speaker_mapping_updated_by": "user_lawyer123",

  "created_at": "2025-12-20T10:00:00Z",
  "updated_at": "2025-12-22T14:30:00Z"
}
```

### 1.2 신규 필드 정의

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `speaker_mapping` | Map | Optional | 화자명 → 인물 정보 매핑 |
| `speaker_mapping.{speaker_label}` | Map | - | 개별 화자 매핑 항목 |
| `speaker_mapping.{speaker_label}.party_id` | String | Required | PartyNode ID |
| `speaker_mapping.{speaker_label}.party_name` | String | Required | 인물 이름 (조회 편의용) |
| `speaker_mapping_updated_at` | String (ISO8601) | Optional | 매핑 마지막 수정 시각 |
| `speaker_mapping_updated_by` | String | Optional | 매핑 수정한 사용자 ID |

## 2. Backend Schemas (Pydantic)

### 2.1 Request/Response Models

**파일**: `backend/app/schemas/evidence.py` (신규 추가)

```python
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class SpeakerMappingItem(BaseModel):
    """개별 화자 매핑 항목"""
    party_id: str = Field(..., description="PartyNode ID")
    party_name: str = Field(..., description="인물 이름 (표시용)")


class SpeakerMappingUpdateRequest(BaseModel):
    """화자 매핑 저장/수정 요청"""
    speaker_mapping: Dict[str, SpeakerMappingItem] = Field(
        default_factory=dict,
        description="화자명 → 인물 정보 매핑. 빈 dict면 매핑 삭제",
        examples=[{
            "나": {"party_id": "party_001", "party_name": "김동우"},
            "상대방": {"party_id": "party_002", "party_name": "김도연"}
        }]
    )


class SpeakerMappingResponse(BaseModel):
    """화자 매핑 응답"""
    evidence_id: str
    speaker_mapping: Optional[Dict[str, SpeakerMappingItem]] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class EvidenceDetailExtended(BaseModel):
    """증거 상세 (화자 매핑 포함) - 기존 EvidenceDetail 확장"""
    id: str
    case_id: str
    type: str
    filename: str
    status: str
    ai_summary: Optional[str] = None
    content: Optional[str] = None
    labels: Optional[list[str]] = None
    speaker: Optional[str] = None
    speaker_mapping: Optional[Dict[str, SpeakerMappingItem]] = None
    speaker_mapping_updated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
```

## 3. Frontend Types (TypeScript)

### 3.1 Type Definitions

**파일**: `frontend/src/types/evidence.ts` (확장)

```typescript
/**
 * 개별 화자 매핑 항목
 */
export interface SpeakerMappingItem {
  party_id: string;
  party_name: string;
}

/**
 * 화자 매핑 객체 (화자명 → 인물 정보)
 */
export type SpeakerMapping = Record<string, SpeakerMappingItem>;

/**
 * Evidence 인터페이스 확장
 */
export interface Evidence {
  id: string;
  caseId: string;
  filename: string;
  type: EvidenceType;
  status: EvidenceStatus;
  uploadDate: string;
  summary?: string;
  size: number;
  downloadUrl?: string;
  content?: string;
  speaker?: SpeakerType;
  labels?: string[];
  timestamp?: string;
  s3Key?: string;
  qdrantId?: string;
  article840Tags?: Article840Tags;
  insights?: AIInsight[];

  // 015-evidence-speaker-mapping: 신규 필드
  speakerMapping?: SpeakerMapping;
  speakerMappingUpdatedAt?: string;
  speakerMappingUpdatedBy?: string;
}

/**
 * 화자 매핑 업데이트 요청
 */
export interface SpeakerMappingUpdateRequest {
  speaker_mapping: SpeakerMapping;
}

/**
 * 화자 매핑 업데이트 응답
 */
export interface SpeakerMappingUpdateResponse {
  evidence_id: string;
  speaker_mapping: SpeakerMapping | null;
  updated_at: string | null;
  updated_by: string | null;
}
```

## 4. Data Validation Rules

### 4.1 Backend Validation

```python
# 화자 매핑 저장 시 검증
class SpeakerMappingValidator:
    MAX_SPEAKERS = 10  # 증거당 최대 화자 수
    MAX_LABEL_LENGTH = 50  # 화자명 최대 길이

    @staticmethod
    def validate(mapping: Dict[str, SpeakerMappingItem], case_id: str) -> None:
        """화자 매핑 유효성 검증"""
        if len(mapping) > SpeakerMappingValidator.MAX_SPEAKERS:
            raise ValidationError(f"화자는 최대 {SpeakerMappingValidator.MAX_SPEAKERS}명까지 매핑 가능합니다")

        for label, item in mapping.items():
            if len(label) > SpeakerMappingValidator.MAX_LABEL_LENGTH:
                raise ValidationError(f"화자명은 {SpeakerMappingValidator.MAX_LABEL_LENGTH}자 이하여야 합니다")

            # party_id가 해당 케이스에 속하는지 확인 (Case Isolation)
            # PartyRepository에서 검증
```

### 4.2 Frontend Validation

```typescript
// 화자 매핑 폼 검증
const validateSpeakerMapping = (mapping: SpeakerMapping): string[] => {
  const errors: string[] = [];

  if (Object.keys(mapping).length > 10) {
    errors.push('화자는 최대 10명까지 매핑할 수 있습니다');
  }

  for (const [label, item] of Object.entries(mapping)) {
    if (label.length > 50) {
      errors.push(`화자명 "${label}"이 너무 깁니다 (최대 50자)`);
    }
    if (!item.party_id) {
      errors.push(`"${label}"에 인물을 선택해주세요`);
    }
  }

  return errors;
};
```

## 5. Migration Strategy

### 5.1 DynamoDB 스키마 확장

DynamoDB는 스키마리스이므로 마이그레이션 불필요.
- 새 필드 `speaker_mapping`은 Optional
- 기존 데이터는 해당 필드 없음 → `None`으로 처리
- 하위 호환성 100% 유지

### 5.2 코드 호환성

```python
# 기존 코드 호환성 유지
def get_speaker_mapping(evidence: Dict) -> Optional[Dict]:
    """안전하게 speaker_mapping 조회"""
    return evidence.get("speaker_mapping")  # 없으면 None

# 사실관계 생성 시
mapping = get_speaker_mapping(evidence)
if mapping:
    # 매핑 정보를 프롬프트에 추가
else:
    # 기존 방식대로 처리
```

## 6. Indexing

### 6.1 DynamoDB GSI

기존 GSI 활용:
- `case_id-index`: case_id로 해당 케이스의 모든 증거 조회

**신규 인덱스 불필요**:
- 화자 매핑으로 검색하는 유스케이스 없음
- 증거 조회 시 함께 반환되므로 별도 쿼리 불필요

## 7. Audit Trail

### 7.1 Audit Log Entry

화자 매핑 변경 시 audit_logs 테이블에 기록:

```python
{
    "log_id": "audit_xxx",
    "action": "SPEAKER_MAPPING_UPDATE",
    "entity_type": "evidence",
    "entity_id": "evt_abc123",
    "user_id": "user_lawyer123",
    "case_id": "case_xyz789",
    "changes": {
        "before": null,  # 또는 이전 매핑
        "after": {
            "나": {"party_id": "party_001", "party_name": "김동우"},
            "상대방": {"party_id": "party_002", "party_name": "김도연"}
        }
    },
    "timestamp": "2025-12-22T14:30:00Z"
}
```

## 8. Data Relationships

```
┌─────────────────┐       ┌─────────────────┐
│ Evidence        │       │ Party (RDS)     │
│ (DynamoDB)      │       │                 │
│                 │       │ id              │
│ evidence_id ────┼───────│ case_id         │
│ case_id         │       │ name            │
│ speaker_mapping │──────▶│ type            │
│   └─party_id    │       │                 │
│                 │       └─────────────────┘
└─────────────────┘
        │
        │ speaker_mapping.party_id
        │ references party.id
        ▼
┌─────────────────────────────────────────┐
│ 제약: party는 동일 case_id에 속해야 함    │
│ (Case Isolation 원칙)                   │
└─────────────────────────────────────────┘
```

# API Contracts: 증거 화자 매핑

**Feature**: 015-evidence-speaker-mapping
**Date**: 2025-12-22
**Phase**: 1 (Design)

## 1. API Endpoints

### 1.1 화자 매핑 저장/수정

**Endpoint**: `PATCH /evidence/{evidence_id}/speaker-mapping`

**Description**: 증거의 화자 매핑 정보를 저장하거나 수정합니다.

**Headers**:
```
Cookie: access_token=<JWT>
Content-Type: application/json
```

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| evidence_id | string | Yes | 증거 ID |

**Request Body**:
```json
{
  "speaker_mapping": {
    "나": {
      "party_id": "party_001",
      "party_name": "김동우"
    },
    "상대방": {
      "party_id": "party_002",
      "party_name": "김도연"
    }
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| speaker_mapping | object | Yes | 화자명 → 인물 정보 매핑. 빈 객체 `{}` 전송 시 기존 매핑 삭제 |
| speaker_mapping.{label} | object | - | 개별 화자 매핑 |
| speaker_mapping.{label}.party_id | string | Yes | PartyNode ID (해당 케이스에 속해야 함) |
| speaker_mapping.{label}.party_name | string | Yes | 인물 이름 (표시용) |

**Response (200 OK)**:
```json
{
  "evidence_id": "evt_abc123",
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
  "updated_at": "2025-12-22T14:30:00Z",
  "updated_by": "user_lawyer123"
}
```

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_REQUEST | 잘못된 요청 형식 |
| 400 | INVALID_PARTY | party_id가 해당 케이스에 속하지 않음 |
| 400 | TOO_MANY_SPEAKERS | 화자 매핑이 10개 초과 |
| 401 | UNAUTHORIZED | 인증 필요 |
| 403 | FORBIDDEN | 증거 접근 권한 없음 |
| 404 | NOT_FOUND | 증거를 찾을 수 없음 |

**Error Response Body**:
```json
{
  "detail": "증거를 찾을 수 없습니다",
  "code": "NOT_FOUND"
}
```

---

### 1.2 화자 매핑 조회 (기존 API 확장)

**Endpoint**: `GET /evidence/{evidence_id}`

**Description**: 증거 상세 조회 시 화자 매핑 정보도 함께 반환합니다.

**Response (200 OK)** - 확장된 응답:
```json
{
  "id": "evt_abc123",
  "case_id": "case_xyz789",
  "type": "image",
  "filename": "kakaotalk_capture.jpg",
  "status": "completed",
  "ai_summary": "카카오톡 대화 내용...",
  "content": "나: 왜 그랬어?\n상대방: 미안해...",
  "labels": ["폭언", "협박"],
  "speaker": "원고",
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
  "created_at": "2025-12-20T10:00:00Z",
  "updated_at": "2025-12-22T14:30:00Z"
}
```

**새로 추가된 필드**:
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| speaker_mapping | object | Yes | 화자 매핑 정보 (없으면 null) |
| speaker_mapping_updated_at | string (ISO8601) | Yes | 매핑 마지막 수정 시각 |

---

### 1.3 증거 목록 조회 (기존 API 확장)

**Endpoint**: `GET /cases/{case_id}/evidence`

**Description**: 증거 목록 조회 시 화자 매핑 여부를 간략히 반환합니다.

**Response (200 OK)** - 확장된 응답:
```json
{
  "evidence": [
    {
      "id": "evt_abc123",
      "case_id": "case_xyz789",
      "type": "image",
      "filename": "kakaotalk_capture.jpg",
      "status": "completed",
      "ai_summary": "카카오톡 대화 내용...",
      "has_speaker_mapping": true,
      "created_at": "2025-12-20T10:00:00Z"
    },
    {
      "id": "evt_def456",
      "case_id": "case_xyz789",
      "type": "audio",
      "filename": "recording.mp3",
      "status": "completed",
      "ai_summary": "통화 녹음 내용...",
      "has_speaker_mapping": false,
      "created_at": "2025-12-21T09:00:00Z"
    }
  ],
  "total": 2
}
```

**새로 추가된 필드**:
| Field | Type | Description |
|-------|------|-------------|
| has_speaker_mapping | boolean | 화자 매핑 설정 여부 |

---

## 2. Related APIs (Existing)

### 2.1 인물 목록 조회

**Endpoint**: `GET /cases/{case_id}/parties`

**Usage**: 화자 매핑 모달에서 인물 선택 드롭다운에 사용

**Response**:
```json
{
  "items": [
    {
      "id": "party_001",
      "case_id": "case_xyz789",
      "type": "plaintiff",
      "name": "김동우",
      "alias": null,
      "created_at": "2025-12-15T10:00:00Z"
    },
    {
      "id": "party_002",
      "case_id": "case_xyz789",
      "type": "defendant",
      "name": "김도연",
      "alias": null,
      "created_at": "2025-12-15T10:00:00Z"
    }
  ],
  "total": 2
}
```

---

### 2.2 사실관계 생성 (수정 필요)

**Endpoint**: `POST /cases/{case_id}/fact-summary/generate`

**내부 로직 변경**:
- `FactSummaryService._collect_evidence_summaries()`에서 `speaker_mapping` 포함 조회
- `_build_generation_prompt()`에서 매핑 정보를 증거 컨텍스트에 추가

**프롬프트 예시**:
```
[증거1] (image) 2024-01-15
[화자 정보: 나=김동우, 상대방=김도연]
카카오톡 대화에서 "나"가 상대방에게 폭언을 했다...
---
```

---

## 3. Frontend API Client

### 3.1 화자 매핑 업데이트

**파일**: `frontend/src/lib/api/evidence.ts`

```typescript
export interface SpeakerMappingItem {
  party_id: string;
  party_name: string;
}

export type SpeakerMapping = Record<string, SpeakerMappingItem>;

export interface SpeakerMappingUpdateRequest {
  speaker_mapping: SpeakerMapping;
}

export interface SpeakerMappingUpdateResponse {
  evidence_id: string;
  speaker_mapping: SpeakerMapping | null;
  updated_at: string | null;
  updated_by: string | null;
}

/**
 * 증거의 화자 매핑 저장/수정
 */
export async function updateSpeakerMapping(
  evidenceId: string,
  request: SpeakerMappingUpdateRequest
): Promise<ApiResponse<SpeakerMappingUpdateResponse>> {
  return apiRequest<SpeakerMappingUpdateResponse>(
    `/evidence/${evidenceId}/speaker-mapping`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    }
  );
}

/**
 * 증거의 화자 매핑 삭제 (빈 객체 전송)
 */
export async function clearSpeakerMapping(
  evidenceId: string
): Promise<ApiResponse<SpeakerMappingUpdateResponse>> {
  return updateSpeakerMapping(evidenceId, { speaker_mapping: {} });
}
```

---

## 4. Error Handling

### 4.1 Backend Error Codes

```python
class SpeakerMappingErrors:
    INVALID_PARTY = "INVALID_PARTY"  # party_id가 케이스에 속하지 않음
    TOO_MANY_SPEAKERS = "TOO_MANY_SPEAKERS"  # 10개 초과
    SPEAKER_LABEL_TOO_LONG = "SPEAKER_LABEL_TOO_LONG"  # 화자명 50자 초과
```

### 4.2 Frontend Error Handling

```typescript
// 화자 매핑 저장 시 에러 처리
const handleSave = async () => {
  try {
    const response = await updateSpeakerMapping(evidenceId, { speaker_mapping });
    if (response.error) {
      switch (response.code) {
        case 'INVALID_PARTY':
          toast.error('선택한 인물이 이 사건에 속하지 않습니다');
          break;
        case 'TOO_MANY_SPEAKERS':
          toast.error('화자는 최대 10명까지 매핑할 수 있습니다');
          break;
        default:
          toast.error('화자 매핑 저장에 실패했습니다');
      }
      return;
    }
    toast.success('화자 매핑이 저장되었습니다');
    onClose();
  } catch (error) {
    toast.error('네트워크 오류가 발생했습니다');
  }
};
```

---

## 5. Testing Contracts

### 5.1 Contract Tests (Backend)

```python
class TestSpeakerMappingAPI:
    """화자 매핑 API 계약 테스트"""

    def test_update_speaker_mapping_success(self, client, auth_headers, evidence):
        """정상적인 화자 매핑 저장"""
        response = client.patch(
            f"/evidence/{evidence.id}/speaker-mapping",
            json={
                "speaker_mapping": {
                    "나": {"party_id": "party_001", "party_name": "김동우"}
                }
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["speaker_mapping"]["나"]["party_id"] == "party_001"

    def test_update_speaker_mapping_invalid_party(self, client, auth_headers, evidence):
        """다른 케이스의 party_id로 매핑 시도"""
        response = client.patch(
            f"/evidence/{evidence.id}/speaker-mapping",
            json={
                "speaker_mapping": {
                    "나": {"party_id": "party_other_case", "party_name": "홍길동"}
                }
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert response.json()["code"] == "INVALID_PARTY"

    def test_clear_speaker_mapping(self, client, auth_headers, evidence_with_mapping):
        """화자 매핑 삭제"""
        response = client.patch(
            f"/evidence/{evidence_with_mapping.id}/speaker-mapping",
            json={"speaker_mapping": {}},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["speaker_mapping"] is None
```

### 5.2 Contract Tests (Frontend)

```typescript
describe('Speaker Mapping API', () => {
  it('should update speaker mapping', async () => {
    const response = await updateSpeakerMapping('evt_123', {
      speaker_mapping: {
        '나': { party_id: 'party_001', party_name: '김동우' }
      }
    });

    expect(response.data).toBeDefined();
    expect(response.data?.speaker_mapping['나'].party_id).toBe('party_001');
  });

  it('should clear speaker mapping with empty object', async () => {
    const response = await clearSpeakerMapping('evt_123');

    expect(response.data).toBeDefined();
    expect(response.data?.speaker_mapping).toBeNull();
  });
});
```

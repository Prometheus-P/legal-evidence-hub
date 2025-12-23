# Research: 증거 화자 매핑

**Feature**: 015-evidence-speaker-mapping
**Date**: 2025-12-22
**Phase**: 0 (Research)

## 1. Existing Code Analysis

### 1.1 Evidence Storage (DynamoDB)

**파일**: `backend/app/utils/dynamo.py`

현재 증거 메타데이터 스키마:
```python
{
    "evidence_id": str,       # PK
    "case_id": str,           # GSI partition key
    "type": str,              # image|audio|video|text|pdf
    "filename": str,
    "s3_key": str,
    "status": str,            # pending|processing|completed|failed
    "timestamp": str,         # ISO8601
    "speaker": str,           # 원고|피고|제3자|unknown (기존 단일 화자)
    "labels": list[str],      # AI-generated labels
    "ai_summary": str,        # AI 요약
    "content": str,           # STT/OCR 전문
    "qdrant_id": str,         # 벡터 저장소 ID
    "created_at": str,
    "updated_at": str
}
```

**확장 필요**: `speaker_mapping` 필드 추가
```python
"speaker_mapping": {
    "나": {"party_id": "party_123", "party_name": "김동우"},
    "상대방": {"party_id": "party_456", "party_name": "김도연"}
}
```

### 1.2 Evidence API (Backend)

**파일**: `backend/app/api/evidence.py`

현재 엔드포인트:
- `POST /evidence/presigned-url` - 업로드 URL 생성
- `POST /evidence/upload-complete` - 업로드 완료 알림
- `GET /evidence/{id}` - 증거 상세 조회
- `GET /evidence/{id}/status` - 처리 상태 조회
- `POST /evidence/{id}/retry` - 재처리 요청

**추가 필요**:
- `PATCH /evidence/{id}/speaker-mapping` - 화자 매핑 저장/수정

### 1.3 Party API (Backend)

**파일**: `backend/app/api/parties.py`

현재 엔드포인트:
- `GET /cases/{case_id}/parties` - 인물 목록 조회
- `GET /cases/{case_id}/parties/{id}` - 인물 상세
- `POST /cases/{case_id}/parties` - 인물 생성
- `PATCH /cases/{case_id}/parties/{id}` - 인물 수정
- `DELETE /cases/{case_id}/parties/{id}` - 인물 삭제

**활용**: 화자 매핑 UI에서 인물 목록 드롭다운에 사용

### 1.4 Fact Summary Service

**파일**: `backend/app/services/fact_summary_service.py`

핵심 메서드:
- `_collect_evidence_summaries()` - DynamoDB에서 증거 수집
- `_build_generation_prompt()` - GPT 프롬프트 생성

**수정 필요**: `_build_generation_prompt()`에서 `speaker_mapping` 정보를 프롬프트에 주입

현재 프롬프트 구조 (라인 272-286):
```python
evidence_text = ""
for i, evidence in enumerate(evidence_list, 1):
    timestamp = evidence.get("timestamp") or evidence.get("created_at") or "날짜 미상"
    summary = evidence.get("ai_summary", "")
    evidence_type = evidence.get("type", "")
    labels = evidence.get("labels", [])
    # ... 증거 포맷팅
```

**확장 방안**:
```python
# speaker_mapping이 있으면 컨텍스트 추가
speaker_mapping = evidence.get("speaker_mapping")
if speaker_mapping:
    mapping_str = ", ".join([f"{k}={v['party_name']}" for k, v in speaker_mapping.items()])
    evidence_text += f"[화자 정보: {mapping_str}]\n"
```

### 1.5 Frontend Evidence Components

**파일**: `frontend/src/components/evidence/EvidenceDataTable.tsx`

- TanStack Table 기반 데이터 테이블
- 컬럼: 파일명, 타입, 상태, 날짜, 요약
- **확장 필요**: 화자 매핑 상태 컬럼/뱃지 추가

**파일**: `frontend/src/lib/api/evidence.ts`

현재 API 함수:
- `getEvidence()` - 목록 조회
- `getEvidenceDetail()` - 상세 조회
- `uploadToS3()` - S3 업로드
- `deleteEvidence()` - 삭제

**추가 필요**:
```typescript
export async function updateSpeakerMapping(
  evidenceId: string,
  mapping: Record<string, { party_id: string; party_name: string }>
): Promise<ApiResponse<Evidence>>
```

### 1.6 Frontend Types

**파일**: `frontend/src/types/evidence.ts`

현재 Evidence 인터페이스에 없는 필드:
```typescript
// 추가 필요
speakerMapping?: Record<string, {
  party_id: string;
  party_name: string;
}>;
```

## 2. Integration Points

### 2.1 화자 매핑 설정 플로우

```
1. 사용자가 증거 상세 페이지 진입
2. "화자 매핑" 버튼 클릭 → SpeakerMappingModal 열림
3. Party API 호출 → 인물 목록 표시
4. 사용자가 화자별 인물 선택 (나 → 김동우, 상대방 → 김도연)
5. 저장 버튼 → PATCH /evidence/{id}/speaker-mapping
6. DynamoDB 업데이트, 화면 반영
```

### 2.2 사실관계 생성 플로우

```
1. POST /cases/{id}/fact-summary/generate 호출
2. FactSummaryService._collect_evidence_summaries()에서 증거 수집
3. 각 증거의 speaker_mapping 확인
4. _build_generation_prompt()에서 매핑 정보를 컨텍스트에 추가
5. GPT-4o-mini가 실제 인물명으로 사실관계 생성
```

## 3. Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Frontend                                                        │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │ EvidenceDetail Page │    │ SpeakerMappingModal │            │
│  │  - 증거 상세 표시    │───▶│  - Party 목록 로드   │            │
│  │  - 매핑 버튼        │    │  - 화자-인물 연결    │            │
│  └─────────────────────┘    └──────────┬──────────┘            │
│                                        │                        │
│                         PATCH /evidence/{id}/speaker-mapping    │
└───────────────────────────────────────┼─────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ Backend                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │ evidence.py Router  │───▶│ EvidenceService     │            │
│  │  - 요청 검증        │    │  - 권한 확인         │            │
│  │  - 응답 포맷팅      │    │  - 매핑 데이터 저장  │            │
│  └─────────────────────┘    └──────────┬──────────┘            │
│                                        │                        │
│                                        ▼                        │
│                             ┌─────────────────────┐            │
│                             │ dynamo.py           │            │
│                             │  - DynamoDB 업데이트 │            │
│                             └─────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│ DynamoDB (leh_evidence)                                         │
│  {                                                              │
│    "evidence_id": "evt_123",                                   │
│    "speaker_mapping": {                                        │
│      "나": {"party_id": "party_1", "party_name": "김동우"},     │
│      "상대방": {"party_id": "party_2", "party_name": "김도연"}  │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Technical Decisions

### 4.1 저장 위치: DynamoDB (증거 메타데이터 내)

**선택**: 증거 메타데이터에 `speaker_mapping` 필드 추가

**이유**:
- 증거와 1:1 관계로 함께 조회/저장 가능
- 별도 테이블 불필요 (조인 없음)
- 기존 `get_evidence_by_case()` 함수로 함께 조회

**대안 검토**:
- 별도 테이블: 오버엔지니어링, 조인 필요
- PostgreSQL: 이미 DynamoDB에 증거 메타데이터 저장 중

### 4.2 UI 위치: 증거 상세 화면 내 모달

**선택**: 증거 상세 페이지에서 "화자 매핑" 버튼 → 모달

**이유**:
- 증거 내용을 보면서 화자 식별 가능
- 증거 목록에서 매핑 상태만 뱃지로 표시

**대안 검토**:
- 업로드 시 매핑: 아직 증거 내용 확인 전이라 부적절
- 별도 페이지: 과도한 네비게이션

### 4.3 프롬프트 주입 방식

**선택**: 증거별 컨텍스트에 화자 정보 추가

```
[증거1] (image) 2024-01-15
[화자 정보: 나=김동우, 상대방=김도연]
카카오톡 대화에서 "나"가 상대방에게 폭언을 했다...
```

**이유**:
- 증거별 컨텍스트 명확
- GPT가 대화 내용을 정확한 인물로 해석 가능

## 5. Edge Cases Handling

| 엣지 케이스 | 처리 방안 |
|------------|----------|
| 인물관계도에 인물 없음 | 매핑 UI에 "인물을 먼저 등록하세요" 안내 |
| 매핑된 인물 삭제됨 | 삭제 시 해당 매핑 자동 해제 (orphan 정리) |
| 부분 매핑 (일부 화자만) | 매핑된 화자만 실제 인물명, 나머지는 원본 |
| 동일 인물 중복 매핑 | 허용 (나=김동우, 화자1=김동우 가능) |
| 대화형 아닌 증거 | 모든 증거에 UI 표시, 선택사항이므로 무해 |

## 6. Dependencies Verification

| 의존성 | 상태 | 비고 |
|--------|------|------|
| 014-case-fact-summary | ✅ 완료 | PR #398 머지됨, FactSummaryService 존재 |
| 012-precedent-integration | ✅ 완료 | PartyNode, PartyAPI 존재 |
| DynamoDB leh_evidence 테이블 | ✅ 존재 | 스키마 확장만 필요 |
| Frontend Evidence 컴포넌트 | ✅ 존재 | EvidenceDataTable, EvidenceDetail |

## 7. Risk Assessment

| 리스크 | 확률 | 영향 | 완화 방안 |
|--------|------|------|----------|
| 기존 증거 처리 영향 | Low | High | Optional 필드로 추가, 하위 호환성 유지 |
| 프롬프트 토큰 증가 | Low | Low | 매핑 정보는 짧은 텍스트 (~50 토큰) |
| 인물 삭제 시 orphan | Medium | Low | 인물 삭제 API에서 매핑 정리 로직 추가 |

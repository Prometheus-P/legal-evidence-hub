# Research: 사건 전체 사실관계 요약

**Feature**: 014-case-fact-summary
**Date**: 2025-12-22

## 1. 저장소 선택: DynamoDB vs PostgreSQL

### Decision: DynamoDB (leh_case_summary 테이블)

### Rationale:
1. **기존 증거 데이터와 일관성**: 증거 메타데이터가 이미 DynamoDB에 저장됨 (leh_evidence)
2. **유연한 스키마**: 사실관계 버전 이력, AI 생성본/수정본 구분 등 동적 필드 지원
3. **case_id 기반 파티셔닝**: 사건 격리 원칙(Constitution II) 자연스럽게 준수
4. **기존 인프라 활용**: 새 RDS 테이블 마이그레이션 불필요

### Alternatives Considered:
- **PostgreSQL**: 관계형 데이터에 적합하나, 사실관계 요약은 단일 사건 내 독립적 문서로 DynamoDB가 더 적합
- **S3**: 대용량 텍스트 저장 가능하나, 빈번한 조회/수정에 비효율적

---

## 2. 사실관계 생성 프롬프트 전략

### Decision: 구조화된 시간순 요약 프롬프트

### Rationale:
1. **시간순 정렬**: 법적 문서는 시간 순서가 중요 (FR-002)
2. **출처 표시**: 각 사실에 증거 ID 태그 포함 (FR-003)
3. **유책사유 강조**: 민법 840조 관련 키워드 우선 배치

### Prompt Template:
```
당신은 이혼 소송 전문 법률 보조 AI입니다.

아래 증거들의 요약을 종합하여 사건의 사실관계를 시간순으로 정리해주세요.

## 작성 규칙:
1. 시간순으로 정렬 (오래된 것 → 최근)
2. 각 사실 앞에 출처 증거 표시: [증거N]
3. 객관적 사실만 기술, 의견이나 추측 배제
4. 유책사유(부정행위, 가정폭력, 악의의 유기 등) 명확히 표시
5. 핵심 사실 위주로 3000자 이내

## 증거 요약:
{evidence_summaries}

## 출력 형식:
### 사건 개요
[혼인 기간, 당사자 관계 등 기본 정보]

### 사실관계
1. [증거1] 2023년 3월 - ...
2. [증거2] 2023년 5월 - ...
...

### 유책사유 요약
- 부정행위: ...
- 가정폭력: ...
```

---

## 3. DraftService/PrecedentService 통합 방식

### Decision: 저장된 사실관계 우선 참조

### Rationale:
1. **일관성**: 변호사가 수정한 사실관계가 모든 후속 작업에 반영
2. **품질 보장**: AI 생성본보다 변호사 검토본 우선
3. **기존 코드 최소 수정**: 각 서비스에 사실관계 조회 로직 추가

### Integration Points:

**DraftService 수정** (`draft_service.py`):
```python
def generate_draft_preview(self, case_id: str, ...):
    # 기존 코드 유지
    ...
    # 사실관계 조회 추가
    fact_summary = get_case_fact_summary(case_id)
    if fact_summary:
        # 수정본 우선, 없으면 AI 생성본
        context = fact_summary.get("modified_summary") or fact_summary.get("ai_summary")
        # 프롬프트에 사실관계 컨텍스트 추가
        prompt_messages = self.prompt_builder.build_draft_prompt(
            ...,
            fact_summary_context=context
        )
```

**PrecedentService 수정** (`precedent_service.py`):
```python
def search_similar_precedents(self, case_id: str, ...):
    # 사실관계 기반 검색 쿼리
    fact_summary = get_case_fact_summary(case_id)
    if fact_summary and fact_summary.get("modified_summary"):
        query = fact_summary["modified_summary"]
    else:
        # 기존 유책사유 키워드 기반 검색
        fault_types = self.get_fault_types(case_id)
        query = " ".join(fault_types)
```

---

## 4. 버전 관리 전략

### Decision: 단순 1-버전 백업

### Rationale:
1. **MVP 우선**: 복잡한 버전 이력보다 핵심 기능 집중
2. **충분한 안전망**: 재생성 시 이전 버전 복구 가능
3. **DynamoDB 비용 효율**: 히스토리 무제한 저장 시 비용 증가

### Schema:
```json
{
  "case_id": "case_xxx",
  "ai_summary": "AI 생성 원본",
  "modified_summary": "변호사 수정본 (null 가능)",
  "previous_version": "재생성 전 이전 수정본 (null 가능)",
  "created_at": "ISO8601",
  "modified_at": "ISO8601",
  "modified_by": "user_xxx"
}
```

---

## 5. 프론트엔드 편집기 선택

### Decision: Textarea + Unsaved Changes Warning

### Rationale:
1. **단순성**: 복잡한 리치 텍스트 에디터 불필요 (법률 문서는 플레인 텍스트)
2. **기존 패턴 일관성**: DraftPreviewPanel과 유사한 UX
3. **즉각적인 구현**: 외부 라이브러리 의존성 최소화

### Alternatives Considered:
- **TipTap/ProseMirror**: 리치 텍스트 지원하나 오버스펙
- **Monaco Editor**: 코드 편집기, 법률 문서에 부적합

---

## 6. API 타임아웃 처리

### Decision: 스트리밍 없이 동기 응답 + 로딩 상태

### Rationale:
1. **API Gateway 30초 제한**: 증거 20개 기준 충분
2. **구현 복잡도**: SSE/WebSocket보다 단순 REST 선호
3. **사용자 경험**: 로딩 스피너로 대기 시간 표시

### Error Handling:
- 타임아웃 시: "생성에 실패했습니다. 다시 시도해주세요" 메시지
- 증거 50개 초과 시: 핵심 증거 50개만 사용 + 경고 메시지

---

## 7. 테스트 전략

### Decision: TDD 사이클 적용

### Rationale:
- Constitution VII 준수
- 서비스 로직 단위 테스트 우선
- DynamoDB Mocking으로 격리된 테스트

### Test Cases:
1. `test_generate_fact_summary_success`: 정상 생성
2. `test_generate_fact_summary_no_evidence`: 증거 없음 오류
3. `test_update_fact_summary`: 수정 저장
4. `test_regenerate_fact_summary`: 재생성 시 이전 버전 백업
5. `test_draft_uses_modified_summary`: 초안 생성 시 수정본 우선
6. `test_precedent_uses_modified_summary`: 판례 검색 시 수정본 우선

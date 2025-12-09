# Data Model: Calm-Control Design System

**Feature**: 010-calm-control-design
**Date**: 2025-12-09

## Entities

### 1. Asset (재산)

**Description**: 이혼 사건의 재산 항목을 나타냅니다.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| case_id | UUID | Yes | 소속 사건 ID (FK → cases) |
| asset_type | Enum | Yes | 재산 유형 |
| name | String(255) | Yes | 재산 명칭 |
| current_value | Decimal | Yes | 현재 가액 (원) |
| ownership | Enum | Yes | 소유권 구분 |
| division_ratio_plaintiff | Integer | Yes | 원고 분할 비율 (0-100) |
| division_ratio_defendant | Integer | Yes | 피고 분할 비율 (0-100) |
| acquisition_date | Date | No | 취득일 |
| notes | Text | No | 비고 |
| created_at | DateTime | Yes | 생성 시각 |
| updated_at | DateTime | Yes | 수정 시각 |

**Enums**:

```
AssetType:
  - real_estate: 부동산
  - vehicle: 차량
  - financial: 금융자산
  - business: 사업자산
  - personal: 개인자산
  - debt: 부채
  - other: 기타

Ownership:
  - joint: 공동소유
  - plaintiff: 원고 단독
  - defendant: 피고 단독
```

**Validation Rules**:
- division_ratio_plaintiff + division_ratio_defendant = 100
- current_value >= 0 (부채는 별도 asset_type으로 처리)
- acquisition_date <= today

**Relationships**:
- Asset N:1 Case (case_id)

---

### 2. Party (당사자)

**Description**: 사건에 관련된 인물을 나타냅니다.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| case_id | UUID | Yes | 소속 사건 ID (FK → cases) |
| name | String(100) | Yes | 이름 |
| role | Enum | Yes | 역할 (원고/피고/증인 등) |
| relationship_to | UUID | No | 관계 대상 Party ID |
| relationship_type | String(50) | No | 관계 유형 (배우자, 자녀, 증인 등) |
| contact | String(255) | No | 연락처 |
| notes | Text | No | 비고 |
| created_at | DateTime | Yes | 생성 시각 |
| updated_at | DateTime | Yes | 수정 시각 |

**Enums**:

```
PartyRole:
  - plaintiff: 원고
  - defendant: 피고
  - witness: 증인
  - child: 자녀
  - relative: 친인척
  - other: 기타
```

**Relationships**:
- Party N:1 Case (case_id)
- Party N:N Party (relationship_to - self-referencing for graph edges)

---

### 3. RiskFlag (위험 플래그)

**Description**: 사건의 주의가 필요한 위험 요소입니다. (읽기 전용, AI Worker 생성)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| case_id | UUID | Yes | 소속 사건 ID |
| level | Enum | Yes | 위험 수준 |
| title | String(100) | Yes | 위험 제목 |
| description | Text | Yes | 상세 설명 |
| evidence_id | UUID | No | 관련 증거 ID |
| created_at | DateTime | Yes | 생성 시각 |
| resolved_at | DateTime | No | 해결 시각 |

**Enums**:

```
RiskLevel:
  - high: 높음 (즉시 대응 필요)
  - medium: 중간 (주의 필요)
  - low: 낮음 (참고)
```

---

### 4. AIRecommendation (AI 추천)

**Description**: AI가 제안하는 다음 행동입니다. (읽기 전용, AI Worker 생성)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| case_id | UUID | Yes | 소속 사건 ID |
| title | String(100) | Yes | 추천 제목 |
| description | Text | Yes | 추천 내용 |
| confidence | Integer | Yes | 신뢰도 (0-100%) |
| action_type | Enum | Yes | 추천 액션 유형 |
| action_payload | JSON | No | 액션 실행에 필요한 데이터 |
| created_at | DateTime | Yes | 생성 시각 |
| dismissed_at | DateTime | No | 무시 시각 |

**Enums**:

```
ActionType:
  - review_evidence: 증거 검토
  - contact_party: 당사자 연락
  - generate_draft: 초안 생성
  - schedule_meeting: 미팅 일정
  - other: 기타
```

---

## State Transitions

### Asset Lifecycle

```
[Created] → [Updated]* → [Deleted]
```

- Created: POST /cases/{id}/assets로 생성
- Updated: PUT /cases/{id}/assets/{assetId}로 분할 비율 등 수정
- Deleted: DELETE /cases/{id}/assets/{assetId}로 삭제

### RiskFlag Lifecycle

```
[Active] → [Resolved]
```

- Active: AI Worker가 분석 후 생성
- Resolved: 변호사가 해결 표시 (resolved_at 설정)

### AIRecommendation Lifecycle

```
[Active] → [Dismissed] or [Actioned]
```

- Active: AI Worker가 분석 후 생성
- Dismissed: 변호사가 무시 (dismissed_at 설정)
- Actioned: 변호사가 실행 (별도 추적)

---

## ER Diagram

```
┌──────────┐       ┌──────────┐       ┌───────────────┐
│  cases   │──1:N──│  assets  │       │  risk_flags   │
└──────────┘       └──────────┘       └───────────────┘
     │                                       │
     │                                       │
     └──────────────1:N─────────────────────┘
     │
     │         ┌──────────┐
     └──1:N────│  parties │───N:N───┐
               └──────────┘         │
                    │               │
                    └───────────────┘
                    (relationship_to)
     │
     │         ┌──────────────────────┐
     └──1:N────│  ai_recommendations  │
               └──────────────────────┘
```

---

## Design Tokens (Non-Entity)

디자인 토큰은 데이터베이스에 저장되지 않고 CSS 변수로 정의됩니다.

### Color Tokens

```css
/* Primary - Teal */
--color-primary-50: hsl(174, 42%, 95%);
--color-primary-100: hsl(174, 42%, 90%);
--color-primary-200: hsl(174, 42%, 80%);
--color-primary-300: hsl(174, 42%, 65%);
--color-primary-400: hsl(174, 42%, 50%);
--color-primary-500: hsl(174, 42%, 40%);  /* Main */
--color-primary-600: hsl(174, 42%, 32%);
--color-primary-700: hsl(174, 42%, 24%);

/* Neutral - Gray */
--color-neutral-50: hsl(220, 10%, 98%);
--color-neutral-100: hsl(220, 10%, 96%);
--color-neutral-200: hsl(220, 10%, 90%);
--color-neutral-300: hsl(220, 10%, 80%);
--color-neutral-400: hsl(220, 10%, 60%);
--color-neutral-500: hsl(220, 10%, 45%);
--color-neutral-600: hsl(220, 10%, 35%);
--color-neutral-700: hsl(220, 10%, 25%);
--color-neutral-800: hsl(220, 10%, 15%);
--color-neutral-900: hsl(220, 10%, 10%);

/* Semantic */
--color-success: hsl(142, 40%, 45%);
--color-warning: hsl(38, 50%, 50%);
--color-error: hsl(0, 50%, 50%);
```

### Typography Tokens

```css
--font-family-sans: 'Pretendard', 'Inter', system-ui, sans-serif;
--font-size-xs: 0.75rem;   /* 12px */
--font-size-sm: 0.875rem;  /* 14px */
--font-size-base: 1rem;    /* 16px */
--font-size-lg: 1.125rem;  /* 18px */
--font-size-xl: 1.25rem;   /* 20px */
--font-size-2xl: 1.5rem;   /* 24px */
--font-size-3xl: 1.875rem; /* 30px */
--font-size-4xl: 2.25rem;  /* 36px */
```

### Spacing Tokens

```css
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
--spacing-12: 3rem;    /* 48px */
```

### Shadow Tokens

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
```

### Animation Tokens

```css
--duration-fast: 100ms;
--duration-normal: 150ms;
--duration-slow: 200ms;
--easing-default: ease-out;
```

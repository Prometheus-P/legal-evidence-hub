# LEH Design System - Calm-Control

> **Version**: 1.0.0
> **Last Updated**: 2025-12-09
> **Status**: Active

## 1. Design Principles (Calm-Control)

### 1.1 Philosophy

LEH의 디자인 시스템은 **"Calm-Control"** 원칙을 따릅니다. 이혼 전문 변호사가 복잡한 사건 데이터를 다루면서도 **심리적 안정감**과 **완전한 통제감**을 동시에 느낄 수 있도록 설계되었습니다.

### 1.2 Core Principles

#### Calm (평온함)
- **저채도 컬러 팔레트**: 눈의 피로를 최소화하는 차분한 색상
- **안정적인 타이포그래피**: 가독성 중심의 서체 선택 (Pretendard)
- **불필요한 애니메이션 최소화**: 모션은 상태 전환 피드백에만 사용
- **충분한 여백**: 정보가 숨 쉴 수 있는 공간 확보
- **일관된 시각적 리듬**: 8pt 그리드 시스템 준수

#### Control (통제감)
- **정보 구조화**: 계층적이고 예측 가능한 정보 배치
- **명확한 상호작용**: 클릭/호버/포커스 상태의 분명한 피드백
- **"변호사가 모든 것을 쥐고 있다"는 감각**: 대시보드 중심 UI
- **AI 제안은 항상 Preview-only**: 자동 제출/발송 절대 금지
- **위험 요소의 조용한 강조**: 색상이 아닌 아이콘+배치+subtle border로 강조

### 1.3 Design Reference

| 역할 | 레퍼런스 | 적용 영역 |
|------|----------|-----------|
| Primary | IBM Carbon Design System | 레이아웃, 컴포넌트, 타이포, 그리드 |
| Secondary | Microsoft Fluent 2 | 포커스, 호버, 모션 강도 |
| Implementation | shadcn/ui + Tailwind CSS | 실제 구현 레이어 |

**왜 이 조합이 LEH에 적합한가?**

1. **Carbon**: 데이터 중심 엔터프라이즈 앱에 최적화. 복잡한 테이블, 폼, 대시보드 패턴이 풍부함
2. **Fluent 2**: 자연스럽고 절제된 인터랙션. 과도한 애니메이션 없이 명확한 피드백 제공
3. **shadcn/ui**: Tailwind 기반으로 커스터마이징 용이. Radix UI primitives로 접근성 기본 제공

---

## 2. Design Tokens

### 2.1 Color Palette

#### Semantic Colors
```css
/* Primary - Clarity Teal (신뢰와 명료함) */
--color-primary: #1ABC9C;
--color-primary-hover: #16A085;
--color-primary-active: #149174;
--color-primary-light: rgba(26, 188, 156, 0.1);

/* Secondary - Deep Trust Blue (권위와 전문성) */
--color-secondary: #2C3E50;
--color-secondary-hover: #1a252f;
--color-secondary-light: rgba(44, 62, 80, 0.1);

/* Neutral Scale (정보 계층 표현) */
--color-neutral-50: #F8F9FA;   /* 배경 */
--color-neutral-100: #EEF2F6;  /* 카드 배경 */
--color-neutral-200: #E2E8F0;  /* 보더 */
--color-neutral-300: #CBD5E1;  /* 비활성 보더 */
--color-neutral-400: #94A3B8;  /* 보조 텍스트 */
--color-neutral-500: #64748B;  /* 캡션 */
--color-neutral-600: #475569;  /* 본문 */
--color-neutral-700: #334155;  /* 강조 본문 */
--color-neutral-800: #1E293B;  /* 제목 */
--color-neutral-900: #0F172A;  /* 최고 강조 */
```

#### Status Colors (Calm Approach)
```css
/* Success - 저채도 녹색 */
--color-success: #2ECC71;
--color-success-light: rgba(46, 204, 113, 0.1);

/* Warning - 저채도 주황 */
--color-warning: #F39C12;
--color-warning-light: rgba(243, 156, 18, 0.1);

/* Error - 저채도 적색 (위험 플래그용) */
--color-error: #E74C3C;
--color-error-light: rgba(231, 76, 60, 0.1);

/* Info - 저채도 청색 */
--color-info: #3498DB;
--color-info-light: rgba(52, 152, 219, 0.1);
```

### 2.2 Typography Scale

| Token | Size | Use Case |
|-------|------|----------|
| `--font-size-xs` | 12px | 라벨, 뱃지, 메타데이터 |
| `--font-size-sm` | 14px | 캡션, 보조 텍스트 |
| `--font-size-base` | 16px | 본문 |
| `--font-size-lg` | 18px | 강조 본문 |
| `--font-size-xl` | 20px | 카드 제목 |
| `--font-size-2xl` | 24px | 섹션 제목 |
| `--font-size-3xl` | 30px | 페이지 제목 |
| `--font-size-4xl` | 36px | 대시보드 숫자 |
| `--font-size-5xl` | 48px | 히어로 디스플레이 |

**Line Height**
- Tight (1.25): 제목, 숫자
- Normal (1.5): 본문
- Relaxed (1.625): 긴 텍스트

### 2.3 Spacing (8pt Grid)

```css
--spacing-1: 4px;    /* 아이콘 내부 */
--spacing-2: 8px;    /* 요소 간 최소 간격 */
--spacing-3: 12px;   /* 관련 요소 간격 */
--spacing-4: 16px;   /* 기본 패딩 */
--spacing-6: 24px;   /* 카드 내부 패딩 */
--spacing-8: 32px;   /* 섹션 간격 */
--spacing-12: 48px;  /* 큰 섹션 간격 */
--spacing-16: 64px;  /* 페이지 섹션 간격 */
```

### 2.4 Elevation (Shadow)

| Level | Token | Use Case |
|-------|-------|----------|
| 0 | none | 플랫 요소 |
| 1 | `--shadow-sm` | 카드, 버튼 |
| 2 | `--shadow-md` | 드롭다운, 팝오버 |
| 3 | `--shadow-lg` | 모달, 다이얼로그 |
| 4 | `--shadow-xl` | 토스트, 알림 |

### 2.5 Border Radius

```css
--radius-sm: 4px;    /* 버튼, 인풋 */
--radius-md: 8px;    /* 카드 */
--radius-lg: 12px;   /* 모달 */
--radius-xl: 16px;   /* 큰 컨테이너 */
--radius-full: 9999px; /* 원형 요소 */
```

---

## 3. Layout Patterns

### 3.1 Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│ Header (64px)                                           │
│ [Logo] [Breadcrumb]                    [Search] [User]  │
├────────────┬────────────────────────────────────────────┤
│ Sidebar    │ Main Content                               │
│ (240px)    │                                            │
│            │ ┌─────────────────────────────────────────┐ │
│ Dashboard  │ │ Stats Row (오늘의 요약)                  │ │
│ Cases      │ └─────────────────────────────────────────┘ │
│ Evidence   │                                            │
│ Drafts     │ ┌──────────────┐ ┌──────────────────────┐ │
│ Calendar   │ │ Priority     │ │ Recent Activity      │ │
│ Settings   │ │ Queue        │ │                      │ │
│            │ │              │ │                      │ │
│            │ └──────────────┘ └──────────────────────┘ │
└────────────┴────────────────────────────────────────────┘
```

### 3.2 Detail Page Layout

```
┌─────────────────────────────────────────────────────────┐
│ Header with Breadcrumb                                  │
├─────────────────────────────────────────────────────────┤
│ Page Title + Actions                                    │
├─────────────────────────────────────────────────────────┤
│ Tab Navigation                                          │
│ [Overview] [Evidence] [Relations] [Assets] [Draft]      │
├─────────────────────────────────────────────────────────┤
│ Tab Content                                             │
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Modal Layout

```
┌─────────────────────────────────────────┐
│ Modal Header                        [X] │
├─────────────────────────────────────────┤
│                                         │
│ Modal Content                           │
│ (max-height: 70vh, scrollable)          │
│                                         │
├─────────────────────────────────────────┤
│ Modal Footer                            │
│             [Cancel] [Primary Action]   │
└─────────────────────────────────────────┘
```

---

## 4. Component Guidelines

### 4.1 Button

**Variants**
- `primary`: 주요 액션 (teal 배경)
- `secondary`: 보조 액션 (투명 배경, teal 테두리)
- `ghost`: 텍스트만 (아이콘 버튼용)
- `danger`: 삭제 등 위험 액션 (error 색상)

**States**
- Default → Hover (darken 10%) → Active (darken 20%) → Disabled (opacity 50%)

**Sizes**
- `sm`: 32px height, 12px font
- `md`: 40px height, 14px font (기본)
- `lg`: 48px height, 16px font

### 4.2 Card

**Structure**
```tsx
<Card>
  <CardHeader>
    <CardTitle>제목</CardTitle>
    <CardDescription>설명</CardDescription>
  </CardHeader>
  <CardContent>
    {/* 내용 */}
  </CardContent>
  <CardFooter>
    {/* 액션 버튼 */}
  </CardFooter>
</Card>
```

**Calm-Control 적용**
- 기본 그림자는 `shadow-sm` (미묘한 존재감)
- Hover 시 `shadow-md`로 살짝 부상
- 위험 사건 카드: 왼쪽에 4px error border만 추가 (색상 강조 최소화)

### 4.3 Table

**Calm-Control 적용**
- 행 사이 구분선은 `neutral-200`
- Hover 행 배경: `neutral-50`
- 정렬 가능 열: 아이콘으로 표시 (색상 변화 없음)
- 선택된 행: `primary-light` 배경

### 4.4 Tag / Badge

**Status Tags (Case)**
```
진행중: neutral-600 bg, neutral-100 text
위험: error-light bg, error text (subtle)
검토필요: warning-light bg, warning text (subtle)
완료: success-light bg, success text
```

**Evidence Tags**
```
이미지: primary-light bg
오디오: secondary-light bg
문서: neutral-200 bg
```

### 4.5 Timeline (Evidence)

```
○──────────────────────────────────────────────────○
│                                                  │
├─ 2024-01-15 ● 카카오톡 대화 (이미지)              │
│                                                  │
├─ 2024-01-14 ○ 녹음 파일                          │
│                                                  │
├─ 2024-01-10 ○ 진단서 (PDF)                       │
│                                                  │
○──────────────────────────────────────────────────○
```

- 현재 포커스된 이벤트: filled circle (●)
- 다른 이벤트: outlined circle (○)
- 연결선: neutral-300

---

## 5. Accessibility & Legal UX

### 5.1 WCAG 2.1 AA Compliance

- **Color Contrast**: 모든 텍스트는 4.5:1 이상 대비율
- **Focus Indicators**: 2px ring, primary 색상
- **Touch Targets**: 최소 44x44px
- **Motion**: `prefers-reduced-motion` 지원

### 5.2 Legal UX Considerations

1. **데이터 무결성 표시**
   - 증거 업로드 시 SHA-256 해시 뱃지 표시
   - Chain of Custody 로그 접근 가능

2. **AI 제안 UI**
   - 항상 "초안 미리보기" 라벨 명시
   - "제출" 버튼은 별도 확인 다이얼로그 필요
   - 자동 제출 기능 없음

3. **위험 플래그**
   - 아이콘: ⚠️ (Shield with exclamation)
   - 색상: subtle border only (error-light)
   - 배치: 대시보드 상단 "위험 사건" 섹션

4. **감사 로그**
   - 모든 CRUD 작업 기록
   - 타임스탬프 + 사용자 표시
   - 읽기 전용 로그 뷰어

---

## 6. Implementation Notes

### 6.1 File Structure

```
frontend/src/
├── styles/
│   └── tokens.css          # Design tokens (CSS variables)
├── app/
│   └── globals.css         # Global styles importing tokens
├── components/
│   ├── ui/                 # Primitive components (shadcn/ui style)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   └── [feature]/          # Feature-specific components
└── tailwind.config.js      # Tailwind theme referencing tokens
```

### 6.2 Token Usage in Components

```tsx
// Good: Use semantic tokens
<button className="bg-primary hover:bg-primary-hover text-primary-contrast">

// Avoid: Hardcoded values
<button className="bg-[#1ABC9C] hover:bg-[#16A085] text-white">
```

### 6.3 Dark Mode Support

모든 토큰은 `.dark` 클래스에서 자동 전환됩니다.
`ThemeProvider`를 통해 시스템 설정 또는 사용자 선택에 따라 적용됩니다.

---

## Appendix: Token Quick Reference

| Category | Token Example | Tailwind Class |
|----------|---------------|----------------|
| Primary Color | `--color-primary` | `bg-primary`, `text-primary` |
| Neutral | `--color-neutral-500` | `bg-neutral-500`, `text-neutral-500` |
| Error | `--color-error` | `bg-error`, `text-error` |
| Shadow | `--shadow-md` | `shadow-md` |
| Radius | `--radius-md` | `rounded-md` |
| Spacing | `--spacing-4` | `p-4`, `m-4` |

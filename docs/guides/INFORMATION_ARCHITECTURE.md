# Information Architecture (IA) Guide

## Overview

Legal Evidence Hub의 정보 구조(Information Architecture) 가이드입니다.
사용자가 원하는 기능에 쉽게 접근할 수 있도록 설계된 화면 간 연결 관계를 문서화합니다.

**Last Updated**: 2025-12-10
**Related Tasks**: T070-T074 (US8 - 정보 구조 개선)

## Design Principles

### 1. 3-Click Rule
모든 주요 기능에 메인 화면에서 3클릭 이내로 접근 가능해야 합니다.

### 2. 1-Depth Navigation
핵심 기능은 메인 네비게이션에서 1-depth로 바로 접근 가능해야 합니다.

### 3. Consistent Navigation
모든 페이지에서 일관된 뒤로가기/홈 버튼 동작을 보장합니다.

## Navigation Structure

### Main Navigation (Sidebar)

변호사 포털 (`/lawyer/*`) 기준:

```
├── 대시보드 (/lawyer/dashboard)
├── 케이스 (/lawyer/cases)
├── 증거 업로드 (/lawyer/evidence/upload)  ← FR-026
├── 초안 생성 (/lawyer/drafts)              ← FR-026
├── 의뢰인 (/lawyer/clients)
├── 일정 (/lawyer/calendar)
├── 메시지 (/lawyer/messages)
├── 청구/결제 (/lawyer/billing)
└── 설정 (/lawyer/settings)
```

### Case List Quick Actions

케이스 목록 페이지 (`/lawyer/cases`)에서 각 케이스 행/카드에 퀵 액션 버튼:

```
케이스 목록 페이지
├── 테이블 뷰 (CaseTable)
│   └── 각 행 → 액션 컬럼
│       ├── 절차 진행 (파란색 아이콘)
│       ├── 재산분할 (초록색 아이콘)
│       └── AI 분석 (보라색 아이콘)
│
└── 카드 뷰 (CaseCard)
    └── 각 카드 → 퀵 액션 버튼
        ├── 절차 (파란색)
        ├── 재산 (초록색)
        └── AI (보라색)
```

### Case Detail Navigation

케이스 상세 페이지 (`/lawyer/cases/[id]`) 내 탭 구조:

```
케이스 상세 페이지
├── 헤더 액션 버튼
│   ├── 절차 진행 → /lawyer/cases/[id]/procedure
│   ├── 재산분할 → /lawyer/cases/[id]/assets
│   ├── 수정 (Modal)
│   ├── 요약 카드 (Modal)
│   └── AI 분석 요청 (Action)
│
├── 탭 네비게이션
│   ├── 증거 자료 (evidence)
│   ├── 타임라인 (timeline)
│   └── 팀원 (members)
│
└── 브레드크럼
    └── 케이스 관리 > 케이스명
```

## Page Hierarchy

### Level 0 (Root)
- `/` - 랜딩 페이지
- `/login` - 로그인
- `/signup` - 회원가입
- `/terms` - 이용약관
- `/privacy` - 개인정보처리방침

### Level 1 (Portal)
- `/lawyer/*` - 변호사 포털
- `/client/*` - 의뢰인 포털
- `/detective/*` - 탐정 포털

### Level 2 (Features)
- `/lawyer/dashboard` - 대시보드
- `/lawyer/cases` - 케이스 목록
- `/lawyer/evidence/upload` - 증거 업로드
- `/lawyer/drafts` - 초안 관리
- `/lawyer/clients` - 의뢰인 관리
- `/lawyer/calendar` - 일정 관리
- `/lawyer/messages` - 메시지
- `/lawyer/billing` - 청구/결제
- `/lawyer/settings` - 설정

### Level 3 (Detail/Action)
- `/lawyer/cases/[id]` - 케이스 상세
- `/lawyer/cases/[id]/procedure` - 절차 진행
- `/lawyer/cases/[id]/assets` - 재산분할
- `/lawyer/cases/[id]/relationship` - 당사자 관계

## Navigation Patterns

### Back Button Behavior

| Page | Back Button Destination |
|------|------------------------|
| 케이스 상세 | 케이스 목록 |
| 절차 진행 | 케이스 상세 |
| 재산분할 | 케이스 상세 |
| 설정 | 이전 페이지 (history.back) |

### Breadcrumb Pattern

모든 Level 3 이상 페이지에 브레드크럼 표시:

```
케이스 관리 / 김철수 v. 이영희 이혼 소송
```

### Home Button

- 로고 클릭: 포털 대시보드로 이동
- 홈 아이콘: 포털 대시보드로 이동

## Access Patterns (3-Click Analysis)

### 증거 업로드

**Before (4+ clicks)**:
대시보드 → 케이스 → 케이스 상세 → 증거 탭 → 업로드

**After (1 click)**:
대시보드 → 증거 업로드 (메인 네비게이션)

### 초안 생성

**Before (3+ clicks)**:
대시보드 → 케이스 → 케이스 상세 → AI 분석 요청

**After (1 click)**:
대시보드 → 초안 생성 (메인 네비게이션)

### 절차 진행 접근

**Before (3+ clicks)**:
대시보드 → 케이스 목록 → 케이스 상세 → 절차 진행 버튼

**After (2 clicks)**:
대시보드 → 케이스 목록 → 절차 진행 퀵 액션 (테이블/카드에서 바로 접근)

### 재산분할 접근

**Before (3+ clicks)**:
대시보드 → 케이스 목록 → 케이스 상세 → 재산분할 버튼

**After (2 clicks)**:
대시보드 → 케이스 목록 → 재산분할 퀵 액션 (테이블/카드에서 바로 접근)

### 케이스 상세 접근

**Path 1**: 대시보드 → 최근 케이스 카드 클릭 (2 clicks)
**Path 2**: 케이스 목록 → 케이스 선택 (2 clicks)

## Footer Navigation

모든 페이지 푸터에 포함:

```
이용약관 | 개인정보처리방침 | 문의하기
© 2025 Legal Evidence Hub. All Rights Reserved. 무단 활용 금지.
```

## Mobile Considerations

### Responsive Sidebar
- Desktop: 고정 사이드바
- Mobile: 햄버거 메뉴 → 드로어

### Touch Targets
- 최소 터치 영역: 44x44px
- 네비게이션 아이템 간격: 8px 이상

## Implementation Files

| Component | File Path |
|-----------|-----------|
| LawyerNav | `frontend/src/components/lawyer/LawyerNav.tsx` |
| PortalSidebar | `frontend/src/components/shared/PortalSidebar.tsx` |
| Footer | `frontend/src/components/common/Footer.tsx` |
| CaseCard | `frontend/src/components/lawyer/CaseCard.tsx` |
| CaseTable | `frontend/src/components/lawyer/CaseTable.tsx` |
| Breadcrumb | Case detail pages (inline) |

## Related Requirements

- **FR-026**: 메인 네비게이션에 주요 기능 1-depth 배치
- **FR-027**: 사건 상세 페이지에서 관련 기능에 1클릭 접근
- **FR-028**: 모든 페이지에서 일관된 뒤로가기/홈 버튼 동작

## Changelog

| Date | Change | Task |
|------|--------|------|
| 2025-12-10 | Initial IA documentation | T074 |
| 2025-12-10 | Added 증거업로드, 초안생성 to main nav | T071 |
| 2025-12-10 | Added quick actions to CaseCard/CaseTable (절차, 재산분할, AI 분석) | IA 개선 |

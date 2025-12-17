# Implementation Plan: Calm-Control Design System

**Branch**: `010-calm-control-design` | **Date**: 2025-12-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-calm-control-design/spec.md`

## Summary

이 기능은 LEH 플랫폼에 "Calm-Control" 디자인 시스템을 구현합니다. 저채도 색상 팔레트, 안정적인 타이포그래피, 최소한의 애니메이션으로 변호사에게 "전문적이고 신뢰할 수 있는" 사용자 경험을 제공합니다.

**주요 구현 항목**:
1. 디자인 토큰 시스템 (색상, 타이포그래피, 간격, 그림자)
2. 대시보드 위젯 컴포넌트 (RiskFlagCard, AIRecommendationCard)
3. 사건 관계도 그래프 (React Flow 기반)
4. 재산 분할 폼 (CRUD + 실시간 계산)

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.11+ (Backend API)
**Primary Dependencies**: Next.js 14, React 18, React Flow, Tailwind CSS
**Storage**: PostgreSQL (cases, assets), Backend API (/cases/{id}/assets)
**Testing**: Jest + React Testing Library (Frontend), pytest (Backend)
**Target Platform**: Web (Desktop-first, Chrome/Edge/Safari)
**Project Type**: Web application (Frontend + Backend)
**Performance Goals**: 60fps UI interactions, <100ms state updates
**Constraints**: 애니메이션 duration ≤200ms, WCAG 2.1 AA 명암비 준수
**Scale/Scope**: ~10 new components, ~5 new API endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | N/A | 디자인 시스템은 증거 데이터를 직접 다루지 않음 |
| II. Case Isolation | ✅ PASS | 재산 분할 API는 case_id로 격리됨 |
| III. No Auto-Submit | ✅ PASS | 모든 UI는 사용자 확인 후 동작 |
| IV. AWS-Only Storage | ✅ PASS | 외부 저장소 사용 없음 |
| V. Clean Architecture | ✅ PASS | Backend는 Router→Service→Repository 패턴 준수 |
| VI. Branch Protection | ✅ PASS | feat/010-calm-control-design 브랜치에서 작업 |
| VII. TDD Cycle | ⚠️ REQUIRED | 프론트엔드 컴포넌트 테스트 우선 작성 필요 |
| VIII. Semantic Versioning | N/A | 디자인 시스템 변경은 MINOR 버전 범프 |

**Gate Result**: PASS (TDD 준수 필요)

## Project Structure

### Documentation (this feature)

```text
specs/010-calm-control-design/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   └── assets-api.yaml  # Asset CRUD OpenAPI spec
└── tasks.md             # Phase 2 output (from /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── styles/
│   │   └── tokens.css           # Design tokens (CSS variables)
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── RiskFlagCard.tsx
│   │   │   ├── RiskFlagCard.test.tsx
│   │   │   ├── AIRecommendationCard.tsx
│   │   │   └── AIRecommendationCard.test.tsx
│   │   ├── case/
│   │   │   ├── CaseRelationsGraph.tsx
│   │   │   ├── CaseRelationsGraph.test.tsx
│   │   │   ├── AssetDivisionForm.tsx
│   │   │   └── AssetDivisionForm.test.tsx
│   │   └── shared/
│   │       └── EmptyStates.tsx  # Reusable empty state component
│   ├── hooks/
│   │   └── useAssets.ts         # Asset CRUD hook
│   ├── lib/api/
│   │   └── assets.ts            # Asset API client
│   └── types/
│       └── assets.ts            # Asset TypeScript types
└── __tests__/
    └── components/              # Component tests

backend/
├── app/
│   ├── api/
│   │   └── assets.py            # Asset router
│   ├── services/
│   │   ├── asset_service.py
│   │   └── division_calculator.py
│   ├── repositories/
│   │   └── asset_repository.py
│   └── schemas/
│       └── assets.py            # Pydantic schemas
└── tests/
    ├── unit/
    │   └── test_division_calculator.py
    └── contract/
        └── test_assets.py
```

**Structure Decision**: Web application 구조 (Frontend + Backend). 기존 LEH 프로젝트 구조를 따르며, 새 컴포넌트는 기능별 폴더(dashboard/, case/)에 배치.

## Complexity Tracking

> No Constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (없음) | - | - |

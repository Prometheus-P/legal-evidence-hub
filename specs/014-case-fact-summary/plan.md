# Implementation Plan: 사건 전체 사실관계 요약

**Branch**: `014-case-fact-summary` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-case-fact-summary/spec.md`

## Summary

개별 증거들의 AI 요약을 종합하여 사건 전체 사실관계(스토리)를 생성하고, 변호사가 이를 수정한 후, 수정된 내용을 기반으로 초안 생성 및 판례 추천에 활용하는 기능 구현. 기존 DraftService/PrecedentService 패턴을 확장하여 FactSummaryService를 신규 구현하고, DynamoDB에 사실관계 요약을 저장한다.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, OpenAI (GPT-4o-mini), boto3
**Storage**: DynamoDB (leh_case_summary 테이블), PostgreSQL (Case 메타데이터 참조)
**Testing**: pytest (Backend), Jest + React Testing Library (Frontend)
**Target Platform**: AWS Lambda (Backend), CloudFront (Frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: 사실관계 생성 30초 이내 (증거 20개 기준)
**Constraints**: API Gateway 30초 타임아웃, Lambda 메모리 제한
**Scale/Scope**: 사건당 최대 100개 증거, 사실관계 텍스트 최대 10,000자

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | ✅ PASS | 사실관계는 증거 원본을 수정하지 않음, 별도 저장 |
| II. Case Isolation | ✅ PASS | case_id 기반 파티셔닝, DynamoDB GSI 활용 |
| III. No Auto-Submit | ✅ PASS | 생성된 사실관계는 Preview Only, 변호사 수정 필수 |
| IV. AWS-Only Storage | ✅ PASS | DynamoDB에 저장, 외부 스토리지 없음 |
| V. Clean Architecture | ✅ PASS | FactSummaryService → DynamoDB Utils 구조 |
| VI. Branch Protection | ✅ PASS | PR 기반 워크플로우 적용 |
| VII. TDD Cycle | ⚠️ APPLICABLE | 테스트 우선 작성 필요 |
| VIII. Semantic Versioning | N/A | 신규 기능, 버전 변경 불필요 |

## Project Structure

### Documentation (this feature)

```text
specs/014-case-fact-summary/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── fact-summary-api.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── fact_summary.py        # NEW: API 라우터
│   ├── schemas/
│   │   └── fact_summary.py        # NEW: Pydantic 스키마
│   ├── services/
│   │   └── fact_summary_service.py  # NEW: 비즈니스 로직
│   └── utils/
│       └── dynamo.py              # MODIFY: 사실관계 CRUD 함수 추가
└── tests/
    ├── unit/
    │   └── test_fact_summary_service.py
    └── integration/
        └── test_fact_summary_api.py

frontend/
├── src/
│   ├── lib/api/
│   │   └── fact-summary.ts        # NEW: API 클라이언트
│   ├── types/
│   │   └── fact-summary.ts        # NEW: TypeScript 타입
│   ├── components/
│   │   └── fact-summary/          # NEW: 컴포넌트 디렉토리
│   │       ├── FactSummaryPanel.tsx
│   │       └── FactSummaryEditor.tsx
│   └── app/lawyer/cases/[id]/
│       └── page.tsx               # MODIFY: FactSummaryPanel 통합
└── tests/
    └── components/
        └── fact-summary/
            └── FactSummaryPanel.test.tsx
```

**Structure Decision**: Web application 패턴 (backend + frontend) 사용. 기존 DraftService, PrecedentService와 동일한 구조로 FactSummaryService 신규 추가.

## Complexity Tracking

> No violations - standard service/API implementation following existing patterns.

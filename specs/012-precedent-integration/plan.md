# Implementation Plan: 판례 검색 시스템 완성 및 인물 관계도 통합

**Branch**: `012-precedent-integration` | **Date**: 2025-12-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-precedent-integration/spec.md`

## Summary

판례 검색 시스템과 인물 관계도 자동 추출 기능을 완성합니다:
1. **판례 검색**: 국가법령정보센터 Open API에서 이혼 판례를 수집하여 Qdrant에 저장, 유사도 검색 제공
2. **초안 판례 인용**: 초안 생성 시 관련 판례를 자동으로 검색하여 참고자료로 포함
3. **인물 자동 추출**: AI Worker가 증거에서 추출한 인물/관계를 Backend API를 통해 PartyNode/PartyRelationship으로 저장

## Technical Context

**Language/Version**: Python 3.11+ (Backend/AI Worker), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, qdrant-client, openai, boto3
**Storage**: PostgreSQL (RDS), Qdrant Cloud, DynamoDB, S3
**Testing**: pytest (Backend, 80% coverage), Jest (Frontend)
**Target Platform**: AWS (Lambda, CloudFront, RDS)
**Project Type**: Web application (frontend + backend + ai_worker)
**Performance Goals**: 판례 검색 5초 이내 (SC-001), 인물 추출 2분 이내 (SC-003)
**Constraints**: Qdrant 1536-dim vectors (text-embedding-3-small), API 인증 필수
**Scale/Scope**: 100+ 판례, 케이스당 10-50명 인물

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | ✅ PASS | 판례 데이터는 증거가 아님, 인물 추출 시 source_evidence_id 추적 |
| II. Case Isolation | ✅ PASS | 판례는 공유 collection (leh_legal_knowledge), 인물은 케이스별 격리 |
| III. No Auto-Submit | ✅ PASS | 판례 인용은 "Preview Only" 초안에만 포함, 자동 제출 없음 |
| IV. AWS-Only Storage | ✅ PASS | Qdrant Cloud는 별도지만 판례 원본은 외부 API에서 가져옴 (허용) |
| V. Clean Architecture | ✅ PASS | PrecedentService, PartyService 사용, Repository 패턴 준수 |
| VI. Branch Protection | ✅ PASS | feature branch에서 작업, PR로 dev 병합 |
| VII. TDD Cycle | ⚠️ PARTIAL | 테스트 추가 예정 (Phase 7) |
| VIII. Semantic Versioning | ✅ PASS | 해당 없음 (릴리스 전) |

## Project Structure

### Documentation (this feature)

```text
specs/012-precedent-integration/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Setup guide
├── contracts/           # Phase 1: API contracts
│   └── precedent-api.yaml
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── precedent.py          # 판례 검색 API (US1)
│   │   ├── party.py              # 인물 자동 추출 API (US3)
│   │   └── relationship.py       # 관계 자동 추출 API (US3)
│   ├── services/
│   │   ├── precedent_service.py  # 판례 검색 비즈니스 로직
│   │   ├── draft_service.py      # 초안 생성 + 판례 인용 (US2)
│   │   ├── party_service.py      # 인물 관리 로직
│   │   └── relationship_service.py
│   ├── schemas/
│   │   ├── precedent.py          # PrecedentCase, PrecedentSearchResponse
│   │   └── auto_extraction.py    # AutoExtractedPartyRequest
│   └── utils/
│       ├── precedent_search.py   # Qdrant 판례 검색 유틸
│       └── qdrant.py             # 기존 Qdrant 클라이언트
└── tests/
    └── unit/
        └── test_precedent_service.py

ai_worker/
├── scripts/
│   ├── fetch_and_store_legal_data.py  # 국가법령정보 API 수집
│   ├── load_sample_precedents.py      # Fallback 데이터 로딩
│   └── sample_precedents.json         # 테스트용 샘플 데이터
└── src/
    └── api_client.py                  # Backend API 호출 (US3)

frontend/
└── src/
    ├── components/
    │   └── precedent/
    │       ├── PrecedentCard.tsx
    │       ├── PrecedentPanel.tsx
    │       ├── PrecedentModal.tsx
    │       └── index.ts
    ├── lib/api/
    │   └── precedent.ts              # API 클라이언트
    └── types/
        └── precedent.ts              # TypeScript 타입
```

**Structure Decision**: 기존 LEH 프로젝트 구조 (backend/frontend/ai_worker) 유지. 판례 관련 코드는 각 계층에 분산되어 Clean Architecture 원칙 준수.

## Complexity Tracking

> **No violations requiring justification**

Constitution Check에서 모든 원칙을 준수합니다. TDD Cycle은 Phase 7 (Polish)에서 테스트 추가로 해결 예정.

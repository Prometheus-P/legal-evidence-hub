# Implementation Plan: 증거 화자 매핑

**Branch**: `015-evidence-speaker-mapping` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-evidence-speaker-mapping/spec.md`

## Summary

대화형 증거(카카오톡 캡쳐, 문자 등)에서 "나", "상대방" 등으로 표시되는 화자를 인물관계도(PartyNode)의 실제 인물과 선택적으로 매핑하여, 사실관계 생성 시 AI가 정확한 맥락으로 해석할 수 있도록 합니다. 기존 기능에 영향을 주지 않는 선택적(optional) 기능으로 구현합니다.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, React 18, boto3, Tailwind CSS
**Storage**: DynamoDB (leh_evidence 테이블 - 증거 메타데이터), PostgreSQL RDS (cases, users 참조)
**Testing**: pytest (Backend), Jest + React Testing Library (Frontend)
**Target Platform**: AWS CloudFront + Lambda + RDS + DynamoDB
**Project Type**: web (frontend + backend)
**Performance Goals**: 화자 매핑 설정 30초 이내 (2명 기준), API 응답 < 500ms
**Constraints**: 기존 증거 처리 기능에 하위 호환성 유지, 매핑 미설정 시 기존 동작 보장
**Scale/Scope**: 증거당 최대 10명 화자, 케이스당 최대 50개 인물

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | ✅ PASS | 화자 매핑은 메타데이터 수정만, 원본 파일 변경 없음. audit_logs 기록 필요 |
| II. Case Isolation | ✅ PASS | 화자 매핑은 해당 케이스의 Party만 참조 가능 |
| III. No Auto-Submit | ✅ PASS | 매핑은 변호사가 수동 설정, AI 자동 추론 없음 |
| IV. AWS-Only Storage | ✅ PASS | DynamoDB에 매핑 데이터 저장 |
| V. Clean Architecture | ✅ PASS | EvidenceService 확장, Repository 패턴 준수 |
| VI. Branch Protection | ✅ PASS | feat/015-* → dev → main PR 워크플로우 |
| VII. TDD Cycle | ✅ PASS | 테스트 먼저 작성 후 구현 |
| VIII. Semantic Versioning | ✅ PASS | MINOR 버전 증가 (새 기능) |

## Project Structure

### Documentation (this feature)

```text
specs/015-evidence-speaker-mapping/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── evidence.py          # PATCH /evidence/{id}/speaker-mapping 추가
│   ├── schemas/
│   │   └── evidence.py          # SpeakerMapping 스키마 추가
│   ├── services/
│   │   ├── evidence_service.py  # 화자 매핑 CRUD 메서드 추가
│   │   └── fact_summary_service.py  # 프롬프트에 매핑 컨텍스트 주입
│   └── utils/
│       └── dynamo.py            # update_evidence_speaker_mapping 함수 추가
└── tests/
    ├── unit/
    │   ├── test_evidence_service.py      # 화자 매핑 로직 테스트
    │   └── test_fact_summary_service.py  # 매핑 반영 프롬프트 테스트
    └── integration/
        └── test_evidence_api.py          # API 엔드포인트 테스트

frontend/
├── src/
│   ├── components/
│   │   └── evidence/
│   │       ├── SpeakerMappingModal.tsx   # 화자 매핑 설정 모달
│   │       ├── SpeakerMappingBadge.tsx   # 목록 뱃지 컴포넌트
│   │       └── EvidenceDataTable.tsx     # 매핑 상태 컬럼 추가
│   ├── lib/api/
│   │   └── evidence.ts                   # updateSpeakerMapping API 추가
│   ├── types/
│   │   └── evidence.ts                   # SpeakerMapping 타입 추가
│   └── hooks/
│       └── useSpeakerMapping.ts          # 매핑 상태 관리 훅
└── tests/
    └── components/
        └── SpeakerMappingModal.test.tsx
```

**Structure Decision**: 기존 web application 구조 유지. Backend는 evidence.py API 확장, Frontend는 evidence 컴포넌트 폴더에 새 컴포넌트 추가.

## Complexity Tracking

> **No violations - standard feature addition within existing architecture**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |

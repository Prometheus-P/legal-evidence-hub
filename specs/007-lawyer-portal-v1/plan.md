# LEH Lawyer Portal v1 구현 계획

**Feature Branch**: `007-lawyer-portal-v1`
**버전**: v1.0
**작성일**: 2025-12-08

---

## 1. 구현 개요

### 1.1 목표

LEH Lawyer Portal v1의 핵심 기능을 구현하여 변호사가 이혼 사건의 당사자 관계를 시각적으로 파악하고, 재산분할 계산 및 절차 진행 상황을 관리할 수 있도록 한다.

### 1.2 범위

| 기능 | 우선순위 | 구현 범위 |
|------|----------|----------|
| **Party Relationship Graph** | P1 (필수) | 전체 구현 |
| **Financial Asset Sheet** | P2 (optional) | 기본 CRUD + 계산 |
| **Procedure Stage Model** | P2 (optional) | 기본 CRUD + 타임라인 |
| **AI 자동 연결** | P3 (v2) | 제외 |

---

## 2. 기술 스택 확장

### 2.1 Frontend 신규 의존성

```json
{
  "@xyflow/react": "^12.0.0",
  "xlsx": "^0.18.5"
}
```

### 2.2 Backend 변경사항

- SQLAlchemy 모델 추가 (5개 테이블)
- Alembic 마이그레이션 생성
- API 라우터 추가

---

## 3. Phase 1: Party Relationship Graph (2주)

### 3.1 Week 1: Backend + DB

#### Day 1-2: Database Schema

**작업 항목**:
1. Alembic 마이그레이션 파일 생성
   - `party_nodes` 테이블
   - `party_relationships` 테이블
   - `evidence_party_links` 테이블
2. SQLAlchemy 모델 정의
3. Pydantic 스키마 정의

**파일 목록**:
```
backend/
├── alembic/versions/
│   ├── xxx_add_party_nodes.py
│   ├── xxx_add_party_relationships.py
│   └── xxx_add_evidence_party_links.py
├── app/
│   ├── db/models/
│   │   ├── party_node.py
│   │   ├── party_relationship.py
│   │   └── evidence_party_link.py
│   └── schemas/
│       └── party.py
```

**검증**:
```bash
alembic upgrade head
pytest tests/test_db/test_party_models.py
```

#### Day 3-4: API Endpoints

**작업 항목**:
1. Repository 레이어 구현
2. Service 레이어 구현
3. API Router 구현

**API 목록**:
| Method | Endpoint | 기능 |
|--------|----------|------|
| GET | `/cases/{case_id}/parties` | 당사자 목록 조회 |
| POST | `/cases/{case_id}/parties` | 당사자 추가 |
| PATCH | `/cases/{case_id}/parties/{party_id}` | 당사자 수정 |
| DELETE | `/cases/{case_id}/parties/{party_id}` | 당사자 삭제 |
| GET | `/cases/{case_id}/relationships` | 관계 목록 조회 |
| POST | `/cases/{case_id}/relationships` | 관계 추가 |
| PATCH | `/cases/{case_id}/relationships/{rel_id}` | 관계 수정 |
| DELETE | `/cases/{case_id}/relationships/{rel_id}` | 관계 삭제 |

**파일 목록**:
```
backend/app/
├── repositories/
│   └── party_repository.py
├── services/
│   └── party_service.py
└── api/
    └── party.py
```

**검증**:
```bash
pytest tests/test_api/test_party.py
```

#### Day 5: Contract Tests

**작업 항목**:
1. Contract 테스트 스키마 정의
2. Integration 테스트 작성

**파일 목록**:
```
backend/tests/
├── contract/
│   └── test_party_contract.py
└── integration/
    └── test_party_integration.py
```

### 3.2 Week 2: Frontend

#### Day 1-2: React Flow Setup

**작업 항목**:
1. React Flow 패키지 설치 및 설정
2. 커스텀 노드 컴포넌트 구현
3. 커스텀 엣지 컴포넌트 구현

**파일 목록**:
```
frontend/src/
├── components/party/
│   ├── PartyGraph.tsx
│   ├── PartyNode.tsx
│   ├── PartyEdge.tsx
│   ├── nodes/
│   │   ├── PlaintiffNode.tsx
│   │   ├── DefendantNode.tsx
│   │   ├── ThirdPartyNode.tsx
│   │   ├── ChildNode.tsx
│   │   └── FamilyNode.tsx
│   └── edges/
│       ├── MarriageEdge.tsx
│       ├── AffairEdge.tsx
│       └── FamilyEdge.tsx
├── hooks/
│   └── usePartyGraph.ts
└── lib/api/
    └── party.ts
```

**검증**:
```bash
npm run test -- --testPathPattern=party
```

#### Day 3-4: CRUD UI

**작업 항목**:
1. 당사자 추가/편집 모달
2. 관계 추가/편집 모달
3. 드래그&드롭 연결 기능

**파일 목록**:
```
frontend/src/components/party/
├── PartyModal.tsx
├── RelationshipModal.tsx
└── PartyGraphControls.tsx
```

#### Day 5: 페이지 통합

**작업 항목**:
1. 사건 상세 페이지에 "관계도" 탭 추가
2. 증거-당사자 연결 기능

**파일 수정**:
```
frontend/src/app/lawyer/cases/[id]/page.tsx  # 탭 추가
```

---

## 4. Phase 2: Financial Asset Sheet (2주) [v1 optional]

### 4.1 Week 1: Backend

#### Day 1-2: Database Schema

**작업 항목**:
1. `assets` 테이블 마이그레이션
2. SQLAlchemy 모델
3. Pydantic 스키마

**파일 목록**:
```
backend/
├── alembic/versions/
│   └── xxx_add_assets.py
├── app/db/models/
│   └── asset.py
└── app/schemas/
    └── asset.py
```

#### Day 3-4: API Endpoints + 분할 계산

**작업 항목**:
1. 자산 CRUD API
2. 분할 계산 로직 구현
3. Excel 내보내기 API

**API 목록**:
| Method | Endpoint | 기능 |
|--------|----------|------|
| GET | `/cases/{case_id}/assets` | 자산 목록 조회 |
| POST | `/cases/{case_id}/assets` | 자산 추가 |
| PATCH | `/cases/{case_id}/assets/{asset_id}` | 자산 수정 |
| DELETE | `/cases/{case_id}/assets/{asset_id}` | 자산 삭제 |
| POST | `/cases/{case_id}/assets/calculate` | 분할 계산 |
| GET | `/cases/{case_id}/assets/export` | Excel 내보내기 |

**파일 목록**:
```
backend/app/
├── repositories/
│   └── asset_repository.py
├── services/
│   ├── asset_service.py
│   └── division_calculator.py
└── api/
    └── asset.py
```

#### Day 5: 분할 계산 로직 상세

```python
# backend/app/services/division_calculator.py

class DivisionCalculator:
    """한국 이혼 재산분할 계산기"""

    def calculate(self, case_id: str) -> DivisionCalculation:
        assets = self._get_assets(case_id)

        # 1. 공동재산 합계
        joint_assets = [a for a in assets if not a.is_separate_property]
        total_joint = sum(a.current_value for a in joint_assets if a.category != 'debt')

        # 2. 채무 합계
        total_debts = sum(
            a.current_value for a in assets
            if a.category == 'debt' and not a.is_separate_property
        )

        # 3. 특유재산
        total_separate_plaintiff = sum(
            a.current_value for a in assets
            if a.is_separate_property and a.owner == 'plaintiff'
        )
        total_separate_defendant = sum(
            a.current_value for a in assets
            if a.is_separate_property and a.owner == 'defendant'
        )

        # 4. 분할대상 순재산
        net_divisible = total_joint - total_debts

        # 5. 기본 분할비율 (50:50)
        # TODO: 기여도 기반 조정 로직
        division_ratio = {"plaintiff": 50, "defendant": 50}

        # 6. 분할액 계산
        plaintiff_share = int(net_divisible * division_ratio["plaintiff"] / 100)
        defendant_share = int(net_divisible * division_ratio["defendant"] / 100)

        # 7. 정산금 계산
        # 피고 명의 자산에서 원고 몫 빼기
        defendant_owned = sum(
            a.current_value for a in joint_assets
            if a.owner == 'defendant'
        )
        settlement_amount = plaintiff_share - (total_joint - defendant_owned)

        return DivisionCalculation(
            case_id=case_id,
            total_joint_assets=total_joint,
            total_separate_plaintiff=total_separate_plaintiff,
            total_separate_defendant=total_separate_defendant,
            total_debts=total_debts,
            net_divisible=net_divisible,
            division_ratio=division_ratio,
            plaintiff_share=plaintiff_share,
            defendant_share=defendant_share,
            settlement_amount=settlement_amount,
            calculated_at=datetime.utcnow().isoformat()
        )
```

### 4.2 Week 2: Frontend

#### Day 1-2: 스프레드시트 컴포넌트

**작업 항목**:
1. 자산 테이블 컴포넌트
2. 자산 추가/편집 모달

**파일 목록**:
```
frontend/src/components/assets/
├── AssetSheet.tsx
├── AssetRow.tsx
├── AssetModal.tsx
└── CategoryFilter.tsx
```

#### Day 3-4: 분할 계산 UI

**작업 항목**:
1. 분할 결과 표시 컴포넌트
2. Excel 다운로드 버튼

**파일 목록**:
```
frontend/src/components/assets/
├── DivisionSummary.tsx
└── ExportButton.tsx
```

#### Day 5: 페이지 통합

**작업 항목**:
1. 사건 상세 페이지에 "재산분할" 탭 추가

---

## 5. Phase 2: Procedure Stage Model (1주) [v1 optional]

### 5.1 Backend (Day 1-3)

**작업 항목**:
1. `procedure_stages` 테이블 마이그레이션
2. SQLAlchemy 모델 및 API 구현
3. 상태 전이 검증 로직

**API 목록**:
| Method | Endpoint | 기능 |
|--------|----------|------|
| GET | `/cases/{case_id}/procedure` | 절차 단계 조회 |
| POST | `/cases/{case_id}/procedure` | 단계 추가/업데이트 |
| PATCH | `/cases/{case_id}/procedure/{stage_id}` | 단계 상세 수정 |

**상태 전이 규칙**:
```python
VALID_TRANSITIONS = {
    'filed': ['served'],
    'served': ['answered'],
    'answered': ['mediation'],
    'mediation': ['mediation_closed'],
    'mediation_closed': ['trial', 'final'],  # 불성립/성립
    'trial': ['judgment'],
    'judgment': ['appeal', 'final'],
    'appeal': ['final'],
}
```

### 5.2 Frontend (Day 4-5)

**작업 항목**:
1. 절차 타임라인 컴포넌트
2. 단계 상세/편집 모달
3. 사건 상세 페이지에 "절차 진행" 탭 추가

**파일 목록**:
```
frontend/src/components/procedure/
├── ProcedureTimeline.tsx
├── StageCard.tsx
└── StageModal.tsx
```

---

## 6. 테스트 전략

### 6.1 Backend 테스트

| 테스트 유형 | 범위 | 커버리지 목표 |
|------------|------|--------------|
| Unit | Service, Calculator | 90% |
| Contract | API 스키마 | 100% |
| Integration | API E2E | 80% |

**테스트 파일 구조**:
```
backend/tests/
├── unit/
│   ├── test_party_service.py
│   ├── test_asset_service.py
│   └── test_division_calculator.py
├── contract/
│   ├── test_party_contract.py
│   ├── test_asset_contract.py
│   └── test_procedure_contract.py
└── integration/
    ├── test_party_api.py
    ├── test_asset_api.py
    └── test_procedure_api.py
```

### 6.2 Frontend 테스트

| 테스트 유형 | 범위 | 커버리지 목표 |
|------------|------|--------------|
| Unit | Hooks, Utils | 80% |
| Component | React 컴포넌트 | 70% |
| E2E | User Flows | 핵심 시나리오 |

**테스트 파일 구조**:
```
frontend/src/__tests__/
├── hooks/
│   ├── usePartyGraph.test.ts
│   └── useAssets.test.ts
└── components/
    ├── party/
    │   ├── PartyGraph.test.tsx
    │   └── PartyModal.test.tsx
    └── assets/
        ├── AssetSheet.test.tsx
        └── DivisionSummary.test.tsx
```

---

## 7. 마일스톤 및 체크포인트

### 7.1 Phase 1 체크포인트

| 마일스톤 | 완료 기준 | 예상 일자 |
|----------|----------|----------|
| M1.1 | DB 마이그레이션 완료, 테이블 생성 확인 | Day 2 |
| M1.2 | Party API 전체 구현, Contract 테스트 통과 | Day 4 |
| M1.3 | React Flow 기본 렌더링 동작 | Day 7 |
| M1.4 | CRUD UI 완성, 드래그&드롭 연결 | Day 9 |
| M1.5 | 페이지 통합 및 E2E 테스트 통과 | Day 10 |

### 7.2 Phase 2 체크포인트

| 마일스톤 | 완료 기준 | 예상 일자 |
|----------|----------|----------|
| M2.1 | Asset DB 및 API 완료 | Day 14 |
| M2.2 | 분할 계산 로직 완료, Unit 테스트 통과 | Day 15 |
| M2.3 | Asset Frontend 완료 | Day 17 |
| M2.4 | Procedure Backend 완료 | Day 19 |
| M2.5 | Procedure Frontend 완료, 전체 통합 | Day 20 |

---

## 8. 리스크 관리

### 8.1 기술적 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| React Flow 성능 이슈 | 중간 | 높음 | 노드 가상화, 그룹핑 |
| 분할 계산 정확도 | 낮음 | 높음 | 법률 전문가 검토 |
| DynamoDB 확장 호환성 | 낮음 | 중간 | optional 필드 설계 |

### 8.2 완화 조치

1. **React Flow 성능**:
   - 50개 노드 이상 시 그룹핑 적용
   - `useMemo`, `useCallback` 최적화
   - 뷰포트 외 노드 렌더링 지연

2. **분할 계산**:
   - 단위 테스트 충분히 작성
   - Edge case 문서화
   - 결과값 수동 검증 체크리스트

---

## 9. 배포 전략

### 9.1 Feature Flag

```typescript
// frontend/src/config/features.ts
export const FEATURES = {
  PARTY_GRAPH: true,      // Phase 1 완료 후 활성화
  ASSET_SHEET: false,     // Phase 2 완료 후 활성화
  PROCEDURE_STAGE: false, // Phase 2 완료 후 활성화
};
```

### 9.2 DB 마이그레이션 순서

```bash
# 1. 테이블 생성 (backward compatible)
alembic upgrade head

# 2. 코드 배포

# 3. Feature flag 활성화
```

### 9.3 롤백 계획

```bash
# 긴급 롤백 시
alembic downgrade -1

# 또는 Feature flag 비활성화로 기능 숨김
```

---

## 10. 참고 자료

- [React Flow 공식 문서](https://reactflow.dev/)
- [한국 민법 제840조](https://www.law.go.kr/법령/민법/제840조)
- [가사소송법](https://www.law.go.kr/법령/가사소송법)
- LEH SSOT 문서들

---

**END OF PLAN.md**

# Quickstart: Calm-Control Design System

**Feature**: 010-calm-control-design
**Date**: 2025-12-09

## Prerequisites

- Node.js 18+ installed
- Python 3.11+ installed
- LEH repository cloned and dependencies installed

## Quick Validation Steps

### 1. Design Tokens

**Verify tokens.css is loaded:**

```bash
# Check if tokens.css exists
ls frontend/src/styles/tokens.css

# Verify CSS variables are defined
grep -E "^--color-primary" frontend/src/styles/tokens.css
```

**Expected**: 색상, 타이포그래피, 간격 변수가 정의되어 있음

### 2. Dashboard Widgets

**Run component tests:**

```bash
cd frontend
npm test -- --testPathPattern="RiskFlagCard|AIRecommendationCard"
```

**Manual verification:**
1. `npm run dev`로 개발 서버 시작
2. http://localhost:3000/lawyer/dashboard 접속
3. RiskFlagCard와 AIRecommendationCard가 표시되는지 확인

**Expected**:
- RiskFlagCard에 위험 수준, 제목, 설명 표시
- AIRecommendationCard에 추천 제목, 신뢰도, 액션 버튼 표시

### 3. Case Relations Graph

**Run component test:**

```bash
cd frontend
npm test -- --testPathPattern="CaseRelationsGraph"
```

**Manual verification:**
1. http://localhost:3000/lawyer/cases/{caseId} 접속
2. "관계도" 탭 클릭
3. 당사자 노드가 그래프로 표시되는지 확인
4. 노드 드래그가 동작하는지 확인

**Expected**:
- 당사자들이 노드로 표시됨
- 관계가 엣지로 연결됨
- 드래그 시 노드 위치 변경됨

### 4. Asset Division Form

**Run component and API tests:**

```bash
# Frontend tests
cd frontend
npm test -- --testPathPattern="AssetDivisionForm|useAssets"

# Backend tests
cd ../backend
pytest tests/contract/test_assets.py -v
pytest tests/unit/test_division_calculator.py -v
```

**Manual verification:**
1. http://localhost:3000/lawyer/cases/{caseId}/assets 접속
2. "재산 추가" 버튼 클릭 → 폼 표시 확인
3. 재산 등록 후 분할 비율 슬라이더 조정
4. 우측 요약 패널에서 실시간 계산 결과 확인

**Expected**:
- 재산 CRUD가 정상 동작
- 분할 비율 변경 시 즉시(100ms 이내) 요약 업데이트
- 총 재산, 총 부채, 순자산, 예상 정산금 표시

### 5. Animation Constraints

**Manual verification:**
1. 카드 컴포넌트에 마우스 호버
2. 버튼 클릭 시 피드백 확인
3. 페이지 전환 시 애니메이션 없음 확인

**Expected**:
- 호버 시 그림자만 미세하게 변화 (150ms)
- 클릭 시 즉각적인 피드백 (100ms)
- 과도한 애니메이션 없음

---

## Success Criteria Checklist

| ID | Criteria | Verification Method |
|----|----------|---------------------|
| SC-001 | 색상 일관성 100% | CSS 변수 사용 검사 (grep -r "hsl\|rgb\|#[0-9a-f]" --include="*.tsx") |
| SC-002 | 정보 파악 3초 이내 | 사용자 테스트 또는 주관적 확인 |
| SC-003 | 노드 드래그 <50ms | React DevTools Profiler 측정 |
| SC-004 | 계산 업데이트 <100ms | Console.time으로 측정 |
| SC-005 | 일관된 피드백 | 모든 인터랙션 수동 확인 |
| SC-006 | 빈 상태 명확성 | 빈 상태에서 다음 행동 버튼 확인 |

---

## Troubleshooting

### React Flow 노드가 표시되지 않음

```bash
# React Flow 설치 확인
cd frontend
npm list reactflow

# 누락 시 설치
npm install reactflow
```

### 백엔드 API 403 에러

```bash
# 로그인 상태 확인
# JWT 토큰이 유효한지 확인
# case_members 테이블에서 사용자-사건 매핑 확인
```

### CSS 변수가 적용되지 않음

```bash
# layout.tsx에서 tokens.css import 확인
grep "tokens.css" frontend/src/app/layout.tsx

# 누락 시 추가
# import '@/styles/tokens.css';
```

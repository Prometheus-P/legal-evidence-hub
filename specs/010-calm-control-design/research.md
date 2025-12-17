# Research: Calm-Control Design System

**Feature**: 010-calm-control-design
**Date**: 2025-12-09
**Status**: Complete

## Research Tasks

### 1. Color Palette Selection

**Task**: 저채도 색상 팔레트 best practices for legal/professional applications

**Decision**: Teal-based primary with neutral gray secondary
- Primary: Teal 계열 (hsl(174, 42%, 40%) ~ hsl(174, 42%, 90%))
- Neutral: Gray 계열 (hsl(220, 10%, 20%) ~ hsl(220, 10%, 98%))
- Semantic: Success(Green), Warning(Amber), Error(Red) - 저채도 버전

**Rationale**:
- Teal은 신뢰성과 전문성을 나타내는 색상으로 법률/의료 분야에서 선호됨
- 저채도(saturation ~40%)는 장시간 작업 시 눈의 피로를 줄임
- Apple Human Interface Guidelines와 Material Design의 법률 앱 사례 참고

**Alternatives Considered**:
- Navy Blue: 너무 어둡고 우울한 느낌
- Purple: 창의적/예술적 느낌이 강해 법률 분야에 부적합
- Pure Gray: 너무 무미건조하여 브랜드 아이덴티티 부족

---

### 2. React Flow Integration

**Task**: React Flow best practices for relationship graphs

**Decision**: React Flow v11+ with custom node components
- nodeTypes 커스텀으로 당사자 노드 디자인
- dagre 레이아웃 알고리즘으로 자동 배치
- onNodeDrag로 사용자 위치 조정 허용

**Rationale**:
- React Flow는 이미 프로젝트에 설치되어 있음 (package.json 확인)
- dagre 레이아웃은 법적 관계도 같은 hierarchical 구조에 적합
- 학습 곡선이 낮고 TypeScript 지원이 우수함

**Alternatives Considered**:
- D3.js: 저수준 API로 구현 복잡도 높음
- Cytoscape.js: React 통합이 어렵고 번들 크기가 큼
- vis.js: 모던 React 생태계와 호환성 낮음

---

### 3. Asset Division Calculation

**Task**: 재산 분할 계산 로직 best practices

**Decision**: 프론트엔드에서 실시간 미리보기, 백엔드에서 최종 저장
- 프론트엔드: useMemo로 분할 비율 변경 시 즉시 계산
- 백엔드: division_calculator.py 서비스로 저장 전 검증
- 부채는 음수 값으로 처리하여 순자산 계산

**Rationale**:
- 실시간 피드백이 사용자 경험에 중요 (SC-004: 100ms 이내)
- 백엔드 검증으로 데이터 무결성 보장
- 법적 계산 로직은 Out of Scope이므로 단순 비율 계산만 수행

**Alternatives Considered**:
- 서버 전송 후 계산: 네트워크 지연으로 UX 저하
- 복잡한 법적 공식 적용: Out of Scope, 향후 확장 고려

---

### 4. Animation Constraints

**Task**: 최소 애니메이션 가이드라인 연구

**Decision**: duration 150-200ms, ease-out timing, 필수 피드백만
- 호버: box-shadow 변화 (150ms)
- 클릭: scale 0.98 → 1.0 (100ms)
- 페이지 전환: 없음 (즉각적)
- 로딩: 스피너만, pulse 애니메이션 금지

**Rationale**:
- 200ms는 사용자가 "즉각적"으로 느끼는 임계값 (Nielsen Norman Group)
- "변호사가 제어한다"는 느낌을 위해 UI가 예측 가능해야 함
- 과도한 애니메이션은 전문적 이미지를 해침

**Alternatives Considered**:
- 300-500ms 애니메이션: 느리고 "장난감 같은" 느낌
- 애니메이션 완전 제거: 피드백 부족으로 클릭 인지 어려움

---

### 5. Typography System

**Task**: 법률 문서에 적합한 타이포그래피 연구

**Decision**: System font stack (Pretendard, Inter) with 8-point scale
- Heading: 700 weight, 1.2 line-height
- Body: 400 weight, 1.5 line-height
- Scale: 12, 14, 16, 18, 20, 24, 30, 36px

**Rationale**:
- Pretendard는 한글 가독성이 우수하고 법률 문서에 적합
- Inter는 숫자/영문 가독성이 뛰어남
- 시스템 폰트 사용으로 로딩 시간 최소화

**Alternatives Considered**:
- Noto Sans KR: 웹폰트 로딩 시간 증가
- 커스텀 법률 폰트: 라이선스 비용 및 유지보수 부담

---

## Summary

모든 기술적 결정이 완료되었습니다. NEEDS CLARIFICATION 항목이 없으므로 Phase 1으로 진행합니다.

| Item | Decision | Confidence |
|------|----------|------------|
| Color Palette | Teal-based low-saturation | High |
| Graph Library | React Flow v11+ | High (already installed) |
| Calculation | Frontend preview + Backend validation | High |
| Animation | ≤200ms, minimal transitions | High |
| Typography | Pretendard + Inter, 8-point scale | High |

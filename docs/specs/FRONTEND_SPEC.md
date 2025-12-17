
### *변호사용 웹 대시보드 프론트엔드 상세 설계서*

**버전:** v3.0
**작성일:** 2025-12-09
**작성자:** Team P
**관련 문서:**

* `PRD.md`
* `ARCHITECTURE.md`
* `BACKEND_DESIGN.md`
* `AI_PIPELINE_DESIGN.md`
* `LEH_DESIGN_SYSTEM.md` ← **디자인 토큰 및 컴포넌트 가이드**
* `.github` 템플릿

---

# 📌 **0. 문서 목적**

본 문서는 LEH(Legal Evidence Hub)의 **프론트엔드(웹 대시보드)** 전체 구조와 화면 설계를 정의한다.
이 문서는 다음을 목표로 한다:

* 개발자(P/H/L)가 동일한 UI/UX 기준을 이해하도록 한다.
* 화면·컴포넌트·라우팅·상태관리 규칙을 명확히 한다.
* 백엔드/AI와의 데이터 연동 인터페이스를 통일한다.
* 보안·프라이버시 기준을 준수한 운영이 가능하게 한다.

이 문서는 **프론트엔드 구현의 Single Source of Truth**이다.

---

# 🧭 **1. 기술 스택 및 기본 정책**

## 1.1 기술 스택

| 구분          | 기술                                            |
| ----------- | --------------------------------------------- |
| Framework   | **React + Next.js**                           |
| 언어          | **TypeScript**                                |
| 스타일         | **Tailwind CSS**                              |
| 상태 관리       | **React Query(Server State)** + Context/Hooks |
| 라우팅         | Next.js File Routing                          |
| HTTP Client | axios 또는 fetch wrapper                        |
| 빌드·배포       | S3 + CloudFront                               |

---

## 1.2 FE 운영 원칙

1. **Preview-Only**

   * AI가 생성한 초안은 자동 제출 X
   * 변호사가 편집·확정해야 법적 효력
2. **Calm-Control 디자인 원칙** (상세: `LEH_DESIGN_SYSTEM.md`)

   * **Calm**: 저채도 컬러, 안정적 타이포, 불필요한 애니메이션 최소화
   * **Control**: 정보 구조화, 명확한 상호작용, 대시보드 중심 UI
   * 위험 요소는 색상이 아닌 아이콘+배치+subtle border로 강조
3. **브라우저 저장 제한**

   * 증거 전문·요약·민감정보는 LocalStorage/IndexedDB에 저장 금지
4. **반응형 + 접근성 우선**

   * WCAG 2.1 AA 준수 (색상 대비 4.5:1, 터치 타겟 44x44px)
   * 인증·필터·Draft 등은 모바일/노트북 모두 지원
5. **모든 API는 JWT 기반**

   * 인증 없으면 요청 차단, FE에서 글로벌 에러 처리

---

# 🗂 **2. 디렉토리 구조 (통일된 LEH 표준)**

Next.js 14 App Router 기반 구조:

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Landing page
│   │   ├── login/            # 로그인 페이지
│   │   ├── signup/           # 회원가입 페이지
│   │   ├── lawyer/           # 변호사 포털 (역할 기반 라우팅)
│   │   │   ├── layout.tsx    # 사이드바 포함 레이아웃
│   │   │   ├── dashboard/    # 대시보드 (US7 Today View)
│   │   │   ├── cases/        # 케이스 목록 및 상세
│   │   │   │   └── [id]/     # 케이스 상세 (탭: overview, evidence, relations, assets, draft)
│   │   │   ├── calendar/     # 일정 관리
│   │   │   ├── messages/     # 메시징
│   │   │   └── billing/      # 청구 관리
│   │   ├── client/           # 의뢰인 포털
│   │   ├── detective/        # 탐정 포털
│   │   └── staff/            # 스태프 포털
│   ├── components/
│   │   ├── shared/           # 공통 컴포넌트 (LoadingSkeletons, ErrorBoundary)
│   │   ├── lawyer/           # 변호사 전용 (StatsCard, TodayCard, RiskFlagCard, AIRecommendationCard)
│   │   ├── cases/            # CaseList, CaseHeader
│   │   ├── evidence/         # EvidenceTimeline / Card / Upload
│   │   ├── draft/            # DraftPreview / CitationList
│   │   └── ui/               # Primitive UI (shadcn/ui 스타일)
│   ├── hooks/                # Custom React hooks
│   ├── lib/api/              # API 클라이언트
│   ├── types/                # TypeScript 타입 정의
│   ├── contexts/             # React Context (AuthContext, ThemeContext)
│   └── styles/
│       ├── tokens.css        # 디자인 토큰 (CSS 변수)
│       └── globals.css       # 전역 스타일
├── tailwind.config.js        # Tailwind 설정 (토큰 참조)
└── package.json
```

디렉토리 기능은 **백엔드 문서 구조와 동일한 논리 레이어링**을 따른다.

---

# 📑 **3. 주요 페이지 정의**

## 3.1 로그인 페이지 (`/login`)

### 목적

* 변호사/스태프/의뢰인/탐정 인증
* JWT 발급 후 역할에 맞는 대시보드로 이동

### UI 요소

* 이메일 / 비밀번호 입력
* 로그인 버튼
* 오류 메시지: "이메일 또는 비밀번호가 올바르지 않습니다."

### 역할별 리다이렉트

| 역할 | 리다이렉트 경로 |
|------|---------------|
| lawyer | `/lawyer/dashboard` |
| staff | `/staff/dashboard` |
| client | `/client/dashboard` |
| detective | `/detective/dashboard` |

---

## 3.2 변호사 대시보드 (`/lawyer/dashboard`)

### 목적 (Calm-Control)

* 오늘 내가 통제해야 할 사건/증거/드래프트를 한눈에 파악
* 우선순위/위험도 기반 카드 위주 UI (타임라인 아님)

### 화면 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│ Header: 대시보드 제목 / 환영 메시지                       │
├─────────────────────────────────────────────────────────┤
│ Stats Grid (4열)                                        │
│ [전체 케이스] [진행 중] [검토 대기] [이번 달 완료]        │
├─────────────────────────────────────────────────────────┤
│ Priority Section (2열)                                  │
│ ┌─────────────────────┐ ┌─────────────────────────────┐ │
│ │ 위험 플래그 사건     │ │ AI 추천 작업               │ │
│ │ (subtle emphasis)    │ │ (Preview-only)             │ │
│ └─────────────────────┘ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Today View Section (2열)                                │
│ ┌─────────────────────┐ ┌─────────────────────────────┐ │
│ │ 오늘의 긴급 항목     │ │ 이번 주 예정               │ │
│ │ (TodayCard)         │ │ (WeeklyPreview)            │ │
│ └─────────────────────┘ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 최근 케이스 (전체 너비)                                  │
└─────────────────────────────────────────────────────────┘
```

### 위험 플래그 카드 (`RiskFlagCard`)

* 위험 유형: 폭력 위험, 아동 관련, 도피 위험, 증거 훼손 우려, 긴급 기한
* Calm-Control 디자인: **색상 강조 최소화**, 아이콘 + 배치 + subtle border만 사용
* 각 사건 클릭 시 `/lawyer/cases/{id}`로 이동

### AI 추천 작업 카드 (`AIRecommendationCard`)

* 추천 유형: 초안 검토, 증거 태깅, 재산 미입력, 기한 알림, 문서 분석
* **"미리보기 전용" 라벨 필수** - 자동 제출 절대 금지
* "작업 시작" 버튼으로 해당 케이스/증거로 이동

---

## 3.3 사건 리스트 페이지 (`/lawyer/cases`)

### 목적

* 내가 맡은 사건 전체 열람
* 사건 생성/검색/정렬

### 구성

* 상단: 페이지 제목, `+ 사건 생성` 버튼
* 검색바: 사건명 검색
* 필터: 상태(진행/종료)
* 리스트: 사건명 / 담당자 / 상태 / 최근 업데이트

### 동작

* 사건 클릭 → `/lawyer/cases/{id}` 이동
* 생성 버튼 → 사건 생성 모달

---

## 3.4 사건 상세 페이지 (`/lawyer/cases/{id}`)

LEH의 핵심 UX. 탭 기반 네비게이션.

### 탭 구조

| 탭 | 경로 | 내용 |
|----|------|------|
| 개요 | `/lawyer/cases/{id}` | 사건 요약, 당사자 정보, 진행 상태 |
| 증거 | `/lawyer/cases/{id}/evidence` | 증거 타임라인 |
| 관계도 | `/lawyer/cases/{id}/relations` | React Flow 기반 당사자 관계 그래프 |
| 재산 | `/lawyer/cases/{id}/assets` | 재산 분할 폼 |
| 초안 | `/lawyer/cases/{id}/draft` | AI Draft Preview |

### 화면 레이아웃 (증거 탭)

```
┌───────────────────────────────────────────────┐
│ CaseHeader: 사건 제목 / 상태 / 멤버 / 버튼들 │
├───────────────────────────────────────────────┤
│ Tab Navigation                                │
│ [개요] [증거] [관계도] [재산] [초안]           │
├───────────────────────────────────────────────┤
│ 좌측: EvidenceFilterBar                       │
│                                               │
│ 우측: EvidenceTimeline (카드 리스트)          │
├───────────────────────────────────────────────┤
│ DraftPreview (하단 고정 혹은 패널)            │
└───────────────────────────────────────────────┘
```

### CaseHeader 기능

* 사건명
* 사건 상태(active/closed)
* 멤버 배지
* 버튼:

  * 증거 업로드
  * 사건 종료
  * RAG 검색 열기

---

# 🧩 **4. 컴포넌트 상세 정의**

## 4.1 Dashboard 컴포넌트

### StatsCard

**기능**
* 통계 수치 표시 (아이콘, 라벨, 값, 변화율)
* 상승/하락 트렌드 표시

### RiskFlagCard (Calm-Control)

**기능**
* 위험 플래그가 설정된 사건 목록 표시
* 위험 유형별 아이콘: 폭력(Shield), 아동(Users), 도피(Plane), 증거훼손(FileX2), 기한(Clock)

**디자인 원칙**
* **색상 강조 최소화**: 빨간색으로 소리치지 않음
* 왼쪽 4px error border + 아이콘으로 식별
* 호버 시 `shadow-md`로 미세한 부상 효과

### AIRecommendationCard (Preview-Only)

**기능**
* AI가 추천하는 작업 목록 표시
* 추천 유형: draft_review, evidence_tagging, asset_incomplete, deadline_reminder, document_analysis

**법적 준수**
* **"미리보기 전용" 라벨 필수 표시**
* 자동 제출/실행 기능 절대 금지
* "작업 시작" 버튼은 해당 페이지로 이동만

### TodayCard

**기능**
* 오늘 마감되는 긴급 항목 표시
* 모든 항목 완료 시 "모든 작업 완료" 메시지

### WeeklyPreview

**기능**
* 이번 주 예정된 항목 미리보기
* 날짜별 그룹핑

---

## 4.2 EvidenceUpload

**기능**

* 파일 Drag & Drop
* Presigned URL 요청 후 S3 업로드
* 업로드 상태: 대기/진행중/분석중/완료 표시
* 오류 발생 시 재시도 버튼

---

## 4.3 EvidenceTimeline

**입력 데이터**
DynamoDB Evidence JSON 리스트

**표시 요소**

* 시간순 정렬
* EvidenceCard 반복 렌더
* 카드 클릭 → EvidenceDetailModal 표시
* 필터(유형/라벨/날짜)에 따라 실시간 갱신

---

## 4.4 EvidenceCard

**요소**

* 유형 아이콘(text/image/audio/pdf)
* 요약
* timestamp
* speaker
* labels(유책사유 Tag)
* 클릭 → 상세 모달

---

## 4.5 EvidenceDetailModal

**표시**

* 원본 (이미지/텍스트/오디오/문서)
* AI 요약
* 라벨(유책사유, 감정)
* 핵심 문장 하이라이트
* 이 증거가 타임라인에서 어느 위치인지 표시

---

## 4.6 DraftPreview

**역할**

* “소장 초안 제안” 패널
* `draft_text` + `citations` 렌더
* Draft 재생성 버튼
* docx 파일 다운로드 버튼

**주의사항 (법적 준수)**

* 자동 제출 금지
* 자동 입력 금지
* FE는 "읽기 + 다운로드"만 제공

---

## 4.7 CaseRelationsGraph (React Flow)

**역할**

* 당사자 간 관계를 시각적 그래프로 표시
* `/lawyer/cases/{id}/relations` 탭에서 사용

**기술 스택**

* React Flow (https://reactflow.dev)
* Custom Node: PartyNode (원고/피고/자녀/제3자)
* Custom Edge: RelationEdge (혼인/친자/불륜/친족 등)

**노드 유형**

| 유형 | 색상 | 아이콘 |
|------|------|--------|
| plaintiff | primary-light | User |
| defendant | secondary-light | User |
| child | success-light | Users |
| third_party | warning-light | User |

**엣지 유형**

| 관계 | 스타일 | 라벨 |
|------|--------|------|
| marriage | solid, primary | 혼인 |
| parent_child | solid, neutral | 친자 |
| affair | dashed, error | 불륜 |
| relative | dotted, neutral | 친족 |

**인터랙션**

* 노드 드래그로 위치 조정
* 노드 클릭 시 상세 팝오버 (증거 연결 목록)
* 엣지 클릭 시 관계 증거 표시

---

## 4.8 AssetDivisionForm

**역할**

* 이혼 사건의 재산 분할 데이터 입력/조회
* `/lawyer/cases/{id}/assets` 탭에서 사용

**재산 유형**

| 유형 | 라벨 | 아이콘 |
|------|------|--------|
| real_estate | 부동산 | Building |
| vehicle | 차량 | Car |
| financial | 금융자산 | Wallet |
| business | 사업자산 | Briefcase |
| personal | 개인자산 | Package |
| debt | 부채 | CreditCard |

**소유 구분**

* plaintiff: 원고 단독
* defendant: 피고 단독
* joint: 공동 소유

**폼 필드**

```
┌─────────────────────────────────────────────────────┐
│ 재산 유형 [Dropdown]                                │
│ 재산명 [Text Input]                                 │
│ 취득일 [Date Picker]                                │
│ 현재 가치 (원) [Number Input]                        │
│ 소유 구분 [Radio: 원고/피고/공동]                    │
│ 분할 비율 [Slider: 0-100%]                          │
│ 비고 [Textarea]                                     │
│ 관련 증거 연결 [Multi-select]                       │
└─────────────────────────────────────────────────────┘
```

**분할 결과 Preview**

* 원고 취득 예정: ₩xxx,xxx,xxx
* 피고 취득 예정: ₩xxx,xxx,xxx
* 차액 정산 필요: ₩xxx,xxx,xxx

---

# 🔌 **5. API 연동 사양 (Front ↔ Back)**

## 5.1 인증

| 동작      | API                | 비고     |
| ------- | ------------------ | ------ |
| 로그인     | `POST /auth/login` | JWT 발급 |
| 토큰 만료 시 | `/auth/refresh`    | 옵션     |

---

## 5.2 대시보드 (신규)

| 목적 | API | 비고 |
|------|-----|------|
| 대시보드 통계 | `GET /dashboard/stats` | 전체/진행중/대기/완료 카운트 |
| 위험 플래그 사건 | `GET /dashboard/risk-flags` | Calm-Control 위험 표시 |
| AI 추천 작업 | `GET /dashboard/ai-recommendations` | Preview-only |
| 오늘 긴급 항목 | `GET /dashboard/today` | Today View (US7) |
| 이번 주 예정 | `GET /dashboard/this-week` | Weekly Preview |

---

## 5.3 사건 관리

| 목적 | API |
|------|-----|
| 사건 리스트 조회 | `GET /cases` |
| 사건 상세 조회 | `GET /cases/{id}` |
| 사건 생성 | `POST /cases` |
| 사건 종료 | `DELETE /cases/{id}` |

---

## 5.4 증거 관리

### Presigned URL

GET /evidence/presigned-url?case_id=xxx&filename=xxx

### 증거 리스트

GET /cases/{id}/evidence

---

## 5.5 당사자 관계 (Relations Graph)

| 목적 | API | 비고 |
|------|-----|------|
| 당사자 목록 조회 | `GET /cases/{id}/parties` | 노드 데이터 |
| 당사자 추가 | `POST /cases/{id}/parties` | |
| 당사자 수정 | `PUT /cases/{id}/parties/{party_id}` | |
| 관계 목록 조회 | `GET /cases/{id}/relations` | 엣지 데이터 |
| 관계 추가 | `POST /cases/{id}/relations` | |
| 관계 수정 | `PUT /cases/{id}/relations/{relation_id}` | |

---

## 5.6 재산 분할 (Assets)

| 목적 | API | 비고 |
|------|-----|------|
| 재산 목록 조회 | `GET /cases/{id}/assets` | |
| 재산 추가 | `POST /cases/{id}/assets` | |
| 재산 수정 | `PUT /cases/{id}/assets/{asset_id}` | |
| 재산 삭제 | `DELETE /cases/{id}/assets/{asset_id}` | |
| 분할 시뮬레이션 | `POST /cases/{id}/assets/simulate-division` | 분할 비율 계산 |

---

## 5.7 Draft 생성

POST /cases/{id}/draft-preview

응답:

```json
{
  "draft_text": "...",
  "citations": [
    { "evidence_id": "ev_123", "quote": "..." }
  ]
}
```

---

# 🔄 **6. FE 내부 데이터 흐름**

## 6.1 증거 업로드 흐름

[1] 사용자가 파일 선택
[2] FE → BE: Presigned URL 요청
[3] FE → S3: 직접 업로드
[4] S3 Event → AI Worker 자동 실행
[5] Worker → DynamoDB 반영
[6] FE → BE: /cases/{id}/evidence 재조회
[7] 타임라인 실시간 갱신

---

## 6.2 Draft 생성 흐름

[1] FE: DraftPreview에서 “Draft 생성”
[2] FE → BE: draft-preview 요청
[3] BE: 사건 증거 → RAG → GPT-4o → 초안 생성
[4] BE → FE: draft_text + citations 반환
[5] FE: Preview 표시

---

# 🔒 **7. 보안 · 프라이버시 정책 (FE)**

1. **민감 정보 브라우저 저장 금지**

   * LocalStorage에는 JWT/token만 저장
   * 증거 전문/요약/라벨 등은 저장 금지

2. **HTTPS 강제**

3. **오류 로그에는 개인정보 제거**

   * Sentry/Logging에 “증거 내용” 포함되면 안 됨

4. **세션 종료 정책**

   * 장시간 미사용 시 자동 로그아웃(UI 안내 필요)

5. **권한 검사**

   * 사건 접근 권한 없으면 `/cases`로 리다이렉트

---

# 🧪 **8. 테스트 전략**

## 8.1 Unit Test

* 컴포넌트 렌더링 (EvidenceCard, DraftPreview 등)
* 필터 로직
* API hook (useEvidence/useCase)

## 8.2 Integration Test

* Presigned URL 발급 → S3 업로드 → EvidenceTimeline 반영 (Mock)

## 8.3 E2E

* Playwright/Cypress

  * 로그인 → 사건 선택 → 증거 업로드 → Draft 생성

---

# 📦 **9. 개발 체크리스트**

* [ ] JWT 로그인/로그아웃 구현
* [ ] 사건 리스트 / 상세 / 상태관리 구현
* [ ] Presigned URL 기반 증거 업로드
* [ ] EvidenceTimeline + 필터 조합
* [ ] EvidenceDetailModal
* [ ] DraftPreview (생성/갱신/다운로드)
* [ ] 글로벌 에러/로딩/권한 처리
* [ ] 민감 데이터 FE 저장 금지 준수

---

# 🔚 END OF FRONTEND_SPEC.md

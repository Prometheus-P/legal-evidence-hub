# Quickstart: Production Login Bug Fix Verification

**Feature**: 011-production-bug-fixes
**Date**: 2025-12-11

## Prerequisites

- Production URL 접근 가능: `https://dpbf86zqulqfy.cloudfront.net`
- API URL: `https://api.legalevidence.hub` (또는 설정된 backend URL)
- 테스트 계정 (각 역할별 1개):
  - Lawyer: `lawyer@test.com`
  - Client: `client@test.com`
  - Detective: `detective@test.com`

## Verification Steps

### Step 1: Cookie Configuration Check (Backend)

브라우저 DevTools에서 Network 탭 열고 로그인 시도:

```bash
# 또는 curl로 확인
curl -X POST "https://api.legalevidence.hub/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"lawyer@test.com","password":"password123"}' \
  -i
```

**Expected Response Headers**:
```
Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=None; Path=/
Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=None; Path=/auth
```

**Failure Signs**:
- `SameSite=Lax` 또는 누락 → Cross-origin 쿠키 전달 실패
- `Secure` 누락 → HTTPS에서 쿠키 설정 실패
- 쿠키 헤더 자체가 없음 → 백엔드 설정 오류

### Step 2: Login Flow Test

1. Production URL로 이동: `https://dpbf86zqulqfy.cloudfront.net/login`
2. 테스트 계정으로 로그인
3. DevTools Application 탭에서 쿠키 확인:
   - `access_token` (HttpOnly) - 값 보이지 않음이 정상
   - `user_data` - JSON 값 확인 가능

**Success Criteria**:
- [ ] SC-001: 로그인 후 `/lawyer/dashboard`로 이동
- [ ] SC-002: 새로고침 후 로그인 상태 유지
- [ ] SC-003: 3초 이내 대시보드 도달
- [ ] SC-004: 로그인 루프 없음

### Step 3: Back Button Test

1. 로그인 성공 후 대시보드에서
2. 브라우저 뒤로가기 버튼 클릭
3. `/login` 페이지가 아닌 대시보드로 다시 리다이렉트되어야 함

**Expected Behavior**: FR-006 충족 - 인증된 사용자는 /login 접근 시 대시보드로 리다이렉트

### Step 4: Multi-Tab Test

1. 탭 A: 로그인 상태 유지
2. 탭 B: 새 탭에서 같은 URL 열기
3. 탭 B에서 로그아웃
4. 탭 A에서 API 호출하는 액션 수행

**Expected Behavior**: 탭 A도 로그인 페이지로 리다이렉트

### Step 5: Role-based Redirect Test

각 역할별로 로그인 후 올바른 대시보드로 이동하는지 확인:

| Role | Expected Dashboard |
|------|-------------------|
| lawyer | `/lawyer/dashboard` |
| client | `/client/dashboard` |
| detective | `/detective/dashboard` |

## Debugging Commands

### Check Backend Cookie Settings

```bash
# backend/app/core/config.py 확인
grep -r "COOKIE_" backend/app/

# 환경 변수 확인
cat .env | grep -E "(COOKIE_|CORS_)"
```

### Check Frontend Auth State

브라우저 콘솔에서:

```javascript
// localStorage 확인
console.log(localStorage.getItem('leh_user_cache'));

// sessionStorage 확인
console.log(sessionStorage.getItem('leh_just_logged_in'));

// 쿠키 확인 (public cookies만)
console.log(document.cookie);
```

### Test API Authentication

```bash
# 로그인 후 받은 쿠키로 /auth/me 호출
curl "https://api.legalevidence.hub/auth/me" \
  -H "Cookie: access_token=<token>" \
  -i
```

## Troubleshooting

### Problem: 쿠키가 설정되지 않음

**Cause**: SameSite/Secure 설정 문제
**Fix**:
```python
# backend/app/api/auth.py
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,        # 반드시 True
    samesite="none",    # 반드시 "none" (cross-origin)
    ...
)
```

### Problem: 로그인 성공 후 바로 로그아웃됨

**Cause**: Race condition - checkAuth()가 캐시보다 먼저 실행
**Fix**: AuthContext의 JUST_LOGGED_IN_KEY 로직 확인

### Problem: 새로고침 시 로그아웃됨

**Cause**: HTTP-only 쿠키가 API 요청에 포함되지 않음
**Fix**:
1. `credentials: 'include'` 설정 확인
2. CORS 설정에 프론트엔드 origin 포함 확인

### Problem: 뒤로가기 시 로그인 페이지 표시

**Cause**: Middleware가 인증 상태를 인식하지 못함
**Fix**: user_data 쿠키 동기화 로직 확인

## Test Commands

```bash
# Backend 테스트
cd backend && pytest tests/contract/test_auth.py -v

# Frontend 테스트
cd frontend && npm test -- --testPathPattern=auth

# E2E 테스트 (로컬)
PLAYWRIGHT_BASE_URL="http://localhost:3000" npx playwright test auth.spec.ts

# E2E 테스트 (Production)
PLAYWRIGHT_BASE_URL="https://dpbf86zqulqfy.cloudfront.net" npx playwright test auth.spec.ts
```

## Success Checklist (US1 - Login Bug)

- [ ] 로그인 API가 올바른 Set-Cookie 헤더 반환
- [ ] 쿠키가 브라우저에 저장됨 (Application 탭)
- [ ] 대시보드 페이지로 리다이렉트됨
- [ ] 새로고침 후 로그인 상태 유지
- [ ] 뒤로가기 시 대시보드로 리다이렉트
- [ ] 로그아웃 후 모든 쿠키/스토리지 정리됨
- [ ] 모든 역할에서 정상 작동

---

# Quickstart: Lawyer Portal Features (US2)

**Date**: 2025-12-12

## Prerequisites

- US1 로그인 버그 수정 완료
- Lawyer 역할 계정으로 로그인 가능
- Backend API 서버 실행 중

## Verification Steps

### Step 6: 알림 드롭다운 (FR-007)

1. Lawyer 계정으로 로그인
2. 상단 네비게이션에서 알림 버튼 (aria-label="알림") 클릭
3. 드롭다운 메뉴 표시 확인

**Success Criteria**:
- [ ] SC-005: 알림 버튼 클릭 시 드롭다운 표시
- [ ] 알림 목록 로드됨 (빈 목록이어도 OK)
- [ ] 알림 클릭 시 읽음 처리

**API Test**:
```bash
curl "https://api.legalevidence.hub/notifications?limit=10" \
  -H "Cookie: access_token=<token>" \
  -i
```

### Step 7: 메시지 기능 (FR-008)

1. 좌측 네비게이션에서 "메시지" 메뉴 클릭
2. 메시지 페이지로 이동 확인
3. 메시지 작성, 전송, 읽기, 삭제 테스트

**Success Criteria**:
- [ ] SC-006: 메시지 목록 조회 정상
- [ ] 메시지 작성 폼 표시
- [ ] 메시지 전송 성공
- [ ] 메시지 상세 조회 정상
- [ ] 메시지 삭제 성공

**API Tests**:
```bash
# 받은 메시지 목록
curl "https://api.legalevidence.hub/messages?folder=inbox" \
  -H "Cookie: access_token=<token>"

# 메시지 전송
curl -X POST "https://api.legalevidence.hub/messages" \
  -H "Cookie: access_token=<token>" \
  -H "Content-Type: application/json" \
  -d '{"recipient_id":"<user_id>","subject":"테스트","content":"테스트 메시지"}'
```

### Step 8: 의뢰인 관리 (FR-009~010, FR-015)

1. 좌측 네비게이션에서 "의뢰인" 메뉴 클릭
2. 의뢰인 목록 페이지 표시 확인
3. "의뢰인 추가" 버튼 클릭
4. 폼에 기본 정보 입력 (이름, 연락처)
5. 저장 후 목록에 표시 확인

**Success Criteria**:
- [ ] SC-007: 의뢰인 추가 폼 표시
- [ ] 의뢰인 목록 조회 정상
- [ ] 의뢰인 추가 성공
- [ ] 의뢰인 수정 성공
- [ ] 의뢰인 삭제 성공

**API Tests**:
```bash
# 의뢰인 목록
curl "https://api.legalevidence.hub/clients" \
  -H "Cookie: access_token=<token>"

# 의뢰인 추가
curl -X POST "https://api.legalevidence.hub/clients" \
  -H "Cookie: access_token=<token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","phone":"010-1234-5678"}'
```

### Step 9: 탐정 관리 (FR-011~012, FR-016)

1. 좌측 네비게이션에서 "탐정" 메뉴 클릭
2. 탐정 목록 페이지 표시 확인
3. "탐정 추가" 버튼 클릭
4. 폼에 기본 정보 입력 (이름, 연락처, 전문분야)
5. 저장 후 목록에 표시 확인

**Success Criteria**:
- [ ] SC-007: 탐정 추가 폼 표시
- [ ] 탐정 목록 조회 정상
- [ ] 탐정 추가 성공
- [ ] 탐정 수정 성공
- [ ] 탐정 삭제 성공

**API Tests**:
```bash
# 탐정 목록
curl "https://api.legalevidence.hub/detectives" \
  -H "Cookie: access_token=<token>"

# 탐정 추가
curl -X POST "https://api.legalevidence.hub/detectives" \
  -H "Cookie: access_token=<token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"김탐정","phone":"010-9876-5432","specialty":"불륜 조사"}'
```

### Step 10: Dashboard 접근권한 (FR-013)

1. Lawyer 계정으로 로그인
2. `/lawyer/dashboard` 직접 URL 접근
3. 페이지 정상 렌더링 확인

**Success Criteria**:
- [ ] SC-008: /lawyer/dashboard 정상 렌더링
- [ ] 권한 오류 없음
- [ ] 페이지 컴포넌트 정상 표시

## Test Commands (US2)

```bash
# Backend Contract Tests
cd backend && pytest tests/contract/test_notifications.py -v
cd backend && pytest tests/contract/test_messages.py -v
cd backend && pytest tests/contract/test_clients.py -v
cd backend && pytest tests/contract/test_detectives.py -v

# Frontend Component Tests
cd frontend && npm test -- --testPathPattern=NotificationDropdown
cd frontend && npm test -- --testPathPattern=ClientForm
cd frontend && npm test -- --testPathPattern=DetectiveForm

# E2E Tests
PLAYWRIGHT_BASE_URL="https://dpbf86zqulqfy.cloudfront.net" \
  npx playwright test lawyer-portal.spec.ts
```

## Success Checklist (US2 - Lawyer Portal)

- [ ] 알림 드롭다운 표시
- [ ] 알림 읽음 처리 동작
- [ ] 메시지 페이지 접근 가능
- [ ] 메시지 CRUD 모두 동작
- [ ] 의뢰인 추가 버튼 동작
- [ ] 의뢰인 CRUD 모두 동작
- [ ] 탐정 추가 버튼 동작
- [ ] 탐정 CRUD 모두 동작
- [ ] /lawyer/dashboard 정상 렌더링

## Troubleshooting (US2)

### Problem: 알림 드롭다운이 표시되지 않음

**Cause**: NotificationDropdown 컴포넌트 미구현 또는 이벤트 핸들러 누락
**Fix**: NotificationBell 컴포넌트에서 드롭다운 상태 토글 확인

### Problem: 의뢰인/탐정 추가 폼이 표시되지 않음

**Cause**: 모달/폼 컴포넌트 미구현
**Fix**: ClientForm, DetectiveForm 컴포넌트 구현 확인

### Problem: API 403 오류

**Cause**: Lawyer 역할 확인 실패
**Fix**: 로그인한 사용자의 role이 "lawyer"인지 확인

### Problem: CRUD 작업 실패

**Cause**: Backend API 미구현 또는 라우터 미등록
**Fix**: `backend/app/main.py`에 라우터 등록 확인

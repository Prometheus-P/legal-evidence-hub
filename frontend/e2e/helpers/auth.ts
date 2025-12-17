/**
 * E2E Test Authentication Helpers
 *
 * Playwright 테스트에서 사용하는 인증 헬퍼 함수들
 */

import { Page, expect } from '@playwright/test';

// 테스트 사용자 정보 (seed 데이터와 일치)
const TEST_USERS = {
  lawyer: {
    email: 'kim.lawyer@leh.dev',
    password: 'test1234',
    role: 'lawyer'
  },
  client: {
    email: 'client@test.com',
    password: 'Test1234!',
    role: 'client'
  },
  detective: {
    email: 'detective@test.com',
    password: 'Test1234!',
    role: 'detective'
  }
} as const;

type UserRole = keyof typeof TEST_USERS;

/**
 * 기본 테스트 사용자로 로그인
 * @param page Playwright Page 객체
 */
export async function loginAsTestUser(page: Page): Promise<void> {
  await loginAs(page, TEST_USERS.lawyer.email, TEST_USERS.lawyer.password);
}

/**
 * 변호사 역할로 로그인
 * @param page Playwright Page 객체
 */
export async function loginAsLawyer(page: Page): Promise<void> {
  await loginAs(page, TEST_USERS.lawyer.email, TEST_USERS.lawyer.password);
}

/**
 * 의뢰인 역할로 로그인
 * @param page Playwright Page 객체
 */
export async function loginAsClient(page: Page): Promise<void> {
  await loginAs(page, TEST_USERS.client.email, TEST_USERS.client.password);
}

/**
 * 탐정 역할로 로그인
 * @param page Playwright Page 객체
 */
export async function loginAsDetective(page: Page): Promise<void> {
  await loginAs(page, TEST_USERS.detective.email, TEST_USERS.detective.password);
}

/**
 * 특정 이메일/비밀번호로 로그인 (실제 UI 사용)
 * @param page Playwright Page 객체
 * @param email 이메일
 * @param password 비밀번호
 */
export async function loginAs(page: Page, email: string, password: string): Promise<void> {
  // 로그인 페이지로 이동
  await page.goto('/login');
  await page.waitForLoadState('domcontentloaded');

  // 로딩 상태가 끝날 때까지 대기 (Next.js hydration)
  await page.waitForTimeout(2000);

  // 로그인 폼 대기 - getByLabel 사용 (더 안정적)
  const emailInput = page.getByLabel(/이메일|email/i);
  const passwordInput = page.getByLabel(/비밀번호|password/i);

  await expect(emailInput).toBeVisible({ timeout: 15000 });
  await expect(passwordInput).toBeVisible({ timeout: 15000 });

  // 로그인 정보 입력
  await emailInput.fill(email);
  await passwordInput.fill(password);

  // 로그인 버튼 클릭
  const submitButton = page.getByRole('button', { name: /로그인|login|sign in/i });
  await submitButton.click();

  // 로그인 완료 대기 - URL이 /login에서 벗어나거나 에러 메시지 표시
  await page.waitForTimeout(3000);

  // 로그인 성공 시 대시보드로 리다이렉트 대기
  try {
    await page.waitForURL(/\/lawyer\/|\/client\/|\/staff\/|\/detective\//, { timeout: 5000 });
  } catch {
    // URL 변경 없으면 계속 진행
  }

  // 로그인 성공 확인 (리다이렉트 또는 에러 메시지)
  const url = page.url();
  const isLoginPage = url.includes('/login');

  if (isLoginPage) {
    // 에러 메시지 확인
    const hasError = await page.locator('text=/오류|실패|잘못된/i').count() > 0;
    if (hasError) {
      console.log('Login failed - trying to create test user');
      // 회원가입 시도
      await signupTestUser(page, email, password);
    }
  }
}

/**
 * 테스트 사용자 회원가입
 */
async function signupTestUser(page: Page, email: string, password: string): Promise<void> {
  await page.goto('/signup');
  await page.waitForLoadState('domcontentloaded');

  // 회원가입 폼 작성
  const nameInput = page.locator('input[name="name"]');
  const emailInput = page.locator('input[type="email"]');
  const passwordInput = page.locator('input[type="password"]');

  if (await nameInput.isVisible()) {
    await nameInput.fill('테스트사용자');
  }

  await emailInput.first().fill(email);
  await passwordInput.first().fill(password);

  // 약관 동의 체크박스 (여러 개일 수 있음)
  const checkboxes = page.locator('input[type="checkbox"]');
  const checkboxCount = await checkboxes.count();
  for (let i = 0; i < checkboxCount; i++) {
    const cb = checkboxes.nth(i);
    if (await cb.isVisible()) {
      await cb.check();
    }
  }

  // 회원가입 버튼 클릭
  const signupButton = page.getByRole('button', { name: /가입|회원가입|무료 체험|signup/i });
  if (await signupButton.isVisible()) {
    await signupButton.click();
    await page.waitForTimeout(3000);
  }
}

/**
 * 로그아웃
 * @param page Playwright Page 객체
 */
export async function logout(page: Page): Promise<void> {
  // 로그아웃 버튼 또는 메뉴 찾기
  const logoutButton = page.getByRole('button', { name: /로그아웃|logout|sign out/i });

  if (await logoutButton.isVisible()) {
    await logoutButton.click();
  } else {
    // 프로필 메뉴를 통한 로그아웃
    const profileMenu = page.locator('[data-testid="profile-menu"]').or(
      page.getByRole('button', { name: /프로필|profile/i })
    );

    if (await profileMenu.isVisible()) {
      await profileMenu.click();
      await page.getByRole('menuitem', { name: /로그아웃|logout/i }).click();
    }
  }

  // 랜딩 페이지 또는 로그인 페이지로 리다이렉트 대기
  await page.waitForURL(/^\/$|\/login/, { timeout: 10000 });
}

/**
 * 인증 상태 확인
 * @param page Playwright Page 객체
 * @returns 인증 여부
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  // 쿠키 확인
  const cookies = await page.context().cookies();
  const hasAuthToken = cookies.some(
    cookie => cookie.name === 'access_token' || cookie.name === 'authToken'
  );

  return hasAuthToken;
}

/**
 * 인증 쿠키 설정 (Mock)
 * @param page Playwright Page 객체
 * @param role 사용자 역할
 */
export async function setAuthCookie(page: Page, role: UserRole = 'lawyer'): Promise<void> {
  const user = TEST_USERS[role];

  // localStorage에 토큰 설정 (일부 앱에서 사용)
  await page.evaluate((userData) => {
    localStorage.setItem('authToken', 'test-jwt-token');
    localStorage.setItem('user', JSON.stringify({
      email: userData.email,
      role: userData.role
    }));
  }, user);
}

/**
 * 인증 상태 초기화
 * @param page Playwright Page 객체
 */
export async function clearAuth(page: Page): Promise<void> {
  // localStorage 초기화
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  // 쿠키 삭제
  await page.context().clearCookies();
}

/**
 * 특정 케이스 페이지로 이동 (인증 필요)
 * Uses path-based route format for S3 static hosting compatibility
 * @param page Playwright Page 객체
 * @param caseId 케이스 ID
 */
export async function navigateToCaseDetail(page: Page, caseId: string): Promise<void> {
  await page.goto(`/lawyer/cases/${caseId}/`);
  await page.waitForLoadState('domcontentloaded');
}

/**
 * 관계도 페이지로 이동 (인증 필요)
 * Uses path-based route format for S3 static hosting compatibility
 * @param page Playwright Page 객체
 * @param caseId 케이스 ID
 */
export async function navigateToRelationshipPage(page: Page, caseId: string): Promise<void> {
  await page.goto(`/lawyer/cases/${caseId}/relationship/`);
  await page.waitForLoadState('domcontentloaded');
}

export { TEST_USERS };

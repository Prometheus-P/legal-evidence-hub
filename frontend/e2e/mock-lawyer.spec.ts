import { test, expect } from '@playwright/test';
import { MOCK_USERS, MOCK_AUTH_RESPONSE, MOCK_CASES, MOCK_CASE_DETAIL } from './fixtures/mocks';

test.describe('Lawyer Flow (Mocked)', () => {
  test.beforeEach(async ({ page }) => {
    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
    // 1. Intercept Auth/Me (Session Checks)
    await page.route('**/api/auth/me', async (route) => {
      // Initially 401 (not logged in), then user after login usually
      // For simplicity in this test, we can Mock it based on state or always return user if we assume "remember me"
      // But for login flow, let's start with 401 if cookie is missing? 
      // Playwright route handler is stateless unless we manage it.
      // Let's mock successful "me" call *after* we simulate login, 
      // OR mostly just rely on the login response setting app state.
      // However, usually apps call /me on mount.
      
      // Let's assume we start unauthenticated
      // If the app calls /me on load, we'll return 401 first.
      await route.fulfill({ status: 401 });
    });

    await page.route('**/api/auth/login', async (route) => {
      const json = MOCK_AUTH_RESPONSE('lawyer');
      // Simulated Set-Cookie for user_data
      const userData = encodeURIComponent(JSON.stringify({ ...MOCK_USERS.lawyer }));
      
      await page.unroute('**/api/auth/me'); 
      await page.route('**/api/auth/me', async (r) => r.fulfill({ 
        json: MOCK_USERS.lawyer,
        headers: {
          'Access-Control-Allow-Origin': 'http://localhost:3000',
          'Access-Control-Allow-Credentials': 'true',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        }
      }));
      
      await route.fulfill({ 
        json,
        headers: {
          'Set-Cookie': `user_data=${userData}; Path=/;`,
          'Access-Control-Allow-Origin': 'http://localhost:3000',
          'Access-Control-Allow-Credentials': 'true',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        }
      });
    });

    // 3. Intercept Cases
    await page.route('**/api/cases', async (route) => {
      await route.fulfill({ 
        json: { data: MOCK_CASES, total: 2, page: 1, size: 10 },
        headers: {
          'Access-Control-Allow-Origin': 'http://localhost:3000',
          'Access-Control-Allow-Credentials': 'true',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        }
      });
    });

    // 4. Intercept Case Detail
    await page.route('**/api/cases/case_001', async (route) => {
      await route.fulfill({ 
        json: MOCK_CASE_DETAIL,
        headers: {
          'Access-Control-Allow-Origin': 'http://localhost:3000',
          'Access-Control-Allow-Credentials': 'true',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        }
      });
    });

    // Clear storage
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should login as lawyer and see dashboard', async ({ page }) => {
    await page.goto('/login');
    
    // Fill credentials
    await page.locator('input[type="email"]').fill('lawyer@leh.dev');
    await page.locator('input[type="password"]').fill('password');
    
    // Click Login
    await page.getByRole('button', { name: '로그인' }).click();

    // Verification: URL should change to /cases (Lawyer Dashboard)
    await expect(page).toHaveURL(/\/lawyer\/dashboard/);
    
    // Check for welcome message or user name
    // Adjust selector based on actual UI
    await expect(page.locator('body')).toContainText('김변호사');
    await expect(page.locator('body')).toContainText('케이스 관리');
  });

  test('should view case list and navigate to detail', async ({ page, context }) => {
    // Setup: Already logged in
    // 1. Set Cookie
    const userData = encodeURIComponent(JSON.stringify({ ...MOCK_USERS.lawyer }));
    await context.addCookies([{
      name: 'user_data',
      value: userData,
      path: '/'
    }]);

    // 2. Mock /me
    await page.unroute('**/api/auth/me');
    await page.route('**/api/auth/me', async (r) => r.fulfill({ 
      json: MOCK_USERS.lawyer,
      headers: {
        'Access-Control-Allow-Origin': 'http://localhost:3000',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      }
    }));
    
    await page.goto('/cases');
    
    // Check Case List
    await expect(page.getByText('2025가합1234')).toBeVisible();
    await expect(page.getByText('서울중앙지방법원 민사소송')).toBeVisible();

    // Click Case
    await page.getByText('서울중앙지방법원 민사소송').click();

    // Verify Navigation to Detail
    await expect(page).toHaveURL(/\/cases\/case_001/);
    await expect(page.getByText('부당해고 구제신청 사건')).toBeVisible();
  });
});

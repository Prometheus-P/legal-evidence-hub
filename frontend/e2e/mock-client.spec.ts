import { test, expect } from '@playwright/test';
import { MOCK_USERS, MOCK_AUTH_RESPONSE, MOCK_CASES } from './fixtures/mocks';

test.describe('Client Flow (Mocked)', () => {
  test.beforeEach(async ({ page }) => {
    // Intercept Login
    await page.route('**/api/auth/login', async (route) => {
      const json = MOCK_AUTH_RESPONSE('client');
      await page.unroute('**/api/auth/me'); 
      await page.route('**/api/auth/me', async (r) => r.fulfill({ json: MOCK_USERS.client }));
      await route.fulfill({ json });
    });

    await page.route('**/api/auth/me', async (route) => {
      await route.fulfill({ status: 401 });
    });

    // Client Portal Data
    await page.route('**/api/client/cases*', async (route) => {
      await route.fulfill({ json: { data: MOCK_CASES } });
    });
    // Fallback for shared endpoints
    await page.route('**/api/cases*', async (route) => {
      await route.fulfill({ json: { data: MOCK_CASES } });
    });

    await page.goto('/login');
  });

  test('should login as client and see client portal', async ({ page }) => {
    await page.locator('input[type="email"]').fill('client@leh.dev');
    await page.locator('input[type="password"]').fill('password');
    await page.getByRole('button', { name: '로그인' }).click();

    // Client portal usually at /client or /cases
    await page.waitForURL(/client|cases/);
    
    await expect(page.locator('body')).toContainText('홍길동');
    
    // Check for "M"y Cases" or similar client specific text if known
    // Assuming generic success for now
    await expect(page.locator('body')).toBeVisible();
  });
});

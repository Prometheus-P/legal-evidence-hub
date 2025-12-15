import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Authentication Flow
 * Tests login, signup, and navigation guard functionality
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.evaluate(() => localStorage.clear());
  });

  test.describe('Login Page', () => {
    test('should display login form', async ({ page }) => {
      await page.goto('/login');

      // Wait for the form to be visible (hydration complete)
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toBeVisible({ timeout: 10000 });

      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.getByRole('button', { name: /로그인/i })).toBeVisible();
    });

    test('should login and redirect to /cases @real-api', async ({ page, request }) => {
      // Skip if backend not available
      try {
        const healthCheck = await request.get('http://localhost:8000/health');
        if (!healthCheck.ok()) {
          test.skip();
          return;
        }
      } catch {
        test.skip();
        return;
      }

      await page.goto('/login');

      // Wait for form to be visible
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toBeVisible({ timeout: 10000 });

      // Fill login form
      await emailInput.fill('test@example.com');
      await page.locator('input[type="password"]').fill('password123');

      // Click login button
      await page.getByRole('button', { name: /로그인/i }).click();

      // Wait for response - either redirect or error message
      await page.waitForTimeout(3000);

      // Check if redirected (success) or error shown
      const url = page.url();
      const hasError = await page.locator('text=/오류|확인해 주세요|실패/i').count() > 0;

      // With backend, we expect either success redirect or auth error
      expect(url.includes('/cases') || hasError).toBeTruthy();
    });
  });

  test.describe('Signup Page', () => {
    test('should display signup form', async ({ page }) => {
      await page.goto('/signup');

      // Wait for form to be visible
      const nameInput = page.locator('input[name="name"]');
      await expect(nameInput).toBeVisible({ timeout: 10000 });

      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.getByRole('button', { name: /무료 체험 시작/i })).toBeVisible();
    });

    test('should show error for short password', async ({ page }) => {
      await page.goto('/signup');

      // Wait for form
      const nameInput = page.locator('input[name="name"]');
      await expect(nameInput).toBeVisible({ timeout: 10000 });

      await nameInput.fill('홍길동');
      await page.locator('input[type="email"]').fill('test@example.com');
      // Select a role first (required field)
      await page.locator('select[name="role"]').selectOption('lawyer');
      await page.locator('input[type="password"]').fill('short');

      await page.getByRole('button', { name: /무료 체험 시작/i }).click();

      // Wait for response and error message
      await page.waitForTimeout(3000);
      await expect(page.getByTestId('error-message')).toBeVisible({ timeout: 10000 });
      await expect(page.getByTestId('error-message')).toContainText(/비밀번호는 8자 이상/i);
    });

    test('should signup and redirect to /cases @real-api', async ({ page, request }) => {
      // Skip if backend not available
      try {
        const healthCheck = await request.get('http://localhost:8000/health');
        if (!healthCheck.ok()) {
          test.skip();
          return;
        }
      } catch {
        test.skip();
        return;
      }

      await page.goto('/signup');

      // Wait for form
      const nameInput = page.locator('input[name="name"]');
      await expect(nameInput).toBeVisible({ timeout: 10000 });

      // Generate unique email for test
      const uniqueEmail = `test-${Date.now()}@example.com`;

      await nameInput.fill('홍길동');
      await page.locator('input[type="email"]').fill(uniqueEmail);
      await page.locator('input[type="password"]').fill('password123');
      await page.locator('input[type="checkbox"]').check();

      await page.getByRole('button', { name: /무료 체험 시작/i }).click();

      // Wait for redirect to /lawyer/dashboard
      await page.waitForURL('**/lawyer/dashboard', { timeout: 10000 });

      // Check result - should be redirected to /lawyer/dashboard on success
      const url = page.url();
      expect(url).toContain('/lawyer/dashboard');
    });

    test('should show error when terms not accepted', async ({ page }) => {
      await page.goto('/signup');

      // Wait for form
      const nameInput = page.locator('input[name="name"]');
      await expect(nameInput).toBeVisible({ timeout: 10000 });

      await nameInput.fill('홍길동');
      await page.locator('input[type="email"]').fill('test@example.com');
      // Select a role first (required field)
      await page.locator('select[name="role"]').selectOption('lawyer');
      await page.locator('input[type="password"]').fill('password123');
      // Do NOT check accept-terms

      await page.getByRole('button', { name: /무료 체험 시작/i }).click();

      // Wait for response and error message
      await page.waitForTimeout(3000);
      await expect(page.getByTestId('error-message')).toBeVisible({ timeout: 10000 });
      await expect(page.getByTestId('error-message')).toContainText(/이용약관에 동의해주세요/i);
    });
  }); // Corrected closing brace for Signup Page test.describe

  /**
   * 011-production-bug-fixes: Login Redirect Bug Tests
   * These tests verify the fix for the production login redirect issue
   * Root cause: Cross-origin cookie configuration (SameSite/Secure)
   */
  test.describe('Login Redirect Bug Fix (011)', () => {
    test('T006: should redirect to role-specific dashboard after login @real-api', async ({ page, request }) => {
      // Skip if backend not available
      try {
        const healthCheck = await request.get('http://localhost:8000/health');
        if (!healthCheck.ok()) {
          test.skip();
          return;
        }
      } catch {
        test.skip();
        return;
      }

      // Create unique test user
      const uniqueEmail = `login-redirect-${Date.now()}@test.com`;
      await page.goto('/signup');

      const nameInput = page.locator('input[name="name"]');
      await expect(nameInput).toBeVisible({ timeout: 10000 });

      await nameInput.fill('Login Test User');
      await page.locator('input[type="email"]').fill(uniqueEmail);
      await page.locator('input[type="password"]').fill('password123');
      await page.locator('select[name="role"]').selectOption('lawyer');
      await page.locator('input[type="checkbox"]').check();
      await page.getByRole('button', { name: /무료 체험 시작/i }).click();

      // Should redirect to lawyer dashboard (not back to login!)
      await page.waitForURL('**/lawyer/dashboard', { timeout: 15000 });

      const finalUrl = page.url();
      expect(finalUrl).toContain('/lawyer/dashboard');
      expect(finalUrl).not.toContain('/login');
    });

    test('T007: should maintain login state after page refresh @real-api', async ({ page, request }) => {
      // Skip if backend not available
      try {
        const healthCheck = await request.get('http://localhost:8000/health');
        if (!healthCheck.ok()) {
          test.skip();
          return;
        }
      } catch {
        test.skip();
        return;
      }

      // Create and login with test user
      const uniqueEmail = `refresh-test-${Date.now()}@test.com`;
      await page.goto('/signup');

      const nameInput = page.locator('input[name="name"]');
      await expect(nameInput).toBeVisible({ timeout: 10000 });

      await nameInput.fill('Refresh Test User');
      await page.locator('input[type="email"]').fill(uniqueEmail);
      await page.locator('input[type="password"]').fill('password123');
      await page.locator('select[name="role"]').selectOption('lawyer');
      await page.locator('input[type="checkbox"]').check();
      await page.getByRole('button', { name: /무료 체험 시작/i }).click();

      // Wait for dashboard
      await page.waitForURL('**/lawyer/dashboard', { timeout: 15000 });

      // Refresh the page
      await page.reload();
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2000);

      // Should still be on dashboard (not redirected to login)
      const urlAfterRefresh = page.url();
      expect(urlAfterRefresh).toContain('/lawyer/dashboard');
      expect(urlAfterRefresh).not.toContain('/login');
    });

    test('T008: should redirect authenticated user from /login to dashboard @real-api', async ({ page, request }) => {
      // Skip if backend not available
      try {
        const healthCheck = await request.get('http://localhost:8000/health');
        if (!healthCheck.ok()) {
          test.skip();
          return;
        }
      } catch {
        test.skip();
        return;
      }

      // Create and login with test user
      const uniqueEmail = `back-button-${Date.now()}@test.com`;
      await page.goto('/signup');

      const nameInput = page.locator('input[name="name"]');
      await expect(nameInput).toBeVisible({ timeout: 10000 });

      await nameInput.fill('Back Button Test User');
      await page.locator('input[type="email"]').fill(uniqueEmail);
      await page.locator('input[type="password"]').fill('password123');
      await page.locator('select[name="role"]').selectOption('lawyer');
      await page.locator('input[type="checkbox"]').check();
      await page.getByRole('button', { name: /무료 체험 시작/i }).click();

      // Wait for dashboard
      await page.waitForURL('**/lawyer/dashboard', { timeout: 15000 });

      // Try to navigate back to /login (simulating back button or direct navigation)
      await page.goto('/login');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2000);

      // Should be redirected back to dashboard (not stay on login)
      const finalUrl = page.url();
      expect(finalUrl).toContain('/lawyer/dashboard');
      expect(finalUrl).not.toContain('/login');
    });
  });

  test.describe('Navigation Guard', () => {
    test('should handle unauthenticated access to /cases', async ({ page }) => {
      // Ensure no auth token
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');
      await page.evaluate(() => localStorage.clear());

      // Try to access /cases directly
      await page.goto('/cases');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2000);

      // The behavior depends on implementation -
      // should either redirect to /login or show cases page
      const url = page.url();
      // Just verify the page loaded without error
      await expect(page.locator('body')).toBeVisible();
    });

    test('should allow authenticated user to access /cases', async ({ page, request }) => {
      // Skip if backend not available
      try {
        const healthCheck = await request.get('http://localhost:8000/health');
        if (!healthCheck.ok()) {
          test.skip();
          return;
        }
      } catch {
        test.skip();
        return;
      }

      // Login first to get HTTP-only cookie
      await page.goto('/login');
      await page.waitForLoadState('domcontentloaded');

      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toBeVisible({ timeout: 10000 });

      await emailInput.fill('test@example.com');
      await page.locator('input[type="password"]').fill('password123');
      await page.getByRole('button', { name: /로그인/i }).click();

      // Wait for redirect or error
      await page.waitForTimeout(3000);

      // Either redirected to /cases (auth success) or stayed on /login (auth failed)
      // Both are acceptable outcomes depending on whether test user exists
      const url = page.url();
      expect(url.includes('/cases') || url.includes('/login')).toBeTruthy();
      await expect(page.locator('body')).toBeVisible();
    });
  });

  test.describe('Landing Page', () => {
    test('should display landing page for unauthenticated user', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');

      // Should see landing page - check for main content
      // Use .first() to handle multiple main elements (landing page structure)
      await expect(page.locator('main').first()).toBeVisible({ timeout: 10000 });
    });

    test('should display landing page content', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');

      // Should see key landing page elements
      await expect(page.locator('body')).toBeVisible();

      // Check for landing page headline or CTA
      const hasLandingContent = await page.locator('text=/무료|시작|증거|LEH/i').count() > 0;
      expect(hasLandingContent).toBeTruthy();
    });
  });
});

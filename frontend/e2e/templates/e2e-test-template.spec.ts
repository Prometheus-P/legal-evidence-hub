/**
 * E2E Test Template
 * ==================
 *
 * Template for writing E2E tests using Page Object Model.
 * Copy and customize for your specific test scenarios.
 *
 * QA Framework v4.0 - Playwright E2E Testing
 *
 * Best Practices:
 * - Use Page Objects for all page interactions
 * - Use explicit waits (never page.waitForTimeout)
 * - Generate unique data per test to prevent conflicts
 * - Clean up test data in afterEach when possible
 *
 * Usage:
 *   1. Copy this file to e2e/specs/your-feature.spec.ts
 *   2. Import relevant Page Objects
 *   3. Implement test cases
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';

// ============================================================================
// Test Data - Generate unique data per test run
// ============================================================================

/**
 * Generate unique email to prevent test conflicts.
 */
function generateUniqueEmail(): string {
  return `test-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`;
}

/**
 * Generate unique title with timestamp.
 */
function generateUniqueTitle(prefix: string): string {
  return `${prefix}-${Date.now()}`;
}

// ============================================================================
// Test Configuration
// ============================================================================

test.describe('Feature Name - E2E Tests', () => {
  // Page Objects
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  // Setup before each test
  test.beforeEach(async ({ page, context }) => {
    // Clear cookies and localStorage to ensure clean state
    await context.clearCookies();
    await page.evaluate(() => localStorage.clear());

    // Initialize Page Objects
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  // Cleanup after each test (optional)
  test.afterEach(async ({ page }) => {
    // Take screenshot on failure (configured in playwright.config.ts)
    // Additional cleanup if needed
  });

  // ============================================================================
  // Happy Path Tests
  // ============================================================================

  test.describe('Happy Path', () => {
    test('should complete main user flow successfully', async ({ page }) => {
      // Arrange
      await loginPage.goto();

      // Act
      await loginPage.login('test@example.com', 'TestPass123!');

      // Assert
      await loginPage.verifyLoginSuccess();
      await dashboardPage.verifyDashboardLoaded();
    });

    test('should navigate between pages correctly', async ({ page }) => {
      // Arrange - Login first
      await loginPage.goto();
      await loginPage.login('test@example.com', 'TestPass123!');
      await loginPage.verifyLoginSuccess();

      // Act - Navigate to cases
      await dashboardPage.goToCases();

      // Assert - Verify navigation
      await expect(page).toHaveURL(/\/cases/);
    });
  });

  // ============================================================================
  // Error Handling Tests
  // ============================================================================

  test.describe('Error Handling', () => {
    test('should display error message on invalid input', async ({ page }) => {
      // Arrange
      await loginPage.goto();

      // Act
      await loginPage.login('invalid-email', 'short');

      // Assert
      await loginPage.verifyLoginFailed(/이메일|email|password|비밀번호/i);
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // Arrange - Mock network failure
      await page.route('**/api/**', (route) => {
        route.abort('failed');
      });

      await loginPage.goto();

      // Act
      await loginPage.login('test@example.com', 'TestPass123!');

      // Assert - Should show error, not crash
      const toast = await loginPage.getToastMessage();
      // Network errors should be handled gracefully
    });

    test('should handle timeout scenarios', async ({ page }) => {
      // Arrange - Mock slow response
      await page.route('**/api/auth/login', async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 5000));
        await route.fulfill({ status: 200, body: '{}' });
      });

      await loginPage.goto();

      // Act & Assert - Should not hang indefinitely
      await loginPage.login('test@example.com', 'TestPass123!');
      // Test will timeout if not handled properly
    });
  });

  // ============================================================================
  // Edge Cases
  // ============================================================================

  test.describe('Edge Cases', () => {
    test('should handle empty input gracefully', async ({ page }) => {
      // Arrange
      await loginPage.goto();

      // Act - Submit with empty fields
      await loginPage.login('', '');

      // Assert - Should show validation errors
      const hasEmailError = await loginPage.hasEmailError();
      const hasPasswordError = await loginPage.hasPasswordError();
      expect(hasEmailError || hasPasswordError).toBe(true);
    });

    test('should handle special characters in input', async ({ page }) => {
      // Arrange
      await loginPage.goto();
      const specialCharsEmail = 'test+special@example.com';

      // Act
      await loginPage.login(specialCharsEmail, 'Password123!@#');

      // Assert - Should not cause errors (may fail login, but gracefully)
      // Either succeeds or shows proper error
    });

    test('should handle rapid repeated actions', async ({ page }) => {
      // Arrange
      await loginPage.goto();

      // Act - Rapid clicks
      const submitButton = page.getByRole('button', { name: /로그인|login/i });
      await loginPage.safeFill(loginPage.emailInput, 'test@example.com');
      await loginPage.safeFill(loginPage.passwordInput, 'TestPass123!');

      // Click multiple times rapidly
      await Promise.all([
        submitButton.click(),
        submitButton.click(),
        submitButton.click(),
      ]);

      // Assert - Should not cause duplicate submissions or errors
      // Wait for any response
      await page.waitForLoadState('networkidle');
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================

  test.describe('Accessibility', () => {
    test('should have no accessibility violations on page load', async ({
      page,
    }) => {
      // This requires @axe-core/playwright
      // Import: import AxeBuilder from '@axe-core/playwright';

      await loginPage.goto();

      // Uncomment when axe-core is set up:
      // const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
      // expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('should be keyboard navigable', async ({ page }) => {
      await loginPage.goto();

      // Tab through form elements
      await page.keyboard.press('Tab');
      await expect(loginPage.emailInput).toBeFocused();

      await page.keyboard.press('Tab');
      await expect(loginPage.passwordInput).toBeFocused();

      await page.keyboard.press('Tab');
      await expect(loginPage.submitButton).toBeFocused();
    });
  });
});

// ============================================================================
// Multi-browser compatibility (runs across all configured browsers)
// ============================================================================

test.describe('Cross-browser Tests', () => {
  test('should render correctly in all browsers', async ({ page, browserName }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // Basic rendering check
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.submitButton).toBeVisible();

    console.log(`Tested successfully in ${browserName}`);
  });
});

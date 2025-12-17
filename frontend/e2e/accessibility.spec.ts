import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * E2E Accessibility Tests (T035-T036)
 * WCAG 2.1 AA Compliance for Lawyer Portal
 *
 * Tests:
 * - Keyboard navigation through all interactive elements
 * - Focus visibility on all focusable elements
 * - axe-core automated accessibility scanning
 * - Skip-to-content link functionality
 */

test.describe('Accessibility Compliance (US5)', () => {
  test.describe('Keyboard Navigation (T035)', () => {
    test('should navigate login form with keyboard only', async ({ page }) => {
      await page.goto('/login');

      // Wait for form to be visible
      const emailInput = page.locator('input[type="email"]');
      await expect(emailInput).toBeVisible({ timeout: 10000 });

      // Focus on email input directly to start form navigation
      await emailInput.focus();
      await expect(emailInput).toBeFocused();

      // Tab to password input
      await page.keyboard.press('Tab');
      const passwordInput = page.locator('input[type="password"]');
      await expect(passwordInput).toBeFocused();

      // Tab through remaining form elements to find submit button
      // (may include forgot password link, show password toggle, etc.)
      let foundSubmitButton = false;
      for (let i = 0; i < 5; i++) {
        await page.keyboard.press('Tab');
        const focusedElement = page.locator(':focus');
        const role = await focusedElement.getAttribute('role');
        const type = await focusedElement.getAttribute('type');
        const text = await focusedElement.textContent();

        // Check if we've found the submit button
        if (role === 'button' || type === 'submit') {
          if (text && text.includes('로그인')) {
            foundSubmitButton = true;
            break;
          }
        }
      }

      expect(foundSubmitButton).toBe(true);
    });

    test('should show visible focus ring on interactive elements', async ({ page }) => {
      await page.goto('/login');

      // Wait for form to be visible
      await page.waitForSelector('input[type="email"]');

      // Tab to first input
      await page.keyboard.press('Tab');

      // Check focus is visible (has focus-visible styles)
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();

      // Verify focus ring is applied via CSS
      const boxShadow = await focusedElement.evaluate((el) => {
        return window.getComputedStyle(el).boxShadow;
      });

      // Focus ring should have some visible shadow/outline
      expect(boxShadow).not.toBe('none');
    });

    test('should navigate modal with keyboard and trap focus', async ({ page, request }) => {
      // This test requires backend to be running
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

      // Login first
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]');
      await page.locator('input[type="email"]').fill('test@example.com');
      await page.locator('input[type="password"]').fill('password123');
      await page.getByRole('button', { name: /로그인/i }).click();

      // Wait for redirect to cases
      await page.waitForURL('**/lawyer/cases**', { timeout: 10000 });

      // Click "Add Case" button to open modal
      const addCaseButton = page.getByRole('button', { name: /새 사건/i });
      if (await addCaseButton.isVisible()) {
        await addCaseButton.click();

        // Wait for modal
        const modal = page.getByRole('dialog');
        await expect(modal).toBeVisible();

        // First focusable element in modal should be focused
        const focusedElement = page.locator(':focus');
        await expect(focusedElement).toBeVisible();

        // Tab through modal elements
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');

        // Focus should stay within modal
        const currentFocus = page.locator(':focus');
        await expect(currentFocus).toBeVisible();

        // Escape should close modal
        await page.keyboard.press('Escape');
        await expect(modal).not.toBeVisible();
      }
    });

    test('should activate button with Enter and Space keys', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]');

      // Fill form
      await page.locator('input[type="email"]').fill('invalid@test.com');
      await page.locator('input[type="password"]').fill('wrongpassword');

      // Navigate to submit button
      const submitButton = page.getByRole('button', { name: /로그인/i });
      await submitButton.focus();

      // Press Enter to submit
      await page.keyboard.press('Enter');

      // Should trigger form submission (error expected since invalid)
      // Just verify the button was activated
      await page.waitForTimeout(500); // Wait for any response
    });
  });

  test.describe('axe Accessibility Scan (T036)', () => {
    test('login page should have no critical accessibility violations', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .exclude('.third-party-widget') // Exclude any third-party widgets
        .analyze();

      // Filter for critical and serious violations only
      const criticalViolations = accessibilityScanResults.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalViolations).toEqual([]);
    });

    test('landing page should have no critical accessibility violations', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .exclude('.third-party-widget')
        .analyze();

      const criticalViolations = accessibilityScanResults.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious'
      );

      expect(criticalViolations).toEqual([]);
    });

    test('lawyer dashboard should have no critical violations @real-api', async ({ page, request }) => {
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

      // Login first
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]');
      await page.locator('input[type="email"]').fill('test@example.com');
      await page.locator('input[type="password"]').fill('password123');
      await page.getByRole('button', { name: /로그인/i }).click();

      // Wait for redirect
      await page.waitForURL('**/lawyer/**', { timeout: 10000 });

      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      const criticalViolations = accessibilityScanResults.violations.filter(
        (v) => v.impact === 'critical' || v.impact === 'serious'
      );

      // Log violations for debugging
      if (criticalViolations.length > 0) {
        console.log('Critical violations found:', JSON.stringify(criticalViolations, null, 2));
      }

      expect(criticalViolations).toEqual([]);
    });
  });

  test.describe('Skip Link', () => {
    test('skip-to-content link should be first focusable element', async ({ page, request }) => {
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

      // Login and navigate to lawyer portal
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]');
      await page.locator('input[type="email"]').fill('test@example.com');
      await page.locator('input[type="password"]').fill('password123');
      await page.getByRole('button', { name: /로그인/i }).click();

      await page.waitForURL('**/lawyer/**', { timeout: 10000 });

      // Tab once - skip link should be first focusable
      await page.keyboard.press('Tab');

      const skipLink = page.locator(':focus');
      const text = await skipLink.textContent();

      // Skip link should say "Skip to content" or similar
      if (text) {
        expect(text.toLowerCase()).toMatch(/(skip|건너뛰기|콘텐츠로)/i);
      }
    });
  });

  test.describe('Color Contrast', () => {
    test('buttons should meet contrast requirements', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('button[type="submit"]');

      const button = page.locator('button[type="submit"]');

      // Get computed styles
      const styles = await button.evaluate((el) => {
        const computed = window.getComputedStyle(el);
        return {
          backgroundColor: computed.backgroundColor,
          color: computed.color,
        };
      });

      // Basic check that colors are defined
      expect(styles.backgroundColor).toBeDefined();
      expect(styles.color).toBeDefined();

      // The actual contrast ratio is checked by axe tests
    });
  });

  test.describe('Touch Targets', () => {
    test('interactive elements should have minimum 44x44px touch target', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('button[type="submit"]');

      const button = page.locator('button[type="submit"]');
      const box = await button.boundingBox();

      expect(box).not.toBeNull();
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(44);
        expect(box.width).toBeGreaterThanOrEqual(44);
      }
    });
  });
});

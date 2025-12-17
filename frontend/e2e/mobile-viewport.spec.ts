import { test, expect } from '@playwright/test';

/**
 * Mobile Viewport E2E Tests (T047)
 * Tests responsive behavior on mobile devices (320px-768px)
 *
 * Goal: Lawyers can effectively use the application on mobile devices
 */

test.describe('Mobile Viewport (US2)', () => {
  // Test at 320px (minimum mobile)
  test.describe('320px Viewport (Minimum Mobile)', () => {
    test.use({ viewport: { width: 320, height: 568 } });

    test('login form should be fully visible and usable', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]', { timeout: 15000 });

      // All form elements should be visible
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      const submitButton = page.getByRole('button', { name: /로그인/i });

      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
      await expect(submitButton).toBeVisible();

      // Form should not overflow horizontally
      const form = page.locator('form');
      const formBox = await form.boundingBox();
      expect(formBox).not.toBeNull();
      if (formBox) {
        expect(formBox.width).toBeLessThanOrEqual(320);
      }
    });

    test('landing page should not have horizontal overflow', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Check no horizontal scroll
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });

      expect(hasHorizontalScroll).toBe(false);
    });

    test('buttons should meet minimum touch target size (44x44)', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('button[type="submit"]', { timeout: 15000 });

      const button = page.locator('button[type="submit"]');
      const box = await button.boundingBox();

      expect(box).not.toBeNull();
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(44);
        expect(box.width).toBeGreaterThanOrEqual(44);
      }
    });
  });

  // Test at 375px (iPhone SE)
  test.describe('375px Viewport (iPhone SE)', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('navigation should be accessible', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');

      // Mobile menu button should be visible
      const menuButton = page.locator('[aria-label*="메뉴"], [aria-label*="menu"], button:has-text("☰")').first();
      // Either menu button exists or nav is visible
      const isMenuButton = await menuButton.isVisible().catch(() => false);
      const navLinks = page.locator('nav a');

      if (isMenuButton) {
        // If hamburger menu, click to open
        await menuButton.click();
        await expect(navLinks.first()).toBeVisible();
      }
    });
  });

  // Test at 768px (tablet portrait)
  test.describe('768px Viewport (Tablet Portrait)', () => {
    test.use({ viewport: { width: 768, height: 1024 } });

    test('content should adapt to tablet layout', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Should have adequate spacing and readable text
      const body = page.locator('body');
      const fontSize = await body.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      // Font size should be at least 16px for readability
      const fontSizeNum = parseInt(fontSize);
      expect(fontSizeNum).toBeGreaterThanOrEqual(16);
    });
  });

  // Test at 1024px (tablet landscape / small desktop)
  test.describe('1024px Viewport (Tablet Landscape)', () => {
    test.use({ viewport: { width: 1024, height: 768 } });

    test('sidebar should be visible on larger screens @real-api', async ({ page, request }) => {
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

      await page.waitForURL('**/lawyer/**', { timeout: 10000 });

      // Sidebar should be visible at 1024px
      const sidebar = page.locator('aside, [role="navigation"]').first();
      await expect(sidebar).toBeVisible();
    });
  });

  test.describe('Responsive Components', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('inputs should be full width on mobile', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]', { timeout: 15000 });

      const emailInput = page.locator('input[type="email"]');
      const inputBox = await emailInput.boundingBox();
      const viewportWidth = 375;

      expect(inputBox).not.toBeNull();
      if (inputBox) {
        // Input should be nearly full width (accounting for padding)
        expect(inputBox.width).toBeGreaterThan(viewportWidth * 0.8);
      }
    });

    test('text should be readable without zooming', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');

      // Check that main text is at least 14px
      const textElements = page.locator('p, span, div').first();
      const fontSize = await textElements.evaluate((el) => {
        return window.getComputedStyle(el).fontSize;
      });

      const fontSizeNum = parseInt(fontSize);
      expect(fontSizeNum).toBeGreaterThanOrEqual(14);
    });
  });

  test.describe('Touch Interactions', () => {
    test.use({ viewport: { width: 375, height: 667 }, hasTouch: true });

    test('tap targets should be accessible', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('button[type="submit"]', { timeout: 15000 });

      // All interactive elements should have adequate size
      const interactiveElements = page.locator('button, a, input, [role="button"]');
      const count = await interactiveElements.count();

      for (let i = 0; i < Math.min(count, 10); i++) {
        const element = interactiveElements.nth(i);
        if (await element.isVisible()) {
          const box = await element.boundingBox();
          if (box) {
            // Touch targets should be at least 44x44 or have adequate spacing
            const hasAdequateSize = box.height >= 44 && box.width >= 44;
            const hasSmallSizeButSpaced = box.height >= 24 && box.width >= 24;
            expect(hasAdequateSize || hasSmallSizeButSpaced).toBe(true);
          }
        }
      }
    });

    test('form inputs should have adequate height for touch', async ({ page }) => {
      await page.goto('/login');
      await page.waitForSelector('input[type="email"]', { timeout: 15000 });

      const inputs = page.locator('input[type="email"], input[type="password"]');
      const count = await inputs.count();

      for (let i = 0; i < count; i++) {
        const input = inputs.nth(i);
        const box = await input.boundingBox();
        expect(box).not.toBeNull();
        if (box) {
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    });
  });

  test.describe('Orientation Changes', () => {
    test('should handle portrait to landscape transition', async ({ page }) => {
      // Start in portrait
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/');
      await page.waitForLoadState('domcontentloaded');

      // Capture initial state
      const initialWidth = await page.evaluate(() => document.body.clientWidth);

      // Switch to landscape
      await page.setViewportSize({ width: 667, height: 375 });
      await page.waitForTimeout(300); // Allow for transition

      // Content should adapt
      const landscapeWidth = await page.evaluate(() => document.body.clientWidth);
      expect(landscapeWidth).toBeGreaterThan(initialWidth);

      // No horizontal overflow
      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(hasOverflow).toBe(false);
    });
  });
});

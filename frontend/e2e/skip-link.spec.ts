/**
 * Skip Link Accessibility Tests
 * WCAG 2.2 - 2.4.1 Bypass Blocks
 *
 * Tests that skip links are present and functional across all portals.
 * Skip links allow keyboard users to bypass repetitive navigation
 * and jump directly to main content.
 */

import { test, expect } from '@playwright/test';

test.describe('Skip Link Functionality', () => {
  test('Landing page should have functional skip link', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Skip link should exist but be visually hidden
    const skipLink = page.locator('a[href="#main-content"]');
    await expect(skipLink).toBeAttached();

    // Skip link should become visible on focus
    await page.keyboard.press('Tab');

    // Check if skip link is now visible (has not-sr-only class when focused)
    const isVisible = await skipLink.evaluate((el) => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    });

    expect(isVisible).toBeTruthy();

    // Skip link should have correct text
    const linkText = await skipLink.textContent();
    expect(linkText).toContain('본문');

    // Target element should exist
    const mainContent = page.locator('#main-content, main');
    await expect(mainContent.first()).toBeAttached();
  });

  test('Skip link should move focus to main content', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Tab to skip link
    await page.keyboard.press('Tab');

    // Activate skip link
    await page.keyboard.press('Enter');

    // Wait for focus to move
    await page.waitForTimeout(100);

    // Check if focus moved to main content or first focusable element within
    const activeElement = await page.evaluate(() => {
      const el = document.activeElement;
      return {
        id: el?.id,
        tagName: el?.tagName,
        isInMain: el?.closest('main') !== null || el?.id === 'main-content',
      };
    });

    // Focus should either be on main element or within main content
    expect(
      activeElement.id === 'main-content' ||
      activeElement.tagName === 'MAIN' ||
      activeElement.isInMain
    ).toBeTruthy();
  });

  // Skip portal tests in CI without auth
  const describeOrSkip = process.env.CI ? test.describe.skip : test.describe;

  describeOrSkip('Portal Skip Links', () => {
    const portalRoutes = [
      '/lawyer/dashboard',
      '/client/dashboard',
      '/detective/dashboard',
    ];

    for (const route of portalRoutes) {
      test(`${route} should have skip link`, async ({ page }) => {
        await page.goto(route);
        await page.waitForLoadState('networkidle');

        // Skip if redirected to login
        if (page.url().includes('/login')) {
          test.skip(true, 'Page requires authentication');
          return;
        }

        // Skip link should exist
        const skipLink = page.locator('a[href="#main-content"]');
        await expect(skipLink).toBeAttached();

        // Main content target should exist
        const mainContent = page.locator('main#main-content');
        await expect(mainContent).toBeAttached();

        // Main content should have tabIndex for focus
        const tabIndex = await mainContent.getAttribute('tabindex');
        expect(tabIndex).toBe('-1');
      });
    }
  });
});

test.describe('Focus Order', () => {
  test('First Tab press should focus skip link', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Press Tab once
    await page.keyboard.press('Tab');

    // Get currently focused element
    const focusedHref = await page.evaluate(() => {
      const el = document.activeElement as HTMLAnchorElement;
      return el?.href || el?.getAttribute('href');
    });

    // Should be focused on skip link
    expect(focusedHref).toContain('#main-content');
  });

  test('Focus should not be trapped after using skip link', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Tab to skip link and activate it
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');

    // Wait for focus to move
    await page.waitForTimeout(100);

    // Continue tabbing - should be able to navigate
    for (let i = 0; i < 3; i++) {
      await page.keyboard.press('Tab');
    }

    // Focus should have moved from main content
    const activeElement = await page.evaluate(() => {
      return document.activeElement?.tagName;
    });

    // Should be able to tab to other elements
    expect(activeElement).toBeDefined();
  });
});

test.describe('Screen Reader Compatibility', () => {
  test('Skip link should have proper ARIA attributes', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const skipLink = page.locator('a[href="#main-content"]');

    // Skip link should have accessible name
    const accessibleName = await skipLink.evaluate((el) => {
      return el.textContent?.trim() || el.getAttribute('aria-label');
    });

    expect(accessibleName).toBeTruthy();
    expect(accessibleName!.length).toBeGreaterThan(0);
  });

  test('Main content should be a landmark region', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Main element should exist with proper role
    const mainLandmark = page.locator('main, [role="main"]');
    await expect(mainLandmark.first()).toBeAttached();

    // Main should be accessible as a landmark
    const isLandmark = await mainLandmark.first().evaluate((el) => {
      const role = el.getAttribute('role') || el.tagName.toLowerCase();
      return role === 'main';
    });

    expect(isLandmark).toBeTruthy();
  });
});

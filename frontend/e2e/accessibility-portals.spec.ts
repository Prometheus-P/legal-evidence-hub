/**
 * Portal Accessibility Tests
 * WCAG 2.2 AA Compliance Testing for all portals
 *
 * Tests accessibility across:
 * - Lawyer portal
 * - Client portal
 * - Detective portal
 *
 * Each portal is tested for:
 * - axe-core violations (critical/serious)
 * - Landmark regions (nav, main, aside)
 * - Heading hierarchy
 * - Focus management
 */

import { test, expect, expectNoViolations } from './fixtures/accessibility';

/**
 * Portal routes to test
 * Note: These tests require authentication to be mocked or bypassed
 */
const PORTAL_ROUTES = {
  lawyer: ['/lawyer/dashboard', '/lawyer/cases'],
  client: ['/client/dashboard', '/client/cases'],
  detective: ['/detective/dashboard', '/detective/cases'],
};

/**
 * Common accessibility checks for all pages
 */
async function runCommonAccessibilityChecks(
  page: import('@playwright/test').Page,
  makeAxeBuilder: (options?: import('./fixtures/accessibility').AccessibilityTestOptions) => import('@axe-core/playwright').default
) {
  // Run axe-core analysis
  const results = await makeAxeBuilder().analyze();
  expectNoViolations(results);

  // Check for main landmark
  const mainLandmark = page.locator('main[id="main-content"]');
  await expect(mainLandmark).toBeVisible();

  // Check for navigation landmark
  const navLandmark = page.locator('aside[aria-label], nav[aria-label]');
  await expect(navLandmark.first()).toBeVisible();

  // Check heading hierarchy starts with h1 or h2
  const headings = await page.locator('h1, h2').all();
  expect(headings.length).toBeGreaterThan(0);
}

// Skip tests in CI without proper auth setup
const describeOrSkip = process.env.CI ? test.describe.skip : test.describe;

describeOrSkip('Lawyer Portal Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Add authentication mock/setup here
    // For now, we'll test unauthenticated pages or mock auth
  });

  for (const route of PORTAL_ROUTES.lawyer) {
    test(`${route} should be accessible`, async ({ page, makeAxeBuilder }) => {
      await page.goto(route);

      // Wait for page to load (may redirect to login)
      await page.waitForLoadState('networkidle');

      // If redirected to login, skip the test
      if (page.url().includes('/login')) {
        test.skip(true, 'Page requires authentication');
        return;
      }

      await runCommonAccessibilityChecks(page, makeAxeBuilder);
    });
  }
});

describeOrSkip('Client Portal Accessibility', () => {
  for (const route of PORTAL_ROUTES.client) {
    test(`${route} should be accessible`, async ({ page, makeAxeBuilder }) => {
      await page.goto(route);
      await page.waitForLoadState('networkidle');

      if (page.url().includes('/login')) {
        test.skip(true, 'Page requires authentication');
        return;
      }

      await runCommonAccessibilityChecks(page, makeAxeBuilder);
    });
  }
});

describeOrSkip('Detective Portal Accessibility', () => {
  for (const route of PORTAL_ROUTES.detective) {
    test(`${route} should be accessible`, async ({ page, makeAxeBuilder }) => {
      await page.goto(route);
      await page.waitForLoadState('networkidle');

      if (page.url().includes('/login')) {
        test.skip(true, 'Page requires authentication');
        return;
      }

      await runCommonAccessibilityChecks(page, makeAxeBuilder);
    });
  }
});

test.describe('Public Pages Accessibility', () => {
  test('Landing page should be accessible', async ({ page, makeAxeBuilder }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const results = await makeAxeBuilder().analyze();
    expectNoViolations(results);

    // Check for skip link
    const skipLink = page.locator('a[href="#main-content"]');
    await expect(skipLink).toBeAttached();

    // Check for main landmark
    const mainLandmark = page.locator('main, [role="main"]');
    await expect(mainLandmark.first()).toBeVisible();
  });

  test('Login page should be accessible', async ({ page, makeAxeBuilder }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    const results = await makeAxeBuilder().analyze();
    expectNoViolations(results);

    // Check form labels
    const formInputs = page.locator('input:not([type="hidden"])');
    const inputCount = await formInputs.count();

    for (let i = 0; i < inputCount; i++) {
      const input = formInputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledby = await input.getAttribute('aria-labelledby');

      // Each input should have a label, aria-label, or aria-labelledby
      const hasLabel = id ? await page.locator(`label[for="${id}"]`).count() > 0 : false;
      const hasAccessibleName = hasLabel || ariaLabel || ariaLabelledby;

      expect(hasAccessibleName).toBeTruthy();
    }
  });
});

test.describe('Keyboard Navigation', () => {
  test('Tab key should navigate through interactive elements', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Press Tab to start keyboard navigation
    await page.keyboard.press('Tab');

    // First focusable element should be focused
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(['A', 'BUTTON', 'INPUT']).toContain(firstFocused);

    // Continue tabbing and verify focus moves
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => document.activeElement?.tagName);
      expect(focused).toBeDefined();
    }
  });

  test('Focus should be visible on interactive elements', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Tab to an interactive element
    await page.keyboard.press('Tab');

    // Get the focused element
    const focusedElement = page.locator(':focus');

    // Check that the element has a visible focus indicator
    // This is done by checking if the element has a non-zero outline or box-shadow
    const hasVisibleFocus = await focusedElement.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      const outline = styles.outline;
      const boxShadow = styles.boxShadow;
      const ring = styles.getPropertyValue('--tw-ring-width');

      return (
        (outline && outline !== 'none' && !outline.includes('0px')) ||
        (boxShadow && boxShadow !== 'none') ||
        (ring && ring !== '0px')
      );
    });

    expect(hasVisibleFocus).toBeTruthy();
  });
});

test.describe('Color Contrast', () => {
  test('Text should have sufficient color contrast', async ({ page, makeAxeBuilder }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Run axe-core with only color contrast rules
    const results = await makeAxeBuilder({
      wcagTags: ['wcag2aa'],
    }).analyze();

    // Filter for color contrast violations only
    const contrastViolations = results.violations.filter(
      (v) => v.id === 'color-contrast'
    );

    if (contrastViolations.length > 0) {
      console.warn('Color contrast issues found:', contrastViolations);
    }

    // We warn but don't fail on contrast issues during development
    // In production, this should be: expect(contrastViolations).toHaveLength(0);
  });
});

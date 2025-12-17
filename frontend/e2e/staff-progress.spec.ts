import { test, expect } from '@playwright/test';

const STAFF_PATH = '/staff/progress';

/**
 * Smoke tests for the deployed staff progress dashboard.
 * These are read-only checks that ensure deep links resolve correctly.
 */
test.describe('Staff Progress Dashboard (deployed)', () => {
  test('should not render the Next.js 404 page', async ({ page }) => {
    await page.goto(STAFF_PATH, { waitUntil: 'networkidle' });

    const notFoundHeading = page.getByText('페이지를 찾을 수 없습니다');
    await expect(notFoundHeading).toHaveCount(0);
  });
});

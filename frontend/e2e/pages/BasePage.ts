/**
 * Base Page Object Model
 * =======================
 *
 * Foundation for all Page Objects in E2E tests.
 * Provides common utilities for navigation, waiting, and interactions.
 *
 * QA Framework v4.0 - Playwright Page Object Model
 *
 * Features:
 * - Explicit waits to prevent flaky tests
 * - Screenshot capture for debugging
 * - Toast/notification detection
 * - Safe click/fill with auto-wait
 *
 * Usage:
 *   class LoginPage extends BasePage {
 *     async goto() {
 *       await this.page.goto('/login');
 *       await this.waitForLoad();
 *     }
 *   }
 */

import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  readonly page: Page;

  /** Default timeout for element interactions (ms) */
  protected readonly defaultTimeout = 15000;

  /** Default timeout for navigation (ms) */
  protected readonly navigationTimeout = 30000;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to the page.
   * Must be implemented by subclasses.
   */
  abstract goto(): Promise<void>;

  /**
   * Wait for page to be fully loaded.
   * Waits for both DOM content and network idle.
   */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for a specific element to be visible.
   *
   * @param locator - Playwright locator for the element
   * @param timeout - Optional custom timeout in ms
   */
  async waitForElement(
    locator: Locator,
    timeout: number = this.defaultTimeout
  ): Promise<void> {
    await expect(locator).toBeVisible({ timeout });
  }

  /**
   * Wait for element to be hidden/removed.
   *
   * @param locator - Playwright locator for the element
   * @param timeout - Optional custom timeout in ms
   */
  async waitForElementHidden(
    locator: Locator,
    timeout: number = this.defaultTimeout
  ): Promise<void> {
    await expect(locator).toBeHidden({ timeout });
  }

  /**
   * Safely click an element with explicit wait.
   * Prevents flaky tests from clicking too early.
   *
   * @param locator - Playwright locator for the element
   */
  async safeClick(locator: Locator): Promise<void> {
    await this.waitForElement(locator);
    await locator.click();
  }

  /**
   * Safely fill an input with explicit wait.
   * Clears existing content before filling.
   *
   * @param locator - Playwright locator for the input
   * @param value - Value to fill
   */
  async safeFill(locator: Locator, value: string): Promise<void> {
    await this.waitForElement(locator);
    await locator.clear();
    await locator.fill(value);
  }

  /**
   * Check if an element exists without throwing.
   *
   * @param locator - Playwright locator for the element
   * @param timeout - Optional timeout in ms
   * @returns true if element is visible, false otherwise
   */
  async elementExists(
    locator: Locator,
    timeout: number = 5000
  ): Promise<boolean> {
    try {
      await expect(locator).toBeVisible({ timeout });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Take a screenshot with timestamp.
   * Useful for debugging test failures.
   *
   * @param name - Base name for the screenshot file
   */
  async takeScreenshot(name: string): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await this.page.screenshot({
      path: `screenshots/${name}-${timestamp}.png`,
      fullPage: true,
    });
  }

  /**
   * Wait for URL to match a pattern.
   *
   * @param urlPattern - String or RegExp to match URL against
   * @param timeout - Optional timeout in ms
   */
  async waitForNavigation(
    urlPattern: string | RegExp,
    timeout: number = this.navigationTimeout
  ): Promise<void> {
    await this.page.waitForURL(urlPattern, { timeout });
  }

  /**
   * Get toast/notification message text.
   * Supports common toast library patterns.
   *
   * @returns Toast message text or null if not found
   */
  async getToastMessage(): Promise<string | null> {
    // Try common toast selectors
    const toastSelectors = [
      '[role="alert"]',
      '.toast',
      '.notification',
      '[data-testid="toast"]',
      '.Toastify__toast-body',
    ];

    for (const selector of toastSelectors) {
      const toast = this.page.locator(selector).first();
      if (await this.elementExists(toast, 2000)) {
        return await toast.textContent();
      }
    }

    return null;
  }

  /**
   * Wait for loading spinner to disappear.
   * Common pattern for async operations.
   */
  async waitForLoadingComplete(): Promise<void> {
    const loadingSelectors = [
      '.loading',
      '[data-testid="loading"]',
      '.spinner',
      '[role="progressbar"]',
    ];

    for (const selector of loadingSelectors) {
      const loading = this.page.locator(selector);
      if (await this.elementExists(loading, 1000)) {
        await this.waitForElementHidden(loading);
      }
    }
  }

  /**
   * Scroll element into view.
   *
   * @param locator - Playwright locator for the element
   */
  async scrollIntoView(locator: Locator): Promise<void> {
    await locator.scrollIntoViewIfNeeded();
  }

  /**
   * Get current page URL.
   */
  getCurrentUrl(): string {
    return this.page.url();
  }

  /**
   * Get current page title.
   */
  async getTitle(): Promise<string> {
    return await this.page.title();
  }
}

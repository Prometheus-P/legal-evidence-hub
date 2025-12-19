/**
 * Dashboard Page Object
 * ======================
 *
 * Encapsulates dashboard page interactions and assertions.
 *
 * QA Framework v4.0 - Page Object Model
 *
 * Usage:
 *   const dashboardPage = new DashboardPage(page);
 *   await dashboardPage.goto();
 *   await dashboardPage.verifyDashboardLoaded();
 */

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class DashboardPage extends BasePage {
  // Locators
  readonly welcomeMessage: Locator;
  readonly casesSection: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;
  readonly newCaseButton: Locator;
  readonly casesList: Locator;
  readonly recentActivity: Locator;

  constructor(page: Page) {
    super(page);

    // Define locators
    this.welcomeMessage = page.getByRole('heading', { name: /환영|welcome|dashboard/i });
    this.casesSection = page.locator('[data-testid="cases-section"], .cases-section');
    this.userMenu = page.getByRole('button', { name: /메뉴|menu|profile/i });
    this.logoutButton = page.getByRole('menuitem', { name: /로그아웃|logout|sign out/i });
    this.newCaseButton = page.getByRole('button', { name: /새.*케이스|new.*case|create.*case/i });
    this.casesList = page.locator('[data-testid="cases-list"], .cases-list');
    this.recentActivity = page.locator('[data-testid="recent-activity"], .recent-activity');
  }

  /**
   * Navigate to dashboard.
   * Requires authenticated user.
   */
  async goto(): Promise<void> {
    await this.page.goto('/dashboard');
    await this.waitForLoad();
  }

  /**
   * Verify dashboard loaded successfully.
   */
  async verifyDashboardLoaded(): Promise<void> {
    // Wait for key elements
    await this.waitForLoadingComplete();

    // Check we're on dashboard URL
    await this.waitForNavigation(/dashboard/);

    // Verify at least one key element is visible
    const keyElements = [
      this.casesSection,
      this.userMenu,
      this.page.getByRole('main'),
    ];

    let foundElement = false;
    for (const element of keyElements) {
      if (await this.elementExists(element, 3000)) {
        foundElement = true;
        break;
      }
    }

    expect(foundElement).toBe(true);
  }

  /**
   * Open user menu dropdown.
   */
  async openUserMenu(): Promise<void> {
    await this.safeClick(this.userMenu);
    await expect(this.logoutButton).toBeVisible();
  }

  /**
   * Logout from the application.
   */
  async logout(): Promise<void> {
    await this.openUserMenu();
    await this.safeClick(this.logoutButton);
    await this.waitForNavigation(/login/);
  }

  /**
   * Navigate to cases page.
   */
  async goToCases(): Promise<void> {
    const casesLink = this.page.getByRole('link', { name: /케이스|cases/i });
    await this.safeClick(casesLink);
    await this.waitForNavigation(/cases/);
  }

  /**
   * Click new case button.
   */
  async createNewCase(): Promise<void> {
    await this.safeClick(this.newCaseButton);
  }

  /**
   * Get count of cases displayed.
   */
  async getCaseCount(): Promise<number> {
    const caseItems = this.page.locator('[data-testid="case-item"], .case-item');
    return await caseItems.count();
  }

  /**
   * Search for a case.
   *
   * @param query - Search query
   */
  async searchCases(query: string): Promise<void> {
    const searchInput = this.page.getByPlaceholder(/검색|search/i);
    await this.safeFill(searchInput, query);
    await this.page.keyboard.press('Enter');
    await this.waitForLoadingComplete();
  }
}

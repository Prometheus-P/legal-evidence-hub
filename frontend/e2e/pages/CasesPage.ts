/**
 * Cases Page Object
 * ==================
 *
 * Encapsulates case listing and management interactions.
 *
 * QA Framework v4.0 - Page Object Model
 *
 * Usage:
 *   const casesPage = new CasesPage(page);
 *   await casesPage.goto();
 *   await casesPage.selectCase('Case Title');
 */

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class CasesPage extends BasePage {
  // Locators
  readonly pageTitle: Locator;
  readonly newCaseButton: Locator;
  readonly searchInput: Locator;
  readonly filterDropdown: Locator;
  readonly caseList: Locator;
  readonly emptyState: Locator;
  readonly pagination: Locator;

  constructor(page: Page) {
    super(page);

    // Define locators
    this.pageTitle = page.getByRole('heading', { name: /케이스|cases/i });
    this.newCaseButton = page.getByRole('button', { name: /새.*케이스|new.*case|추가/i });
    this.searchInput = page.getByPlaceholder(/검색|search/i);
    this.filterDropdown = page.getByRole('combobox', { name: /필터|filter|상태/i });
    this.caseList = page.locator('[data-testid="case-list"], .case-list, table tbody');
    this.emptyState = page.getByText(/케이스가 없습니다|no cases/i);
    this.pagination = page.locator('[data-testid="pagination"], .pagination');
  }

  /**
   * Navigate to cases page.
   */
  async goto(): Promise<void> {
    await this.page.goto('/cases');
    await this.waitForLoad();
    await this.waitForLoadingComplete();
  }

  /**
   * Verify cases page loaded.
   */
  async verifyCasesPageLoaded(): Promise<void> {
    await this.waitForNavigation(/cases/);
    // Either case list or empty state should be visible
    const hasContent =
      (await this.elementExists(this.caseList, 5000)) ||
      (await this.elementExists(this.emptyState, 5000));
    expect(hasContent).toBe(true);
  }

  /**
   * Get all case items on current page.
   */
  getCaseItems(): Locator {
    return this.page.locator('[data-testid="case-item"], .case-item, tr[data-case-id]');
  }

  /**
   * Get count of cases on current page.
   */
  async getCaseCount(): Promise<number> {
    return await this.getCaseItems().count();
  }

  /**
   * Select a case by its title.
   *
   * @param title - Case title to click
   */
  async selectCase(title: string): Promise<void> {
    const caseRow = this.page.getByRole('row', { name: new RegExp(title, 'i') });
    const caseLink = caseRow.getByRole('link').first();

    if (await this.elementExists(caseLink, 3000)) {
      await this.safeClick(caseLink);
    } else {
      // Fallback: click the row itself
      await this.safeClick(caseRow);
    }

    await this.waitForNavigation(/cases\/[^/]+/);
  }

  /**
   * Search for cases.
   *
   * @param query - Search query
   */
  async searchCases(query: string): Promise<void> {
    await this.safeFill(this.searchInput, query);
    await this.page.keyboard.press('Enter');
    await this.waitForLoadingComplete();
  }

  /**
   * Filter cases by status.
   *
   * @param status - Status to filter by
   */
  async filterByStatus(status: string): Promise<void> {
    await this.safeClick(this.filterDropdown);
    const option = this.page.getByRole('option', { name: new RegExp(status, 'i') });
    await this.safeClick(option);
    await this.waitForLoadingComplete();
  }

  /**
   * Click new case button to start creation.
   */
  async startNewCase(): Promise<void> {
    await this.safeClick(this.newCaseButton);
  }

  /**
   * Check if a specific case exists in the list.
   *
   * @param title - Case title to look for
   */
  async caseExists(title: string): Promise<boolean> {
    const caseElement = this.page.getByText(title);
    return await this.elementExists(caseElement, 3000);
  }

  /**
   * Go to next page of results.
   */
  async goToNextPage(): Promise<void> {
    const nextButton = this.pagination.getByRole('button', { name: /다음|next/i });
    if (await this.elementExists(nextButton, 2000)) {
      await this.safeClick(nextButton);
      await this.waitForLoadingComplete();
    }
  }

  /**
   * Go to previous page of results.
   */
  async goToPreviousPage(): Promise<void> {
    const prevButton = this.pagination.getByRole('button', { name: /이전|prev/i });
    if (await this.elementExists(prevButton, 2000)) {
      await this.safeClick(prevButton);
      await this.waitForLoadingComplete();
    }
  }

  /**
   * Delete a case by title (if delete button exists).
   *
   * @param title - Case title to delete
   */
  async deleteCase(title: string): Promise<void> {
    const caseRow = this.page.getByRole('row', { name: new RegExp(title, 'i') });
    const deleteButton = caseRow.getByRole('button', { name: /삭제|delete/i });

    if (await this.elementExists(deleteButton, 3000)) {
      await this.safeClick(deleteButton);

      // Confirm dialog
      const confirmButton = this.page.getByRole('button', { name: /확인|confirm|yes/i });
      if (await this.elementExists(confirmButton, 2000)) {
        await this.safeClick(confirmButton);
      }

      await this.waitForLoadingComplete();
    }
  }
}

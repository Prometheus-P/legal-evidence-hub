/**
 * Login Page Object
 * ==================
 *
 * Encapsulates login page interactions and assertions.
 *
 * QA Framework v4.0 - Page Object Model
 *
 * Usage:
 *   const loginPage = new LoginPage(page);
 *   await loginPage.goto();
 *   await loginPage.login('user@example.com', 'password');
 *   await loginPage.verifyLoginSuccess();
 */

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  // Locators
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;
  readonly signUpLink: Locator;

  constructor(page: Page) {
    super(page);

    // Define locators using accessible selectors
    this.emailInput = page.getByLabel(/이메일|email/i);
    this.passwordInput = page.getByLabel(/비밀번호|password/i);
    this.submitButton = page.getByRole('button', { name: /로그인|login|sign in/i });
    this.errorMessage = page.getByRole('alert');
    this.forgotPasswordLink = page.getByRole('link', { name: /비밀번호.*찾기|forgot.*password/i });
    this.signUpLink = page.getByRole('link', { name: /회원가입|sign up|register/i });
  }

  /**
   * Navigate to login page.
   */
  async goto(): Promise<void> {
    await this.page.goto('/login');
    await this.waitForLoad();
    await this.waitForElement(this.emailInput);
  }

  /**
   * Fill and submit login form.
   *
   * @param email - User email
   * @param password - User password
   */
  async login(email: string, password: string): Promise<void> {
    await this.safeFill(this.emailInput, email);
    await this.safeFill(this.passwordInput, password);
    await this.safeClick(this.submitButton);
  }

  /**
   * Verify login was successful.
   * Checks for redirect to dashboard.
   */
  async verifyLoginSuccess(): Promise<void> {
    await this.waitForNavigation(/\/(dashboard|cases|lawyer|staff)/);
    // Optionally verify user menu is visible
    const userMenu = this.page.getByRole('button', { name: /메뉴|menu|profile/i });
    await expect(userMenu).toBeVisible({ timeout: 10000 });
  }

  /**
   * Verify login failed with error message.
   *
   * @param expectedMessage - Expected error text (optional)
   */
  async verifyLoginFailed(expectedMessage?: string | RegExp): Promise<void> {
    await this.waitForElement(this.errorMessage);

    if (expectedMessage) {
      await expect(this.errorMessage).toContainText(expectedMessage);
    }

    // Should still be on login page
    expect(this.page.url()).toContain('/login');
  }

  /**
   * Check if email input has validation error.
   */
  async hasEmailError(): Promise<boolean> {
    const emailError = this.page.locator('[data-testid="email-error"], #email-error');
    return await this.elementExists(emailError);
  }

  /**
   * Check if password input has validation error.
   */
  async hasPasswordError(): Promise<boolean> {
    const passwordError = this.page.locator('[data-testid="password-error"], #password-error');
    return await this.elementExists(passwordError);
  }

  /**
   * Click forgot password link.
   */
  async goToForgotPassword(): Promise<void> {
    await this.safeClick(this.forgotPasswordLink);
    await this.waitForNavigation(/forgot|reset/);
  }

  /**
   * Click sign up link.
   */
  async goToSignUp(): Promise<void> {
    await this.safeClick(this.signUpLink);
    await this.waitForNavigation(/signup|register/);
  }
}

/**
 * Accessibility Testing Fixtures
 * WCAG 2.2 AA Compliance Testing with axe-core
 *
 * This fixture provides axe-core accessibility testing capabilities
 * for Playwright E2E tests.
 *
 * Usage:
 * ```typescript
 * import { test, expect } from '../fixtures/accessibility';
 *
 * test('page should be accessible', async ({ page, makeAxeBuilder }) => {
 *   await page.goto('/lawyer/dashboard');
 *   const accessibilityResults = await makeAxeBuilder().analyze();
 *   expect(accessibilityResults.violations).toEqual([]);
 * });
 * ```
 */

import { test as base } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * WCAG 2.2 AA tags for axe-core
 * These tags ensure we test against WCAG 2.2 Level AA compliance
 */
export const WCAG_22_AA_TAGS = [
  'wcag2a',
  'wcag2aa',
  'wcag21a',
  'wcag21aa',
  'wcag22aa',
  'best-practice',
];

/**
 * Severity levels for accessibility violations
 */
export type ViolationImpact = 'minor' | 'moderate' | 'serious' | 'critical';

/**
 * Configuration options for accessibility testing
 */
export interface AccessibilityTestOptions {
  /** Only fail on these impact levels (default: ['critical', 'serious']) */
  failOnImpact?: ViolationImpact[];
  /** Additional axe-core rules to disable */
  disableRules?: string[];
  /** Specific elements to exclude from testing */
  excludeSelectors?: string[];
  /** WCAG tags to test against */
  wcagTags?: string[];
}

/**
 * Default options for accessibility testing
 */
const defaultOptions: AccessibilityTestOptions = {
  failOnImpact: ['critical', 'serious'],
  disableRules: [],
  excludeSelectors: [],
  wcagTags: WCAG_22_AA_TAGS,
};

/**
 * Extended test fixture with accessibility testing support
 */
export const test = base.extend<{
  makeAxeBuilder: (options?: AccessibilityTestOptions) => AxeBuilder;
}>({
  makeAxeBuilder: async ({ page }, use) => {
    const makeAxeBuilder = (options: AccessibilityTestOptions = {}) => {
      const mergedOptions = { ...defaultOptions, ...options };

      let builder = new AxeBuilder({ page })
        .withTags(mergedOptions.wcagTags || WCAG_22_AA_TAGS);

      // Disable specific rules if requested
      if (mergedOptions.disableRules && mergedOptions.disableRules.length > 0) {
        builder = builder.disableRules(mergedOptions.disableRules);
      }

      // Exclude specific selectors from testing
      if (mergedOptions.excludeSelectors && mergedOptions.excludeSelectors.length > 0) {
        builder = builder.exclude(mergedOptions.excludeSelectors);
      }

      return builder;
    };

    await use(makeAxeBuilder);
  },
});

/**
 * Filter violations by impact level
 */
export function filterViolationsByImpact(
  violations: Awaited<ReturnType<AxeBuilder['analyze']>>['violations'],
  impacts: ViolationImpact[]
): typeof violations {
  return violations.filter((v) => impacts.includes(v.impact as ViolationImpact));
}

/**
 * Format violations for readable error output
 */
export function formatViolations(
  violations: Awaited<ReturnType<AxeBuilder['analyze']>>['violations']
): string {
  if (violations.length === 0) return 'No accessibility violations found.';

  return violations
    .map((violation) => {
      const nodes = violation.nodes
        .map((node) => `  - ${node.html}\n    ${node.failureSummary}`)
        .join('\n');

      return `
[${violation.impact?.toUpperCase()}] ${violation.id}: ${violation.description}
Help: ${violation.helpUrl}
Affected elements:
${nodes}
`;
    })
    .join('\n---\n');
}

/**
 * Custom expect for accessibility testing
 */
export function expectNoViolations(
  results: Awaited<ReturnType<AxeBuilder['analyze']>>,
  options: AccessibilityTestOptions = {}
) {
  const mergedOptions = { ...defaultOptions, ...options };
  const filteredViolations = filterViolationsByImpact(
    results.violations,
    mergedOptions.failOnImpact || ['critical', 'serious']
  );

  if (filteredViolations.length > 0) {
    throw new Error(
      `Accessibility violations found:\n${formatViolations(filteredViolations)}`
    );
  }
}

export { expect } from '@playwright/test';

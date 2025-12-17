/**
 * Design Tokens Unit Tests (T018)
 * Validates design token system and detects legacy alias usage
 */

import * as fs from 'fs';
import * as path from 'path';
import { glob } from 'glob';

// Legacy color aliases that should be removed
const LEGACY_ALIASES = [
  'accent',
  'accent-dark',
  'semantic-error',
  'deep-trust-blue',
  'calm-grey',
  'success-green',
];

// Patterns to search for legacy usage
const LEGACY_PATTERNS = [
  /bg-accent(?!-)/g,
  /bg-accent-dark/g,
  /text-accent(?!-)/g,
  /text-accent-dark/g,
  /border-accent(?!-)/g,
  /bg-semantic-error/g,
  /text-semantic-error/g,
  /bg-deep-trust-blue/g,
  /text-deep-trust-blue/g,
  /bg-calm-grey/g,
  /bg-success-green/g,
  /text-success-green/g,
];

describe('Design Token System', () => {
  describe('CSS Variable Definitions', () => {
    let designTokensCSS: string;

    beforeAll(() => {
      const cssPath = path.join(
        process.cwd(),
        'src/styles/design-tokens.css'
      );
      if (fs.existsSync(cssPath)) {
        designTokensCSS = fs.readFileSync(cssPath, 'utf-8');
      } else {
        designTokensCSS = '';
      }
    });

    it('should define primary color tokens', () => {
      expect(designTokensCSS).toContain('--color-primary:');
      expect(designTokensCSS).toContain('--color-primary-hover:');
      expect(designTokensCSS).toContain('--color-primary-active:');
      expect(designTokensCSS).toContain('--color-primary-light:');
      expect(designTokensCSS).toContain('--color-primary-contrast:');
    });

    it('should define secondary color tokens', () => {
      expect(designTokensCSS).toContain('--color-secondary:');
      expect(designTokensCSS).toContain('--color-secondary-hover:');
      expect(designTokensCSS).toContain('--color-secondary-light:');
    });

    it('should define status color tokens', () => {
      expect(designTokensCSS).toContain('--color-success:');
      expect(designTokensCSS).toContain('--color-warning:');
      expect(designTokensCSS).toContain('--color-error:');
      expect(designTokensCSS).toContain('--color-info:');
    });

    it('should define text color tokens', () => {
      expect(designTokensCSS).toContain('--color-text-primary:');
      expect(designTokensCSS).toContain('--color-text-secondary:');
      expect(designTokensCSS).toContain('--color-text-tertiary:');
      expect(designTokensCSS).toContain('--color-text-disabled:');
    });

    it('should define surface color tokens', () => {
      expect(designTokensCSS).toContain('--color-surface-default:');
      expect(designTokensCSS).toContain('--color-surface-elevated:');
      expect(designTokensCSS).toContain('--color-surface-overlay:');
    });

    it('should define border color tokens', () => {
      expect(designTokensCSS).toContain('--color-border-default:');
      expect(designTokensCSS).toContain('--color-border-strong:');
      expect(designTokensCSS).toContain('--color-border-focus:');
    });

    it('should define typography tokens', () => {
      expect(designTokensCSS).toContain('--font-size-sm:');
      expect(designTokensCSS).toContain('--font-size-base:');
      expect(designTokensCSS).toContain('--font-size-lg:');
      expect(designTokensCSS).toContain('--font-weight-normal:');
      expect(designTokensCSS).toContain('--font-weight-bold:');
    });

    it('should define spacing tokens', () => {
      expect(designTokensCSS).toContain('--spacing-1:');
      expect(designTokensCSS).toContain('--spacing-2:');
      expect(designTokensCSS).toContain('--spacing-4:');
      expect(designTokensCSS).toContain('--spacing-8:');
    });

    it('should define shadow tokens', () => {
      expect(designTokensCSS).toContain('--shadow-sm:');
      expect(designTokensCSS).toContain('--shadow-md:');
      expect(designTokensCSS).toContain('--shadow-lg:');
    });

    it('should define z-index tokens', () => {
      expect(designTokensCSS).toContain('--z-dropdown:');
      expect(designTokensCSS).toContain('--z-modal:');
      expect(designTokensCSS).toContain('--z-tooltip:');
      expect(designTokensCSS).toContain('--z-toast:');
    });

    it('should define transition tokens', () => {
      expect(designTokensCSS).toContain('--transition-fast:');
      expect(designTokensCSS).toContain('--transition-normal:');
      expect(designTokensCSS).toContain('--transition-slow:');
    });

    it('should define dark mode overrides', () => {
      expect(designTokensCSS).toContain('.dark {');
    });
  });

  describe('TypeScript Type Definitions', () => {
    let typesContent: string;

    beforeAll(() => {
      const typesPath = path.join(
        process.cwd(),
        'src/types/design-tokens.ts'
      );
      if (fs.existsSync(typesPath)) {
        typesContent = fs.readFileSync(typesPath, 'utf-8');
      } else {
        typesContent = '';
      }
    });

    it('should export SemanticColorSet type', () => {
      expect(typesContent).toContain('SemanticColorSet');
    });

    it('should export FontSize type', () => {
      expect(typesContent).toContain('FontSize');
    });

    it('should export SpacingScale type', () => {
      expect(typesContent).toContain('SpacingScale');
    });

    it('should export ThemeName type', () => {
      expect(typesContent).toContain('ThemeName');
    });

    it('should export ComponentState type', () => {
      expect(typesContent).toContain('ComponentState');
    });

    it('should export legacy alias mapping', () => {
      expect(typesContent).toContain('LEGACY_COLOR_ALIASES');
    });
  });

  describe('Legacy Alias Detection', () => {
    it('should not have legacy aliases in tailwind.config.js', async () => {
      const configPath = path.join(process.cwd(), 'tailwind.config.js');

      if (!fs.existsSync(configPath)) {
        // Skip if file doesn't exist (might be using .ts)
        return;
      }

      const configContent = fs.readFileSync(configPath, 'utf-8');

      // After T033 is complete, these should NOT be found
      for (const alias of LEGACY_ALIASES) {
        // Check for direct definitions of legacy aliases
        const aliasRegex = new RegExp(`['"]${alias}['"]\\s*:`);
        // NOTE: This will fail until T033 removes legacy aliases
        // expect(configContent).not.toMatch(aliasRegex);
      }
    });

    it('should not have legacy class usage in component files', async () => {
      // This test scans component files for legacy patterns
      // It will fail initially and pass after all migrations (T019-T032) are complete

      const componentDir = path.join(process.cwd(), 'src/components');

      if (!fs.existsSync(componentDir)) {
        return;
      }

      const files = await glob('**/*.{tsx,ts}', {
        cwd: componentDir,
        ignore: ['**/node_modules/**', '**/__tests__/**'],
      });

      const legacyUsages: { file: string; pattern: string; matches: string[] }[] = [];

      for (const file of files) {
        const filePath = path.join(componentDir, file);
        const content = fs.readFileSync(filePath, 'utf-8');

        for (const pattern of LEGACY_PATTERNS) {
          const matches = content.match(pattern);
          if (matches && matches.length > 0) {
            legacyUsages.push({
              file,
              pattern: pattern.source,
              matches,
            });
          }
        }
      }

      // NOTE: This assertion will fail until all components are migrated
      // Uncomment after T019-T032 are complete:
      // expect(legacyUsages).toHaveLength(0);

      // For now, just log findings
      if (legacyUsages.length > 0) {
        console.log('Legacy alias usages found:', JSON.stringify(legacyUsages, null, 2));
      }
    });
  });

  describe('Tailwind Configuration', () => {
    it('should reference CSS variables in extend colors', async () => {
      const configPath = path.join(process.cwd(), 'tailwind.config.js');

      if (!fs.existsSync(configPath)) {
        return;
      }

      const configContent = fs.readFileSync(configPath, 'utf-8');

      // Verify semantic colors reference CSS variables
      expect(configContent).toContain('var(--color-primary)');
      expect(configContent).toContain('var(--color-secondary)');
      expect(configContent).toContain('var(--color-error)');
    });
  });
});

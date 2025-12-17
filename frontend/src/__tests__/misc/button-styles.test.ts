import * as fs from 'fs';
import * as path from 'path';

describe('Button Style Rules', () => {
    // Go up from src/__tests__/misc to frontend root
    const projectRoot = path.resolve(__dirname, '../../../');

    test('Primary CTA buttons should use primary semantic token (#1ABC9C)', () => {
        const globalsCssPath = path.join(projectRoot, 'src/styles/globals.css');
        const cssContent = fs.readFileSync(globalsCssPath, 'utf-8');

        // Check for .btn-primary class definition
        const btnPrimaryMatch = cssContent.match(/\.btn-primary\s*{([^}]*)}/);
        expect(btnPrimaryMatch).not.toBeNull();

        if (btnPrimaryMatch) {
            const btnPrimaryContent = btnPrimaryMatch[1];
            // Should use bg-primary (semantic token - migrated from bg-accent)
            expect(btnPrimaryContent).toMatch(/bg-primary/);
        }
    });

    test('design tokens should define primary color', () => {
        const tokensPath = path.join(projectRoot, 'src/styles/design-tokens.css');
        const tokensContent = fs.readFileSync(tokensPath, 'utf-8');

        // Check that primary color is defined in design tokens (may use variable reference)
        expect(tokensContent).toMatch(/--color-primary:/);
    });

    test('Destructive action buttons should use error semantic token (#E74C3C)', () => {
        const globalsCssPath = path.join(projectRoot, 'src/styles/globals.css');
        const cssContent = fs.readFileSync(globalsCssPath, 'utf-8');

        // Check for .btn-danger class definition
        const btnDangerMatch = cssContent.match(/\.btn-danger\s*{([^}]*)}/);
        expect(btnDangerMatch).not.toBeNull();

        if (btnDangerMatch) {
            const btnDangerContent = btnDangerMatch[1];
            // Should use bg-error (semantic token - migrated from bg-semantic-error)
            expect(btnDangerContent).toMatch(/bg-error/);
        }
    });

    test('design tokens should define error color', () => {
        const tokensPath = path.join(projectRoot, 'src/styles/design-tokens.css');
        const tokensContent = fs.readFileSync(tokensPath, 'utf-8');

        // Check that error color is defined in design tokens (may use variable reference)
        expect(tokensContent).toMatch(/--color-error:/);
    });
});

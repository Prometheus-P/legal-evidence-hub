# Quickstart Guide: UI Upgrade

**Feature**: 013-ui-upgrade | **Date**: 2025-12-17

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+ or yarn 1.22+
- Git
- VS Code (recommended) with extensions:
  - Tailwind CSS IntelliSense
  - ESLint
  - Prettier
  - axe Accessibility Linter

## Initial Setup

### 1. Clone and Checkout

```bash
# Clone repository (if not already)
git clone https://github.com/your-org/leh.git
cd leh

# Checkout feature branch
git checkout 013-ui-upgrade
```

### 2. Install Dependencies

```bash
cd frontend
npm install

# Install accessibility testing tools
npm install -D jest-axe @axe-core/playwright
```

### 3. Start Development Server

```bash
npm run dev
# Open http://localhost:3000
```

## Project Structure for UI Upgrade

```
frontend/src/
├── styles/
│   ├── globals.css           # Base styles (existing)
│   └── design-tokens.css     # NEW: Consolidated tokens
├── components/
│   ├── primitives/           # Base components (Button, Input, etc.)
│   ├── shared/               # Cross-feature (EmptyState, Skeleton, etc.)
│   ├── cases/                # Case-specific components
│   ├── evidence/             # Evidence components
│   ├── draft/                # Draft components
│   └── relationship/         # Relationship graph components
└── app/lawyer/               # Lawyer portal pages
```

## Development Workflow

### TDD Cycle (Required per Constitution)

1. **Red**: Write failing test first
2. **Green**: Implement minimal code to pass
3. **Refactor**: Clean up while keeping tests green

```bash
# Run tests in watch mode during development
npm test -- --watch
```

### Component Development Pattern

```tsx
// 1. Write the test first
// __tests__/components/shared/EmptyState.test.tsx
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { EmptyState } from '@/components/shared/EmptyState';
import { FileQuestion } from 'lucide-react';

expect.extend(toHaveNoViolations);

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(
      <EmptyState
        icon={FileQuestion}
        title="No items"
        description="Add your first item to get started"
      />
    );

    expect(screen.getByText('No items')).toBeInTheDocument();
    expect(screen.getByText('Add your first item to get started')).toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    const onClick = jest.fn();
    render(
      <EmptyState
        icon={FileQuestion}
        title="No items"
        description="Add your first item"
        action={{ label: 'Add Item', onClick }}
      />
    );

    expect(screen.getByRole('button', { name: 'Add Item' })).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(
      <EmptyState
        icon={FileQuestion}
        title="No items"
        description="Add your first item"
      />
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Design Token Usage

```tsx
// Use semantic tokens via Tailwind classes
// ✅ Good - uses semantic tokens
<button className="bg-primary text-primary-contrast hover:bg-primary-hover">
  Submit
</button>

// ❌ Bad - uses raw color values
<button className="bg-blue-500 text-white hover:bg-blue-600">
  Submit
</button>

// ❌ Bad - uses legacy aliases (to be removed)
<button className="bg-accent text-white hover:bg-accent-dark">
  Submit
</button>
```

### Responsive Design Pattern

```tsx
// Mobile-first responsive design
<div className="
  flex flex-col gap-4        // Mobile: stack vertically
  md:flex-row md:gap-6       // Tablet+: horizontal layout
  lg:gap-8                   // Desktop: more spacing
">
  <Card className="w-full md:w-1/2 lg:w-1/3" />
  <Card className="w-full md:w-1/2 lg:w-1/3" />
</div>
```

### Accessibility Checklist

Before submitting a component, verify:

- [ ] Keyboard navigable (Tab, Enter, Escape)
- [ ] Focus indicator visible (`focus-visible:ring-2`)
- [ ] ARIA labels on interactive elements
- [ ] Color contrast meets 4.5:1 ratio
- [ ] Touch targets ≥ 44x44px on mobile
- [ ] No accessibility violations in jest-axe

## Testing Commands

```bash
# Unit tests
npm test

# Unit tests with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# E2E tests (Playwright)
npm run test:e2e

# E2E tests with UI
npm run test:e2e:ui

# Lint
npm run lint
```

## Common Tasks

### Adding a New Skeleton Loader

```tsx
// components/shared/skeletons/CaseCardSkeleton.tsx
import { Skeleton } from '../Skeleton';

export const CaseCardSkeleton = () => (
  <div className="p-4 border rounded-lg space-y-3">
    <Skeleton className="h-6 w-3/4" />
    <Skeleton className="h-4 w-1/2" />
    <div className="flex gap-2 pt-2">
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-8 w-20" />
    </div>
  </div>
);
```

### Adding Empty State to a Page

```tsx
// app/lawyer/cases/page.tsx
import { EmptyState } from '@/components/shared/EmptyState';
import { Briefcase } from 'lucide-react';

export default function CasesPage() {
  const { cases, isLoading } = useCases();

  if (isLoading) return <CasesListSkeleton />;

  if (cases.length === 0) {
    return (
      <EmptyState
        icon={Briefcase}
        title="아직 배정된 사건이 없습니다"
        description="새 사건을 생성하거나 관리자에게 사건 배정을 요청하세요."
        action={{
          label: '새 사건 만들기',
          onClick: () => setShowAddModal(true),
        }}
      />
    );
  }

  return <CasesList cases={cases} />;
}
```

### Testing Accessibility

```tsx
// Add to any component test
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| CSS variables not working | Check `design-tokens.css` is imported in `globals.css` |
| Dark mode flash | Ensure `ThemeProvider` wraps app, check script in `<head>` |
| Touch targets too small | Add `min-h-[44px] min-w-[44px]` to interactive elements |
| Focus not visible | Use `focus-visible:ring-2` instead of `focus:ring-2` |
| jest-axe not finding violations | Ensure component is fully rendered before running axe |

### Useful Debug Commands

```bash
# Find legacy color usage
grep -r "bg-accent\|text-accent\|semantic-error" frontend/src/

# Check Tailwind output
npx tailwindcss --help

# Validate TypeScript
npx tsc --noEmit
```

## Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)
- [Radix UI Primitives](https://www.radix-ui.com/primitives) (reference for accessible patterns)
- [LEH Design Tokens](./data-model.md)
- [Component Interfaces](./contracts/components.md)

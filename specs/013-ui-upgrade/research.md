# Research: UI Upgrade

**Feature**: 013-ui-upgrade | **Date**: 2025-12-17

## Research Topics

1. Design Token Architecture for Tailwind CSS
2. Responsive Data Table Patterns
3. WCAG 2.1 AA Accessibility Implementation
4. Loading State Patterns in React
5. Empty State UX Best Practices

---

## 1. Design Token Architecture

### Decision: CSS Custom Properties + Tailwind Extend

**Rationale**: The existing codebase already uses CSS variables referenced in `tailwind.config.js`. This approach provides:
- Runtime theme switching (dark mode without rebuild)
- Single source of truth for design values
- Tailwind utility class integration
- Good browser support (97%+ globally)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|-----------------|
| Tailwind-only (no CSS vars) | No runtime theme switching, rebuild required for theme changes |
| CSS-in-JS (Styled Components) | Major architectural change, increases bundle size |
| Design token platform (Style Dictionary) | Over-engineering for ~45 components |

### Token Structure

```css
/* Semantic layers (recommended structure) */
:root {
  /* Primitives - raw values */
  --color-blue-500: #3b82f6;
  --color-neutral-900: #0f172a;

  /* Semantic - purpose-based */
  --color-primary: var(--color-blue-500);
  --color-text-primary: var(--color-neutral-900);

  /* Component - specific use */
  --button-bg-primary: var(--color-primary);
  --button-text-primary: white;
}
```

### Migration Path

1. Audit existing `globals.css` and `tailwind.config.js`
2. Extract all color/spacing/typography values
3. Create `design-tokens.css` with semantic layer
4. Update Tailwind config to reference new tokens
5. Deprecate legacy aliases (accent, semantic-error, etc.)
6. Update components incrementally

---

## 2. Responsive Data Table Patterns

### Decision: Stacked Cards on Mobile + Horizontal Scroll for Complex Tables

**Rationale**: Legal data (cases, evidence) has many columns. Two patterns work best:
- **Simple tables (≤4 columns)**: Stack into cards on mobile
- **Complex tables (>4 columns)**: Horizontal scroll with sticky first column

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|-----------------|
| Hide columns on mobile | Users lose access to important data |
| Accordion rows | Poor scannability for list views |
| Force landscape orientation | Poor UX, users rarely comply |

### Implementation Pattern

```tsx
// Responsive table wrapper
<div className="overflow-x-auto md:overflow-visible">
  {/* Desktop: Standard table */}
  <table className="hidden md:table w-full">
    {/* ... */}
  </table>

  {/* Mobile: Stacked cards */}
  <div className="md:hidden space-y-4">
    {items.map(item => (
      <Card key={item.id}>
        <CardHeader>{item.title}</CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-2">
            <dt>Status</dt><dd>{item.status}</dd>
            {/* ... */}
          </dl>
        </CardContent>
      </Card>
    ))}
  </div>
</div>
```

### Breakpoint Strategy

| Viewport | Behavior |
|----------|----------|
| < 640px (sm) | Stacked cards or single column |
| 640-768px (md) | Simplified table or 2-column cards |
| ≥ 768px | Full table view |

---

## 3. WCAG 2.1 AA Accessibility

### Decision: Comprehensive Implementation with axe-core Testing

**Rationale**: Legal applications must be accessible (potential ADA requirements for law firms). WCAG 2.1 AA is the industry standard for web applications.

**Key Requirements**:

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 1.4.3 Contrast | 4.5:1 text, 3:1 UI | Design token colors with verified contrast |
| 2.1.1 Keyboard | All functionality via keyboard | Focus management, tab order |
| 2.4.7 Focus Visible | Visible focus indicator | `focus-visible:ring-2` on all interactive |
| 4.1.2 Name, Role, Value | Proper ARIA | Semantic HTML, aria-label where needed |

### Focus Management Pattern

```tsx
// Modal focus trap
const Modal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      // Save previous focus
      const previousFocus = document.activeElement;

      // Focus first focusable element
      modalRef.current?.querySelector('button, [href], input')?.focus();

      return () => {
        // Restore focus on close
        (previousFocus as HTMLElement)?.focus();
      };
    }
  }, [isOpen]);

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {children}
    </div>
  );
};
```

### Testing Strategy

1. **Automated**: jest-axe for unit tests, Playwright + axe-core for E2E
2. **Manual**: Keyboard navigation walkthrough on all pages
3. **Screen Reader**: VoiceOver (Mac) testing on key flows

---

## 4. Loading State Patterns

### Decision: Skeleton Loaders + Spinner for Actions

**Rationale**: Different loading contexts need different feedback:
- **Page/data loading**: Skeleton loaders (shows structure, reduces perceived wait)
- **User actions**: Spinners (clear feedback that action is processing)
- **Long operations**: Progress indicators (evidence upload, AI processing)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|-----------------|
| Spinners only | Jarring layout shifts when content loads |
| Blur/dim overlay | Feels sluggish, hides content structure |
| No loading state | Users don't know if action worked |

### Skeleton Component Pattern

```tsx
// Reusable skeleton with animation
const Skeleton = ({ className }: { className?: string }) => (
  <div
    className={cn(
      "animate-pulse rounded-md bg-neutral-200 dark:bg-neutral-700",
      className
    )}
    aria-hidden="true"
  />
);

// Skeleton variants
const CaseCardSkeleton = () => (
  <div className="p-4 border rounded-lg">
    <Skeleton className="h-6 w-3/4 mb-2" />
    <Skeleton className="h-4 w-1/2 mb-4" />
    <div className="flex gap-2">
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-8 w-20" />
    </div>
  </div>
);
```

### Loading State Hierarchy

| Context | Component | Duration Threshold |
|---------|-----------|-------------------|
| Page load | Page skeleton | 0ms (immediate) |
| Data fetch | Content skeleton | 200ms delay (prevent flash) |
| Button action | Inline spinner | 0ms (immediate) |
| File upload | Progress bar | 0ms with % |
| AI processing | Progress + status text | 0ms with stage info |

---

## 5. Empty State UX

### Decision: Contextual Empty States with Clear CTAs

**Rationale**: Empty states are key onboarding moments. They should:
- Explain what would normally appear
- Guide users on how to populate the view
- Feel helpful, not broken

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|-----------------|
| Generic "No data" message | Not helpful, feels like error |
| Auto-redirect to create | Confusing if user intentionally has no data |
| Hide empty sections | User doesn't know feature exists |

### Empty State Component Pattern

```tsx
interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const EmptyState = ({ icon: Icon, title, description, action }: EmptyStateProps) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    <div className="rounded-full bg-neutral-100 p-4 mb-4">
      <Icon className="h-8 w-8 text-neutral-400" />
    </div>
    <h3 className="text-lg font-medium text-neutral-900 mb-2">{title}</h3>
    <p className="text-neutral-500 max-w-sm mb-6">{description}</p>
    {action && (
      <Button onClick={action.onClick}>
        {action.label}
      </Button>
    )}
  </div>
);
```

### Contextual Messages

| Page | Title | Description | CTA |
|------|-------|-------------|-----|
| Cases list | 아직 배정된 사건이 없습니다 | 새 사건을 생성하거나 관리자에게 사건 배정을 요청하세요. | 새 사건 만들기 |
| Evidence | 아직 증거가 없습니다 | 이미지, 오디오, 문서 등의 증거 자료를 업로드하세요. | 증거 업로드 |
| Drafts | 생성된 초안이 없습니다 | 증거 분석을 바탕으로 AI가 초안을 작성합니다. | 초안 생성 |
| Search results | 검색 결과가 없습니다 | 다른 검색어로 다시 시도해보세요. | (none) |

---

## Summary

All research topics resolved. No NEEDS CLARIFICATION items remain.

| Topic | Decision | Key Artifact |
|-------|----------|--------------|
| Design Tokens | CSS vars + Tailwind extend | design-tokens.css |
| Responsive Tables | Cards on mobile + scroll for complex | ResponsiveTable component |
| Accessibility | WCAG 2.1 AA with axe-core | Focus management, ARIA patterns |
| Loading States | Skeleton + spinner hybrid | Skeleton components per page |
| Empty States | Contextual with CTAs | EmptyState component |

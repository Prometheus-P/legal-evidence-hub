# Implementation Plan: UI Upgrade

**Branch**: `013-ui-upgrade` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-ui-upgrade/spec.md`

## Summary

Upgrade the Core Lawyer Portal UI to achieve design consistency, mobile responsiveness, comprehensive loading/empty states, and WCAG 2.1 AA accessibility compliance. This frontend-only feature builds on the existing CSS variable-based design token system and Tailwind CSS infrastructure, focusing on ~45 components across cases, evidence, drafts, relationship graphs, and shared UI elements.

## Technical Context

**Language/Version**: TypeScript 5.x
**Primary Dependencies**: Next.js 14, React 18, Tailwind CSS, Lucide-React, clsx, tailwind-merge
**Storage**: N/A (frontend-only, no new data persistence)
**Testing**: Jest + React Testing Library (unit/component), Playwright (E2E), axe-core (accessibility)
**Target Platform**: Web - modern browsers (Chrome, Firefox, Safari, Edge latest 2 versions)
**Project Type**: Web application (frontend focus)
**Performance Goals**: N/A (visual/UX upgrade, no performance-critical changes)
**Constraints**: WCAG 2.1 AA compliance, 320px-1920px viewport support, 44x44px minimum touch targets
**Scale/Scope**: ~45 components in Core Lawyer Portal (cases, evidence, drafts, relationships, shared)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applicable | Status | Notes |
|-----------|------------|--------|-------|
| I. Evidence Integrity | No | N/A | Frontend visual changes only, no evidence handling changes |
| II. Case Isolation | No | N/A | No data layer changes |
| III. No Auto-Submit | No | N/A | UI styling only, no submission logic changes |
| IV. AWS-Only Storage | No | N/A | No storage changes |
| V. Clean Architecture | Partial | PASS | Frontend component organization follows existing patterns |
| VI. Branch Protection | Yes | PASS | Working on feature branch `013-ui-upgrade` |
| VII. TDD Cycle | Yes | PASS | Will write accessibility/component tests first |
| VIII. Semantic Versioning | Yes | PASS | Minor version bump (new features, backward-compatible) |
| Tech Stack | Yes | PASS | Next.js 14, TypeScript, Tailwind CSS (no changes) |
| Testing Requirements | Yes | PASS | Jest + RTL, Playwright for E2E, axe-core for a11y |

**Gate Status**: PASS - No violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/013-ui-upgrade/
├── plan.md              # This file
├── research.md          # Phase 0 output - design patterns research
├── data-model.md        # Phase 1 output - design token structure
├── quickstart.md        # Phase 1 output - dev setup guide
├── contracts/           # Phase 1 output - component interface specs
│   └── components.md    # Component prop interfaces
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/lawyer/              # Lawyer portal pages (~26 files)
│   │   ├── cases/               # Case list, detail, assets, relations
│   │   ├── dashboard/           # Dashboard with loading state
│   │   ├── calendar/            # Calendar page
│   │   ├── messages/            # Messages page
│   │   └── layout.tsx           # Portal layout wrapper
│   │
│   ├── components/              # Reusable components
│   │   ├── cases/               # Case-specific (6 files)
│   │   ├── evidence/            # Evidence management (7 files)
│   │   ├── draft/               # Draft generation (5 files)
│   │   ├── relationship/        # Relationship graph (6 files)
│   │   ├── shared/              # Cross-feature (15+ files)
│   │   └── primitives/          # Base components (5 files)
│   │
│   ├── styles/
│   │   ├── globals.css          # CSS variables, base styles
│   │   └── design-tokens.css    # Design token definitions (NEW)
│   │
│   └── hooks/                   # Custom hooks (no changes expected)
│
├── tailwind.config.js           # Design token integration
└── __tests__/                   # Component and E2E tests
    ├── components/              # Component unit tests
    └── e2e/                     # Playwright E2E tests
```

**Structure Decision**: Existing Next.js App Router structure preserved. New design-tokens.css file added to consolidate CSS variables. No structural changes to component organization.

## Complexity Tracking

> No Constitution Check violations to justify.

N/A - All gates passed without violations.

## Component Inventory

### Priority 1: Primitives (Foundation)

| Component | Path | Status | Changes Needed |
|-----------|------|--------|----------------|
| Button | primitives/Button | Partial | Complete variant coverage, a11y audit |
| Input | primitives/Input | TBD | Create or enhance with design tokens |
| Modal | primitives/Modal | TBD | Focus trap, a11y, responsive |
| Spinner | primitives/Spinner | Done | Minor design token alignment |
| IconButton | primitives/IconButton | TBD | Touch target size, a11y |

### Priority 2: Shared Components

| Component | Path | Status | Changes Needed |
|-----------|------|--------|----------------|
| EmptyStates | shared/EmptyStates | Exists | Enhance with contextual messaging |
| LoadingSkeletons | shared/LoadingSkeletons | Exists | Add more variants for tables/cards |
| ThemeToggle | shared/ThemeToggle | Exists | Smooth transition, persist pref |
| PortalSidebar | shared/PortalSidebar | Exists | Mobile responsive drawer |
| ErrorBoundary | shared/ErrorBoundary | Exists | Better error UI, retry action |

### Priority 3: Feature Components

| Domain | Component Count | Key Focus |
|--------|-----------------|-----------|
| Cases | 6 | CaseCard responsive, CaseModal a11y |
| Evidence | 7 | DataTable responsive, Upload feedback |
| Draft | 5 | Editor a11y, Preview mobile |
| Relationship | 6 | Flow mobile view, Node touch targets |

## Implementation Phases

### Phase 1: Design Token Consolidation (P1 - Design Consistency)
- Audit existing CSS variables and Tailwind config
- Create unified design-tokens.css
- Remove legacy color aliases
- Document token usage guidelines

### Phase 2: Primitive Component Upgrade (P1 - Foundation)
- Enhance Button, Input, Modal with full design token coverage
- Add loading states to all interactive primitives
- Ensure WCAG 2.1 AA compliance (focus, contrast, labels)

### Phase 3: Responsive Layout (P2 - Mobile)
- Implement responsive sidebar (drawer on mobile)
- Create responsive data table pattern
- Add mobile-specific empty states

### Phase 4: Loading & Empty States (P3)
- Standardize skeleton loaders across all pages
- Create contextual empty state components
- Add error state UI with retry actions

### Phase 5: Accessibility Audit (P2)
- Run automated axe-core tests
- Manual keyboard navigation testing
- Screen reader testing on key flows
- Fix identified issues

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing styles | Medium | High | Incremental changes, visual regression tests |
| Scope creep to non-portal areas | Low | Medium | Strict scope enforcement to lawyer portal |
| Accessibility false negatives | Medium | Medium | Combine automated + manual testing |
| Mobile layout edge cases | Medium | Low | Device testing matrix, progressive enhancement |

## Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Legacy color usage | 0 instances | grep for legacy aliases |
| Accessibility violations | 0 critical/serious | axe-core automated tests |
| Mobile usability | All core flows work | Manual testing on 320px viewport |
| Theme switch | No flash | Visual inspection |
| Component test coverage | 80%+ | Jest coverage report |

# Component Interface Contracts

**Feature**: 013-ui-upgrade | **Date**: 2025-12-17

> This document defines the TypeScript interfaces for UI components being upgraded or created.

## Primitive Components

### Button

```typescript
// components/primitives/Button/Button.tsx
import { ButtonHTMLAttributes, ReactNode } from 'react';

export type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'ghost'
  | 'destructive'
  | 'outline';

export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual variant of the button */
  variant?: ButtonVariant;
  /** Size of the button */
  size?: ButtonSize;
  /** Shows loading spinner and disables button */
  isLoading?: boolean;
  /** Loading text for screen readers */
  loadingText?: string;
  /** Icon to display before children */
  leftIcon?: ReactNode;
  /** Icon to display after children */
  rightIcon?: ReactNode;
  /** Makes button full width */
  fullWidth?: boolean;
  /** Button content */
  children: ReactNode;
}
```

### Input

```typescript
// components/primitives/Input/Input.tsx
import { InputHTMLAttributes, ReactNode } from 'react';

export type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Size of the input */
  size?: InputSize;
  /** Label text (required for accessibility) */
  label: string;
  /** Hide label visually but keep for screen readers */
  hideLabel?: boolean;
  /** Helper text below input */
  helperText?: string;
  /** Error message (shows error state when provided) */
  error?: string;
  /** Icon to display at start of input */
  leftIcon?: ReactNode;
  /** Icon to display at end of input */
  rightIcon?: ReactNode;
  /** Makes input full width */
  fullWidth?: boolean;
}
```

### Modal

```typescript
// components/primitives/Modal/Modal.tsx
import { ReactNode } from 'react';

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

export interface ModalProps {
  /** Controls modal visibility */
  isOpen: boolean;
  /** Callback when modal should close */
  onClose: () => void;
  /** Modal title (required for accessibility) */
  title: string;
  /** Modal description for screen readers */
  description?: string;
  /** Size of the modal */
  size?: ModalSize;
  /** Modal content */
  children: ReactNode;
  /** Footer content (typically buttons) */
  footer?: ReactNode;
  /** Close modal on overlay click */
  closeOnOverlayClick?: boolean;
  /** Close modal on Escape key */
  closeOnEscape?: boolean;
  /** Prevent body scroll when modal is open */
  blockScroll?: boolean;
}
```

### Spinner

```typescript
// components/primitives/Spinner/Spinner.tsx
export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg';

export interface SpinnerProps {
  /** Size of the spinner */
  size?: SpinnerSize;
  /** Accessible label for screen readers */
  label?: string;
  /** Additional CSS classes */
  className?: string;
}
```

### IconButton

```typescript
// components/primitives/IconButton/IconButton.tsx
import { ButtonHTMLAttributes, ReactNode } from 'react';

export type IconButtonVariant = 'default' | 'ghost' | 'outline';
export type IconButtonSize = 'sm' | 'md' | 'lg';

export interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Icon element to display */
  icon: ReactNode;
  /** Accessible label (required) */
  'aria-label': string;
  /** Visual variant */
  variant?: IconButtonVariant;
  /** Size of the button */
  size?: IconButtonSize;
  /** Shows loading state */
  isLoading?: boolean;
}
```

---

## Shared Components

### EmptyState

```typescript
// components/shared/EmptyState.tsx
import { LucideIcon } from 'lucide-react';
import { ReactNode } from 'react';

export interface EmptyStateProps {
  /** Icon to display */
  icon: LucideIcon;
  /** Title text */
  title: string;
  /** Description text */
  description: string;
  /** Primary action button */
  action?: {
    label: string;
    onClick: () => void;
    icon?: LucideIcon;
  };
  /** Secondary action link */
  secondaryAction?: {
    label: string;
    href: string;
  };
  /** Custom content below description */
  children?: ReactNode;
}
```

### Skeleton

```typescript
// components/shared/Skeleton.tsx
export interface SkeletonProps {
  /** Width of skeleton (CSS value) */
  width?: string | number;
  /** Height of skeleton (CSS value) */
  height?: string | number;
  /** Border radius variant */
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
  /** Additional CSS classes */
  className?: string;
}

// Pre-built skeleton variants
export interface CardSkeletonProps {
  /** Show image placeholder */
  showImage?: boolean;
  /** Number of text lines */
  lines?: number;
}

export interface TableRowSkeletonProps {
  /** Number of columns */
  columns: number;
}

export interface ListSkeletonProps {
  /** Number of items to show */
  count?: number;
  /** Skeleton item variant */
  variant?: 'simple' | 'detailed';
}
```

### LoadingOverlay

```typescript
// components/shared/LoadingOverlay.tsx
export interface LoadingOverlayProps {
  /** Show the overlay */
  isLoading: boolean;
  /** Loading message */
  message?: string;
  /** Show progress percentage */
  progress?: number;
  /** Make overlay opaque (vs semi-transparent) */
  opaque?: boolean;
}
```

### ErrorState

```typescript
// components/shared/ErrorState.tsx
import { LucideIcon } from 'lucide-react';

export interface ErrorStateProps {
  /** Error title */
  title: string;
  /** Error description */
  description: string;
  /** Custom icon (default: AlertCircle) */
  icon?: LucideIcon;
  /** Retry callback */
  onRetry?: () => void;
  /** Retry button text */
  retryLabel?: string;
  /** Technical error details (collapsible) */
  details?: string;
}
```

### ThemeToggle

```typescript
// components/shared/ThemeToggle.tsx
export interface ThemeToggleProps {
  /** Current theme */
  theme: 'light' | 'dark' | 'system';
  /** Callback when theme changes */
  onThemeChange: (theme: 'light' | 'dark' | 'system') => void;
  /** Show labels */
  showLabel?: boolean;
  /** Size variant */
  size?: 'sm' | 'md';
}
```

### ResponsiveTable

```typescript
// components/shared/ResponsiveTable.tsx
import { ReactNode } from 'react';

export interface Column<T> {
  /** Unique column key */
  key: string;
  /** Column header text */
  header: string;
  /** Render cell content */
  cell: (row: T) => ReactNode;
  /** Show on mobile (default: first 2-3 columns) */
  mobileVisible?: boolean;
  /** Column width (CSS value) */
  width?: string;
  /** Enable sorting */
  sortable?: boolean;
}

export interface ResponsiveTableProps<T> {
  /** Table data */
  data: T[];
  /** Column definitions */
  columns: Column<T>[];
  /** Unique key for each row */
  getRowKey: (row: T) => string;
  /** Loading state */
  isLoading?: boolean;
  /** Empty state content */
  emptyState?: ReactNode;
  /** Error state content */
  errorState?: ReactNode;
  /** Mobile card render (override default) */
  renderMobileCard?: (row: T) => ReactNode;
  /** Sort state */
  sortBy?: string;
  /** Sort direction */
  sortDirection?: 'asc' | 'desc';
  /** Sort change callback */
  onSortChange?: (key: string, direction: 'asc' | 'desc') => void;
}
```

---

## Feature Components

### CaseCard

```typescript
// components/cases/CaseCard.tsx
export interface CaseCardProps {
  /** Case data */
  case: {
    id: string;
    title: string;
    status: 'active' | 'pending' | 'closed';
    clientName: string;
    createdAt: string;
    updatedAt: string;
    evidenceCount: number;
  };
  /** Click handler */
  onClick?: () => void;
  /** Show actions menu */
  showActions?: boolean;
  /** Compact mode for list views */
  compact?: boolean;
}
```

### EvidenceUpload

```typescript
// components/evidence/EvidenceUpload.tsx
export interface EvidenceUploadProps {
  /** Case ID to upload to */
  caseId: string;
  /** Accepted file types */
  acceptedTypes?: string[];
  /** Max file size in bytes */
  maxSize?: number;
  /** Allow multiple files */
  multiple?: boolean;
  /** Upload progress callback */
  onProgress?: (progress: number) => void;
  /** Upload complete callback */
  onComplete?: (evidenceIds: string[]) => void;
  /** Upload error callback */
  onError?: (error: Error) => void;
  /** Disable upload */
  disabled?: boolean;
}
```

### DataTable (Evidence/Cases)

```typescript
// components/evidence/EvidenceDataTable.tsx
export interface DataTableColumn<T> {
  id: string;
  header: string;
  accessorKey?: keyof T;
  cell?: (row: T) => ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  width?: string;
  minWidth?: string;
}

export interface DataTableProps<T> {
  /** Table data */
  data: T[];
  /** Column definitions */
  columns: DataTableColumn<T>[];
  /** Loading state */
  isLoading?: boolean;
  /** Enable row selection */
  selectable?: boolean;
  /** Selected row IDs */
  selectedIds?: string[];
  /** Selection change callback */
  onSelectionChange?: (ids: string[]) => void;
  /** Pagination config */
  pagination?: {
    page: number;
    pageSize: number;
    totalCount: number;
    onPageChange: (page: number) => void;
    onPageSizeChange: (size: number) => void;
  };
  /** Search/filter value */
  searchValue?: string;
  /** Search change callback */
  onSearchChange?: (value: string) => void;
  /** Empty state component */
  emptyState?: ReactNode;
}
```

---

## Accessibility Requirements

All components MUST implement:

```typescript
// Shared accessibility props
interface AccessibilityProps {
  /** Unique ID for ARIA associations */
  id?: string;
  /** Accessible name if not provided by children */
  'aria-label'?: string;
  /** ID of element that labels this component */
  'aria-labelledby'?: string;
  /** ID of element that describes this component */
  'aria-describedby'?: string;
}

// Focus management for modals/dialogs
interface FocusManagementProps {
  /** Element to focus on open */
  initialFocusRef?: React.RefObject<HTMLElement>;
  /** Element to focus on close */
  finalFocusRef?: React.RefObject<HTMLElement>;
  /** Trap focus within component */
  trapFocus?: boolean;
}
```

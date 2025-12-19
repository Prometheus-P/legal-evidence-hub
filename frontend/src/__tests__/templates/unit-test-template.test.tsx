/**
 * Jest Unit Test Template
 * =========================
 *
 * Template for writing React component unit tests.
 * Copy and customize for your specific components.
 *
 * QA Framework v4.0 - Jest + React Testing Library
 *
 * Best Practices:
 * - Test behavior, not implementation
 * - Use accessible queries (getByRole, getByLabelText)
 * - Mock external dependencies
 * - Test user interactions with userEvent
 *
 * Usage:
 *   1. Copy to src/__tests__/components/YourComponent.test.tsx
 *   2. Import your actual component
 *   3. Implement test cases
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// ============================================================================
// Mock Setup
// ============================================================================

// Mock Next.js router
const mockPush = jest.fn();
const mockReplace = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/test-path',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock API calls - uncomment and replace with your actual API module
// jest.mock('@/lib/api/your-api', () => ({
//   fetchData: jest.fn(),
//   submitData: jest.fn(),
// }));

// ============================================================================
// Sample Component (replace with your actual component import)
// ============================================================================

interface SampleComponentProps {
  title: string;
  onSubmit: (data: { value: string }) => void;
  isLoading?: boolean;
}

const SampleComponent: React.FC<SampleComponentProps> = ({
  title,
  onSubmit,
  isLoading = false,
}) => {
  const [value, setValue] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ value });
  };

  return (
    <form onSubmit={handleSubmit} aria-label="sample form">
      <h1>{title}</h1>
      <label htmlFor="input-field">
        Input Field
        <input
          id="input-field"
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={isLoading}
        />
      </label>
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Submit'}
      </button>
    </form>
  );
};

// ============================================================================
// Test Utilities
// ============================================================================

/**
 * Render component with common wrappers.
 * Add providers (ThemeProvider, QueryClientProvider, etc.) as needed.
 */
function renderComponent(props: Partial<SampleComponentProps> = {}) {
  const defaultProps: SampleComponentProps = {
    title: 'Test Title',
    onSubmit: jest.fn(),
    isLoading: false,
  };

  const mergedProps = { ...defaultProps, ...props };

  return {
    ...render(<SampleComponent {...mergedProps} />),
    props: mergedProps,
  };
}

// ============================================================================
// Tests
// ============================================================================

describe('SampleComponent', () => {
  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // ============================================================================
  // Rendering Tests
  // ============================================================================

  describe('Rendering', () => {
    it('should render the title', () => {
      renderComponent({ title: 'My Title' });

      expect(screen.getByRole('heading', { name: 'My Title' })).toBeInTheDocument();
    });

    it('should render input field', () => {
      renderComponent();

      expect(screen.getByLabelText(/input field/i)).toBeInTheDocument();
    });

    it('should render submit button', () => {
      renderComponent();

      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
    });

    it('should render with default props', () => {
      renderComponent();

      expect(screen.getByRole('form')).toBeInTheDocument();
    });
  });

  // ============================================================================
  // User Interaction Tests
  // ============================================================================

  describe('User Interactions', () => {
    it('should update input value when user types', async () => {
      const user = userEvent.setup();
      renderComponent();

      const input = screen.getByLabelText(/input field/i);
      await user.type(input, 'test value');

      expect(input).toHaveValue('test value');
    });

    it('should call onSubmit with form data when submitted', async () => {
      const user = userEvent.setup();
      const mockOnSubmit = jest.fn();
      renderComponent({ onSubmit: mockOnSubmit });

      const input = screen.getByLabelText(/input field/i);
      await user.type(input, 'submitted value');

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith({ value: 'submitted value' });
      expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    });

    it('should submit form on Enter key press', async () => {
      const user = userEvent.setup();
      const mockOnSubmit = jest.fn();
      renderComponent({ onSubmit: mockOnSubmit });

      const input = screen.getByLabelText(/input field/i);
      await user.type(input, 'enter test{Enter}');

      expect(mockOnSubmit).toHaveBeenCalled();
    });
  });

  // ============================================================================
  // Loading State Tests
  // ============================================================================

  describe('Loading State', () => {
    it('should disable input when loading', () => {
      renderComponent({ isLoading: true });

      expect(screen.getByLabelText(/input field/i)).toBeDisabled();
    });

    it('should disable submit button when loading', () => {
      renderComponent({ isLoading: true });

      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('should show loading text in button when loading', () => {
      renderComponent({ isLoading: true });

      expect(screen.getByRole('button', { name: /loading/i })).toBeInTheDocument();
    });

    it('should show submit text when not loading', () => {
      renderComponent({ isLoading: false });

      expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
    });
  });

  // ============================================================================
  // Error State Tests
  // ============================================================================

  describe('Error States', () => {
    it('should handle empty submission gracefully', async () => {
      const user = userEvent.setup();
      const mockOnSubmit = jest.fn();
      renderComponent({ onSubmit: mockOnSubmit });

      // Submit without entering any value
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Should still call onSubmit (validation is component's responsibility)
      expect(mockOnSubmit).toHaveBeenCalledWith({ value: '' });
    });
  });

  // ============================================================================
  // Accessibility Tests
  // ============================================================================

  describe('Accessibility', () => {
    it('should have accessible form label', () => {
      renderComponent();

      expect(screen.getByRole('form', { name: /sample form/i })).toBeInTheDocument();
    });

    it('should have accessible input label', () => {
      renderComponent();

      const input = screen.getByLabelText(/input field/i);
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('id', 'input-field');
    });

    it('should be focusable via keyboard', () => {
      renderComponent();

      const input = screen.getByLabelText(/input field/i);
      input.focus();

      expect(input).toHaveFocus();
    });
  });

  // ============================================================================
  // Async Operations Tests
  // ============================================================================

  describe('Async Operations', () => {
    it('should handle async operations with waitFor', async () => {
      const user = userEvent.setup();
      const mockOnSubmit = jest.fn().mockImplementation(() => {
        return new Promise((resolve) => setTimeout(resolve, 100));
      });
      renderComponent({ onSubmit: mockOnSubmit });

      const input = screen.getByLabelText(/input field/i);
      await user.type(input, 'async test');

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled();
      });
    });
  });
});

// ============================================================================
// Snapshot Tests (use sparingly)
// ============================================================================

describe('SampleComponent Snapshots', () => {
  it('should match snapshot in default state', () => {
    const { container } = renderComponent();
    expect(container).toMatchSnapshot();
  });

  it('should match snapshot in loading state', () => {
    const { container } = renderComponent({ isLoading: true });
    expect(container).toMatchSnapshot();
  });
});

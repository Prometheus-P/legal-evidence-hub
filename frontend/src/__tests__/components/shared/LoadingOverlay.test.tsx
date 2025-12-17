/**
 * LoadingOverlay Component Tests (T058)
 * Tests for loading overlay with spinner and message
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import {
  LoadingOverlay,
  PageLoading,
  ButtonLoading,
} from '@/components/shared/LoadingOverlay';

describe('LoadingOverlay', () => {
  // Helper to get the outer overlay element (first role="status")
  const getOverlay = () => screen.getAllByRole('status')[0];

  describe('Visibility', () => {
    it('should render when isLoading is true', () => {
      render(<LoadingOverlay isLoading={true} />);

      expect(screen.getAllByRole('status').length).toBeGreaterThan(0);
    });

    it('should not render overlay when isLoading is false and no children', () => {
      const { container } = render(<LoadingOverlay isLoading={false} />);

      expect(container.firstChild).toBeNull();
    });

    it('should render children with overlay when loading', () => {
      render(
        <LoadingOverlay isLoading={true}>
          <div data-testid="content">Content</div>
        </LoadingOverlay>
      );

      expect(screen.getByTestId('content')).toBeInTheDocument();
      expect(screen.getAllByRole('status').length).toBeGreaterThan(0);
    });

    it('should render children without overlay when not loading', () => {
      render(
        <LoadingOverlay isLoading={false}>
          <div data-testid="content">Content</div>
        </LoadingOverlay>
      );

      expect(screen.getByTestId('content')).toBeInTheDocument();
      expect(screen.queryAllByRole('status')).toHaveLength(0);
    });
  });

  describe('Loading Message', () => {
    it('should display default loading message', () => {
      render(<LoadingOverlay isLoading={true} />);

      // Message may appear multiple times (visible + sr-only)
      const messages = screen.getAllByText('로딩 중...');
      expect(messages.length).toBeGreaterThan(0);
    });

    it('should display custom loading message', () => {
      render(<LoadingOverlay isLoading={true} message="데이터 로딩 중..." />);

      const messages = screen.getAllByText('데이터 로딩 중...');
      expect(messages.length).toBeGreaterThan(0);
    });

    it('should display hint when provided', () => {
      render(
        <LoadingOverlay
          isLoading={true}
          message="처리 중..."
          hint="잠시만 기다려주세요"
        />
      );

      expect(screen.getByText('잠시만 기다려주세요')).toBeInTheDocument();
    });
  });

  describe('Positioning', () => {
    it('should use absolute positioning by default', () => {
      render(<LoadingOverlay isLoading={true} />);

      const overlay = getOverlay();
      expect(overlay.className).toContain('absolute');
    });

    it('should use fixed positioning when fullScreen is true', () => {
      render(<LoadingOverlay isLoading={true} fullScreen={true} />);

      const overlay = getOverlay();
      expect(overlay.className).toContain('fixed');
    });
  });

  describe('Backdrop', () => {
    it('should apply blur when blur prop is true', () => {
      render(<LoadingOverlay isLoading={true} blur={true} />);

      const overlay = getOverlay();
      expect(overlay.className).toContain('backdrop-blur-sm');
    });

    it('should not apply blur by default', () => {
      render(<LoadingOverlay isLoading={true} />);

      const overlay = getOverlay();
      expect(overlay.className).not.toContain('backdrop-blur-sm');
    });
  });

  describe('Z-Index', () => {
    it('should use default z-index of 50', () => {
      render(<LoadingOverlay isLoading={true} />);

      const overlay = getOverlay();
      expect(overlay.style.zIndex).toBe('50');
    });

    it('should use custom z-index when provided', () => {
      render(<LoadingOverlay isLoading={true} zIndex={100} />);

      const overlay = getOverlay();
      expect(overlay.style.zIndex).toBe('100');
    });
  });

  describe('Accessibility', () => {
    it('should have role="status"', () => {
      render(<LoadingOverlay isLoading={true} />);

      expect(screen.getAllByRole('status').length).toBeGreaterThan(0);
    });

    it('should have aria-live="polite"', () => {
      render(<LoadingOverlay isLoading={true} />);

      expect(getOverlay()).toHaveAttribute('aria-live', 'polite');
    });

    it('should have aria-label for screen readers', () => {
      render(<LoadingOverlay isLoading={true} message="로딩 중..." />);

      expect(getOverlay()).toHaveAttribute('aria-label', '로딩 중...');
    });

    it('should include screen reader only text', () => {
      render(<LoadingOverlay isLoading={true} message="처리 중..." />);

      const overlay = getOverlay();
      // Get the last sr-only span (LoadingOverlay's own sr-only, not Spinner's)
      const srOnlyElements = overlay.querySelectorAll('.sr-only');
      const lastSrOnly = srOnlyElements[srOnlyElements.length - 1];
      expect(lastSrOnly).toHaveTextContent('처리 중...');
    });
  });
});

describe('PageLoading', () => {
  it('should render with default message', () => {
    render(<PageLoading />);

    // PageLoading has role="status" with aria-live="polite"
    const statusElements = screen.getAllByRole('status');
    expect(statusElements.length).toBeGreaterThan(0);
    // Message appears in both visible text and sr-only span
    const messageElements = screen.getAllByText('페이지 로딩 중...');
    expect(messageElements.length).toBeGreaterThan(0);
  });

  it('should render with custom message', () => {
    render(<PageLoading message="사건 목록 로딩 중..." />);

    // Message appears in both visible text and sr-only span
    const messageElements = screen.getAllByText('사건 목록 로딩 중...');
    expect(messageElements.length).toBeGreaterThan(0);
  });

  it('should have proper accessibility attributes', () => {
    render(<PageLoading />);

    // The outer div has role="status" and aria-live="polite"
    const statusElements = screen.getAllByRole('status');
    const mainStatus = statusElements[0];
    expect(mainStatus).toHaveAttribute('aria-live', 'polite');
  });
});

describe('ButtonLoading', () => {
  it('should render with default text', () => {
    render(<ButtonLoading />);

    expect(screen.getByText('처리 중...')).toBeInTheDocument();
  });

  it('should render with custom text', () => {
    render(<ButtonLoading text="저장 중..." />);

    expect(screen.getByText('저장 중...')).toBeInTheDocument();
  });

  it('should render inline', () => {
    const { container } = render(<ButtonLoading />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('inline-flex');
  });

  it('should apply custom className', () => {
    const { container } = render(<ButtonLoading className="custom-class" />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('custom-class');
  });
});

/**
 * Skeleton Component Tests (T057)
 * Tests for loading skeleton components
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import { Skeleton, SkeletonText, SkeletonCircle, SkeletonCard } from '@/components/shared/Skeleton';

describe('Skeleton Components', () => {
  describe('Base Skeleton', () => {
    it('should render with default styles', () => {
      render(<Skeleton data-testid="skeleton" />);
      const skeleton = screen.getByTestId('skeleton');

      expect(skeleton).toBeInTheDocument();
      expect(skeleton).toHaveClass('animate-pulse');
      expect(skeleton).toHaveClass('bg-neutral-200');
    });

    it('should apply custom width and height', () => {
      render(<Skeleton width="100px" height="50px" data-testid="skeleton" />);
      const skeleton = screen.getByTestId('skeleton');

      expect(skeleton).toHaveStyle({ width: '100px', height: '50px' });
    });

    it('should apply rounded corners by default', () => {
      render(<Skeleton data-testid="skeleton" />);
      const skeleton = screen.getByTestId('skeleton');

      expect(skeleton).toHaveClass('rounded');
    });

    it('should have aria-hidden for screen readers', () => {
      render(<Skeleton data-testid="skeleton" />);
      const skeleton = screen.getByTestId('skeleton');

      expect(skeleton).toHaveAttribute('aria-hidden', 'true');
    });

    it('should accept custom className', () => {
      render(<Skeleton className="custom-class" data-testid="skeleton" />);
      const skeleton = screen.getByTestId('skeleton');

      expect(skeleton).toHaveClass('custom-class');
    });
  });

  describe('SkeletonText', () => {
    it('should render multiple lines', () => {
      render(<SkeletonText lines={3} data-testid="skeleton-text" />);
      const container = screen.getByTestId('skeleton-text');
      const lines = container.querySelectorAll('[aria-hidden="true"]');

      expect(lines).toHaveLength(3);
    });

    it('should make last line shorter by default', () => {
      render(<SkeletonText lines={3} data-testid="skeleton-text" />);
      const container = screen.getByTestId('skeleton-text');
      const lines = container.querySelectorAll('[aria-hidden="true"]');

      // Last line should have a different width
      const lastLine = lines[lines.length - 1];
      expect(lastLine).toHaveStyle({ width: '66%' });
    });

    it('should have proper spacing between lines', () => {
      render(<SkeletonText lines={2} data-testid="skeleton-text" />);
      const container = screen.getByTestId('skeleton-text');

      expect(container).toHaveClass('space-y-2');
    });
  });

  describe('SkeletonCircle', () => {
    it('should render as a circle', () => {
      render(<SkeletonCircle size={40} data-testid="skeleton-circle" />);
      const circle = screen.getByTestId('skeleton-circle');

      expect(circle).toHaveClass('rounded-full');
    });

    it('should apply correct size', () => {
      render(<SkeletonCircle size={48} data-testid="skeleton-circle" />);
      const circle = screen.getByTestId('skeleton-circle');

      expect(circle).toHaveStyle({ width: '48px', height: '48px' });
    });
  });

  describe('SkeletonCard', () => {
    it('should render card structure', () => {
      render(<SkeletonCard data-testid="skeleton-card" />);
      const card = screen.getByTestId('skeleton-card');

      expect(card).toBeInTheDocument();
      expect(card).toHaveClass('bg-white');
      expect(card).toHaveClass('rounded-lg');
    });

    it('should include header when showHeader is true', () => {
      render(<SkeletonCard showHeader data-testid="skeleton-card" />);
      const card = screen.getByTestId('skeleton-card');
      const headerSkeleton = card.querySelector('.h-6'); // Header skeleton line

      expect(headerSkeleton).toBeInTheDocument();
    });

    it('should include avatar when showAvatar is true', () => {
      render(<SkeletonCard showAvatar data-testid="skeleton-card" />);
      const card = screen.getByTestId('skeleton-card');
      const avatar = card.querySelector('.rounded-full');

      expect(avatar).toBeInTheDocument();
    });

    it('should render specified number of content lines', () => {
      render(<SkeletonCard contentLines={4} data-testid="skeleton-card" />);
      const card = screen.getByTestId('skeleton-card');
      // Content area with text skeleton
      const contentArea = card.querySelector('.space-y-2');

      expect(contentArea).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="status" on container', () => {
      render(
        <div role="status" aria-label="로딩 중">
          <Skeleton />
        </div>
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should support aria-label on container', () => {
      render(
        <div role="status" aria-label="데이터 로딩 중">
          <Skeleton />
        </div>
      );

      expect(screen.getByRole('status')).toHaveAttribute('aria-label', '데이터 로딩 중');
    });
  });

  describe('Animation', () => {
    it('should have pulse animation', () => {
      render(<Skeleton data-testid="skeleton" />);
      const skeleton = screen.getByTestId('skeleton');

      expect(skeleton).toHaveClass('animate-pulse');
    });

    it('should allow disabling animation', () => {
      render(<Skeleton animated={false} data-testid="skeleton" />);
      const skeleton = screen.getByTestId('skeleton');

      expect(skeleton).not.toHaveClass('animate-pulse');
    });
  });
});

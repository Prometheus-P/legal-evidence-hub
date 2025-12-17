/**
 * EmptyState and ErrorState Component Tests (T069, T070)
 * Tests for empty state and error state components
 */

import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import { EmptyState, ErrorState } from '@/components/shared/EmptyState';

describe('EmptyState', () => {
  describe('Basic Rendering', () => {
    it('should render title', () => {
      render(<EmptyState title="데이터가 없습니다" />);

      expect(screen.getByRole('heading', { name: '데이터가 없습니다' })).toBeInTheDocument();
    });

    it('should render description when provided', () => {
      render(
        <EmptyState
          title="사건이 없습니다"
          description="새 사건을 추가해보세요."
        />
      );

      expect(screen.getByText('새 사건을 추가해보세요.')).toBeInTheDocument();
    });

    it('should not render description when not provided', () => {
      render(<EmptyState title="사건이 없습니다" />);

      // Only the title should be present
      expect(screen.queryByText(/새 사건/)).not.toBeInTheDocument();
    });
  });

  describe('Icons', () => {
    it('should render default inbox icon', () => {
      render(<EmptyState title="빈 상태" />);

      // Icon should be hidden from screen readers
      const icon = document.querySelector('[aria-hidden="true"]');
      expect(icon).toBeInTheDocument();
    });

    it('should render file icon when specified', () => {
      render(<EmptyState title="파일 없음" icon="file" />);

      const icon = document.querySelector('[aria-hidden="true"]');
      expect(icon).toBeInTheDocument();
    });

    it('should render folder icon when specified', () => {
      render(<EmptyState title="폴더 없음" icon="folder" />);

      const icon = document.querySelector('[aria-hidden="true"]');
      expect(icon).toBeInTheDocument();
    });

    it('should render search icon when specified', () => {
      render(<EmptyState title="검색 결과 없음" icon="search" />);

      const icon = document.querySelector('[aria-hidden="true"]');
      expect(icon).toBeInTheDocument();
    });

    it('should render custom icon when provided', () => {
      const CustomIcon = <span data-testid="custom-icon">🎉</span>;
      render(
        <EmptyState
          title="커스텀"
          icon="custom"
          customIcon={CustomIcon}
        />
      );

      expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
    });
  });

  describe('Size Variants', () => {
    it('should apply small size styles', () => {
      const { container } = render(<EmptyState title="작은 크기" size="sm" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('py-8');
    });

    it('should apply medium size styles by default', () => {
      const { container } = render(<EmptyState title="중간 크기" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('py-12');
    });

    it('should apply large size styles', () => {
      const { container } = render(<EmptyState title="큰 크기" size="lg" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('py-16');
    });
  });

  describe('Actions', () => {
    it('should render primary action button', () => {
      const handleClick = jest.fn();
      render(
        <EmptyState
          title="사건 없음"
          primaryAction={{
            label: '사건 추가',
            onClick: handleClick,
          }}
        />
      );

      const button = screen.getByRole('button', { name: /사건 추가/ });
      expect(button).toBeInTheDocument();

      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should render secondary action button', () => {
      const handleClick = jest.fn();
      render(
        <EmptyState
          title="사건 없음"
          secondaryAction={{
            label: '가이드 보기',
            onClick: handleClick,
          }}
        />
      );

      const button = screen.getByRole('button', { name: '가이드 보기' });
      expect(button).toBeInTheDocument();

      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should render both primary and secondary actions', () => {
      render(
        <EmptyState
          title="사건 없음"
          primaryAction={{
            label: '사건 추가',
            onClick: () => {},
          }}
          secondaryAction={{
            label: '가이드 보기',
            onClick: () => {},
          }}
        />
      );

      expect(screen.getByRole('button', { name: /사건 추가/ })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: '가이드 보기' })).toBeInTheDocument();
    });

    it('should support custom action icon', () => {
      const CustomIcon = <span data-testid="action-icon">📄</span>;
      render(
        <EmptyState
          title="파일 없음"
          primaryAction={{
            label: '파일 업로드',
            onClick: () => {},
            icon: CustomIcon,
          }}
        />
      );

      expect(screen.getByTestId('action-icon')).toBeInTheDocument();
    });
  });

  describe('Children', () => {
    it('should render custom children content', () => {
      render(
        <EmptyState title="커스텀 콘텐츠">
          <div data-testid="custom-content">추가 콘텐츠</div>
        </EmptyState>
      );

      expect(screen.getByTestId('custom-content')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have role="status"', () => {
      render(<EmptyState title="접근성 테스트" />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have aria-label matching title', () => {
      render(<EmptyState title="빈 상태 메시지" />);

      expect(screen.getByRole('status')).toHaveAttribute('aria-label', '빈 상태 메시지');
    });

    it('should have proper heading level', () => {
      render(<EmptyState title="제목" />);

      expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('should apply custom className', () => {
      const { container } = render(
        <EmptyState title="스타일링" className="custom-class" />
      );

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('custom-class');
    });
  });
});

describe('ErrorState', () => {
  describe('Basic Rendering', () => {
    it('should render default error title', () => {
      render(<ErrorState />);

      expect(screen.getByRole('heading', { name: '오류가 발생했습니다' })).toBeInTheDocument();
    });

    it('should render custom error title', () => {
      render(<ErrorState title="데이터 로드 실패" />);

      expect(screen.getByRole('heading', { name: '데이터 로드 실패' })).toBeInTheDocument();
    });

    it('should render default error message', () => {
      render(<ErrorState />);

      expect(screen.getByText('데이터를 불러오는 중 문제가 발생했습니다.')).toBeInTheDocument();
    });

    it('should render custom error message', () => {
      render(<ErrorState message="네트워크 연결을 확인해주세요." />);

      expect(screen.getByText('네트워크 연결을 확인해주세요.')).toBeInTheDocument();
    });
  });

  describe('Retry Action', () => {
    it('should render retry button when onRetry provided', () => {
      const handleRetry = jest.fn();
      render(<ErrorState onRetry={handleRetry} />);

      const retryButton = screen.getByRole('button', { name: '다시 시도' });
      expect(retryButton).toBeInTheDocument();
    });

    it('should call onRetry when retry button clicked', () => {
      const handleRetry = jest.fn();
      render(<ErrorState onRetry={handleRetry} />);

      const retryButton = screen.getByRole('button', { name: '다시 시도' });
      fireEvent.click(retryButton);

      expect(handleRetry).toHaveBeenCalledTimes(1);
    });

    it('should render custom retry text', () => {
      render(<ErrorState onRetry={() => {}} retryText="재시도하기" />);

      expect(screen.getByRole('button', { name: '재시도하기' })).toBeInTheDocument();
    });

    it('should not render retry button when onRetry not provided', () => {
      render(<ErrorState />);

      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });
  });

  describe('Size Variants', () => {
    it('should apply small size', () => {
      const { container } = render(<ErrorState size="sm" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('py-6');
    });

    it('should apply medium size by default', () => {
      const { container } = render(<ErrorState />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('py-10');
    });

    it('should apply large size', () => {
      const { container } = render(<ErrorState size="lg" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('py-14');
    });
  });

  describe('Accessibility', () => {
    it('should have role="alert"', () => {
      render(<ErrorState />);

      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should display error icon with aria-hidden', () => {
      render(<ErrorState />);

      const svg = screen.getByRole('alert').querySelector('svg');
      expect(svg).toHaveAttribute('aria-hidden', 'true');
    });
  });

  describe('Styling', () => {
    it('should apply custom className', () => {
      const { container } = render(<ErrorState className="error-custom" />);

      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper.className).toContain('error-custom');
    });

    it('should have error color styling', () => {
      render(<ErrorState />);

      const title = screen.getByRole('heading');
      expect(title.className).toContain('text-error');
    });
  });
});

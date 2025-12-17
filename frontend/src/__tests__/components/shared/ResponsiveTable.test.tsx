/**
 * ResponsiveTable Component Tests (T046)
 * Tests for responsive table that switches to card view on mobile
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import { ResponsiveTable, ResponsiveTableColumn } from '@/components/shared/ResponsiveTable';

interface TestData {
  id: string;
  name: string;
  status: string;
  date: string;
}

const mockData: TestData[] = [
  { id: '1', name: 'Test Item 1', status: 'active', date: '2024-01-01' },
  { id: '2', name: 'Test Item 2', status: 'inactive', date: '2024-01-02' },
  { id: '3', name: 'Test Item 3', status: 'active', date: '2024-01-03' },
];

const columns: ResponsiveTableColumn<TestData>[] = [
  { key: 'name', header: '이름', primary: true },
  { key: 'status', header: '상태' },
  { key: 'date', header: '날짜' },
];

// Mock matchMedia for responsive tests
const mockMatchMedia = (matches: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query) => ({
      matches,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
};

describe('ResponsiveTable', () => {
  describe('Desktop View (>768px)', () => {
    beforeEach(() => {
      mockMatchMedia(false); // Not mobile
    });

    it('should render as a table on desktop', () => {
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
        />
      );

      // Should have table element
      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('should render table headers', () => {
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
        />
      );

      expect(screen.getByText('이름')).toBeInTheDocument();
      expect(screen.getByText('상태')).toBeInTheDocument();
      expect(screen.getByText('날짜')).toBeInTheDocument();
    });

    it('should render all data rows', () => {
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
        />
      );

      expect(screen.getByText('Test Item 1')).toBeInTheDocument();
      expect(screen.getByText('Test Item 2')).toBeInTheDocument();
      expect(screen.getByText('Test Item 3')).toBeInTheDocument();
    });

    it('should have accessible table structure', () => {
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
          caption="테스트 데이터 목록"
        />
      );

      const table = screen.getByRole('table');
      expect(table).toHaveAttribute('aria-label', '테스트 데이터 목록');
    });
  });

  describe('Mobile View (<=768px)', () => {
    beforeEach(() => {
      mockMatchMedia(true); // Is mobile
    });

    it('should render as cards on mobile', () => {
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
        />
      );

      // Should have card list
      const cardList = screen.getByRole('list');
      expect(cardList).toBeInTheDocument();
    });

    it('should render card items', () => {
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
        />
      );

      const items = screen.getAllByRole('listitem');
      expect(items).toHaveLength(3);
    });

    it('should highlight primary column in cards', () => {
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
        />
      );

      // Primary column (name) should be more prominent
      const primaryValues = screen.getAllByText(/Test Item/);
      expect(primaryValues).toHaveLength(3);
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria-label for table', () => {
      mockMatchMedia(false);
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
          caption="증거 목록"
        />
      );

      expect(screen.getByRole('table')).toHaveAttribute('aria-label', '증거 목록');
    });

    it('should have proper aria-label for card list', () => {
      mockMatchMedia(true);
      render(
        <ResponsiveTable
          data={mockData}
          columns={columns}
          keyExtractor={(item) => item.id}
          caption="증거 목록"
        />
      );

      expect(screen.getByRole('list')).toHaveAttribute('aria-label', '증거 목록');
    });
  });

  describe('Empty State', () => {
    it('should render empty message when no data', () => {
      mockMatchMedia(false);
      render(
        <ResponsiveTable
          data={[]}
          columns={columns}
          keyExtractor={(item) => item.id}
          emptyMessage="데이터가 없습니다"
        />
      );

      expect(screen.getByText('데이터가 없습니다')).toBeInTheDocument();
    });
  });

  describe('Custom Rendering', () => {
    it('should use custom render function for columns', () => {
      mockMatchMedia(false);
      const columnsWithRender: ResponsiveTableColumn<TestData>[] = [
        { key: 'name', header: '이름', primary: true },
        {
          key: 'status',
          header: '상태',
          render: (value) => (
            <span data-testid="custom-status">{value === 'active' ? '활성' : '비활성'}</span>
          ),
        },
      ];

      render(
        <ResponsiveTable
          data={mockData}
          columns={columnsWithRender}
          keyExtractor={(item) => item.id}
        />
      );

      const customStatuses = screen.getAllByTestId('custom-status');
      expect(customStatuses).toHaveLength(3);
      expect(customStatuses[0]).toHaveTextContent('활성');
    });
  });
});

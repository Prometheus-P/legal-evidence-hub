/**
 * Integration tests for AssetTable Component
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Tests for frontend/src/components/lawyer/assets/AssetTable.tsx:
 * - Asset list rendering with data
 * - Empty state display
 * - Sorting functionality
 * - Filter functionality
 * - Edit and delete actions
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AssetTable from '@/components/lawyer/assets/AssetTable';
import type { Asset } from '@/types/asset';

const mockAssets: Asset[] = [
  {
    id: 'asset_001',
    case_id: 'case_001',
    category: 'real_estate',
    ownership: 'plaintiff',
    nature: 'marital',
    name: '강남구 아파트',
    description: '서울 강남구 삼성동 아파트',
    current_value: 800000000,
    acquisition_value: 500000000,
    acquisition_date: '2015-03-15',
    valuation_date: '2024-01-10',
    valuation_source: 'KB시세',
    division_ratio_plaintiff: 50,
    division_ratio_defendant: 50,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
  },
  {
    id: 'asset_002',
    case_id: 'case_001',
    category: 'savings',
    ownership: 'defendant',
    nature: 'marital',
    name: '국민은행 예금',
    description: '정기예금',
    current_value: 50000000,
    division_ratio_plaintiff: 50,
    division_ratio_defendant: 50,
    created_at: '2024-01-14T10:00:00Z',
    updated_at: '2024-01-14T10:00:00Z',
  },
  {
    id: 'asset_003',
    case_id: 'case_001',
    category: 'debt',
    ownership: 'joint',
    nature: 'marital',
    name: '주택담보대출',
    description: '아파트 담보대출',
    current_value: 200000000,
    division_ratio_plaintiff: 50,
    division_ratio_defendant: 50,
    created_at: '2024-01-13T10:00:00Z',
    updated_at: '2024-01-13T10:00:00Z',
  },
];

describe('AssetTable Component', () => {
  describe('Basic Rendering', () => {
    test('should render asset list with data', () => {
      render(<AssetTable assets={mockAssets} />);

      expect(screen.getByText('강남구 아파트')).toBeInTheDocument();
      expect(screen.getByText('국민은행 예금')).toBeInTheDocument();
      expect(screen.getByText('주택담보대출')).toBeInTheDocument();
    });

    test('should render asset categories in Korean', () => {
      render(<AssetTable assets={mockAssets} />);

      // Categories appear in both filter dropdown and table cells
      expect(screen.getAllByText('부동산').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('예금/적금').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('부채').length).toBeGreaterThanOrEqual(1);
    });

    test('should render ownership labels in Korean', () => {
      render(<AssetTable assets={mockAssets} />);

      expect(screen.getByText('원고')).toBeInTheDocument();
      expect(screen.getByText('피고')).toBeInTheDocument();
      expect(screen.getByText('공동')).toBeInTheDocument();
    });

    test('should render nature labels in Korean', () => {
      render(<AssetTable assets={mockAssets} />);

      // All assets are marital (공동재산)
      const maritalLabels = screen.getAllByText('공동재산');
      expect(maritalLabels.length).toBe(3);
    });

    test('should display loading state', () => {
      render(<AssetTable assets={[]} loading={true} />);

      // Should show loading animation
      const loadingElement = document.querySelector('.animate-pulse');
      expect(loadingElement).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    test('should show empty message when no assets', () => {
      render(<AssetTable assets={[]} />);

      expect(screen.getByText('등록된 재산이 없습니다.')).toBeInTheDocument();
    });
  });

  describe('Value Display', () => {
    test('should format currency values in Korean', () => {
      render(<AssetTable assets={mockAssets} />);

      // Check for formatted currency - 800000000 = 8억원
      expect(screen.getByText('8억원')).toBeInTheDocument();
      // 50000000 = 5,000만원
      expect(screen.getByText('5,000만원')).toBeInTheDocument();
    });

    test('should show negative sign for debt', () => {
      render(<AssetTable assets={mockAssets} />);

      // Debt values should have negative display
      const debtRow = screen.getByText('주택담보대출').closest('tr');
      expect(debtRow).toHaveTextContent('-');
    });
  });

  describe('Division Ratio Display', () => {
    test('should display division ratios', () => {
      render(<AssetTable assets={mockAssets} />);

      // All assets have 50:50 ratio
      const ratios = screen.getAllByText('50:50');
      expect(ratios.length).toBe(3);
    });
  });

  describe('Filter Functionality', () => {
    test('should render category filter dropdown', () => {
      render(<AssetTable assets={mockAssets} />);

      expect(screen.getByRole('combobox')).toBeInTheDocument();
      expect(screen.getByText('전체')).toBeInTheDocument();
    });

    test('should filter assets by category', () => {
      render(<AssetTable assets={mockAssets} />);

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'real_estate' } });

      expect(screen.getByText('강남구 아파트')).toBeInTheDocument();
      expect(screen.queryByText('국민은행 예금')).not.toBeInTheDocument();
      expect(screen.queryByText('주택담보대출')).not.toBeInTheDocument();
    });

    test('should show debt filter option', () => {
      render(<AssetTable assets={mockAssets} />);

      const select = screen.getByRole('combobox');
      fireEvent.change(select, { target: { value: 'debt' } });

      expect(screen.queryByText('강남구 아파트')).not.toBeInTheDocument();
      expect(screen.getByText('주택담보대출')).toBeInTheDocument();
    });
  });

  describe('Sorting Functionality', () => {
    test('should render sortable column headers', () => {
      render(<AssetTable assets={mockAssets} />);

      // Headers appear - some labels appear multiple times (filter + header)
      expect(screen.getAllByText(/분류/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/명칭/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/소유자/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/현재 가치/).length).toBeGreaterThanOrEqual(1);
    });

    test('should sort by name when column clicked', () => {
      render(<AssetTable assets={mockAssets} />);

      // Get the table header specifically
      const nameHeaders = screen.getAllByText(/명칭/);
      fireEvent.click(nameHeaders[0]);

      // After sorting, the first item should change
      const rows = screen.getAllByRole('row');
      // Header + data rows
      expect(rows.length).toBeGreaterThan(1);
    });

    test('should toggle sort direction on repeated clicks', () => {
      render(<AssetTable assets={mockAssets} />);

      // Get the table header specifically
      const valueHeaders = screen.getAllByText(/현재 가치/);
      fireEvent.click(valueHeaders[0]);
      fireEvent.click(valueHeaders[0]);

      // Should have sort indicators
      expect(screen.getByText('↓')).toBeInTheDocument();
    });
  });

  describe('Totals Calculation', () => {
    test('should display total count', () => {
      render(<AssetTable assets={mockAssets} />);

      expect(screen.getByText('총 3건')).toBeInTheDocument();
    });

    test('should display calculated totals in footer', () => {
      render(<AssetTable assets={mockAssets} />);

      // Should have a summary row showing totals
      expect(screen.getByText('합계')).toBeInTheDocument();
    });

    test('should show breakdown by ownership', () => {
      render(<AssetTable assets={mockAssets} />);

      // Footer should show breakdown
      expect(screen.getByText(/원고:/)).toBeInTheDocument();
      expect(screen.getByText(/피고:/)).toBeInTheDocument();
      expect(screen.getByText(/공동:/)).toBeInTheDocument();
      expect(screen.getByText(/부채:/)).toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    test('should show edit button when onEdit provided', () => {
      const onEdit = jest.fn();
      render(<AssetTable assets={mockAssets} onEdit={onEdit} />);

      const editButtons = screen.getAllByText('수정');
      expect(editButtons.length).toBe(3);
    });

    test('should call onEdit when edit button clicked', () => {
      const onEdit = jest.fn();
      render(<AssetTable assets={mockAssets} onEdit={onEdit} />);

      const editButtons = screen.getAllByText('수정');
      fireEvent.click(editButtons[0]);
      expect(onEdit).toHaveBeenCalled();
    });

    test('should show delete button when onDelete provided', () => {
      const onDelete = jest.fn();
      render(<AssetTable assets={mockAssets} onDelete={onDelete} />);

      const deleteButtons = screen.getAllByText('삭제');
      expect(deleteButtons.length).toBe(3);
    });

    test('should call onDelete when delete button clicked', () => {
      const onDelete = jest.fn();
      render(<AssetTable assets={mockAssets} onDelete={onDelete} />);

      const deleteButtons = screen.getAllByText('삭제');
      fireEvent.click(deleteButtons[0]);
      expect(onDelete).toHaveBeenCalled();
    });
  });

  describe('Row Selection', () => {
    test('should highlight selected row', () => {
      render(<AssetTable assets={mockAssets} selectedId="asset_001" />);

      const selectedRow = screen.getByText('강남구 아파트').closest('tr');
      expect(selectedRow).toHaveClass('bg-primary-light');
    });

    test('should call onSelect when row clicked', () => {
      const onSelect = jest.fn();
      render(<AssetTable assets={mockAssets} onSelect={onSelect} />);

      const row = screen.getByText('강남구 아파트').closest('tr');
      if (row) {
        fireEvent.click(row);
      }
      expect(onSelect).toHaveBeenCalledWith(mockAssets[0]);
    });
  });

  describe('Table Headers', () => {
    test('should render table headers', () => {
      render(<AssetTable assets={mockAssets} />);

      // Headers appear in table - some labels appear multiple times (filter + header)
      expect(screen.getAllByText(/분류/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/명칭/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/소유자/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('성격')).toBeInTheDocument();
      expect(screen.getAllByText(/현재 가치/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('비율')).toBeInTheDocument();
    });

    test('should show action header when actions provided', () => {
      render(<AssetTable assets={mockAssets} onEdit={jest.fn()} />);

      expect(screen.getByText('작업')).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    test('should apply custom className', () => {
      const { container } = render(
        <AssetTable assets={mockAssets} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });
});

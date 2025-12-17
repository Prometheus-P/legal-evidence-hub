/**
 * Integration tests for AssetForm Component
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Tests for frontend/src/components/lawyer/assets/AssetForm.tsx:
 * - Form rendering
 * - Field validation
 * - Form submission
 * - Edit mode
 * - Division ratio sync
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AssetForm from '@/components/lawyer/assets/AssetForm';
import type { Asset } from '@/types/asset';

const mockAsset: Asset = {
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
  division_ratio_plaintiff: 60,
  division_ratio_defendant: 40,
  notes: '시세 상승',
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-15T10:00:00Z',
};

describe('AssetForm Component', () => {
  describe('Basic Rendering', () => {
    test('should render form with label texts', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      // Check that all labels are rendered
      expect(screen.getByText(/분류/)).toBeInTheDocument();
      expect(screen.getByText(/소유자/)).toBeInTheDocument();
      expect(screen.getByText(/재산 성격/)).toBeInTheDocument();
      expect(screen.getByText(/재산 명칭/)).toBeInTheDocument();
      expect(screen.getByText(/현재 가치/)).toBeInTheDocument();
      expect(screen.getByText(/설명/)).toBeInTheDocument();
    });

    test('should render category options in Korean', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      expect(screen.getByText('부동산')).toBeInTheDocument();
      expect(screen.getByText('예금/적금')).toBeInTheDocument();
      expect(screen.getByText('부채')).toBeInTheDocument();
    });

    test('should render ownership options in Korean', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      expect(screen.getByText('원고')).toBeInTheDocument();
      expect(screen.getByText('피고')).toBeInTheDocument();
      expect(screen.getByText('공동')).toBeInTheDocument();
      expect(screen.getByText('제3자')).toBeInTheDocument();
    });

    test('should render nature options in Korean', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      expect(screen.getByText('공동재산')).toBeInTheDocument();
      expect(screen.getByText('특유재산')).toBeInTheDocument();
      expect(screen.getByText('혼합재산')).toBeInTheDocument();
    });

    test('should render submit button with "추가" text for new asset', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      expect(screen.getByRole('button', { name: '추가' })).toBeInTheDocument();
    });

    test('should render submit button with "수정" text in edit mode', () => {
      render(<AssetForm asset={mockAsset} onSubmit={jest.fn()} />);

      expect(screen.getByRole('button', { name: '수정' })).toBeInTheDocument();
    });
  });

  describe('Default Values', () => {
    test('should have default division ratio as 50:50', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      const ratioInputs = screen.getAllByRole('spinbutton');
      expect(ratioInputs[0]).toHaveValue(50);
    });
  });

  describe('Edit Mode', () => {
    test('should populate form with asset data', () => {
      render(<AssetForm asset={mockAsset} onSubmit={jest.fn()} />);

      expect(screen.getByDisplayValue('강남구 아파트')).toBeInTheDocument();
      expect(screen.getByDisplayValue('800000000')).toBeInTheDocument();
      expect(screen.getByDisplayValue('500000000')).toBeInTheDocument();
      expect(screen.getByDisplayValue('KB시세')).toBeInTheDocument();
      expect(screen.getByDisplayValue('시세 상승')).toBeInTheDocument();
    });

    test('should populate division ratio from asset', () => {
      render(<AssetForm asset={mockAsset} onSubmit={jest.fn()} />);

      const ratioInputs = screen.getAllByRole('spinbutton');
      expect(ratioInputs[0]).toHaveValue(60);
      expect(ratioInputs[1]).toHaveValue(40);
    });
  });

  describe('Division Ratio Sync', () => {
    test('should auto-sync defendant ratio when plaintiff ratio changes', async () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      const ratioInputs = screen.getAllByRole('spinbutton');
      const plaintiffInput = ratioInputs[0];
      const defendantInput = ratioInputs[1];

      fireEvent.change(plaintiffInput, { target: { value: '70' } });

      await waitFor(() => {
        expect(defendantInput).toHaveValue(30);
      });
    });

    test('should keep defendant ratio read-only', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      const ratioInputs = screen.getAllByRole('spinbutton');
      const defendantInput = ratioInputs[1];

      expect(defendantInput).toHaveAttribute('readonly');
    });
  });

  describe('Form Validation', () => {
    test('should show error when required fields are empty', async () => {
      const onSubmit = jest.fn();
      render(<AssetForm onSubmit={onSubmit} />);

      const submitButton = screen.getByRole('button', { name: '추가' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('재산 명칭을 입력해 주세요.')).toBeInTheDocument();
      });
      expect(onSubmit).not.toHaveBeenCalled();
    });
  });

  describe('Form Submission', () => {
    test('should call onSubmit with form data', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<AssetForm onSubmit={onSubmit} />);

      const nameInput = screen.getByPlaceholderText('예: 강남구 아파트');
      fireEvent.change(nameInput, { target: { value: '신규 아파트' } });

      const valueInput = screen.getByPlaceholderText('500000000');
      fireEvent.change(valueInput, { target: { value: '500000000' } });

      const submitButton = screen.getByRole('button', { name: '추가' });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            name: '신규 아파트',
            current_value: 500000000,
          })
        );
      });
    });
  });

  describe('Cancel Button', () => {
    test('should render cancel button when onCancel provided', () => {
      render(<AssetForm onSubmit={jest.fn()} onCancel={jest.fn()} />);

      expect(screen.getByRole('button', { name: '취소' })).toBeInTheDocument();
    });

    test('should not render cancel button when onCancel not provided', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      expect(screen.queryByRole('button', { name: '취소' })).not.toBeInTheDocument();
    });

    test('should call onCancel when cancel button clicked', () => {
      const onCancel = jest.fn();
      render(<AssetForm onSubmit={jest.fn()} onCancel={onCancel} />);

      fireEvent.click(screen.getByRole('button', { name: '취소' }));
      expect(onCancel).toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    test('should show loading text on submit button', () => {
      render(<AssetForm onSubmit={jest.fn()} loading={true} />);

      expect(screen.getByRole('button', { name: '저장 중...' })).toBeInTheDocument();
    });

    test('should disable submit button when loading', () => {
      render(<AssetForm onSubmit={jest.fn()} loading={true} />);

      const submitButton = screen.getByRole('button', { name: '저장 중...' });
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Input Placeholders', () => {
    test('should show Korean placeholders', () => {
      render(<AssetForm onSubmit={jest.fn()} />);

      expect(screen.getByPlaceholderText('예: 강남구 아파트')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('500000000')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('300000000')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('예: KB시세, 한국감정원')).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    test('should apply custom className', () => {
      const { container } = render(
        <AssetForm onSubmit={jest.fn()} className="custom-class" />
      );

      expect(container.querySelector('form')).toHaveClass('custom-class');
    });
  });
});

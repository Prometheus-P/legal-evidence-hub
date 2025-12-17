/**
 * DetectiveForm Component Tests
 * 011-production-bug-fixes Feature - US2 (T058)
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DetectiveForm } from '@/components/lawyer/detectives/DetectiveForm';
import type { DetectiveContact } from '@/types/investigator';

const mockDetective: DetectiveContact = {
  id: '1',
  lawyerId: 'lawyer-1',
  name: '박탐정',
  phone: '010-1111-2222',
  email: 'park@detective.com',
  specialty: '불륜 조사',
  memo: '경력 10년 전문 탐정',
  createdAt: new Date().toISOString(),
};

describe('DetectiveForm', () => {
  const defaultProps = {
    onSubmit: jest.fn(),
    onCancel: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders add form title when no detective provided', () => {
      render(<DetectiveForm {...defaultProps} />);

      expect(screen.getByText('탐정 추가')).toBeInTheDocument();
    });

    it('renders edit form title when detective provided', () => {
      render(<DetectiveForm {...defaultProps} detective={mockDetective} />);

      expect(screen.getByText('탐정 수정')).toBeInTheDocument();
    });

    it('renders all form fields', () => {
      render(<DetectiveForm {...defaultProps} />);

      expect(screen.getByLabelText(/이름/)).toBeInTheDocument();
      expect(screen.getByLabelText(/전화번호/)).toBeInTheDocument();
      expect(screen.getByLabelText(/이메일/)).toBeInTheDocument();
      expect(screen.getByLabelText(/전문 분야/)).toBeInTheDocument();
      expect(screen.getByLabelText(/메모/)).toBeInTheDocument();
    });

    it('shows required indicator for name field', () => {
      render(<DetectiveForm {...defaultProps} />);

      const nameLabel = screen.getByText('이름');
      const requiredIndicator = nameLabel.parentElement?.querySelector('.text-red-500');
      expect(requiredIndicator).toBeInTheDocument();
      expect(requiredIndicator).toHaveTextContent('*');
    });

    it('renders specialty dropdown with options', () => {
      render(<DetectiveForm {...defaultProps} />);

      const specialtySelect = screen.getByLabelText(/전문 분야/);
      expect(specialtySelect).toBeInTheDocument();

      // Check for some specialty options
      expect(screen.getByText('선택하세요')).toBeInTheDocument();
      expect(screen.getByText('불륜 조사')).toBeInTheDocument();
      expect(screen.getByText('자산 추적')).toBeInTheDocument();
      expect(screen.getByText('실종자 수색')).toBeInTheDocument();
    });

    it('renders submit and cancel buttons', () => {
      render(<DetectiveForm {...defaultProps} />);

      expect(screen.getByText('추가')).toBeInTheDocument();
      expect(screen.getByText('취소')).toBeInTheDocument();
    });

    it('shows 수정 button in edit mode', () => {
      render(<DetectiveForm {...defaultProps} detective={mockDetective} />);

      expect(screen.getByText('수정')).toBeInTheDocument();
    });

    it('renders close button with aria-label', () => {
      render(<DetectiveForm {...defaultProps} />);

      const closeButton = screen.getByLabelText('닫기');
      expect(closeButton).toBeInTheDocument();
    });
  });

  describe('Specialty Options', () => {
    it('contains all specialty options', () => {
      render(<DetectiveForm {...defaultProps} />);

      const expectedSpecialties = [
        '불륜 조사',
        '자산 추적',
        '실종자 수색',
        '배경 조사',
        '보험 조사',
        '기업 조사',
        '기타',
      ];

      expectedSpecialties.forEach((specialty) => {
        expect(screen.getByText(specialty)).toBeInTheDocument();
      });
    });

    it('allows selecting a specialty', async () => {
      render(<DetectiveForm {...defaultProps} />);

      const specialtySelect = screen.getByLabelText(/전문 분야/);
      await userEvent.selectOptions(specialtySelect, '자산 추적');

      expect(specialtySelect).toHaveValue('자산 추적');
    });
  });

  describe('Edit Mode', () => {
    it('pre-fills form fields with detective data', () => {
      render(<DetectiveForm {...defaultProps} detective={mockDetective} />);

      expect(screen.getByDisplayValue('박탐정')).toBeInTheDocument();
      expect(screen.getByDisplayValue('010-1111-2222')).toBeInTheDocument();
      expect(screen.getByDisplayValue('park@detective.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('경력 10년 전문 탐정')).toBeInTheDocument();

      const specialtySelect = screen.getByLabelText(/전문 분야/);
      expect(specialtySelect).toHaveValue('불륜 조사');
    });

    it('handles detective with missing optional fields', () => {
      const minimalDetective: DetectiveContact = {
        id: '2',
        lawyerId: 'lawyer-1',
        name: '김탐정',
        createdAt: new Date().toISOString(),
      };

      render(<DetectiveForm {...defaultProps} detective={minimalDetective} />);

      expect(screen.getByDisplayValue('김탐정')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('shows error when name is empty', async () => {
      render(<DetectiveForm {...defaultProps} />);

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('이름을 입력하세요')).toBeInTheDocument();
      });
    });

    it('shows error when neither phone nor email is provided', async () => {
      render(<DetectiveForm {...defaultProps} />);

      const nameInput = screen.getByLabelText(/이름/);
      await userEvent.type(nameInput, '테스트');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getAllByText('전화번호 또는 이메일 중 하나는 필수입니다')).toHaveLength(2);
      });
    });

    it('shows error for invalid email format', async () => {
      render(<DetectiveForm {...defaultProps} />);

      const nameInput = screen.getByLabelText(/이름/);
      const emailInput = screen.getByLabelText(/이메일/);
      const form = nameInput.closest('form')!;

      await userEvent.type(nameInput, '테스트');
      await userEvent.type(emailInput, 'invalid-email');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('올바른 이메일 형식을 입력하세요')).toBeInTheDocument();
      });
    });

    it('shows error for invalid phone format', async () => {
      render(<DetectiveForm {...defaultProps} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);
      const form = nameInput.closest('form')!;

      await userEvent.type(nameInput, '테스트');
      await userEvent.type(phoneInput, 'abc-invalid');
      fireEvent.submit(form);

      await waitFor(() => {
        expect(screen.getByText('올바른 전화번호 형식을 입력하세요')).toBeInTheDocument();
      });
    });

    it('accepts valid phone number formats', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<DetectiveForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);

      await userEvent.type(nameInput, '테스트');
      await userEvent.type(phoneInput, '010-1234-5678');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled();
      });
    });

    it('accepts international phone formats', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<DetectiveForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);

      await userEvent.type(nameInput, '테스트');
      await userEvent.type(phoneInput, '+82-10-1234-5678');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled();
      });
    });

    it('accepts valid email format', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<DetectiveForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const emailInput = screen.getByLabelText(/이메일/);

      await userEvent.type(nameInput, '테스트');
      await userEvent.type(emailInput, 'test@example.com');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled();
      });
    });

    it('applies error styling to invalid fields', async () => {
      render(<DetectiveForm {...defaultProps} />);

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        const nameInput = screen.getByLabelText(/이름/);
        expect(nameInput).toHaveClass('border-red-500');
      });
    });
  });

  describe('Form Submission', () => {
    it('calls onSubmit with form data including specialty', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<DetectiveForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);
      const emailInput = screen.getByLabelText(/이메일/);
      const specialtySelect = screen.getByLabelText(/전문 분야/);
      const memoInput = screen.getByLabelText(/메모/);

      await userEvent.type(nameInput, '이탐정');
      await userEvent.type(phoneInput, '010-9876-5432');
      await userEvent.type(emailInput, 'lee@detective.com');
      await userEvent.selectOptions(specialtySelect, '자산 추적');
      await userEvent.type(memoInput, '전문 탐정');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          name: '이탐정',
          phone: '010-9876-5432',
          email: 'lee@detective.com',
          specialty: '자산 추적',
          memo: '전문 탐정',
        });
      });
    });

    it('trims whitespace from input values', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<DetectiveForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);

      await userEvent.type(nameInput, '  이탐정  ');
      await userEvent.type(phoneInput, '  010-9876-5432  ');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            name: '이탐정',
            phone: '010-9876-5432',
          })
        );
      });
    });

    it('excludes empty optional fields from submission', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<DetectiveForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);

      await userEvent.type(nameInput, '이탐정');
      await userEvent.type(phoneInput, '010-9876-5432');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          name: '이탐정',
          phone: '010-9876-5432',
          email: undefined,
          specialty: undefined,
          memo: undefined,
        });
      });
    });

    it('does not call onSubmit when validation fails', async () => {
      const onSubmit = jest.fn();
      render(<DetectiveForm {...defaultProps} onSubmit={onSubmit} />);

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('이름을 입력하세요')).toBeInTheDocument();
      });

      expect(onSubmit).not.toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('shows loading spinner when isSubmitting is true', () => {
      render(<DetectiveForm {...defaultProps} isSubmitting={true} />);

      expect(screen.getByText('저장 중...')).toBeInTheDocument();
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('disables submit button when isSubmitting is true', () => {
      render(<DetectiveForm {...defaultProps} isSubmitting={true} />);

      const submitButton = screen.getByRole('button', { name: /저장 중/i });
      expect(submitButton).toBeDisabled();
    });

    it('disables cancel button when isSubmitting is true', () => {
      render(<DetectiveForm {...defaultProps} isSubmitting={true} />);

      const cancelButton = screen.getByText('취소');
      expect(cancelButton).toBeDisabled();
    });
  });

  describe('Cancel Functionality', () => {
    it('calls onCancel when cancel button is clicked', () => {
      render(<DetectiveForm {...defaultProps} />);

      const cancelButton = screen.getByText('취소');
      fireEvent.click(cancelButton);

      expect(defaultProps.onCancel).toHaveBeenCalled();
    });

    it('calls onCancel when close button is clicked', () => {
      render(<DetectiveForm {...defaultProps} />);

      const closeButton = screen.getByLabelText('닫기');
      fireEvent.click(closeButton);

      expect(defaultProps.onCancel).toHaveBeenCalled();
    });
  });

  describe('Modal Overlay', () => {
    it('renders with modal overlay', () => {
      render(<DetectiveForm {...defaultProps} />);

      const overlay = document.querySelector('.bg-black\\/50');
      expect(overlay).toBeInTheDocument();
    });

    it('has fixed positioning', () => {
      render(<DetectiveForm {...defaultProps} />);

      const overlay = document.querySelector('.fixed.inset-0');
      expect(overlay).toBeInTheDocument();
    });

    it('has z-50 for proper stacking', () => {
      render(<DetectiveForm {...defaultProps} />);

      const overlay = document.querySelector('.z-50');
      expect(overlay).toBeInTheDocument();
    });
  });

  describe('Purple Theme Styling', () => {
    it('uses purple color for submit button', () => {
      render(<DetectiveForm {...defaultProps} />);

      const submitButton = screen.getByText('추가');
      expect(submitButton).toHaveClass('bg-purple-600');
    });

    it('uses purple focus ring on specialty select', () => {
      render(<DetectiveForm {...defaultProps} />);

      const specialtySelect = screen.getByLabelText(/전문 분야/);
      expect(specialtySelect).toHaveClass('focus:ring-purple-500');
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      render(<DetectiveForm {...defaultProps} />);

      expect(screen.getByLabelText(/이름/)).toBeInTheDocument();
      expect(screen.getByLabelText(/전화번호/)).toBeInTheDocument();
      expect(screen.getByLabelText(/이메일/)).toBeInTheDocument();
      expect(screen.getByLabelText(/전문 분야/)).toBeInTheDocument();
      expect(screen.getByLabelText(/메모/)).toBeInTheDocument();
    });

    it('uses proper input types', () => {
      render(<DetectiveForm {...defaultProps} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);
      const emailInput = screen.getByLabelText(/이메일/);

      expect(nameInput).toHaveAttribute('type', 'text');
      expect(phoneInput).toHaveAttribute('type', 'tel');
      expect(emailInput).toHaveAttribute('type', 'email');
    });

    it('has placeholder text for inputs', () => {
      render(<DetectiveForm {...defaultProps} />);

      expect(screen.getByPlaceholderText('탐정 이름')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('010-1234-5678')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('example@email.com')).toBeInTheDocument();
    });

    it('has textarea for memo field', () => {
      render(<DetectiveForm {...defaultProps} />);

      const memoTextarea = screen.getByLabelText(/메모/);
      expect(memoTextarea.tagName).toBe('TEXTAREA');
    });
  });
});

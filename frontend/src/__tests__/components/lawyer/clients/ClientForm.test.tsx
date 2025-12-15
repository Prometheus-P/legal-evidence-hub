/**
 * ClientForm Component Tests
 * 011-production-bug-fixes Feature - US2 (T057)
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ClientForm } from '@/components/lawyer/clients/ClientForm';
import type { ClientContact } from '@/types/client';

const mockClient: ClientContact = {
  id: '1',
  lawyerId: 'lawyer-1',
  name: '홍길동',
  phone: '010-1234-5678',
  email: 'hong@example.com',
  memo: '테스트 메모',
  createdAt: new Date().toISOString(),
};

describe('ClientForm', () => {
  const defaultProps = {
    onSubmit: jest.fn(),
    onCancel: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders add form title when no client provided', () => {
      render(<ClientForm {...defaultProps} />);

      expect(screen.getByText('의뢰인 추가')).toBeInTheDocument();
    });

    it('renders edit form title when client provided', () => {
      render(<ClientForm {...defaultProps} client={mockClient} />);

      expect(screen.getByText('의뢰인 수정')).toBeInTheDocument();
    });

    it('renders all form fields', () => {
      render(<ClientForm {...defaultProps} />);

      expect(screen.getByLabelText(/이름/)).toBeInTheDocument();
      expect(screen.getByLabelText(/전화번호/)).toBeInTheDocument();
      expect(screen.getByLabelText(/이메일/)).toBeInTheDocument();
      expect(screen.getByLabelText(/메모/)).toBeInTheDocument();
    });

    it('shows required indicator for name field', () => {
      render(<ClientForm {...defaultProps} />);

      const nameLabel = screen.getByText('이름');
      const requiredIndicator = nameLabel.parentElement?.querySelector('.text-red-500');
      expect(requiredIndicator).toBeInTheDocument();
      expect(requiredIndicator).toHaveTextContent('*');
    });

    it('renders submit and cancel buttons', () => {
      render(<ClientForm {...defaultProps} />);

      expect(screen.getByText('추가')).toBeInTheDocument();
      expect(screen.getByText('취소')).toBeInTheDocument();
    });

    it('shows 수정 button in edit mode', () => {
      render(<ClientForm {...defaultProps} client={mockClient} />);

      expect(screen.getByText('수정')).toBeInTheDocument();
    });

    it('renders close button with aria-label', () => {
      render(<ClientForm {...defaultProps} />);

      const closeButton = screen.getByLabelText('닫기');
      expect(closeButton).toBeInTheDocument();
    });
  });

  describe('Edit Mode', () => {
    it('pre-fills form fields with client data', () => {
      render(<ClientForm {...defaultProps} client={mockClient} />);

      expect(screen.getByDisplayValue('홍길동')).toBeInTheDocument();
      expect(screen.getByDisplayValue('010-1234-5678')).toBeInTheDocument();
      expect(screen.getByDisplayValue('hong@example.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('테스트 메모')).toBeInTheDocument();
    });

    it('handles client with missing optional fields', () => {
      const minimalClient: ClientContact = {
        id: '2',
        lawyerId: 'lawyer-1',
        name: '김철수',
        createdAt: new Date().toISOString(),
      };

      render(<ClientForm {...defaultProps} client={minimalClient} />);

      expect(screen.getByDisplayValue('김철수')).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('shows error when name is empty', async () => {
      render(<ClientForm {...defaultProps} />);

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('이름을 입력하세요')).toBeInTheDocument();
      });
    });

    it('shows error when neither phone nor email is provided', async () => {
      render(<ClientForm {...defaultProps} />);

      const nameInput = screen.getByLabelText(/이름/);
      await userEvent.type(nameInput, '테스트');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getAllByText('전화번호 또는 이메일 중 하나는 필수입니다')).toHaveLength(2);
      });
    });

    it('shows error for invalid email format', async () => {
      render(<ClientForm {...defaultProps} />);

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
      render(<ClientForm {...defaultProps} />);

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
      render(<ClientForm {...defaultProps} onSubmit={onSubmit} />);

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

    it('accepts valid email format', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<ClientForm {...defaultProps} onSubmit={onSubmit} />);

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
      render(<ClientForm {...defaultProps} />);

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        const nameInput = screen.getByLabelText(/이름/);
        expect(nameInput).toHaveClass('border-red-500');
      });
    });
  });

  describe('Form Submission', () => {
    it('calls onSubmit with form data', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<ClientForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);
      const emailInput = screen.getByLabelText(/이메일/);
      const memoInput = screen.getByLabelText(/메모/);

      await userEvent.type(nameInput, '김영희');
      await userEvent.type(phoneInput, '010-9876-5432');
      await userEvent.type(emailInput, 'kim@example.com');
      await userEvent.type(memoInput, '새 의뢰인 메모');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          name: '김영희',
          phone: '010-9876-5432',
          email: 'kim@example.com',
          memo: '새 의뢰인 메모',
        });
      });
    });

    it('trims whitespace from input values', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<ClientForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);

      await userEvent.type(nameInput, '  김영희  ');
      await userEvent.type(phoneInput, '  010-9876-5432  ');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            name: '김영희',
            phone: '010-9876-5432',
          })
        );
      });
    });

    it('excludes empty optional fields from submission', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(<ClientForm {...defaultProps} onSubmit={onSubmit} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);

      await userEvent.type(nameInput, '김영희');
      await userEvent.type(phoneInput, '010-9876-5432');

      const submitButton = screen.getByText('추가');
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          name: '김영희',
          phone: '010-9876-5432',
          email: undefined,
          memo: undefined,
        });
      });
    });

    it('does not call onSubmit when validation fails', async () => {
      const onSubmit = jest.fn();
      render(<ClientForm {...defaultProps} onSubmit={onSubmit} />);

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
      render(<ClientForm {...defaultProps} isSubmitting={true} />);

      expect(screen.getByText('저장 중...')).toBeInTheDocument();
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('disables submit button when isSubmitting is true', () => {
      render(<ClientForm {...defaultProps} isSubmitting={true} />);

      const submitButton = screen.getByRole('button', { name: /저장 중/i });
      expect(submitButton).toBeDisabled();
    });

    it('disables cancel button when isSubmitting is true', () => {
      render(<ClientForm {...defaultProps} isSubmitting={true} />);

      const cancelButton = screen.getByText('취소');
      expect(cancelButton).toBeDisabled();
    });
  });

  describe('Cancel Functionality', () => {
    it('calls onCancel when cancel button is clicked', () => {
      render(<ClientForm {...defaultProps} />);

      const cancelButton = screen.getByText('취소');
      fireEvent.click(cancelButton);

      expect(defaultProps.onCancel).toHaveBeenCalled();
    });

    it('calls onCancel when close button is clicked', () => {
      render(<ClientForm {...defaultProps} />);

      const closeButton = screen.getByLabelText('닫기');
      fireEvent.click(closeButton);

      expect(defaultProps.onCancel).toHaveBeenCalled();
    });
  });

  describe('Modal Overlay', () => {
    it('renders with modal overlay', () => {
      render(<ClientForm {...defaultProps} />);

      const overlay = document.querySelector('.bg-black\\/50');
      expect(overlay).toBeInTheDocument();
    });

    it('has fixed positioning', () => {
      render(<ClientForm {...defaultProps} />);

      const overlay = document.querySelector('.fixed.inset-0');
      expect(overlay).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      render(<ClientForm {...defaultProps} />);

      expect(screen.getByLabelText(/이름/)).toBeInTheDocument();
      expect(screen.getByLabelText(/전화번호/)).toBeInTheDocument();
      expect(screen.getByLabelText(/이메일/)).toBeInTheDocument();
      expect(screen.getByLabelText(/메모/)).toBeInTheDocument();
    });

    it('uses proper input types', () => {
      render(<ClientForm {...defaultProps} />);

      const nameInput = screen.getByLabelText(/이름/);
      const phoneInput = screen.getByLabelText(/전화번호/);
      const emailInput = screen.getByLabelText(/이메일/);

      expect(nameInput).toHaveAttribute('type', 'text');
      expect(phoneInput).toHaveAttribute('type', 'tel');
      expect(emailInput).toHaveAttribute('type', 'email');
    });

    it('has placeholder text for inputs', () => {
      render(<ClientForm {...defaultProps} />);

      expect(screen.getByPlaceholderText('의뢰인 이름')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('010-1234-5678')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('example@email.com')).toBeInTheDocument();
    });
  });
});

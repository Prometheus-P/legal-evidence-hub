/**
 * Input Accessibility Tests (T008)
 * TDD: Tests should verify accessibility requirements
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import '@testing-library/jest-dom';

import { Input } from '@/components/primitives/Input/Input';

expect.extend(toHaveNoViolations);

describe('Input Accessibility', () => {
  describe('WCAG 2.1 AA Compliance', () => {
    it('should have no axe accessibility violations with label', async () => {
      const { container } = render(<Input label="이름" />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations with error state', async () => {
      const { container } = render(
        <Input label="이메일" error="유효하지 않은 이메일입니다" />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations when disabled', async () => {
      const { container } = render(<Input label="비활성" disabled />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations with hint text', async () => {
      const { container } = render(
        <Input label="비밀번호" hint="8자 이상 입력하세요" />
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Label Association', () => {
    it('should have label associated with input via htmlFor', () => {
      render(<Input label="이메일" />);
      const input = screen.getByRole('textbox', { name: '이메일' });
      expect(input).toBeInTheDocument();
    });

    it('should have unique id for each input', () => {
      render(
        <>
          <Input label="First Name" />
          <Input label="Last Name" />
        </>
      );
      const inputs = screen.getAllByRole('textbox');
      expect(inputs[0].id).not.toBe(inputs[1].id);
    });
  });

  describe('Error State', () => {
    it('should have aria-invalid="true" when error is present', () => {
      render(<Input label="이메일" error="필수 항목입니다" />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });

    it('should have aria-describedby linking to error message', () => {
      render(<Input label="이메일" error="필수 항목입니다" />);
      const input = screen.getByRole('textbox');
      const errorId = input.getAttribute('aria-describedby');
      expect(errorId).toBeTruthy();
      expect(screen.getByText('필수 항목입니다')).toHaveAttribute('id', errorId);
    });

    it('should display error with role="alert"', () => {
      render(<Input label="이메일" error="필수 항목입니다" />);
      const error = screen.getByRole('alert');
      expect(error).toHaveTextContent('필수 항목입니다');
    });
  });

  describe('Hint Text', () => {
    it('should have aria-describedby linking to hint when no error', () => {
      render(<Input label="비밀번호" hint="8자 이상" />);
      const input = screen.getByRole('textbox');
      const hintId = input.getAttribute('aria-describedby');
      expect(hintId).toBeTruthy();
      expect(screen.getByText('8자 이상')).toHaveAttribute('id', hintId);
    });

    it('should prioritize error over hint in aria-describedby', () => {
      render(<Input label="비밀번호" hint="8자 이상" error="너무 짧습니다" />);
      const input = screen.getByRole('textbox');
      const describedBy = input.getAttribute('aria-describedby');
      expect(describedBy).toContain('error');
    });
  });

  describe('Required Field', () => {
    it('should have required attribute when required', () => {
      render(<Input label="이름" required />);
      const input = screen.getByRole('textbox');
      expect(input).toBeRequired();
    });

    it('should display visual required indicator', () => {
      render(<Input label="이름" required />);
      expect(screen.getByText('*')).toHaveAttribute('aria-hidden', 'true');
    });

    it('should announce required state to screen readers', () => {
      render(<Input label="이름" required />);
      expect(screen.getByText('(필수)')).toHaveClass('sr-only');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should be focusable', async () => {
      render(<Input label="이름" />);
      const input = screen.getByRole('textbox');

      input.focus();
      expect(input).toHaveFocus();
    });

    it('should accept text input', async () => {
      render(<Input label="이름" />);
      const input = screen.getByRole('textbox');

      await userEvent.type(input, '홍길동');
      expect(input).toHaveValue('홍길동');
    });

    it('should not be focusable when disabled', async () => {
      render(<Input label="이름" disabled />);
      const input = screen.getByRole('textbox');

      expect(input).toBeDisabled();
    });
  });

  describe('Focus Visibility', () => {
    it('should have focus ring styles', () => {
      render(<Input label="이름" />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('focus:ring-2');
    });
  });

  describe('Icon Accessibility', () => {
    it('should hide left icon from screen readers', () => {
      const Icon = () => <span data-testid="icon">🔍</span>;
      const { container } = render(<Input label="검색" leftIcon={<Icon />} />);
      const iconWrapper = container.querySelector('[aria-hidden="true"]');
      expect(iconWrapper).toBeInTheDocument();
    });
  });
});

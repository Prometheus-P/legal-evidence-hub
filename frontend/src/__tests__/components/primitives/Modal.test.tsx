/**
 * Modal Accessibility Tests (T009)
 * TDD: Tests for focus trap and ARIA compliance
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import '@testing-library/jest-dom';
import { useRef } from 'react';

import { Modal } from '@/components/primitives/Modal/Modal';
import { Button } from '@/components/primitives/Button/Button';

expect.extend(toHaveNoViolations);

// Mock createPortal for testing
jest.mock('react-dom', () => {
  const original = jest.requireActual('react-dom');
  return {
    ...original,
    createPortal: (node: React.ReactNode) => node,
  };
});

describe('Modal Accessibility', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    title: '확인',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('WCAG 2.1 AA Compliance', () => {
    it('should have no axe accessibility violations', async () => {
      const { container } = render(
        <Modal {...defaultProps}>
          <p>Modal content</p>
        </Modal>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations with description', async () => {
      const { container } = render(
        <Modal {...defaultProps} description="이 작업을 수행하시겠습니까?">
          <p>Modal content</p>
        </Modal>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations with footer', async () => {
      const { container } = render(
        <Modal
          {...defaultProps}
          footer={
            <>
              <Button variant="ghost">취소</Button>
              <Button>확인</Button>
            </>
          }
        >
          <p>Modal content</p>
        </Modal>
      );
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('ARIA Attributes', () => {
    it('should have role="dialog"', () => {
      render(<Modal {...defaultProps}>Content</Modal>);
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should have aria-modal="true"', () => {
      render(<Modal {...defaultProps}>Content</Modal>);
      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
    });

    it('should have aria-labelledby pointing to title', () => {
      render(<Modal {...defaultProps}>Content</Modal>);
      const dialog = screen.getByRole('dialog');
      const titleId = dialog.getAttribute('aria-labelledby');
      expect(titleId).toBeTruthy();
      expect(screen.getByText('확인')).toHaveAttribute('id', titleId);
    });

    it('should have aria-describedby when description is provided', () => {
      render(
        <Modal {...defaultProps} description="설명 텍스트">
          Content
        </Modal>
      );
      const dialog = screen.getByRole('dialog');
      const descId = dialog.getAttribute('aria-describedby');
      expect(descId).toBeTruthy();
      expect(screen.getByText('설명 텍스트')).toHaveAttribute('id', descId);
    });
  });

  describe('Keyboard Navigation', () => {
    it('should close on Escape key', async () => {
      const onClose = jest.fn();
      render(
        <Modal {...defaultProps} onClose={onClose}>
          Content
        </Modal>
      );

      await userEvent.keyboard('{Escape}');
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it('should not close on Escape when closeOnEscape is false', async () => {
      const onClose = jest.fn();
      render(
        <Modal {...defaultProps} onClose={onClose} closeOnEscape={false}>
          Content
        </Modal>
      );

      await userEvent.keyboard('{Escape}');
      expect(onClose).not.toHaveBeenCalled();
    });
  });

  describe('Focus Management', () => {
    it('should move focus into modal when opened', async () => {
      render(
        <Modal {...defaultProps}>
          <Button>First Button</Button>
        </Modal>
      );

      // Modal focuses first focusable element which is the close button in header
      await waitFor(() => {
        const closeButton = screen.getByRole('button', { name: '닫기' });
        expect(closeButton).toHaveFocus();
      });
    });

    it('should focus close button when no other focusable elements in body', async () => {
      render(<Modal {...defaultProps}>Non-interactive content only</Modal>);

      await waitFor(() => {
        const closeButton = screen.getByRole('button', { name: '닫기' });
        expect(closeButton).toHaveFocus();
      });
    });

    it('should trap focus within modal', async () => {
      render(
        <Modal {...defaultProps}>
          <Button>First</Button>
          <Button>Second</Button>
        </Modal>
      );

      // Close button is first focusable element in DOM order (in header)
      await waitFor(() => {
        const closeButton = screen.getByRole('button', { name: '닫기' });
        expect(closeButton).toHaveFocus();
      });

      // Tab through all focusable elements
      await userEvent.tab();
      expect(screen.getByRole('button', { name: 'First' })).toHaveFocus();

      await userEvent.tab();
      expect(screen.getByRole('button', { name: 'Second' })).toHaveFocus();

      // Should wrap back to close button
      await userEvent.tab();
      expect(screen.getByRole('button', { name: '닫기' })).toHaveFocus();
    });

    it('should trap focus in reverse with Shift+Tab', async () => {
      render(
        <Modal {...defaultProps}>
          <Button>First</Button>
          <Button>Second</Button>
        </Modal>
      );

      await waitFor(() => {
        const closeButton = screen.getByRole('button', { name: '닫기' });
        expect(closeButton).toHaveFocus();
      });

      // Shift+Tab should go to last focusable element
      await userEvent.tab({ shift: true });
      expect(screen.getByRole('button', { name: 'Second' })).toHaveFocus();
    });
  });

  describe('Close Button', () => {
    it('should have aria-label="닫기"', () => {
      render(<Modal {...defaultProps}>Content</Modal>);
      const closeButton = screen.getByRole('button', { name: '닫기' });
      expect(closeButton).toHaveAttribute('aria-label', '닫기');
    });

    it('should have type="button"', () => {
      render(<Modal {...defaultProps}>Content</Modal>);
      const closeButton = screen.getByRole('button', { name: '닫기' });
      expect(closeButton).toHaveAttribute('type', 'button');
    });

    it('should call onClose when clicked', async () => {
      const onClose = jest.fn();
      render(
        <Modal {...defaultProps} onClose={onClose}>
          Content
        </Modal>
      );

      await userEvent.click(screen.getByRole('button', { name: '닫기' }));
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it('should be hidden when hideCloseButton is true', () => {
      render(
        <Modal {...defaultProps} hideCloseButton>
          Content
        </Modal>
      );
      expect(screen.queryByRole('button', { name: '닫기' })).not.toBeInTheDocument();
    });
  });

  describe('Overlay Interaction', () => {
    it('should close when clicking overlay by default', async () => {
      const onClose = jest.fn();
      render(
        <Modal {...defaultProps} onClose={onClose}>
          Content
        </Modal>
      );

      // Click on the backdrop
      const backdrop = document.querySelector('[aria-hidden="true"]');
      if (backdrop) {
        await userEvent.click(backdrop);
        expect(onClose).toHaveBeenCalledTimes(1);
      }
    });

    it('should not close when closeOnOverlayClick is false', async () => {
      const onClose = jest.fn();
      render(
        <Modal {...defaultProps} onClose={onClose} closeOnOverlayClick={false}>
          Content
        </Modal>
      );

      const backdrop = document.querySelector('[aria-hidden="true"]');
      if (backdrop) {
        await userEvent.click(backdrop);
        expect(onClose).not.toHaveBeenCalled();
      }
    });
  });

  describe('Rendering', () => {
    it('should not render when isOpen is false', () => {
      render(
        <Modal {...defaultProps} isOpen={false}>
          Content
        </Modal>
      );
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('should render title in header', () => {
      render(<Modal {...defaultProps}>Content</Modal>);
      expect(screen.getByRole('heading', { name: '확인' })).toBeInTheDocument();
    });
  });
});

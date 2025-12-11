/**
 * Integration tests for EvidenceReviewCard Component
 * Task T092 - US10 Tests
 *
 * Tests for frontend/src/components/lawyer/EvidenceReviewCard.tsx:
 * - Rendering with evidence data
 * - Review status badge display
 * - Approve/reject actions
 * - Modal interactions
 * - Loading states
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EvidenceReviewCard, {
  type EvidenceWithReview,
  type ReviewStatus,
} from '@/components/lawyer/EvidenceReviewCard';

describe('EvidenceReviewCard Component', () => {
  const mockEvidence: EvidenceWithReview = {
    id: 'ev-123',
    case_id: 'case-456',
    filename: 'test-document.pdf',
    type: 'pdf',
    size: 1024 * 1024 * 2, // 2MB
    created_at: '2024-01-15T10:30:00Z',
    review_status: 'pending_review',
    uploaded_by: 'user-789',
    uploaded_by_name: '홍길동',
    ai_summary: 'AI 분석 요약 내용입니다.',
    labels: ['폭언', '불륜증거'],
  };

  const mockOnApprove = jest.fn();
  const mockOnReject = jest.fn();
  const mockOnViewDetail = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    test('should render filename', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
    });

    test('should render file size formatted', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      expect(screen.getByText('2.0 MB')).toBeInTheDocument();
    });

    test('should render upload date', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      // Date should be formatted in Korean
      expect(screen.getByText(/2024/)).toBeInTheDocument();
    });

    test('should render uploader name', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      expect(screen.getByText('홍길동')).toBeInTheDocument();
    });

    test('should render AI summary', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      expect(screen.getByText('AI 분석 요약 내용입니다.')).toBeInTheDocument();
    });

    test('should render labels', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      expect(screen.getByText('폭언')).toBeInTheDocument();
      expect(screen.getByText('불륜증거')).toBeInTheDocument();
    });

    test('should show +N for excess labels', () => {
      const evidenceWithManyLabels = {
        ...mockEvidence,
        labels: ['라벨1', '라벨2', '라벨3', '라벨4', '라벨5', '라벨6', '라벨7'],
      };
      render(<EvidenceReviewCard evidence={evidenceWithManyLabels} />);

      expect(screen.getByText('+2')).toBeInTheDocument();
    });
  });

  describe('Review Status Badge', () => {
    test('should show "검토 대기" for pending_review status', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      expect(screen.getByText('검토 대기')).toBeInTheDocument();
    });

    test('should show "승인됨" for approved status', () => {
      const approvedEvidence = { ...mockEvidence, review_status: 'approved' as ReviewStatus };
      render(<EvidenceReviewCard evidence={approvedEvidence} />);

      expect(screen.getByText('승인됨')).toBeInTheDocument();
    });

    test('should show "반려됨" for rejected status', () => {
      const rejectedEvidence = { ...mockEvidence, review_status: 'rejected' as ReviewStatus };
      render(<EvidenceReviewCard evidence={rejectedEvidence} />);

      expect(screen.getByText('반려됨')).toBeInTheDocument();
    });

    test('should have yellow background for pending status', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      const badge = screen.getByText('검토 대기');
      expect(badge).toHaveClass('bg-yellow-100');
      expect(badge).toHaveClass('text-yellow-700');
    });

    test('should have green background for approved status', () => {
      const approvedEvidence = { ...mockEvidence, review_status: 'approved' as ReviewStatus };
      render(<EvidenceReviewCard evidence={approvedEvidence} />);

      const badge = screen.getByText('승인됨');
      expect(badge).toHaveClass('bg-green-100');
      expect(badge).toHaveClass('text-green-700');
    });

    test('should have red background for rejected status', () => {
      const rejectedEvidence = { ...mockEvidence, review_status: 'rejected' as ReviewStatus };
      render(<EvidenceReviewCard evidence={rejectedEvidence} />);

      const badge = screen.getByText('반려됨');
      expect(badge).toHaveClass('bg-red-100');
      expect(badge).toHaveClass('text-red-700');
    });
  });

  describe('File Type Icons', () => {
    test('should show PDF icon for pdf type', () => {
      render(<EvidenceReviewCard evidence={mockEvidence} />);

      const iconContainer = document.querySelector('.text-red-500');
      expect(iconContainer).toBeInTheDocument();
    });

    test('should show image icon for image type', () => {
      const imageEvidence = { ...mockEvidence, type: 'image' };
      render(<EvidenceReviewCard evidence={imageEvidence} />);

      const iconContainer = document.querySelector('.text-blue-500');
      expect(iconContainer).toBeInTheDocument();
    });

    test('should show audio icon for audio type', () => {
      const audioEvidence = { ...mockEvidence, type: 'audio' };
      render(<EvidenceReviewCard evidence={audioEvidence} />);

      const iconContainer = document.querySelector('.text-green-500');
      expect(iconContainer).toBeInTheDocument();
    });

    test('should show video icon for video type', () => {
      const videoEvidence = { ...mockEvidence, type: 'video' };
      render(<EvidenceReviewCard evidence={videoEvidence} />);

      const iconContainer = document.querySelector('.text-purple-500');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    test('should show approve and reject buttons for pending status', () => {
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onApprove={mockOnApprove}
          onReject={mockOnReject}
        />
      );

      expect(screen.getByText('승인')).toBeInTheDocument();
      expect(screen.getByText('반려')).toBeInTheDocument();
    });

    test('should not show action buttons for approved status', () => {
      const approvedEvidence = { ...mockEvidence, review_status: 'approved' as ReviewStatus };
      render(
        <EvidenceReviewCard
          evidence={approvedEvidence}
          onApprove={mockOnApprove}
          onReject={mockOnReject}
        />
      );

      expect(screen.queryByText('승인')).not.toBeInTheDocument();
      expect(screen.queryByText('반려')).not.toBeInTheDocument();
    });

    test('should not show action buttons for rejected status', () => {
      const rejectedEvidence = { ...mockEvidence, review_status: 'rejected' as ReviewStatus };
      render(
        <EvidenceReviewCard
          evidence={rejectedEvidence}
          onApprove={mockOnApprove}
          onReject={mockOnReject}
        />
      );

      expect(screen.queryByText('승인')).not.toBeInTheDocument();
      expect(screen.queryByText('반려')).not.toBeInTheDocument();
    });

    test('should always show "상세 보기" button', () => {
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onViewDetail={mockOnViewDetail}
        />
      );

      expect(screen.getByText('상세 보기')).toBeInTheDocument();
    });
  });

  describe('Approve Action', () => {
    test('should call onApprove when approve button is clicked', async () => {
      mockOnApprove.mockResolvedValue(undefined);
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onApprove={mockOnApprove}
        />
      );

      fireEvent.click(screen.getByText('승인'));

      await waitFor(() => {
        expect(mockOnApprove).toHaveBeenCalledWith('ev-123');
      });
    });

    test('should show loading state during approval', async () => {
      let resolveApprove: () => void;
      mockOnApprove.mockImplementation(
        () =>
          new Promise<void>((resolve) => {
            resolveApprove = resolve;
          })
      );

      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onApprove={mockOnApprove}
        />
      );

      fireEvent.click(screen.getByText('승인'));

      // Loading spinner should appear
      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).toBeInTheDocument();
      });

      // Resolve the promise
      resolveApprove!();
    });

    test('should disable buttons during loading', async () => {
      let resolveApprove: () => void;
      mockOnApprove.mockImplementation(
        () =>
          new Promise<void>((resolve) => {
            resolveApprove = resolve;
          })
      );

      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onApprove={mockOnApprove}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('승인'));

      await waitFor(() => {
        const rejectButton = screen.getByText('반려');
        expect(rejectButton).toBeDisabled();
      });

      resolveApprove!();
    });
  });

  describe('Reject Modal', () => {
    test('should open reject modal when reject button is clicked', () => {
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('반려'));

      expect(screen.getByText('증거 반려')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('반려 사유 입력...')).toBeInTheDocument();
    });

    test('should close modal when cancel is clicked', () => {
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('반려'));
      expect(screen.getByText('증거 반려')).toBeInTheDocument();

      fireEvent.click(screen.getByText('취소'));
      expect(screen.queryByText('증거 반려')).not.toBeInTheDocument();
    });

    test('should disable submit button when reason is empty', () => {
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('반려'));

      const submitButton = screen.getByText('반려하기');
      expect(submitButton).toBeDisabled();
    });

    test('should enable submit button when reason is provided', () => {
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('반려'));

      const textarea = screen.getByPlaceholderText('반려 사유 입력...');
      fireEvent.change(textarea, { target: { value: '증거가 불명확합니다.' } });

      const submitButton = screen.getByText('반려하기');
      expect(submitButton).not.toBeDisabled();
    });

    test('should call onReject with evidence ID and reason', async () => {
      mockOnReject.mockResolvedValue(undefined);
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('반려'));

      const textarea = screen.getByPlaceholderText('반려 사유 입력...');
      fireEvent.change(textarea, { target: { value: '증거가 불명확합니다.' } });

      fireEvent.click(screen.getByText('반려하기'));

      await waitFor(() => {
        expect(mockOnReject).toHaveBeenCalledWith('ev-123', '증거가 불명확합니다.');
      });
    });

    test('should close modal after successful rejection', async () => {
      mockOnReject.mockResolvedValue(undefined);
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('반려'));

      const textarea = screen.getByPlaceholderText('반려 사유 입력...');
      fireEvent.change(textarea, { target: { value: '증거가 불명확합니다.' } });

      fireEvent.click(screen.getByText('반려하기'));

      await waitFor(() => {
        expect(screen.queryByText('증거 반려')).not.toBeInTheDocument();
      });
    });

    test('should show loading text during rejection', async () => {
      let resolveReject: () => void;
      mockOnReject.mockImplementation(
        () =>
          new Promise<void>((resolve) => {
            resolveReject = resolve;
          })
      );

      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onReject={mockOnReject}
        />
      );

      fireEvent.click(screen.getByText('반려'));

      const textarea = screen.getByPlaceholderText('반려 사유 입력...');
      fireEvent.change(textarea, { target: { value: '테스트 사유' } });

      fireEvent.click(screen.getByText('반려하기'));

      await waitFor(() => {
        expect(screen.getByText('처리 중...')).toBeInTheDocument();
      });

      resolveReject!();
    });
  });

  describe('View Detail Action', () => {
    test('should call onViewDetail when clicked', () => {
      render(
        <EvidenceReviewCard
          evidence={mockEvidence}
          onViewDetail={mockOnViewDetail}
        />
      );

      fireEvent.click(screen.getByText('상세 보기'));

      expect(mockOnViewDetail).toHaveBeenCalledWith('ev-123');
    });
  });

  describe('Without AI Summary', () => {
    test('should render without AI summary', () => {
      const evidenceWithoutSummary = { ...mockEvidence, ai_summary: undefined };
      render(<EvidenceReviewCard evidence={evidenceWithoutSummary} />);

      expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
      expect(screen.queryByText('AI 분석 요약')).not.toBeInTheDocument();
    });
  });

  describe('Without Labels', () => {
    test('should render without labels', () => {
      const evidenceWithoutLabels = { ...mockEvidence, labels: [] };
      render(<EvidenceReviewCard evidence={evidenceWithoutLabels} />);

      expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
    });

    test('should render with undefined labels', () => {
      const evidenceWithUndefinedLabels = { ...mockEvidence, labels: undefined };
      render(<EvidenceReviewCard evidence={evidenceWithUndefinedLabels} />);

      expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
    });
  });

  describe('Default Review Status', () => {
    test('should default to pending_review when status is undefined', () => {
      const evidenceNoStatus = { ...mockEvidence, review_status: undefined };
      render(<EvidenceReviewCard evidence={evidenceNoStatus} />);

      expect(screen.getByText('검토 대기')).toBeInTheDocument();
    });
  });

  describe('File Size Formatting', () => {
    test('should format bytes correctly', () => {
      const smallEvidence = { ...mockEvidence, size: 500 };
      render(<EvidenceReviewCard evidence={smallEvidence} />);

      expect(screen.getByText('500 B')).toBeInTheDocument();
    });

    test('should format KB correctly', () => {
      const kbEvidence = { ...mockEvidence, size: 1024 * 5 }; // 5KB
      render(<EvidenceReviewCard evidence={kbEvidence} />);

      expect(screen.getByText('5.0 KB')).toBeInTheDocument();
    });

    test('should format MB correctly', () => {
      const mbEvidence = { ...mockEvidence, size: 1024 * 1024 * 3.5 }; // 3.5MB
      render(<EvidenceReviewCard evidence={mbEvidence} />);

      expect(screen.getByText('3.5 MB')).toBeInTheDocument();
    });
  });
});

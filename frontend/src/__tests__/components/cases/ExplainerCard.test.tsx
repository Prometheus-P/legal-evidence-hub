/**
 * ExplainerCard Component Tests
 * US8 - 진행 상태 요약 카드 (Progress Summary Cards)
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ExplainerCard from '@/components/cases/ExplainerCard';
import * as summaryApi from '@/lib/api/summary';

// Mock the API module
jest.mock('@/lib/api/summary');

const mockSummaryApi = summaryApi as jest.Mocked<typeof summaryApi>;

// Mock summary response
const mockSummary = {
  case_id: 'case_123',
  case_title: '김○○ 이혼 사건',
  court_reference: '2024가합12345',
  client_name: '김민수',
  current_stage: '조정 절차 진행 중',
  current_stage_status: '진행중',
  progress_percent: 33,
  completed_stages: [
    { stage_label: '소장 접수', completed_date: '2024-10-15T10:00:00Z' },
    { stage_label: '송달 완료', completed_date: '2024-10-25T14:00:00Z' },
  ],
  next_schedules: [
    {
      event_type: '조정기일',
      scheduled_date: '2024-12-11T14:00:00Z',
      location: '서울가정법원 305호',
      notes: null,
    },
  ],
  evidence_total: 12,
  evidence_stats: [
    { category: '부정행위 관련', count: 8 },
    { category: '재산분할 관련', count: 4 },
  ],
  lawyer: {
    name: '홍길동',
    phone: '02-1234-5678',
    email: 'hong@lawfirm.com',
  },
  generated_at: '2024-12-09T10:00:00Z',
};

describe('ExplainerCard Component', () => {
  const defaultProps = {
    caseId: 'case_123',
    isOpen: true,
    onClose: jest.fn(),
    onShare: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockSummaryApi.getCaseSummary.mockResolvedValue({
      data: mockSummary,
      error: null,
    });
  });

  describe('Modal rendering', () => {
    it('should not render when isOpen is false', () => {
      render(<ExplainerCard {...defaultProps} isOpen={false} />);
      expect(screen.queryByText('사건 진행 현황 요약')).not.toBeInTheDocument();
    });

    it('should render when isOpen is true', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('사건 진행 현황 요약')).toBeInTheDocument();
      });
    });

    it('should call onClose when close button is clicked', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('사건 진행 현황 요약')).toBeInTheDocument();
      });

      const closeButton = screen.getByText('닫기');
      fireEvent.click(closeButton);

      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  describe('Data display', () => {
    it('should display case title and court reference', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/김○○ 이혼 사건/)).toBeInTheDocument();
        expect(screen.getByText(/2024가합12345/)).toBeInTheDocument();
      });
    });

    it('should display current stage', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('조정 절차 진행 중')).toBeInTheDocument();
      });
    });

    it('should display progress percentage', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/진행률 33%/)).toBeInTheDocument();
      });
    });

    it('should display completed stages', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('소장 접수')).toBeInTheDocument();
        expect(screen.getByText('송달 완료')).toBeInTheDocument();
      });
    });

    it('should display next schedules', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('조정기일')).toBeInTheDocument();
        expect(screen.getByText(/서울가정법원 305호/)).toBeInTheDocument();
      });
    });

    it('should display lawyer info', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('홍길동')).toBeInTheDocument();
        expect(screen.getByText(/02-1234-5678/)).toBeInTheDocument();
        expect(screen.getByText(/hong@lawfirm.com/)).toBeInTheDocument();
      });
    });
  });

  describe('Loading state', () => {
    it('should show loading indicator while fetching', () => {
      // Don't resolve the mock immediately
      mockSummaryApi.getCaseSummary.mockImplementation(
        () => new Promise(() => {})
      );

      render(<ExplainerCard {...defaultProps} />);

      // The modal should be open and showing loading
      expect(screen.getByText('사건 진행 현황 요약')).toBeInTheDocument();
    });
  });

  describe('Error state', () => {
    it('should display error message when API fails', async () => {
      mockSummaryApi.getCaseSummary.mockResolvedValue({
        data: null,
        error: '요약 정보를 불러올 수 없습니다.',
      });

      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('요약 정보를 불러올 수 없습니다.')).toBeInTheDocument();
      });
    });

    it('should show retry button on error', async () => {
      mockSummaryApi.getCaseSummary.mockResolvedValue({
        data: null,
        error: '오류가 발생했습니다.',
      });

      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('다시 시도')).toBeInTheDocument();
      });
    });
  });

  describe('Actions', () => {
    it('should call onShare when share button is clicked', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('의뢰인에게 전송')).toBeInTheDocument();
      });

      const shareButton = screen.getByText('의뢰인에게 전송');
      fireEvent.click(shareButton);

      expect(defaultProps.onShare).toHaveBeenCalled();
    });

    it('should have PDF download button', async () => {
      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('PDF 다운로드')).toBeInTheDocument();
      });
    });
  });

  describe('Empty states', () => {
    it('should show empty state for completed stages', async () => {
      mockSummaryApi.getCaseSummary.mockResolvedValue({
        data: {
          ...mockSummary,
          completed_stages: [],
        },
        error: null,
      });

      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('아직 완료된 단계가 없습니다.')).toBeInTheDocument();
      });
    });

    it('should show empty state for next schedules', async () => {
      mockSummaryApi.getCaseSummary.mockResolvedValue({
        data: {
          ...mockSummary,
          next_schedules: [],
        },
        error: null,
      });

      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('예정된 일정이 없습니다.')).toBeInTheDocument();
      });
    });

    it('should show empty state for evidence', async () => {
      mockSummaryApi.getCaseSummary.mockResolvedValue({
        data: {
          ...mockSummary,
          evidence_total: 0,
          evidence_stats: [],
        },
        error: null,
      });

      render(<ExplainerCard {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('등록된 증거가 없습니다.')).toBeInTheDocument();
      });
    });
  });
});

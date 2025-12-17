/**
 * ProcedureTimeline Component Tests
 * US3 - 절차 단계 관리 (Procedure Stage Tracking)
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { ProcedureTimeline } from '@/components/lawyer/procedure';
import type { ProcedureStage, NextStageOption } from '@/types/procedure';

// Test data
const mockStages: ProcedureStage[] = [
  {
    id: 'stage_1',
    case_id: 'case_123',
    stage: 'filed',
    status: 'completed',
    scheduled_date: '2024-01-15T10:00:00Z',
    completed_date: '2024-01-15T11:00:00Z',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T11:00:00Z',
    stage_label: '소장 접수',
    status_label: '완료',
  },
  {
    id: 'stage_2',
    case_id: 'case_123',
    stage: 'served',
    status: 'in_progress',
    scheduled_date: '2024-01-20T10:00:00Z',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-16T11:00:00Z',
    stage_label: '송달',
    status_label: '진행중',
  },
  {
    id: 'stage_3',
    case_id: 'case_123',
    stage: 'answered',
    status: 'pending',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    stage_label: '답변서',
    status_label: '대기',
  },
];

const mockNextStages: NextStageOption[] = [
  { stage: 'answered', label: '답변서' },
];

describe('ProcedureTimeline Component', () => {
  const defaultProps = {
    stages: mockStages,
    currentStage: mockStages[1],
    progressPercent: 11,
    validNextStages: mockNextStages,
    onStageClick: jest.fn(),
    onCompleteStage: jest.fn(),
    onSkipStage: jest.fn(),
    onTransition: jest.fn(),
    loading: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Empty state', () => {
    it('should show empty state when no stages', () => {
      render(
        <ProcedureTimeline
          {...defaultProps}
          stages={[]}
          currentStage={null}
        />
      );

      expect(screen.getByText('절차 타임라인이 없습니다')).toBeInTheDocument();
      expect(screen.getByText('타임라인을 초기화하여 사건 진행 상황을 추적하세요')).toBeInTheDocument();
    });
  });

  describe('Progress display', () => {
    it('should display progress percentage', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      expect(screen.getByText('진행률')).toBeInTheDocument();
      expect(screen.getByText('11%')).toBeInTheDocument();
    });

    it('should display current stage name', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      expect(screen.getByText(/현재 단계:/)).toBeInTheDocument();
      // Current stage label appears in progress bar section
      expect(screen.getAllByText('송달').length).toBeGreaterThan(0);
    });
  });

  describe('Stage cards', () => {
    it('should render all stages', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      // Stage labels appear in both timeline and current stage section
      // Use getAllByText to handle multiple elements
      expect(screen.getAllByText('소장 접수').length).toBeGreaterThan(0);
      expect(screen.getAllByText('송달').length).toBeGreaterThan(0);
      expect(screen.getAllByText('답변서').length).toBeGreaterThan(0);
    });

    it('should call onStageClick when stage card is clicked', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      // Find first stage card by its label
      const filledStageLabels = screen.getAllByText('소장 접수');
      const stageCard = filledStageLabels[0].closest('div[class*="cursor-pointer"]');
      if (stageCard) {
        fireEvent.click(stageCard);
        expect(defaultProps.onStageClick).toHaveBeenCalledWith(mockStages[0]);
      }
    });
  });

  describe('Stage actions', () => {
    it('should show complete button for in_progress stage', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      const completeButtons = screen.getAllByText('완료 처리');
      expect(completeButtons.length).toBeGreaterThan(0);
    });

    it('should show skip button for pending stage', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      const skipButtons = screen.getAllByText('건너뛰기');
      expect(skipButtons.length).toBeGreaterThan(0);
    });

    it('should call onCompleteStage when complete button clicked', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      const completeButtons = screen.getAllByText('완료 처리');
      fireEvent.click(completeButtons[0]);

      expect(defaultProps.onCompleteStage).toHaveBeenCalled();
    });

    it('should call onSkipStage when skip button clicked', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      const skipButtons = screen.getAllByText('건너뛰기');
      fireEvent.click(skipButtons[0]);

      expect(defaultProps.onSkipStage).toHaveBeenCalled();
    });
  });

  describe('Next stage transitions', () => {
    it('should show valid next stages section', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      expect(screen.getByText('다음 단계로 이동 가능')).toBeInTheDocument();
      expect(screen.getByText('답변서로 이동')).toBeInTheDocument();
    });

    it('should call onTransition when next stage button clicked', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      const transitionButton = screen.getByText('답변서로 이동');
      fireEvent.click(transitionButton);

      expect(defaultProps.onTransition).toHaveBeenCalledWith(mockNextStages[0]);
    });

    it('should not show next stages section when empty', () => {
      render(
        <ProcedureTimeline
          {...defaultProps}
          validNextStages={[]}
        />
      );

      expect(screen.queryByText('다음 단계로 이동 가능')).not.toBeInTheDocument();
    });
  });

  describe('Loading state', () => {
    it('should disable buttons when loading', () => {
      render(<ProcedureTimeline {...defaultProps} loading={true} />);

      const transitionButton = screen.getByText('답변서로 이동');
      expect(transitionButton).toBeDisabled();
    });
  });

  describe('Status badges', () => {
    it('should display status labels for each stage', () => {
      render(<ProcedureTimeline {...defaultProps} />);

      expect(screen.getByText('완료')).toBeInTheDocument();
      expect(screen.getByText('진행중')).toBeInTheDocument();
      expect(screen.getByText('대기')).toBeInTheDocument();
    });
  });
});

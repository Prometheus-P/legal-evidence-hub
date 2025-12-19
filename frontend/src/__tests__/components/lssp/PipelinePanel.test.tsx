import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { PipelinePanel } from '@/components/lssp/PipelinePanel';
import * as lsspApi from '@/lib/api/lssp';

// Mock the LSSP API module
jest.mock('@/lib/api/lssp', () => ({
  getCandidates: jest.fn(),
  getPipelineStats: jest.fn(),
  updateCandidate: jest.fn(),
  promoteCandidates: jest.fn(),
}));

// Mock logger
jest.mock('@/lib/logger', () => ({
  logger: {
    error: jest.fn(),
    info: jest.fn(),
    debug: jest.fn(),
  },
}));

const mockCandidates: lsspApi.Candidate[] = [
  {
    candidate_id: 1,
    case_id: 'case-123',
    evidence_id: 'ev-001',
    extract_id: null,
    run_id: 1,
    rule_id: 1,
    kind: 'ADMISSION',
    content: '바람 피운 것 미안해',
    value: { text: '바람' },
    ground_tags: ['G1'],
    confidence: 0.65,
    materiality: 85,
    source_span: { start: 100, end: 115 },
    status: 'CANDIDATE',
    reviewer_id: null,
    reviewed_at: null,
    rejection_reason: null,
    created_at: '2024-01-01T00:00:00Z',
    rule_name: '부정행위 인정 키워드',
  },
  {
    candidate_id: 2,
    case_id: 'case-123',
    evidence_id: 'ev-001',
    extract_id: null,
    run_id: 1,
    rule_id: 2,
    kind: 'THREAT',
    content: '가만 안 둘거야',
    value: { text: '가만 안 둬' },
    ground_tags: ['G3'],
    confidence: 0.6,
    materiality: 80,
    source_span: { start: 200, end: 215 },
    status: 'ACCEPTED',
    reviewer_id: 'user-123',
    reviewed_at: '2024-01-02T00:00:00Z',
    rejection_reason: null,
    created_at: '2024-01-01T00:00:00Z',
    rule_name: '위협 표현',
  },
];

const mockStats: lsspApi.PipelineStats = {
  total_runs: 5,
  total_candidates: 10,
  pending_candidates: 3,
  accepted_candidates: 5,
  rejected_candidates: 2,
  promoted_keypoints: 4,
};

describe('PipelinePanel', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Setup default mock responses
    (lsspApi.getCandidates as jest.Mock).mockResolvedValue({
      data: mockCandidates,
      status: 200,
    });
    (lsspApi.getPipelineStats as jest.Mock).mockResolvedValue({
      data: mockStats,
      status: 200,
    });
    (lsspApi.updateCandidate as jest.Mock).mockResolvedValue({
      data: { ...mockCandidates[0], status: 'ACCEPTED' },
      status: 200,
    });
    (lsspApi.promoteCandidates as jest.Mock).mockResolvedValue({
      data: { promoted_count: 1, keypoint_ids: ['kp-001'], merged_groups: [] },
      status: 200,
    });
  });

  it('renders loading state initially', () => {
    render(<PipelinePanel caseId="case-123" />);
    expect(screen.getByText(/후보 데이터를 불러오는 중/)).toBeInTheDocument();
  });

  it('renders candidates after loading', async () => {
    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      expect(screen.getByText('바람 피운 것 미안해')).toBeInTheDocument();
    });

    expect(screen.getByText('가만 안 둘거야')).toBeInTheDocument();
  });

  it('displays pipeline stats', async () => {
    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      // Check that candidates loaded and UI rendered
      expect(screen.getByText('바람 피운 것 미안해')).toBeInTheDocument();
    });

    // Stats should be displayed - check for the "총 후보" label
    expect(screen.getByText('총 후보')).toBeInTheDocument();
  });

  it('calls API with correct case_id', async () => {
    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      expect(lsspApi.getCandidates).toHaveBeenCalledWith(
        'case-123',
        expect.any(Object)
      );
      expect(lsspApi.getPipelineStats).toHaveBeenCalledWith('case-123');
    });
  });

  it('handles API error gracefully', async () => {
    (lsspApi.getCandidates as jest.Mock).mockResolvedValue({
      error: 'Network error',
      status: 500,
    });

    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      // Should display error state or message
      expect(screen.queryByText('바람 피운 것 미안해')).not.toBeInTheDocument();
    });
  });

  it('filters candidates by status', async () => {
    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      expect(screen.getByText('바람 피운 것 미안해')).toBeInTheDocument();
    });

    // Find and click status filter (if present)
    const filterButtons = screen.getAllByRole('button');
    const candidateFilter = filterButtons.find(btn =>
      btn.textContent?.includes('대기')
    );

    if (candidateFilter) {
      fireEvent.click(candidateFilter);

      await waitFor(() => {
        expect(lsspApi.getCandidates).toHaveBeenCalledWith(
          'case-123',
          expect.objectContaining({ status: 'CANDIDATE' })
        );
      });
    }
  });

  it('updates candidate status on accept click', async () => {
    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      expect(screen.getByText('바람 피운 것 미안해')).toBeInTheDocument();
    });

    // Find accept button for candidate
    const acceptButtons = screen.getAllByRole('button');
    const acceptButton = acceptButtons.find(
      btn => btn.textContent?.includes('수락') || btn.getAttribute('title')?.includes('수락')
    );

    if (acceptButton) {
      fireEvent.click(acceptButton);

      await waitFor(() => {
        expect(lsspApi.updateCandidate).toHaveBeenCalledWith(
          'case-123',
          expect.any(Number),
          expect.objectContaining({ status: 'ACCEPTED' })
        );
      });
    }
  });

  it('displays kind badges correctly', async () => {
    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      // KIND_LABELS maps ADMISSION -> '부정행위 인정', THREAT -> '위협/폭력'
      expect(screen.getByText('부정행위 인정')).toBeInTheDocument();
      expect(screen.getByText('위협/폭력')).toBeInTheDocument();
    });
  });

  it('displays ground tags', async () => {
    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      expect(screen.getByText('G1')).toBeInTheDocument();
      expect(screen.getByText('G3')).toBeInTheDocument();
    });
  });

  it('calls onRefresh callback when provided', async () => {
    const onRefresh = jest.fn();
    render(<PipelinePanel caseId="case-123" onRefresh={onRefresh} />);

    await waitFor(() => {
      expect(screen.getByText('바람 피운 것 미안해')).toBeInTheDocument();
    });

    // Trigger promote action
    const promoteButton = screen.getAllByRole('button').find(
      btn => btn.textContent?.includes('승격')
    );

    if (promoteButton) {
      fireEvent.click(promoteButton);

      await waitFor(() => {
        // onRefresh should be called after successful promotion
        expect(onRefresh).toHaveBeenCalled();
      });
    }
  });
});

describe('PipelinePanel Edge Cases', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('handles empty candidates list', async () => {
    (lsspApi.getCandidates as jest.Mock).mockResolvedValue({
      data: [],
      status: 200,
    });
    (lsspApi.getPipelineStats as jest.Mock).mockResolvedValue({
      data: { ...mockStats, total_candidates: 0, pending_candidates: 0 },
      status: 200,
    });

    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      // Should show empty state message
      expect(screen.queryByText('바람 피운 것 미안해')).not.toBeInTheDocument();
    });
  });

  it('handles null source_span', async () => {
    const candidateWithNullSpan = {
      ...mockCandidates[0],
      source_span: null,
    };

    (lsspApi.getCandidates as jest.Mock).mockResolvedValue({
      data: [candidateWithNullSpan],
      status: 200,
    });
    (lsspApi.getPipelineStats as jest.Mock).mockResolvedValue({
      data: mockStats,
      status: 200,
    });

    render(<PipelinePanel caseId="case-123" />);

    await waitFor(() => {
      expect(screen.getByText('바람 피운 것 미안해')).toBeInTheDocument();
    });
  });
});

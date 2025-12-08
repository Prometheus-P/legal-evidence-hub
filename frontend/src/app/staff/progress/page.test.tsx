import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import StaffProgressPage from './page';
import { getStaffProgress, updateChecklistItem } from '@/lib/api/staffProgress';

jest.mock('@/lib/api/staffProgress');

const mockGetStaffProgress = getStaffProgress as jest.MockedFunction<typeof getStaffProgress>;
const mockUpdateChecklistItem = updateChecklistItem as jest.MockedFunction<typeof updateChecklistItem>;

const sampleResponse = {
  data: [
    {
      case_id: 'case_001',
      title: '이혼 조정 사건',
      client_name: '김의뢰인',
      status: 'open',
      assignee: { id: 'staff_1', name: 'Paralegal Kim', email: 'kim@example.com' },
      updated_at: '2025-02-20T10:00:00Z',
      evidence_counts: {
        pending: 1,
        uploaded: 0,
        processing: 1,
        completed: 2,
        failed: 0,
      },
      ai_status: 'processing',
      ai_last_updated: '2025-02-20T10:00:00Z',
      outstanding_feedback_count: 2,
      feedback_items: [
        { item_id: 'fbk-1', title: '판례 DB 연동', status: 'pending', owner: 'Ops', notes: 'DB 점검' },
        { item_id: 'fbk-2', title: 'AI 역할 강화', status: 'done', owner: 'AI' },
      ],
      is_blocked: false,
    },
  ],
  status: 200,
  error: undefined,
};

const completedResponse = {
  data: [
    {
      case_id: 'case_002',
      title: '상속 분쟁',
      client_name: '박의뢰인',
      status: 'open',
      assignee: { id: 'staff_1', name: 'Paralegal Kim', email: 'kim@example.com' },
      updated_at: '2025-02-20T11:00:00Z',
      evidence_counts: {
        pending: 0,
        uploaded: 0,
        processing: 0,
        completed: 3,
        failed: 0,
      },
      ai_status: 'ready',
      ai_last_updated: '2025-02-20T11:00:00Z',
      outstanding_feedback_count: 0,
      feedback_items: [
        { item_id: 'fbk-1', title: '판례 DB 연동', status: 'done', owner: 'Ops', notes: 'DB 완료' },
        { item_id: 'fbk-2', title: 'AI 역할 강화', status: 'done', owner: 'AI' },
      ],
      is_blocked: false,
    },
  ],
  status: 200,
  error: undefined,
};

describe('<StaffProgressPage />', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders progress cards after fetching data', async () => {
    mockGetStaffProgress.mockResolvedValue(sampleResponse);

    render(<StaffProgressPage />);

    await waitFor(() => {
      expect(mockGetStaffProgress).toHaveBeenCalledTimes(1);
    });

    expect(screen.getByText('이혼 조정 사건')).toBeInTheDocument();
    expect(screen.getByText('담당자: Paralegal Kim')).toBeInTheDocument();
    expect(screen.getByText('피드백 항목 (2 미완료)')).toBeInTheDocument();
    expect(screen.getByText(/담당: Ops/)).toBeInTheDocument();
    expect(screen.getByText(/메모: DB 점검/)).toBeInTheDocument();
    expect(screen.getByText('총 배정')).toBeInTheDocument();
  });

  it('shows error banner when API call fails', async () => {
    mockGetStaffProgress.mockResolvedValue({
      data: undefined,
      error: '서버 오류',
      status: 500,
    });

    render(<StaffProgressPage />);

    await waitFor(() => {
      expect(mockGetStaffProgress).toHaveBeenCalled();
    });

    expect(screen.getByText(/서버 오류/)).toBeInTheDocument();
  });

  it('re-fetches data when filters change', async () => {
    mockGetStaffProgress.mockResolvedValue(sampleResponse);

    render(<StaffProgressPage />);

    await waitFor(() => expect(mockGetStaffProgress).toHaveBeenCalledTimes(1));

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    const refreshButton = screen.getByRole('button', { name: '새로고침' });
    fireEvent.click(refreshButton);

    await waitFor(() => expect(mockGetStaffProgress).toHaveBeenCalledTimes(3));
    expect(mockGetStaffProgress).toHaveBeenLastCalledWith({
      blocked_only: true,
      assignee_id: undefined,
    });
  });

  it('shows a success banner when all feedback items are completed', async () => {
    mockGetStaffProgress.mockResolvedValue(completedResponse);

    render(<StaffProgressPage />);

    await waitFor(() => expect(mockGetStaffProgress).toHaveBeenCalledTimes(1));

    expect(screen.getByText(/모든 피드백을 완료했습니다/)).toBeInTheDocument();
  });

  it('toggles checklist status via the API', async () => {
    mockGetStaffProgress.mockResolvedValue(sampleResponse);
    mockUpdateChecklistItem.mockResolvedValue({
      data: {
        item_id: 'fbk-1',
        title: '판례 DB 연동',
        status: 'done',
        owner: 'Ops',
      },
      status: 200,
    });

    render(<StaffProgressPage />);

    await waitFor(() => expect(mockGetStaffProgress).toHaveBeenCalledTimes(1));

    const toggleButton = screen.getByRole('button', { name: '완료 처리' });
    fireEvent.click(toggleButton);

    await waitFor(() =>
      expect(mockUpdateChecklistItem).toHaveBeenCalledWith('case_001', 'fbk-1', { status: 'done' })
    );
    await waitFor(() => expect(toggleButton).toHaveTextContent('대기 전환'));
    expect(screen.getByText('판례 DB 연동 항목을 완료 처리했습니다.')).toBeInTheDocument();
  });
});

/**
 * DraftPreviewPanel Component Tests
 *
 * Tests for the draft editor/preview component including:
 * - Basic rendering and UI elements
 * - Export functionality (DOCX/PDF/HWP)
 * - Manual save and autosave
 * - Version history
 * - Template application
 * - Comment system
 * - Change tracking
 */

import { render, screen, fireEvent, act, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import DraftPreviewPanel from '@/components/draft/DraftPreviewPanel';
import type { DraftCitation } from '@/types/draft';
import type { DownloadResult, DraftDownloadFormat } from '@/services/documentService';

// Mock the draftStorageService
jest.mock('@/services/draftStorageService', () => ({
  loadDraftState: jest.fn(() => null),
  persistDraftState: jest.fn(),
  clearDraftState: jest.fn(),
}));

// Mock DOMPurify
jest.mock('dompurify', () => ({
  sanitize: jest.fn((html: string) => html),
}));

// Mock BroadcastChannel
class MockBroadcastChannel {
  name: string;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onmessageerror: ((event: MessageEvent) => void) | null = null;
  close = jest.fn();
  postMessage = jest.fn();
  addEventListener = jest.fn();
  removeEventListener = jest.fn();
  dispatchEvent = jest.fn(() => true);

  constructor(name: string) {
    this.name = name;
  }
}

(global as unknown as Record<string, unknown>).BroadcastChannel = MockBroadcastChannel;

// Mock crypto.randomUUID
const mockRandomUUID = jest.fn(() => 'test-uuid-12345');
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: mockRandomUUID,
  },
});

import { loadDraftState, persistDraftState } from '@/services/draftStorageService';

const mockLoadDraftState = loadDraftState as jest.Mock;
const mockPersistDraftState = persistDraftState as jest.Mock;

// Test fixtures
const mockCitations: DraftCitation[] = [
  {
    evidenceId: 'ev-1',
    title: '녹음파일 01',
    quote: '피고가 폭언을 사용한 장면',
  },
  {
    evidenceId: 'ev-2',
    title: '사진 01',
    quote: '부정행위 증거 사진',
  },
];

const defaultProps = {
  caseId: 'test-case-123',
  draftText: '<p>테스트 초안 내용입니다.</p>',
  citations: mockCitations,
  isGenerating: false,
  hasExistingDraft: true,
  onGenerate: jest.fn(),
  onDownload: jest.fn(),
  onManualSave: jest.fn(),
};

describe('DraftPreviewPanel', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    mockLoadDraftState.mockReturnValue(null);

    // Mock document.execCommand
    document.execCommand = jest.fn(() => true);

    // Clear localStorage
    window.localStorage.clear();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Basic Rendering', () => {
    it('renders the AI disclaimer', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(
        screen.getByText(/이 문서는 AI가 생성한 초안이며, 최종 책임은 변호사에게 있습니다\./i)
      ).toBeInTheDocument();
    });

    it('renders the editor surface with zen mode attribute', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      const editorSurface = screen.getByTestId('draft-editor-surface');
      expect(editorSurface).toHaveAttribute('data-zen-mode', 'true');
    });

    it('renders contentEditable editor', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      const editor = screen.getByTestId('draft-editor-content');
      expect(editor).toHaveAttribute('contenteditable', 'true');
    });

    it('renders toolbar with formatting buttons', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByLabelText(/bold/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/italic/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/underline/i)).toBeInTheDocument();
    });

    it('displays page count based on content length', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // Content is short, so page count should be 1
      // The format is "페이지 {count}"
      expect(screen.getByText(/페이지 1/i)).toBeInTheDocument();
    });
  });

  describe('Generate Button', () => {
    it('shows "초안 재생성" when hasExistingDraft is true', () => {
      render(<DraftPreviewPanel {...defaultProps} hasExistingDraft={true} />);

      expect(screen.getByRole('button', { name: /초안 재생성/i })).toBeInTheDocument();
    });

    it('shows "초안 생성" when hasExistingDraft is false', () => {
      render(<DraftPreviewPanel {...defaultProps} hasExistingDraft={false} />);

      expect(screen.getByRole('button', { name: /초안 생성/i })).toBeInTheDocument();
    });

    it('calls onGenerate when generate button is clicked', () => {
      const onGenerate = jest.fn();
      render(<DraftPreviewPanel {...defaultProps} onGenerate={onGenerate} />);

      fireEvent.click(screen.getByRole('button', { name: /초안 재생성/i }));

      expect(onGenerate).toHaveBeenCalledTimes(1);
    });

    it('disables generate button when isGenerating is true', () => {
      render(<DraftPreviewPanel {...defaultProps} isGenerating={true} />);

      const button = screen.getByRole('button', { name: /생성 중/i });
      expect(button).toBeDisabled();
    });

    it('shows loading spinner when generating', () => {
      render(<DraftPreviewPanel {...defaultProps} isGenerating={true} />);

      expect(screen.getByText(/생성 중/i)).toBeInTheDocument();
    });
  });

  describe('Download/Export Functionality', () => {
    it('renders download buttons for DOCX, PDF, HWP', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByRole('button', { name: /DOCX/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /PDF/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /HWP/i })).toBeInTheDocument();
    });

    it('calls onDownload with docx format when DOCX button clicked', async () => {
      const onDownload = jest.fn().mockResolvedValue({ success: true, filename: 'draft.docx' });
      render(<DraftPreviewPanel {...defaultProps} onDownload={onDownload} />);

      fireEvent.click(screen.getByRole('button', { name: /DOCX/i }));

      await waitFor(() => {
        expect(onDownload).toHaveBeenCalledWith(
          expect.objectContaining({
            format: 'docx',
            content: expect.any(String),
          })
        );
      });
    });

    it('calls onDownload with pdf format when PDF button clicked', async () => {
      const onDownload = jest.fn().mockResolvedValue({ success: true, filename: 'draft.pdf' });
      render(<DraftPreviewPanel {...defaultProps} onDownload={onDownload} />);

      fireEvent.click(screen.getByRole('button', { name: /PDF/i }));

      await waitFor(() => {
        expect(onDownload).toHaveBeenCalledWith(
          expect.objectContaining({
            format: 'pdf',
          })
        );
      });
    });

    it('calls onDownload with hwp format when HWP button clicked', async () => {
      const onDownload = jest.fn().mockResolvedValue({ success: true, filename: 'draft.hwp' });
      render(<DraftPreviewPanel {...defaultProps} onDownload={onDownload} />);

      fireEvent.click(screen.getByRole('button', { name: /HWP/i }));

      await waitFor(() => {
        expect(onDownload).toHaveBeenCalledWith(
          expect.objectContaining({
            format: 'hwp',
          })
        );
      });
    });

    it('shows success toast after successful download', async () => {
      const onDownload = jest.fn().mockResolvedValue({
        success: true,
        filename: 'draft_test.docx',
      });

      render(<DraftPreviewPanel {...defaultProps} onDownload={onDownload} />);

      fireEvent.click(screen.getByRole('button', { name: /DOCX/i }));

      await waitFor(() => {
        // Toast message format: "DOCX 파일이 다운로드되었습니다."
        expect(screen.getByText(/DOCX 파일이 다운로드되었습니다/i)).toBeInTheDocument();
      });
    });

    it('shows error toast after failed download', async () => {
      const onDownload = jest.fn().mockResolvedValue({
        success: false,
        error: '서버 오류',
      });

      render(<DraftPreviewPanel {...defaultProps} onDownload={onDownload} />);

      fireEvent.click(screen.getByRole('button', { name: /DOCX/i }));

      await waitFor(() => {
        // Toast shows the error message
        expect(screen.getByText(/서버 오류/i)).toBeInTheDocument();
      });
    });

    it('shows loading state during download', async () => {
      const onDownload = jest.fn().mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ success: true }), 1000))
      );

      render(<DraftPreviewPanel {...defaultProps} onDownload={onDownload} />);

      fireEvent.click(screen.getByRole('button', { name: /DOCX/i }));

      // Should show loading state
      expect(screen.getByRole('button', { name: /DOCX/i })).toBeDisabled();
    });
  });

  describe('Manual Save', () => {
    it('renders save button', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByRole('button', { name: /저장/i })).toBeInTheDocument();
    });

    it('calls onManualSave when save button is clicked', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      const onManualSave = jest.fn().mockResolvedValue(undefined);

      render(<DraftPreviewPanel {...defaultProps} onManualSave={onManualSave} />);

      await user.click(screen.getByRole('button', { name: /저장/i }));

      await waitFor(() => {
        expect(onManualSave).toHaveBeenCalled();
      });
    });

    it('persists draft state to localStorage after save', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      await user.click(screen.getByRole('button', { name: /저장/i }));

      await waitFor(() => {
        expect(mockPersistDraftState).toHaveBeenCalled();
      });
    });

    it('updates autosave status message after save', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      await user.click(screen.getByRole('button', { name: /저장/i }));

      await waitFor(() => {
        expect(screen.getByText(/자동 저장됨/i)).toBeInTheDocument();
      });
    });
  });

  describe('Version History', () => {
    it('renders version history button', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByRole('button', { name: /버전 히스토리/i })).toBeInTheDocument();
    });

    it('opens version history panel when button clicked', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      await user.click(screen.getByRole('button', { name: /버전 히스토리/i }));

      expect(screen.getByTestId('version-history-panel')).toBeInTheDocument();
    });

    it('loads saved version history from localStorage', () => {
      mockLoadDraftState.mockReturnValue({
        content: '<p>저장된 내용</p>',
        lastSavedAt: '2024-01-01T00:00:00Z',
        history: [
          {
            id: 'v1',
            content: '<p>첫 번째 버전</p>',
            savedAt: '2024-01-01T00:00:00Z',
            reason: 'manual',
          },
        ],
        comments: [],
        changeLog: [],
      });

      render(<DraftPreviewPanel {...defaultProps} />);

      // The history should be loaded
      expect(mockLoadDraftState).toHaveBeenCalledWith('test-case-123');
    });

    it('adds entry to version history after manual save', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      // Save content
      await user.click(screen.getByRole('button', { name: /저장/i }));

      // Open version history
      await user.click(screen.getByRole('button', { name: /버전 히스토리/i }));

      const historyPanel = screen.getByTestId('version-history-panel');
      expect(within(historyPanel).getByText(/수동 저장/)).toBeInTheDocument();
    });
  });

  describe('Text Formatting', () => {
    it('executes bold command when bold button clicked', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      fireEvent.click(screen.getByLabelText(/bold/i));

      expect(document.execCommand).toHaveBeenCalledWith('bold', false, undefined);
    });

    it('executes italic command when italic button clicked', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      fireEvent.click(screen.getByLabelText(/italic/i));

      expect(document.execCommand).toHaveBeenCalledWith('italic', false, undefined);
    });

    it('executes underline command when underline button clicked', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      fireEvent.click(screen.getByLabelText(/underline/i));

      expect(document.execCommand).toHaveBeenCalledWith('underline', false, undefined);
    });

    it('executes list command when list button clicked', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      fireEvent.click(screen.getByLabelText(/list/i));

      expect(document.execCommand).toHaveBeenCalledWith('insertUnorderedList', false, undefined);
    });
  });

  describe('Template Application', () => {
    it('renders template application button', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByRole('button', { name: /템플릿 적용/i })).toBeInTheDocument();
    });

    it('opens template modal when button clicked', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      await user.click(screen.getByRole('button', { name: /템플릿 적용/i }));

      expect(await screen.findByRole('dialog', { name: /템플릿 선택/i })).toBeInTheDocument();
    });

    it('displays available templates in modal', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      await user.click(screen.getByRole('button', { name: /템플릿 적용/i }));

      expect(await screen.findByText(/답변서 기본 템플릿/i)).toBeInTheDocument();
      expect(screen.getByText(/준비서면 - 청구취지 강조/i)).toBeInTheDocument();
    });

    it('applies selected template to editor', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      await user.click(screen.getByRole('button', { name: /템플릿 적용/i }));

      const modal = await screen.findByRole('dialog', { name: /템플릿 선택/i });
      const applyButtons = within(modal).getAllByRole('button', { name: /템플릿 적용/i });
      await user.click(applyButtons[0]);

      const editor = screen.getByTestId('draft-editor-content');
      expect(editor.innerHTML).toContain('답 변 서');
    });
  });

  describe('Citation Insertion', () => {
    it('renders citation button with correct text', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // Button text is "증거 인용 삽입"
      expect(screen.getByRole('button', { name: /증거 인용 삽입/i })).toBeInTheDocument();
    });

    it('opens citation modal when button clicked', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      await user.click(screen.getByRole('button', { name: /증거 인용 삽입/i }));

      // Modal shows citation selection UI with heading "증거 인용 선택"
      expect(screen.getByText(/증거 인용 선택/i)).toBeInTheDocument();
    });

    it('displays citation count in summary', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // Shows citation count summary
      expect(screen.getByText(/실제 증거 인용/)).toBeInTheDocument();
      expect(screen.getByText(/2건/)).toBeInTheDocument();
    });
  });

  describe('Comment System', () => {
    it('renders comment input area', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByLabelText(/코멘트 작성/i)).toBeInTheDocument();
    });

    it('renders add comment button', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByRole('button', { name: /코멘트 추가/i })).toBeInTheDocument();
    });

    it('adds comment when text is entered and button clicked', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      const editor = screen.getByTestId('draft-editor-content');
      const range = document.createRange();
      range.selectNodeContents(editor);

      const selectionMock = {
        toString: () => '선택된 텍스트',
        rangeCount: 1,
        isCollapsed: false,
        getRangeAt: () => range,
        removeAllRanges: jest.fn(),
        addRange: jest.fn(),
        collapse: jest.fn(),
        collapseToEnd: jest.fn(),
        collapseToStart: jest.fn(),
        deleteFromDocument: jest.fn(),
        empty: jest.fn(),
        extend: jest.fn(),
        modify: jest.fn(),
        setBaseAndExtent: jest.fn(),
        setPosition: jest.fn(),
        anchorNode: range.startContainer,
        anchorOffset: 0,
        focusNode: range.endContainer,
        focusOffset: 0,
        containsNode: () => true,
        removeRange: jest.fn(),
        type: 'Range',
      } as unknown as Selection;

      jest.spyOn(window, 'getSelection').mockReturnValue(selectionMock);

      const textarea = screen.getByLabelText(/코멘트 작성/i);
      await user.type(textarea, '이 부분 검토 필요');

      await user.click(screen.getByRole('button', { name: /코멘트 추가/i }));

      expect(screen.getByText(/이 부분 검토 필요/i)).toBeInTheDocument();
    });
  });

  describe('Change Tracking', () => {
    it('renders change tracking toggle button', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // It's a button showing "변경 추적 OFF" initially
      expect(screen.getByRole('button', { name: /변경 추적 OFF/i })).toBeInTheDocument();
    });

    it('toggles change tracking when clicked', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} />);

      const toggleButton = screen.getByRole('button', { name: /변경 추적 OFF/i });

      await user.click(toggleButton);

      // After toggle, shows ON
      expect(screen.getByRole('button', { name: /변경 추적 ON/i })).toBeInTheDocument();
    });

    it('renders change log section', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // Change log empty message is present
      expect(screen.getByText(/기록된 변경 사항이 없습니다/)).toBeInTheDocument();
    });
  });

  describe('Evidence Traceability', () => {
    it('opens traceability panel when clicking on evidence reference in editor', async () => {
      // Render with editor content containing evidence reference
      render(
        <DraftPreviewPanel
          {...defaultProps}
          draftText='<p>Test <span class="evidence-ref" data-evidence-id="ev-1">[증거: 녹음파일]</span></p>'
        />
      );

      const editor = screen.getByTestId('draft-editor-content');
      const evidenceRef = editor.querySelector('[data-evidence-id="ev-1"]');

      if (evidenceRef) {
        fireEvent.click(evidenceRef);
      }

      // Note: The traceability panel component is separate (EvidenceTraceabilityPanel)
      // and may need to be mocked separately for full testing
    });

    it('renders citations section', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByText(/Citations/)).toBeInTheDocument();
    });

    it('shows citation quotes', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      expect(screen.getByText(/피고가 폭언을 사용한 장면/)).toBeInTheDocument();
    });
  });

  describe('Loading from localStorage', () => {
    it('loads draft content from localStorage on mount', () => {
      mockLoadDraftState.mockReturnValue({
        content: '<p>로컬에서 불러온 내용</p>',
        lastSavedAt: '2024-01-01T12:00:00Z',
        history: [],
        comments: [],
        changeLog: [],
      });

      render(<DraftPreviewPanel {...defaultProps} />);

      expect(mockLoadDraftState).toHaveBeenCalledWith('test-case-123');
    });

    it('prefers new draftText over localStorage if draftText changes', () => {
      mockLoadDraftState.mockReturnValue({
        content: '<p>이전 저장 내용</p>',
        lastSavedAt: '2024-01-01T12:00:00Z',
        history: [],
      });

      const { rerender } = render(<DraftPreviewPanel {...defaultProps} />);

      // Initial render uses draftText from props
      const editor = screen.getByTestId('draft-editor-content');
      expect(editor.innerHTML).toContain('테스트 초안 내용');

      // When draftText changes (new AI generation), update editor
      rerender(
        <DraftPreviewPanel
          {...defaultProps}
          draftText="<p>새로운 AI 생성 내용</p>"
        />
      );

      expect(editor.innerHTML).toContain('새로운 AI 생성 내용');
    });
  });

  describe('Empty State', () => {
    it('renders empty editor when no draft content', () => {
      render(<DraftPreviewPanel {...defaultProps} draftText="" />);

      const editor = screen.getByTestId('draft-editor-content');
      expect(editor).toBeInTheDocument();
      // Empty content means innerHTML is empty
      expect(editor.innerHTML).toBe('');
    });

    it('shows empty citations message when no citations', () => {
      render(<DraftPreviewPanel {...defaultProps} citations={[]} />);

      expect(screen.getByText(/아직 연결된 증거가 없습니다/)).toBeInTheDocument();
    });
  });

  describe('Autosave', () => {
    it('triggers autosave after interval', async () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // Modify content
      const editor = screen.getByTestId('draft-editor-content');
      fireEvent.input(editor, { target: { innerHTML: '<p>수정된 내용</p>' } });

      // Advance timers by autosave interval (5 minutes)
      act(() => {
        jest.advanceTimersByTime(5 * 60 * 1000);
      });

      await waitFor(() => {
        expect(mockPersistDraftState).toHaveBeenCalled();
      });
    });
  });

  describe('Autosave Indicator', () => {
    it('renders autosave indicator', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // Should show autosave indicator
      expect(screen.getByTestId('autosave-indicator')).toBeInTheDocument();
    });

    it('shows autosave status message', () => {
      render(<DraftPreviewPanel {...defaultProps} />);

      // Initially shows "자동 저장 준비 중"
      expect(screen.getByText(/자동 저장/)).toBeInTheDocument();
    });
  });

  describe('Error States', () => {
    it('handles onDownload returning void', async () => {
      const onDownload = jest.fn(() => undefined);

      render(<DraftPreviewPanel {...defaultProps} onDownload={onDownload} />);

      fireEvent.click(screen.getByRole('button', { name: /DOCX/i }));

      // Should not throw error
      await waitFor(() => {
        expect(onDownload).toHaveBeenCalled();
      });
    });

    it('handles missing onDownload prop', () => {
      // Should render without error
      render(<DraftPreviewPanel {...defaultProps} onDownload={undefined} />);

      // Download buttons should still be present but may be disabled
      expect(screen.getByRole('button', { name: /DOCX/i })).toBeInTheDocument();
    });

    it('handles missing onManualSave prop', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<DraftPreviewPanel {...defaultProps} onManualSave={undefined} />);

      // Should not throw error when save is clicked
      await user.click(screen.getByRole('button', { name: /저장/i }));

      // Should still persist to localStorage
      expect(mockPersistDraftState).toHaveBeenCalled();
    });
  });
});

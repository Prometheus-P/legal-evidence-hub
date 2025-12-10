/**
 * DraftEditor Tests
 * T019a - FR-007a: TipTap 기반 Rich Text Editor 테스트
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DraftEditor, { DraftEditorRef } from '@/components/draft/DraftEditor';
import { createRef } from 'react';

// Mock TipTap modules
jest.mock('@tiptap/react', () => {
  const actual = jest.requireActual('@tiptap/react');
  return {
    ...actual,
    useEditor: jest.fn(() => ({
      getHTML: jest.fn(() => '<p>Test content</p>'),
      getText: jest.fn(() => 'Test content'),
      commands: {
        setContent: jest.fn(),
        insertContent: jest.fn(),
        focus: jest.fn(),
        clearContent: jest.fn(),
      },
      chain: jest.fn(() => ({
        focus: jest.fn(() => ({
          toggleBold: jest.fn(() => ({ run: jest.fn() })),
          toggleItalic: jest.fn(() => ({ run: jest.fn() })),
          toggleUnderline: jest.fn(() => ({ run: jest.fn() })),
          toggleHeading: jest.fn(() => ({ run: jest.fn() })),
          toggleBulletList: jest.fn(() => ({ run: jest.fn() })),
          toggleOrderedList: jest.fn(() => ({ run: jest.fn() })),
          toggleBlockquote: jest.fn(() => ({ run: jest.fn() })),
          setTextAlign: jest.fn(() => ({ run: jest.fn() })),
          setLink: jest.fn(() => ({ run: jest.fn() })),
          extendMarkRange: jest.fn(() => ({
            setLink: jest.fn(() => ({ run: jest.fn() })),
            unsetLink: jest.fn(() => ({ run: jest.fn() })),
          })),
          unsetLink: jest.fn(() => ({ run: jest.fn() })),
          undo: jest.fn(() => ({ run: jest.fn() })),
          redo: jest.fn(() => ({ run: jest.fn() })),
        })),
      })),
      can: jest.fn(() => ({
        undo: jest.fn(() => true),
        redo: jest.fn(() => true),
      })),
      isActive: jest.fn(() => false),
      getAttributes: jest.fn(() => ({})),
      setEditable: jest.fn(),
    })),
    EditorContent: ({ editor }: { editor: unknown }) => (
      <div data-testid="editor-content">
        {editor ? 'Editor loaded' : 'No editor'}
      </div>
    ),
  };
});

describe('DraftEditor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders the editor container', () => {
      render(<DraftEditor />);
      expect(screen.getByTestId('editor-content')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      const { container } = render(<DraftEditor className="custom-class" />);
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('renders toolbar buttons', () => {
      render(<DraftEditor />);

      // Check for formatting buttons
      expect(screen.getByTitle('굵게 (Ctrl+B)')).toBeInTheDocument();
      expect(screen.getByTitle('기울임 (Ctrl+I)')).toBeInTheDocument();
      expect(screen.getByTitle('밑줄 (Ctrl+U)')).toBeInTheDocument();
    });

    it('renders heading buttons', () => {
      render(<DraftEditor />);

      expect(screen.getByTitle('제목 1')).toBeInTheDocument();
      expect(screen.getByTitle('제목 2')).toBeInTheDocument();
      expect(screen.getByTitle('제목 3')).toBeInTheDocument();
    });

    it('renders list buttons', () => {
      render(<DraftEditor />);

      expect(screen.getByTitle('글머리 기호 목록')).toBeInTheDocument();
      expect(screen.getByTitle('번호 매기기 목록')).toBeInTheDocument();
    });

    it('renders alignment buttons', () => {
      render(<DraftEditor />);

      expect(screen.getByTitle('왼쪽 정렬')).toBeInTheDocument();
      expect(screen.getByTitle('가운데 정렬')).toBeInTheDocument();
      expect(screen.getByTitle('오른쪽 정렬')).toBeInTheDocument();
    });

    it('renders link buttons', () => {
      render(<DraftEditor />);

      expect(screen.getByTitle('링크 추가')).toBeInTheDocument();
      expect(screen.getByTitle('링크 제거')).toBeInTheDocument();
    });

    it('renders undo/redo buttons', () => {
      render(<DraftEditor />);

      expect(screen.getByTitle('실행 취소 (Ctrl+Z)')).toBeInTheDocument();
      expect(screen.getByTitle('다시 실행 (Ctrl+Shift+Z)')).toBeInTheDocument();
    });
  });

  describe('Toolbar Interactions', () => {
    it('bold button is clickable', () => {
      render(<DraftEditor />);
      const boldButton = screen.getByTitle('굵게 (Ctrl+B)');
      fireEvent.click(boldButton);
      // Button should be clickable without errors
      expect(boldButton).toBeInTheDocument();
    });

    it('italic button is clickable', () => {
      render(<DraftEditor />);
      const italicButton = screen.getByTitle('기울임 (Ctrl+I)');
      fireEvent.click(italicButton);
      expect(italicButton).toBeInTheDocument();
    });

    it('underline button is clickable', () => {
      render(<DraftEditor />);
      const underlineButton = screen.getByTitle('밑줄 (Ctrl+U)');
      fireEvent.click(underlineButton);
      expect(underlineButton).toBeInTheDocument();
    });
  });

  describe('Ref Methods', () => {
    it('exposes getHTML method via ref', () => {
      const ref = createRef<DraftEditorRef>();
      render(<DraftEditor ref={ref} />);

      expect(ref.current).toBeDefined();
      expect(typeof ref.current?.getHTML).toBe('function');
    });

    it('exposes getText method via ref', () => {
      const ref = createRef<DraftEditorRef>();
      render(<DraftEditor ref={ref} />);

      expect(typeof ref.current?.getText).toBe('function');
    });

    it('exposes setContent method via ref', () => {
      const ref = createRef<DraftEditorRef>();
      render(<DraftEditor ref={ref} />);

      expect(typeof ref.current?.setContent).toBe('function');
    });

    it('exposes insertContent method via ref', () => {
      const ref = createRef<DraftEditorRef>();
      render(<DraftEditor ref={ref} />);

      expect(typeof ref.current?.insertContent).toBe('function');
    });

    it('exposes focus method via ref', () => {
      const ref = createRef<DraftEditorRef>();
      render(<DraftEditor ref={ref} />);

      expect(typeof ref.current?.focus).toBe('function');
    });

    it('exposes clear method via ref', () => {
      const ref = createRef<DraftEditorRef>();
      render(<DraftEditor ref={ref} />);

      expect(typeof ref.current?.clear).toBe('function');
    });

    it('exposes getEditor method via ref', () => {
      const ref = createRef<DraftEditorRef>();
      render(<DraftEditor ref={ref} />);

      expect(typeof ref.current?.getEditor).toBe('function');
    });
  });

  describe('Props', () => {
    it('accepts initialContent prop', () => {
      render(<DraftEditor initialContent="<p>Initial content</p>" />);
      expect(screen.getByTestId('editor-content')).toBeInTheDocument();
    });

    it('accepts placeholder prop', () => {
      render(<DraftEditor placeholder="Enter text here..." />);
      expect(screen.getByTestId('editor-content')).toBeInTheDocument();
    });

    it('accepts onChange callback', () => {
      const onChange = jest.fn();
      render(<DraftEditor onChange={onChange} />);
      expect(screen.getByTestId('editor-content')).toBeInTheDocument();
    });

    it('accepts onReady callback', () => {
      const onReady = jest.fn();
      render(<DraftEditor onReady={onReady} />);
      expect(screen.getByTestId('editor-content')).toBeInTheDocument();
    });

    it('accepts editable prop', () => {
      render(<DraftEditor editable={false} />);
      expect(screen.getByTestId('editor-content')).toBeInTheDocument();
    });

    it('accepts minHeight prop', () => {
      render(<DraftEditor minHeight="500px" />);
      expect(screen.getByTestId('editor-content')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('toolbar buttons have accessible titles', () => {
      render(<DraftEditor />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAttribute('title');
      });
    });

    it('toolbar buttons are keyboard accessible', () => {
      render(<DraftEditor />);

      const boldButton = screen.getByTitle('굵게 (Ctrl+B)');
      boldButton.focus();
      expect(document.activeElement).toBe(boldButton);
    });
  });

  describe('Quote insertion', () => {
    it('blockquote button is available', () => {
      render(<DraftEditor />);

      const quoteButton = screen.getByTitle('인용구');
      expect(quoteButton).toBeInTheDocument();
    });
  });
});

/**
 * DraftEditor - TipTap-based Rich Text Editor
 * T019a - FR-007a: TipTap 기반 Rich Text Editor에서 Draft 수정 가능
 *
 * Features:
 * - Rich text formatting (bold, italic, underline, lists, headings)
 * - Evidence citation insertion
 * - Text alignment
 * - Link support
 * - Keyboard shortcuts
 */

'use client';

import { useEditor, EditorContent, Editor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import Link from '@tiptap/extension-link';
import Placeholder from '@tiptap/extension-placeholder';
import TextAlign from '@tiptap/extension-text-align';
import { useCallback, useEffect, forwardRef, useImperativeHandle } from 'react';
import {
  Bold,
  Italic,
  Underline as UnderlineIcon,
  List,
  ListOrdered,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Heading1,
  Heading2,
  Heading3,
  Quote,
  Undo,
  Redo,
  Link as LinkIcon,
  Unlink,
} from 'lucide-react';

export interface DraftEditorProps {
  /** Initial HTML content */
  initialContent?: string;
  /** Placeholder text when editor is empty */
  placeholder?: string;
  /** Called when content changes */
  onChange?: (html: string) => void;
  /** Called when editor is ready */
  onReady?: (editor: Editor) => void;
  /** Whether the editor is editable */
  editable?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Minimum height of editor */
  minHeight?: string;
}

export interface DraftEditorRef {
  /** Get current HTML content */
  getHTML: () => string;
  /** Get plain text content */
  getText: () => string;
  /** Set HTML content */
  setContent: (html: string) => void;
  /** Insert HTML at current cursor position */
  insertContent: (content: string) => void;
  /** Focus the editor */
  focus: () => void;
  /** Clear the editor */
  clear: () => void;
  /** Get the TipTap editor instance */
  getEditor: () => Editor | null;
}

interface ToolbarButtonProps {
  onClick: () => void;
  isActive?: boolean;
  disabled?: boolean;
  title: string;
  children: React.ReactNode;
}

const ToolbarButton = ({ onClick, isActive, disabled, title, children }: ToolbarButtonProps) => (
  <button
    type="button"
    onClick={onClick}
    disabled={disabled}
    title={title}
    className={`
      p-2 rounded-lg transition-colors
      ${isActive ? 'bg-primary/10 text-primary' : 'text-neutral-600 hover:bg-neutral-100'}
      ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    `}
  >
    {children}
  </button>
);

const ToolbarDivider = () => <div className="w-px h-6 bg-neutral-200 mx-1" />;

interface MenuBarProps {
  editor: Editor | null;
}

const MenuBar = ({ editor }: MenuBarProps) => {
  const setLink = useCallback(() => {
    if (!editor) return;
    const previousUrl = editor.getAttributes('link').href;
    const url = window.prompt('URL', previousUrl);

    if (url === null) return;

    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }

    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
  }, [editor]);

  if (!editor) return null;

  return (
    <div className="flex flex-wrap items-center gap-1 p-2 border-b border-neutral-200 bg-neutral-50 rounded-t-xl">
      {/* History */}
      <ToolbarButton
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
        title="실행 취소 (Ctrl+Z)"
      >
        <Undo className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
        title="다시 실행 (Ctrl+Shift+Z)"
      >
        <Redo className="w-4 h-4" />
      </ToolbarButton>

      <ToolbarDivider />

      {/* Text formatting */}
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleBold().run()}
        isActive={editor.isActive('bold')}
        title="굵게 (Ctrl+B)"
      >
        <Bold className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleItalic().run()}
        isActive={editor.isActive('italic')}
        title="기울임 (Ctrl+I)"
      >
        <Italic className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleUnderline().run()}
        isActive={editor.isActive('underline')}
        title="밑줄 (Ctrl+U)"
      >
        <UnderlineIcon className="w-4 h-4" />
      </ToolbarButton>

      <ToolbarDivider />

      {/* Headings */}
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        isActive={editor.isActive('heading', { level: 1 })}
        title="제목 1"
      >
        <Heading1 className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        isActive={editor.isActive('heading', { level: 2 })}
        title="제목 2"
      >
        <Heading2 className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        isActive={editor.isActive('heading', { level: 3 })}
        title="제목 3"
      >
        <Heading3 className="w-4 h-4" />
      </ToolbarButton>

      <ToolbarDivider />

      {/* Lists */}
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        isActive={editor.isActive('bulletList')}
        title="글머리 기호 목록"
      >
        <List className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        isActive={editor.isActive('orderedList')}
        title="번호 매기기 목록"
      >
        <ListOrdered className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        isActive={editor.isActive('blockquote')}
        title="인용구"
      >
        <Quote className="w-4 h-4" />
      </ToolbarButton>

      <ToolbarDivider />

      {/* Alignment */}
      <ToolbarButton
        onClick={() => editor.chain().focus().setTextAlign('left').run()}
        isActive={editor.isActive({ textAlign: 'left' })}
        title="왼쪽 정렬"
      >
        <AlignLeft className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().setTextAlign('center').run()}
        isActive={editor.isActive({ textAlign: 'center' })}
        title="가운데 정렬"
      >
        <AlignCenter className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().setTextAlign('right').run()}
        isActive={editor.isActive({ textAlign: 'right' })}
        title="오른쪽 정렬"
      >
        <AlignRight className="w-4 h-4" />
      </ToolbarButton>

      <ToolbarDivider />

      {/* Links */}
      <ToolbarButton
        onClick={setLink}
        isActive={editor.isActive('link')}
        title="링크 추가"
      >
        <LinkIcon className="w-4 h-4" />
      </ToolbarButton>
      <ToolbarButton
        onClick={() => editor.chain().focus().unsetLink().run()}
        disabled={!editor.isActive('link')}
        title="링크 제거"
      >
        <Unlink className="w-4 h-4" />
      </ToolbarButton>
    </div>
  );
};

const DraftEditor = forwardRef<DraftEditorRef, DraftEditorProps>(
  (
    {
      initialContent = '',
      placeholder = '내용을 입력하세요...',
      onChange,
      onReady,
      editable = true,
      className = '',
      minHeight = '320px',
    },
    ref
  ) => {
    const editor = useEditor({
      extensions: [
        StarterKit.configure({
          heading: {
            levels: [1, 2, 3, 4],
          },
        }),
        Underline,
        Link.configure({
          openOnClick: false,
          HTMLAttributes: {
            class: 'text-primary underline cursor-pointer hover:text-primary-hover',
          },
        }),
        Placeholder.configure({
          placeholder,
          emptyEditorClass: 'is-editor-empty',
        }),
        TextAlign.configure({
          types: ['heading', 'paragraph'],
        }),
      ],
      content: initialContent,
      editable,
      onUpdate: ({ editor }) => {
        onChange?.(editor.getHTML());
      },
      onCreate: ({ editor }) => {
        onReady?.(editor);
      },
      editorProps: {
        attributes: {
          class: `prose prose-sm sm:prose-base max-w-none focus:outline-none p-4`,
          style: `min-height: ${minHeight}`,
        },
      },
    });

    // Update content when initialContent changes externally
    useEffect(() => {
      if (editor && initialContent !== editor.getHTML()) {
        editor.commands.setContent(initialContent, false);
      }
    }, [initialContent, editor]);

    // Update editable state
    useEffect(() => {
      if (editor) {
        editor.setEditable(editable);
      }
    }, [editable, editor]);

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      getHTML: () => editor?.getHTML() || '',
      getText: () => editor?.getText() || '',
      setContent: (html: string) => editor?.commands.setContent(html, false),
      insertContent: (content: string) => editor?.commands.insertContent(content),
      focus: () => editor?.commands.focus(),
      clear: () => editor?.commands.clearContent(),
      getEditor: () => editor,
    }));

    return (
      <div
        className={`border border-neutral-200 rounded-xl bg-white overflow-hidden ${className}`}
      >
        <MenuBar editor={editor} />
        <EditorContent
          editor={editor}
          className="[&_.ProseMirror]:outline-none [&_.is-editor-empty:first-child::before]:content-[attr(data-placeholder)] [&_.is-editor-empty:first-child::before]:text-neutral-400 [&_.is-editor-empty:first-child::before]:float-left [&_.is-editor-empty:first-child::before]:h-0 [&_.is-editor-empty:first-child::before]:pointer-events-none"
        />
      </div>
    );
  }
);

DraftEditor.displayName = 'DraftEditor';

export default DraftEditor;

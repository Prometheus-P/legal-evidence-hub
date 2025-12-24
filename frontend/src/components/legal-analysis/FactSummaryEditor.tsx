'use client';

/**
 * FactSummaryEditor - Notion-style Markdown Editor
 * 014-ui-settings-completion Feature
 *
 * Tiptap-based rich text editor for fact summary editing.
 * Features:
 * - Block-based editing (headings, lists, quotes)
 * - Real-time markdown rendering
 * - Toolbar with formatting options
 */

import { useEditor, EditorContent } from '@tiptap/react';
// Note: BubbleMenu removed due to module resolution issues
// Can be re-added when moduleResolution is updated to 'bundler'
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import { useEffect, useCallback } from 'react';
import {
  Bold,
  Italic,
  Underline as UnderlineIcon,
  List,
  ListOrdered,
  Quote,
  Heading1,
  Heading2,
  Heading3,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Link as LinkIcon,
  Undo,
  Redo,
} from 'lucide-react';

interface FactSummaryEditorProps {
  content: string;
  onChange: (content: string) => void;
  placeholder?: string;
  editable?: boolean;
  className?: string;
}

interface ToolbarButtonProps {
  onClick: () => void;
  isActive?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  title: string;
}

function ToolbarButton({ onClick, isActive, disabled, children, title }: ToolbarButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`
        p-1.5 rounded transition-colors
        ${isActive
          ? 'bg-[var(--color-primary)] text-white'
          : 'text-[var(--color-text-secondary)] hover:bg-gray-100 dark:hover:bg-neutral-700'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      {children}
    </button>
  );
}

function ToolbarDivider() {
  return <div className="w-px h-6 bg-gray-200 dark:bg-neutral-700 mx-1" />;
}

export function FactSummaryEditor({
  content,
  onChange,
  placeholder = '사실관계를 입력하세요...',
  editable = true,
  className = '',
}: FactSummaryEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Placeholder.configure({
        placeholder,
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-[var(--color-primary)] underline',
        },
      }),
      Underline,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  // Update content when prop changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);

  // Update editable state
  useEffect(() => {
    if (editor) {
      editor.setEditable(editable);
    }
  }, [editable, editor]);

  const setLink = useCallback(() => {
    if (!editor) return;

    const previousUrl = editor.getAttributes('link').href;
    const url = window.prompt('URL을 입력하세요', previousUrl);

    if (url === null) return;

    if (url === '') {
      editor.chain().focus().extendMarkRange('link').unsetLink().run();
      return;
    }

    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
  }, [editor]);

  if (!editor) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 dark:bg-neutral-700 rounded mb-2" />
        <div className="h-64 bg-gray-100 dark:bg-neutral-800 rounded" />
      </div>
    );
  }

  return (
    <div className={`border border-gray-200 dark:border-neutral-700 rounded-lg overflow-hidden ${className}`}>
      {/* Toolbar */}
      {editable && (
        <div className="flex items-center gap-0.5 px-2 py-1.5 border-b border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-800 flex-wrap">
          {/* Undo/Redo */}
          <ToolbarButton
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().undo()}
            title="실행 취소"
          >
            <Undo className="w-4 h-4" />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().redo()}
            title="다시 실행"
          >
            <Redo className="w-4 h-4" />
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

          {/* Text Formatting */}
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBold().run()}
            isActive={editor.isActive('bold')}
            title="굵게"
          >
            <Bold className="w-4 h-4" />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleItalic().run()}
            isActive={editor.isActive('italic')}
            title="기울임"
          >
            <Italic className="w-4 h-4" />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleUnderline().run()}
            isActive={editor.isActive('underline')}
            title="밑줄"
          >
            <UnderlineIcon className="w-4 h-4" />
          </ToolbarButton>

          <ToolbarDivider />

          {/* Lists */}
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            isActive={editor.isActive('bulletList')}
            title="글머리 기호"
          >
            <List className="w-4 h-4" />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            isActive={editor.isActive('orderedList')}
            title="번호 매기기"
          >
            <ListOrdered className="w-4 h-4" />
          </ToolbarButton>
          <ToolbarButton
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            isActive={editor.isActive('blockquote')}
            title="인용"
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

          {/* Link */}
          <ToolbarButton
            onClick={setLink}
            isActive={editor.isActive('link')}
            title="링크"
          >
            <LinkIcon className="w-4 h-4" />
          </ToolbarButton>
        </div>
      )}

      {/* Note: BubbleMenu (selection-based formatting) removed due to module resolution issues */}

      {/* Editor Content */}
      <EditorContent
        editor={editor}
        className={`
          prose prose-sm dark:prose-invert max-w-none
          p-4 min-h-[200px] max-h-[500px] overflow-y-auto
          focus:outline-none
          ${editable ? 'bg-white dark:bg-neutral-900' : 'bg-gray-50 dark:bg-neutral-800'}
          [&_.ProseMirror]:outline-none
          [&_.ProseMirror_p.is-editor-empty:first-child::before]:content-[attr(data-placeholder)]
          [&_.ProseMirror_p.is-editor-empty:first-child::before]:text-gray-400
          [&_.ProseMirror_p.is-editor-empty:first-child::before]:dark:text-neutral-500
          [&_.ProseMirror_p.is-editor-empty:first-child::before]:float-left
          [&_.ProseMirror_p.is-editor-empty:first-child::before]:h-0
          [&_.ProseMirror_p.is-editor-empty:first-child::before]:pointer-events-none
        `}
      />
    </div>
  );
}

export default FactSummaryEditor;

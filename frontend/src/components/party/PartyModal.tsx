/**
 * PartyModal - Modal for adding/editing party nodes
 * User Story 1: Party Relationship Graph
 */

'use client';

import { useState, useEffect, useRef, useCallback, useId } from 'react';
import type {
  PartyNode,
  PartyType,
  PartyNodeCreate,
  PartyNodeUpdate,
} from '@/types/party';
import { PARTY_TYPE_LABELS } from '@/types/party';

interface PartyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: PartyNodeCreate | PartyNodeUpdate) => Promise<void>;
  party?: PartyNode | null; // null for new party, object for edit
  defaultPosition?: { x: number; y: number };
}

const PARTY_TYPES: PartyType[] = [
  'plaintiff',
  'defendant',
  'third_party',
  'child',
  'family',
];

/**
 * Get all focusable elements within a container
 */
function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const focusableSelectors = [
    'button:not([disabled])',
    '[href]',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ');

  return Array.from(container.querySelectorAll<HTMLElement>(focusableSelectors));
}

export function PartyModal({
  isOpen,
  onClose,
  onSave,
  party,
  defaultPosition = { x: 250, y: 250 },
}: PartyModalProps) {
  const isEditMode = !!party;
  const modalRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const nameInputId = useId();
  const aliasInputId = useId();
  const birthYearInputId = useId();
  const occupationInputId = useId();

  const [formData, setFormData] = useState<{
    type: PartyType;
    name: string;
    alias: string;
    birth_year: string;
    occupation: string;
  }>({
    type: 'plaintiff',
    name: '',
    alias: '',
    birth_year: '',
    occupation: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes or party changes
  useEffect(() => {
    if (isOpen) {
      if (party) {
        setFormData({
          type: party.type,
          name: party.name,
          alias: party.alias || '',
          birth_year: party.birth_year?.toString() || '',
          occupation: party.occupation || '',
        });
      } else {
        setFormData({
          type: 'plaintiff',
          name: '',
          alias: '',
          birth_year: '',
          occupation: '',
        });
      }
      setError(null);
    }
  }, [isOpen, party]);

  // Focus trap and keyboard handling
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!isOpen || !modalRef.current) return;

      // Skip if IME composition is in progress
      if (event.isComposing || event.keyCode === 229) return;

      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key === 'Tab') {
        const focusableElements = getFocusableElements(modalRef.current);
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    },
    [isOpen, onClose]
  );

  // Setup keyboard listener and initial focus
  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      // Focus first focusable element
      requestAnimationFrame(() => {
        if (modalRef.current) {
          const focusableElements = getFocusableElements(modalRef.current);
          if (focusableElements.length > 0) {
            focusableElements[0].focus();
          }
        }
      });
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, handleKeyDown]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!formData.name.trim()) {
      setError('이름을 입력해주세요.');
      return;
    }

    setIsSubmitting(true);

    try {
      const birthYear = formData.birth_year
        ? parseInt(formData.birth_year, 10)
        : undefined;

      if (isEditMode) {
        // Edit mode - only send changed fields
        const updateData: PartyNodeUpdate = {
          name: formData.name.trim(),
          alias: formData.alias.trim() || undefined,
          birth_year: birthYear,
          occupation: formData.occupation.trim() || undefined,
        };
        await onSave(updateData);
      } else {
        // Create mode
        const createData: PartyNodeCreate = {
          type: formData.type,
          name: formData.name.trim(),
          alias: formData.alias.trim() || undefined,
          birth_year: birthYear,
          occupation: formData.occupation.trim() || undefined,
          position: defaultPosition,
        };
        await onSave(createData);
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '저장에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 id={titleId} className="text-lg font-semibold text-gray-900">
            {isEditMode ? '당사자 수정' : '당사자 추가'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
            aria-label="닫기"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="px-6 py-4 space-y-4">
            {/* Error message */}
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg">
                {error}
              </div>
            )}

            {/* Type (only for create mode) */}
            {!isEditMode && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  유형 <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {PARTY_TYPES.map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setFormData({ ...formData, type })}
                      className={`
                        px-3 py-2 text-sm rounded-lg border transition-colors
                        ${formData.type === type
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                    >
                      {PARTY_TYPE_LABELS[type]}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Name */}
            <div>
              <label htmlFor={nameInputId} className="block text-sm font-medium text-gray-700 mb-1">
                이름 <span className="text-red-500">*</span>
              </label>
              <input
                id={nameInputId}
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-800 dark:border-neutral-600 dark:text-white"
                placeholder="실명 또는 가명"
                autoFocus
              />
            </div>

            {/* Alias */}
            <div>
              <label htmlFor={aliasInputId} className="block text-sm font-medium text-gray-700 mb-1">
                소장용 가명
              </label>
              <input
                id={aliasInputId}
                type="text"
                value={formData.alias}
                onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-800 dark:border-neutral-600 dark:text-white"
                placeholder="예: 김○○"
              />
            </div>

            {/* Birth year */}
            <div>
              <label htmlFor={birthYearInputId} className="block text-sm font-medium text-gray-700 mb-1">
                출생년도
              </label>
              <input
                id={birthYearInputId}
                type="number"
                value={formData.birth_year}
                onChange={(e) => setFormData({ ...formData, birth_year: e.target.value })}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-800 dark:border-neutral-600 dark:text-white"
                placeholder="예: 1985"
                min={1900}
                max={new Date().getFullYear()}
              />
            </div>

            {/* Occupation */}
            <div>
              <label htmlFor={occupationInputId} className="block text-sm font-medium text-gray-700 mb-1">
                직업
              </label>
              <input
                id={occupationInputId}
                type="text"
                value={formData.occupation}
                onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-800 dark:border-neutral-600 dark:text-white"
                placeholder="예: 회사원"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 px-6 py-4 border-t bg-gray-50 rounded-b-lg">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
              disabled={isSubmitting}
            >
              취소
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? '저장 중...' : isEditMode ? '수정' : '추가'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

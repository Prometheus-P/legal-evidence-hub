/**
 * RelationshipModal - Modal for adding/editing party relationships
 * User Story 1: Party Relationship Graph
 */

'use client';

import { useState, useEffect, useRef, useCallback, useId } from 'react';
import type {
  PartyNode,
  PartyRelationship,
  RelationshipType,
  RelationshipCreate,
  RelationshipUpdate,
} from '@/types/party';
import { RELATIONSHIP_TYPE_LABELS } from '@/types/party';

interface RelationshipModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: RelationshipCreate | RelationshipUpdate) => Promise<void>;
  onDelete?: () => Promise<void>;
  relationship?: PartyRelationship | null;
  parties: PartyNode[];
  // Pre-selected parties for new relationship (from drag)
  sourcePartyId?: string;
  targetPartyId?: string;
}

const RELATIONSHIP_TYPES: RelationshipType[] = [
  'marriage',
  'affair',
  'parent_child',
  'sibling',
  'in_law',
  'cohabit',
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

export function RelationshipModal({
  isOpen,
  onClose,
  onSave,
  onDelete,
  relationship,
  parties,
  sourcePartyId,
  targetPartyId,
}: RelationshipModalProps) {
  const isEditMode = !!relationship;
  const modalRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const sourcePartySelectId = useId();
  const targetPartySelectId = useId();
  const startDateInputId = useId();
  const endDateInputId = useId();
  const notesTextareaId = useId();

  const [formData, setFormData] = useState<{
    source_party_id: string;
    target_party_id: string;
    type: RelationshipType;
    start_date: string;
    end_date: string;
    notes: string;
  }>({
    source_party_id: '',
    target_party_id: '',
    type: 'marriage',
    start_date: '',
    end_date: '',
    notes: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      if (relationship) {
        setFormData({
          source_party_id: relationship.source_party_id,
          target_party_id: relationship.target_party_id,
          type: relationship.type,
          start_date: relationship.start_date?.split('T')[0] || '',
          end_date: relationship.end_date?.split('T')[0] || '',
          notes: relationship.notes || '',
        });
      } else {
        setFormData({
          source_party_id: sourcePartyId || '',
          target_party_id: targetPartyId || '',
          type: 'marriage',
          start_date: '',
          end_date: '',
          notes: '',
        });
      }
      setError(null);
    }
  }, [isOpen, relationship, sourcePartyId, targetPartyId]);

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
    if (!formData.source_party_id || !formData.target_party_id) {
      setError('당사자를 선택해주세요.');
      return;
    }
    if (formData.source_party_id === formData.target_party_id) {
      setError('같은 당사자를 선택할 수 없습니다.');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isEditMode) {
        const updateData: RelationshipUpdate = {
          type: formData.type,
          start_date: formData.start_date || undefined,
          end_date: formData.end_date || undefined,
          notes: formData.notes.trim() || undefined,
        };
        await onSave(updateData);
      } else {
        const createData: RelationshipCreate = {
          source_party_id: formData.source_party_id,
          target_party_id: formData.target_party_id,
          type: formData.type,
          start_date: formData.start_date || undefined,
          end_date: formData.end_date || undefined,
          notes: formData.notes.trim() || undefined,
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

  const handleDelete = async () => {
    if (!onDelete) return;

    if (!window.confirm('이 관계를 삭제하시겠습니까?')) return;

    setIsDeleting(true);
    try {
      await onDelete();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '삭제에 실패했습니다.');
    } finally {
      setIsDeleting(false);
    }
  };

  const getPartyLabel = (partyId: string) => {
    const party = parties.find((p) => p.id === partyId);
    return party ? party.name : partyId;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />

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
            {isEditMode ? '관계 수정' : '관계 추가'}
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

            {/* Parties selection (only for create mode) */}
            {!isEditMode && (
              <>
                <div>
                  <label htmlFor={sourcePartySelectId} className="block text-sm font-medium text-gray-700 mb-1">
                    출발 당사자 <span className="text-red-500">*</span>
                  </label>
                  <select
                    id={sourcePartySelectId}
                    value={formData.source_party_id}
                    onChange={(e) =>
                      setFormData({ ...formData, source_party_id: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-800 dark:border-neutral-600 dark:text-white"
                  >
                    <option value="">선택해주세요</option>
                    {parties.map((party) => (
                      <option key={party.id} value={party.id}>
                        {party.name} ({party.type})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor={targetPartySelectId} className="block text-sm font-medium text-gray-700 mb-1">
                    도착 당사자 <span className="text-red-500">*</span>
                  </label>
                  <select
                    id={targetPartySelectId}
                    value={formData.target_party_id}
                    onChange={(e) =>
                      setFormData({ ...formData, target_party_id: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-800 dark:border-neutral-600 dark:text-white"
                  >
                    <option value="">선택해주세요</option>
                    {parties
                      .filter((p) => p.id !== formData.source_party_id)
                      .map((party) => (
                        <option key={party.id} value={party.id}>
                          {party.name} ({party.type})
                        </option>
                      ))}
                  </select>
                </div>
              </>
            )}

            {/* Party info (edit mode only) */}
            {isEditMode && relationship && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{getPartyLabel(relationship.source_party_id)}</span>
                  {' → '}
                  <span className="font-medium">{getPartyLabel(relationship.target_party_id)}</span>
                </p>
              </div>
            )}

            {/* Relationship type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                관계 유형 <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                {RELATIONSHIP_TYPES.map((type) => (
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
                    {RELATIONSHIP_TYPE_LABELS[type]}
                  </button>
                ))}
              </div>
            </div>

            {/* Date range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor={startDateInputId} className="block text-sm font-medium text-gray-700 mb-1">
                  시작일
                </label>
                <input
                  id={startDateInputId}
                  type="date"
                  value={formData.start_date}
                  onChange={(e) =>
                    setFormData({ ...formData, start_date: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label htmlFor={endDateInputId} className="block text-sm font-medium text-gray-700 mb-1">
                  종료일
                </label>
                <input
                  id={endDateInputId}
                  type="date"
                  value={formData.end_date}
                  onChange={(e) =>
                    setFormData({ ...formData, end_date: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Notes */}
            <div>
              <label htmlFor={notesTextareaId} className="block text-sm font-medium text-gray-700 mb-1">
                메모
              </label>
              <textarea
                id={notesTextareaId}
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                className="w-full px-3 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-800 dark:border-neutral-600 dark:text-white resize-none"
                rows={3}
                placeholder="관계에 대한 추가 설명"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-between px-6 py-4 border-t bg-gray-50 rounded-b-lg">
            <div>
              {isEditMode && onDelete && (
                <button
                  type="button"
                  onClick={handleDelete}
                  className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg disabled:opacity-50"
                  disabled={isSubmitting || isDeleting}
                >
                  {isDeleting ? '삭제 중...' : '삭제'}
                </button>
              )}
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
                disabled={isSubmitting || isDeleting}
              >
                취소
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary/90 rounded-lg disabled:opacity-50"
                disabled={isSubmitting || isDeleting}
              >
                {isSubmitting ? '저장 중...' : isEditMode ? '수정' : '추가'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

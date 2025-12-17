'use client';

/**
 * EditCaseModal Component
 * 011-production-bug-fixes Feature
 *
 * Modal for editing existing case details (title, client_name, description).
 */

import React, { useState, useRef, useEffect } from 'react';
import { Modal, Button } from '@/components/primitives';
import { updateCase, ApiCase } from '@/lib/api/cases';

interface EditCaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (updatedCase: ApiCase) => void;
  caseData: {
    id: string;
    title: string;
    clientName?: string;
    description?: string;
  } | null;
}

const EditCaseModal: React.FC<EditCaseModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  caseData,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const formRef = useRef<HTMLFormElement>(null);

  // Reset error when modal opens
  useEffect(() => {
    if (isOpen) {
      setErrorMessage(null);
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseData) return;

    setIsSubmitting(true);
    setErrorMessage(null);

    const formData = new FormData(formRef.current!);
    const title = formData.get('title') as string;
    const clientName = formData.get('clientName') as string;
    const description = formData.get('description') as string;

    try {
      const response = await updateCase(caseData.id, {
        title,
        client_name: clientName,
        description: description || undefined,
      });

      if (response.error) {
        setErrorMessage(`사건 수정 실패: ${response.error}`);
        return;
      }

      if (response.data) {
        onSuccess?.(response.data);
      }
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setErrorMessage(null);
    onClose();
  };

  if (!caseData) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="사건 정보 수정"
      size="md"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose}>
            취소
          </Button>
          <Button
            type="submit"
            form="edit-case-form"
            variant="primary"
            isLoading={isSubmitting}
          >
            저장
          </Button>
        </>
      }
    >
      <form ref={formRef} id="edit-case-form" onSubmit={handleSubmit} className="space-y-4">
        {errorMessage && (
          <div
            className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm"
            role="alert"
          >
            {errorMessage}
          </div>
        )}
        <div>
          <label
            htmlFor="edit-case-title"
            className="block text-sm font-medium text-neutral-700 dark:text-gray-300 mb-1.5"
          >
            사건명 <span className="text-red-500">*</span>
          </label>
          <input
            id="edit-case-title"
            name="title"
            type="text"
            defaultValue={caseData.title}
            placeholder="예: 김철수 이혼 소송"
            required
            className="w-full h-11 px-3 text-base block rounded-lg border bg-white dark:bg-neutral-900 text-neutral-900 dark:text-gray-100
                       border-neutral-300 dark:border-neutral-600 hover:border-neutral-400 dark:hover:border-neutral-500
                       focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
                       placeholder:text-neutral-400 dark:placeholder:text-neutral-500 transition-colors duration-200"
          />
        </div>

        <div>
          <label
            htmlFor="edit-client-name"
            className="block text-sm font-medium text-neutral-700 dark:text-gray-300 mb-1.5"
          >
            의뢰인 이름 <span className="text-red-500">*</span>
          </label>
          <input
            id="edit-client-name"
            name="clientName"
            type="text"
            defaultValue={caseData.clientName || ''}
            placeholder="예: 김철수"
            required
            className="w-full h-11 px-3 text-base block rounded-lg border bg-white dark:bg-neutral-900 text-neutral-900 dark:text-gray-100
                       border-neutral-300 dark:border-neutral-600 hover:border-neutral-400 dark:hover:border-neutral-500
                       focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
                       placeholder:text-neutral-400 dark:placeholder:text-neutral-500 transition-colors duration-200"
          />
        </div>

        <div>
          <label
            htmlFor="edit-description"
            className="block text-sm font-medium text-neutral-700 dark:text-gray-300 mb-1.5"
          >
            설명 <span className="text-neutral-400 text-xs">(선택)</span>
          </label>
          <textarea
            id="edit-description"
            name="description"
            defaultValue={caseData.description || ''}
            placeholder="사건에 대한 간략한 설명을 입력하세요"
            rows={3}
            className="w-full px-3 py-2 text-base block rounded-lg border bg-white dark:bg-neutral-900 text-neutral-900 dark:text-gray-100
                       border-neutral-300 dark:border-neutral-600 hover:border-neutral-400 dark:hover:border-neutral-500
                       focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary
                       placeholder:text-neutral-400 dark:placeholder:text-neutral-500 transition-colors duration-200 resize-none"
          />
        </div>
      </form>
    </Modal>
  );
};

export default EditCaseModal;

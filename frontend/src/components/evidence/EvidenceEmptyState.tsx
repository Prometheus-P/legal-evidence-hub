/**
 * EvidenceEmptyState Component (T074)
 *
 * Empty state for evidence section when no evidence exists.
 * Guides users to upload their first evidence.
 */

'use client';

import { FileImage, Upload, FileText } from 'lucide-react';
import { EmptyState } from '@/components/shared/EmptyState';

interface EvidenceEmptyStateProps {
  /**
   * Handler for uploading evidence
   */
  onUploadEvidence?: () => void;
  /**
   * Handler for viewing supported formats
   */
  onViewFormats?: () => void;
  /**
   * Case title for context
   */
  caseTitle?: string;
  /**
   * Size variant
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Additional classes
   */
  className?: string;
}

export function EvidenceEmptyState({
  onUploadEvidence,
  onViewFormats,
  caseTitle,
  size = 'md',
  className = '',
}: EvidenceEmptyStateProps) {
  const title = '증거 자료가 없습니다';

  const description = caseTitle
    ? `'${caseTitle}' 사건에 증거 자료를 업로드하세요. 이미지, 오디오, 비디오, PDF 등 다양한 형식을 지원합니다.`
    : '증거 자료를 업로드하세요. 이미지, 오디오, 비디오, PDF 등 다양한 형식을 지원합니다.';

  return (
    <EmptyState
      icon="custom"
      customIcon={
        <FileImage
          className="w-full h-full text-neutral-400 dark:text-neutral-500"
          aria-hidden="true"
        />
      }
      title={title}
      description={description}
      size={size}
      className={className}
      primaryAction={
        onUploadEvidence
          ? {
              label: '증거 업로드',
              onClick: onUploadEvidence,
              variant: 'primary',
              icon: <Upload className="w-4 h-4 mr-2" />,
            }
          : undefined
      }
      secondaryAction={
        onViewFormats
          ? {
              label: '지원 형식 보기',
              onClick: onViewFormats,
              variant: 'ghost',
              icon: <FileText className="w-4 h-4 mr-2" />,
            }
          : undefined
      }
    >
      {/* Supported formats hint */}
      <div className="flex flex-wrap justify-center gap-2 mt-2">
        {['이미지', '오디오', '비디오', 'PDF', '텍스트'].map((format) => (
          <span
            key={format}
            className="px-2 py-1 text-xs bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 rounded-full"
          >
            {format}
          </span>
        ))}
      </div>
    </EmptyState>
  );
}

export default EvidenceEmptyState;

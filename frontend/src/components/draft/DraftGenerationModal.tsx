'use client';

import { useState } from 'react';
import { FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { DraftTemplate } from '@/types/draft';
import { Modal, Button } from '@/components/primitives';

interface DraftGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: () => void;
  hasFactSummary?: boolean;
  templates?: DraftTemplate[];
  // Async generation progress
  progress?: number;
  status?: 'queued' | 'processing' | 'completed' | 'failed' | null;
}

export default function DraftGenerationModal({
  isOpen,
  onClose,
  onGenerate,
  hasFactSummary = false,
  templates = [
    { id: 'default', name: '기본 양식', updatedAt: '2024-05-01' },
    { id: 'custom-1', name: '이혼 소송 답변서 v1', updatedAt: '2024-05-10' },
  ],
  progress = 0,
  status = null,
}: DraftGenerationModalProps) {
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>(
    templates[0]?.id ?? 'default'
  );
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await onGenerate();
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="초안 생성"
      description="사실관계 요약을 기반으로 법률 문서 초안을 생성합니다."
      size="md"
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            취소
          </Button>
          <Button
            variant="secondary"
            onClick={handleGenerate}
            disabled={!hasFactSummary || isGenerating}
            isLoading={isGenerating}
            leftIcon={<FileText className="w-4 h-4" />}
          >
            초안 생성
          </Button>
        </>
      }
    >
      {/* Progress Bar (visible during generation) */}
      {isGenerating && status && (
        <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-700">
              {status === 'queued' && '초안 생성 대기 중...'}
              {status === 'processing' && '초안을 생성하고 있습니다...'}
              {status === 'completed' && '초안 생성 완료!'}
              {status === 'failed' && '초안 생성 실패'}
            </span>
            <span className="text-sm text-blue-600">{progress}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-blue-500 mt-2">
            AI가 사실관계 요약을 분석하여 법률 문서를 작성 중입니다. 약 30-60초 소요됩니다.
          </p>
        </div>
      )}

      {/* Fact Summary Status */}
      <div className={`p-4 rounded-lg border mb-4 ${
        hasFactSummary
          ? 'bg-green-50 border-green-200'
          : 'bg-amber-50 border-amber-200'
      }`}>
        <div className="flex items-start gap-3">
          {hasFactSummary ? (
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          )}
          <div>
            <p className={`text-sm font-medium ${
              hasFactSummary ? 'text-green-800' : 'text-amber-800'
            }`}>
              {hasFactSummary
                ? '사실관계 요약이 준비되었습니다'
                : '사실관계 요약이 필요합니다'}
            </p>
            <p className={`text-xs mt-1 ${
              hasFactSummary ? 'text-green-600' : 'text-amber-600'
            }`}>
              {hasFactSummary
                ? '사실관계 요약을 기반으로 초안을 생성합니다.'
                : '[법률분석] → [사실관계 요약] 탭에서 먼저 사실관계 요약을 생성해주세요.'}
            </p>
          </div>
        </div>
      </div>

      {/* Template Selection */}
      <div className="space-y-3">
        <label className="flex flex-col text-sm text-neutral-700">
          <span className="font-medium mb-1">템플릿 선택</span>
          <select
            aria-label="템플릿 선택"
            className="w-full px-3 py-2 border border-neutral-300 rounded-lg
                       focus:outline-none focus:ring-2 focus:ring-primary
                       bg-white text-sm transition-colors duration-200"
            value={selectedTemplateId}
            onChange={(e) => setSelectedTemplateId(e.target.value)}
            disabled={isGenerating || !hasFactSummary}
          >
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Info Text */}
      <div className="mt-4 p-3 bg-neutral-50 rounded-lg">
        <p className="text-xs text-neutral-600">
          초안은 사실관계 요약, 관련 법률 조문, 유사 판례를 참조하여 생성됩니다.
          생성된 초안은 검토 후 수정할 수 있습니다.
        </p>
      </div>
    </Modal>
  );
}

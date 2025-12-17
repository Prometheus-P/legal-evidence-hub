/**
 * StageModal Component
 * US3 - 절차 단계 관리 (Procedure Stage Tracking)
 *
 * Modal for viewing and editing stage details
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import type { ProcedureStage, ProcedureStageUpdate } from '@/types/procedure';
import {
  STAGE_LABELS,
  STATUS_LABELS,
  formatStageDate,
} from '@/types/procedure';

interface StageModalProps {
  stage: ProcedureStage | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate?: (stageId: string, data: ProcedureStageUpdate) => Promise<ProcedureStage | null>;
  onComplete?: (stageId: string, outcome?: string) => Promise<ProcedureStage | null>;
  onSkip?: (stageId: string, reason?: string) => Promise<ProcedureStage | null>;
  loading?: boolean;
}

export function StageModal({
  stage,
  isOpen,
  onClose,
  onUpdate,
  onComplete,
  onSkip,
  loading = false,
}: StageModalProps) {
  const [formData, setFormData] = useState<ProcedureStageUpdate>({});
  const [outcome, setOutcome] = useState('');
  const [skipReason, setSkipReason] = useState('');
  const [activeTab, setActiveTab] = useState<'details' | 'complete' | 'skip'>('details');

  // Reset form when stage changes
  useEffect(() => {
    if (stage) {
      setFormData({
        scheduled_date: stage.scheduled_date?.slice(0, 16) || '',
        court_reference: stage.court_reference || '',
        judge_name: stage.judge_name || '',
        court_room: stage.court_room || '',
        notes: stage.notes || '',
      });
      setOutcome(stage.outcome || '');
      setSkipReason('');
      setActiveTab('details');
    }
  }, [stage]);

  const handleInputChange = useCallback((
    field: keyof ProcedureStageUpdate,
    value: string
  ) => {
    setFormData(prev => ({ ...prev, [field]: value || undefined }));
  }, []);

  const handleSave = async () => {
    if (!stage || !onUpdate) return;

    const updateData: ProcedureStageUpdate = {};

    // Only include changed fields
    if (formData.scheduled_date && formData.scheduled_date !== stage.scheduled_date?.slice(0, 16)) {
      updateData.scheduled_date = new Date(formData.scheduled_date).toISOString();
    }
    if (formData.court_reference !== stage.court_reference) {
      updateData.court_reference = formData.court_reference || undefined;
    }
    if (formData.judge_name !== stage.judge_name) {
      updateData.judge_name = formData.judge_name || undefined;
    }
    if (formData.court_room !== stage.court_room) {
      updateData.court_room = formData.court_room || undefined;
    }
    if (formData.notes !== stage.notes) {
      updateData.notes = formData.notes || undefined;
    }

    if (Object.keys(updateData).length > 0) {
      await onUpdate(stage.id, updateData);
    }
    onClose();
  };

  const handleComplete = async () => {
    if (!stage || !onComplete) return;
    await onComplete(stage.id, outcome || undefined);
    onClose();
  };

  const handleSkip = async () => {
    if (!stage || !onSkip) return;
    await onSkip(stage.id, skipReason || undefined);
    onClose();
  };

  if (!isOpen || !stage) return null;

  const canComplete = stage.status === 'in_progress';
  const canSkip = stage.status === 'pending' || stage.status === 'in_progress';
  const canEdit = stage.status !== 'completed' && stage.status !== 'skipped';

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-lg bg-white dark:bg-neutral-800 rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-neutral-200 dark:border-neutral-700">
            <div>
              <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                {STAGE_LABELS[stage.stage]}
              </h2>
              <p className="text-sm text-neutral-500 dark:text-neutral-400">
                상태: {STATUS_LABELS[stage.status]}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          {(canComplete || canSkip) && (
            <div className="flex border-b border-neutral-200 dark:border-neutral-700">
              <button
                onClick={() => setActiveTab('details')}
                className={`flex-1 py-2 text-sm font-medium transition-colors ${
                  activeTab === 'details'
                    ? 'text-primary border-b-2 border-primary'
                    : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'
                }`}
              >
                상세 정보
              </button>
              {canComplete && (
                <button
                  onClick={() => setActiveTab('complete')}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'complete'
                      ? 'text-green-600 border-b-2 border-green-600'
                      : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'
                  }`}
                >
                  완료 처리
                </button>
              )}
              {canSkip && stage.status === 'pending' && (
                <button
                  onClick={() => setActiveTab('skip')}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'skip'
                      ? 'text-yellow-600 border-b-2 border-yellow-600'
                      : 'text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300'
                  }`}
                >
                  건너뛰기
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="p-4">
            {activeTab === 'details' && (
              <div className="space-y-4">
                {/* Dates (Read-only for completed/skipped) */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      예정일
                    </label>
                    {canEdit ? (
                      <input
                        type="datetime-local"
                        value={formData.scheduled_date || ''}
                        onChange={(e) => handleInputChange('scheduled_date', e.target.value)}
                        className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-sm"
                      />
                    ) : (
                      <p className="text-sm text-neutral-600 dark:text-neutral-400">
                        {formatStageDate(stage.scheduled_date)}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      완료일
                    </label>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 py-2">
                      {formatStageDate(stage.completed_date)}
                    </p>
                  </div>
                </div>

                {/* Court Info */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                    법원 사건번호
                  </label>
                  {canEdit ? (
                    <input
                      type="text"
                      value={formData.court_reference || ''}
                      onChange={(e) => handleInputChange('court_reference', e.target.value)}
                      placeholder="예: 2024드합12345"
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-sm"
                    />
                  ) : (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      {stage.court_reference || '-'}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      담당 판사
                    </label>
                    {canEdit ? (
                      <input
                        type="text"
                        value={formData.judge_name || ''}
                        onChange={(e) => handleInputChange('judge_name', e.target.value)}
                        className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-sm"
                      />
                    ) : (
                      <p className="text-sm text-neutral-600 dark:text-neutral-400">
                        {stage.judge_name || '-'}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      법정
                    </label>
                    {canEdit ? (
                      <input
                        type="text"
                        value={formData.court_room || ''}
                        onChange={(e) => handleInputChange('court_room', e.target.value)}
                        placeholder="예: 제301호"
                        className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-sm"
                      />
                    ) : (
                      <p className="text-sm text-neutral-600 dark:text-neutral-400">
                        {stage.court_room || '-'}
                      </p>
                    )}
                  </div>
                </div>

                {/* Outcome (read-only) */}
                {stage.outcome && (
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      결과
                    </label>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      {stage.outcome}
                    </p>
                  </div>
                )}

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                    메모
                  </label>
                  {canEdit ? (
                    <textarea
                      value={formData.notes || ''}
                      onChange={(e) => handleInputChange('notes', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-sm resize-none"
                    />
                  ) : (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      {stage.notes || '-'}
                    </p>
                  )}
                </div>

                {/* Documents */}
                {stage.documents && stage.documents.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                      첨부 문서
                    </label>
                    <ul className="text-sm text-neutral-600 dark:text-neutral-400 space-y-1">
                      {stage.documents.map((doc, idx) => (
                        <li key={idx} className="flex items-center gap-2">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            />
                          </svg>
                          {doc.name}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'complete' && (
              <div className="space-y-4">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  이 단계를 완료 처리합니다. 완료 후에는 수정할 수 없습니다.
                </p>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                    결과 (선택)
                  </label>
                  <input
                    type="text"
                    value={outcome}
                    onChange={(e) => setOutcome(e.target.value)}
                    placeholder="예: 조정 성립, 인용, 기각 등"
                    className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-sm"
                  />
                </div>
              </div>
            )}

            {activeTab === 'skip' && (
              <div className="space-y-4">
                <p className="text-sm text-neutral-600 dark:text-neutral-400">
                  이 단계를 건너뜁니다. 예: 조정 없이 본안으로 진행하는 경우
                </p>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                    건너뛴 사유 (선택)
                  </label>
                  <textarea
                    value={skipReason}
                    onChange={(e) => setSkipReason(e.target.value)}
                    rows={2}
                    placeholder="예: 당사자 간 합의로 조정 생략"
                    className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-sm resize-none"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-4 border-t border-neutral-200 dark:border-neutral-700">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-md transition-colors"
            >
              취소
            </button>
            {activeTab === 'details' && canEdit && (
              <button
                onClick={handleSave}
                disabled={loading}
                className="px-4 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary-hover transition-colors disabled:opacity-50"
              >
                {loading ? '저장 중...' : '저장'}
              </button>
            )}
            {activeTab === 'complete' && (
              <button
                onClick={handleComplete}
                disabled={loading}
                className="px-4 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {loading ? '처리 중...' : '완료 처리'}
              </button>
            )}
            {activeTab === 'skip' && (
              <button
                onClick={handleSkip}
                disabled={loading}
                className="px-4 py-2 text-sm bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors disabled:opacity-50"
              >
                {loading ? '처리 중...' : '건너뛰기'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

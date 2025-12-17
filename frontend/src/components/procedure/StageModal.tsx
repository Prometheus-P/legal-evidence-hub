/**
 * StageModal Component
 * T143 - US3: Modal for editing procedure stage details
 */

'use client';

import React, { memo, useState, useEffect, useCallback } from 'react';
import type { ProcedureStage, ProcedureStageUpdate } from '@/types/procedure';
import { STAGE_LABELS, STATUS_LABELS, STATUS_COLORS } from '@/types/procedure';

interface StageModalProps {
  stage: ProcedureStage | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (stageId: string, data: ProcedureStageUpdate) => Promise<ProcedureStage | null>;
  onComplete?: (stageId: string, outcome?: string) => Promise<ProcedureStage | null>;
  onSkip?: (stageId: string, reason?: string) => Promise<ProcedureStage | null>;
  loading?: boolean;
}

function StageModalComponent({
  stage,
  isOpen,
  onClose,
  onSave,
  onComplete,
  onSkip,
  loading = false,
}: StageModalProps) {
  const [formData, setFormData] = useState<ProcedureStageUpdate>({});
  const [saving, setSaving] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [skipping, setSkipping] = useState(false);
  const [outcome, setOutcome] = useState('');
  const [skipReason, setSkipReason] = useState('');
  const [showCompleteForm, setShowCompleteForm] = useState(false);
  const [showSkipForm, setShowSkipForm] = useState(false);

  // Reset form when stage changes
  useEffect(() => {
    if (stage) {
      setFormData({
        scheduled_date: stage.scheduled_date?.split('T')[0] || '',
        court_reference: stage.court_reference || '',
        judge_name: stage.judge_name || '',
        court_room: stage.court_room || '',
        notes: stage.notes || '',
      });
      setOutcome(stage.outcome || '');
      setSkipReason('');
      setShowCompleteForm(false);
      setShowSkipForm(false);
    }
  }, [stage]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  const handleChange = useCallback((field: keyof ProcedureStageUpdate, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleSave = useCallback(async () => {
    if (!stage) return;
    setSaving(true);
    try {
      await onSave(stage.id, formData);
      onClose();
    } finally {
      setSaving(false);
    }
  }, [stage, formData, onSave, onClose]);

  const handleComplete = useCallback(async () => {
    if (!stage || !onComplete) return;
    setCompleting(true);
    try {
      await onComplete(stage.id, outcome || undefined);
      onClose();
    } finally {
      setCompleting(false);
    }
  }, [stage, outcome, onComplete, onClose]);

  const handleSkip = useCallback(async () => {
    if (!stage || !onSkip) return;
    setSkipping(true);
    try {
      await onSkip(stage.id, skipReason || undefined);
      onClose();
    } finally {
      setSkipping(false);
    }
  }, [stage, skipReason, onSkip, onClose]);

  if (!isOpen || !stage) return null;

  const statusColor = STATUS_COLORS[stage.status];
  const isEditable = stage.status !== 'completed' && stage.status !== 'skipped';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="stage-modal-title"
    >
      <div
        className="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={`px-6 py-4 border-b border-gray-200 dark:border-gray-700 ${statusColor.bg}`}>
          <div className="flex items-center justify-between">
            <h2 id="stage-modal-title" className={`text-lg font-semibold ${statusColor.text}`}>
              {stage.stage_label || STAGE_LABELS[stage.stage]}
            </h2>
            <button
              onClick={onClose}
              className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              aria-label="닫기"
            >
              <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <span className={`inline-block mt-1 text-sm px-2 py-0.5 rounded-full ${statusColor.bg} ${statusColor.text}`}>
            {stage.status_label || STATUS_LABELS[stage.status]}
          </span>
        </div>

        {/* Body */}
        <div className="px-6 py-4 space-y-4">
          {/* Scheduled Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              예정일
            </label>
            <input
              type="date"
              value={formData.scheduled_date || ''}
              onChange={(e) => handleChange('scheduled_date', e.target.value)}
              disabled={!isEditable || loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
            />
          </div>

          {/* Court Reference */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              사건번호
            </label>
            <input
              type="text"
              value={formData.court_reference || ''}
              onChange={(e) => handleChange('court_reference', e.target.value)}
              disabled={!isEditable || loading}
              placeholder="2024드단12345"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
            />
          </div>

          {/* Court Room & Judge */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                법정
              </label>
              <input
                type="text"
                value={formData.court_room || ''}
                onChange={(e) => handleChange('court_room', e.target.value)}
                disabled={!isEditable || loading}
                placeholder="301호"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                담당 판사
              </label>
              <input
                type="text"
                value={formData.judge_name || ''}
                onChange={(e) => handleChange('judge_name', e.target.value)}
                disabled={!isEditable || loading}
                placeholder="김판사"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              메모
            </label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => handleChange('notes', e.target.value)}
              disabled={!isEditable || loading}
              rows={3}
              placeholder="단계 관련 메모..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
            />
          </div>

          {/* Outcome (if completed) */}
          {stage.outcome && (
            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-md">
              <span className="text-sm font-medium text-green-800 dark:text-green-300">결과:</span>{' '}
              <span className="text-green-700 dark:text-green-400">{stage.outcome}</span>
            </div>
          )}

          {/* Complete Form */}
          {showCompleteForm && onComplete && stage.status === 'in_progress' && (
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-md space-y-3">
              <h3 className="font-medium text-gray-900 dark:text-white">단계 완료</h3>
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  결과 (선택)
                </label>
                <input
                  type="text"
                  value={outcome}
                  onChange={(e) => setOutcome(e.target.value)}
                  placeholder="예: 조정 성립, 기각, 인용 등"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleComplete}
                  disabled={completing}
                  className="flex-1 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                >
                  {completing ? '처리 중...' : '완료 확인'}
                </button>
                <button
                  onClick={() => setShowCompleteForm(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200"
                >
                  취소
                </button>
              </div>
            </div>
          )}

          {/* Skip Form */}
          {showSkipForm && onSkip && stage.status !== 'completed' && stage.status !== 'skipped' && (
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-md space-y-3">
              <h3 className="font-medium text-gray-900 dark:text-white">단계 건너뛰기</h3>
              <div>
                <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                  사유 (선택)
                </label>
                <input
                  type="text"
                  value={skipReason}
                  onChange={(e) => setSkipReason(e.target.value)}
                  placeholder="예: 조정 불회부, 협의 이혼 등"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleSkip}
                  disabled={skipping}
                  className="flex-1 px-4 py-2 text-sm font-medium text-white bg-yellow-600 rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 disabled:opacity-50"
                >
                  {skipping ? '처리 중...' : '건너뛰기 확인'}
                </button>
                <button
                  onClick={() => setShowSkipForm(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200"
                >
                  취소
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <div className="flex gap-2">
            {onComplete && stage.status === 'in_progress' && !showCompleteForm && !showSkipForm && (
              <button
                onClick={() => setShowCompleteForm(true)}
                className="px-3 py-1.5 text-sm font-medium text-green-700 bg-green-100 rounded-md hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400"
              >
                완료하기
              </button>
            )}
            {onSkip && stage.status !== 'completed' && stage.status !== 'skipped' && !showCompleteForm && !showSkipForm && (
              <button
                onClick={() => setShowSkipForm(true)}
                className="px-3 py-1.5 text-sm font-medium text-yellow-700 bg-yellow-100 rounded-md hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400"
              >
                건너뛰기
              </button>
            )}
          </div>

          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
            >
              닫기
            </button>
            {isEditable && !showCompleteForm && !showSkipForm && (
              <button
                onClick={handleSave}
                disabled={saving || loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {saving ? '저장 중...' : '저장'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export const StageModal = memo(StageModalComponent);
export default StageModal;

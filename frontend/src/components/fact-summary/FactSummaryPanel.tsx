/**
 * Fact Summary Panel Component
 * 014-case-fact-summary: T015
 *
 * 사건 전체 사실관계 요약 패널
 * - 생성 버튼, 로딩 상태, 결과 표시
 * - 편집 모드 지원 (US2)
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Loader2, Sparkles, RefreshCw, FileText, AlertCircle, Edit3, Save, X } from 'lucide-react';
import toast from 'react-hot-toast';
import type { FactSummary, FactSummaryGenerateResponse } from '@/types/fact-summary';
import { getFactSummary, generateFactSummary, updateFactSummary } from '@/lib/api/fact-summary';

interface FactSummaryPanelProps {
  caseId: string;
  className?: string;
  hideHeader?: boolean;
}

export function FactSummaryPanel({ caseId, className = '', hideHeader = false }: FactSummaryPanelProps) {
  // Data state
  const [factSummary, setFactSummary] = useState<FactSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Edit state (US2)
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Regenerate confirmation modal state (US5 T030)
  const [showRegenerateModal, setShowRegenerateModal] = useState(false);

  // Fetch existing fact summary on mount
  const fetchFactSummary = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getFactSummary(caseId);
      if (response.error) {
        // 404 is expected when no summary exists yet
        if (response.status === 404) {
          setFactSummary(null);
        } else {
          setError(response.error);
        }
      } else if (response.data) {
        setFactSummary(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '사실관계를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchFactSummary();
  }, [fetchFactSummary]);

  // T021: Unsaved changes warning (beforeunload)
  useEffect(() => {
    const hasUnsavedChanges = isEditing && editContent !== (factSummary?.modified_summary || factSummary?.ai_summary || '');

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '저장하지 않은 변경사항이 있습니다. 정말 나가시겠습니까?';
        return e.returnValue;
      }
    };

    if (hasUnsavedChanges) {
      window.addEventListener('beforeunload', handleBeforeUnload);
      return () => window.removeEventListener('beforeunload', handleBeforeUnload);
    }
  }, [isEditing, editContent, factSummary]);

  // Generate fact summary
  const handleGenerate = async (forceRegenerate = false) => {
    setGenerating(true);
    setError(null);

    try {
      const response = await generateFactSummary(caseId, { force_regenerate: forceRegenerate });
      if (response.error) {
        setError(response.error);
        toast.error(response.error);
      } else if (response.data) {
        // Refresh to get full data
        await fetchFactSummary();
        toast.success('사실관계가 생성되었습니다.');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '사실관계 생성 중 오류가 발생했습니다.';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setGenerating(false);
    }
  };

  // Start editing
  const handleStartEdit = () => {
    const content = factSummary?.modified_summary || factSummary?.ai_summary || '';
    setEditContent(content);
    setIsEditing(true);
  };

  // Cancel editing
  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditContent('');
  };

  // Save edited content
  const handleSaveEdit = async () => {
    if (!editContent.trim()) {
      toast.error('내용을 입력해주세요.');
      return;
    }

    setIsSaving(true);
    try {
      const response = await updateFactSummary(caseId, { modified_summary: editContent });
      if (response.error) {
        toast.error(response.error);
      } else if (response.data) {
        await fetchFactSummary();
        setIsEditing(false);
        setEditContent('');
        toast.success('사실관계가 저장되었습니다.');
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : '저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  // Get display content
  const displayContent = factSummary?.modified_summary || factSummary?.ai_summary || '';
  const isModified = !!factSummary?.modified_summary;

  // T033: Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="animate-pulse space-y-4">
      {/* Header skeleton */}
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 bg-gray-200 dark:bg-neutral-700 rounded" />
        <div className="h-5 w-32 bg-gray-200 dark:bg-neutral-700 rounded" />
      </div>
      {/* Fault types skeleton */}
      <div className="flex gap-2">
        <div className="h-5 w-16 bg-gray-200 dark:bg-neutral-700 rounded" />
        <div className="h-5 w-20 bg-gray-200 dark:bg-neutral-700 rounded" />
      </div>
      {/* Content skeleton */}
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-full" />
        <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-5/6" />
        <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-4/5" />
        <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-full" />
        <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-3/4" />
      </div>
      {/* Action buttons skeleton */}
      <div className="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-neutral-700">
        <div className="h-4 w-40 bg-gray-200 dark:bg-neutral-700 rounded" />
        <div className="flex gap-2">
          <div className="h-8 w-16 bg-gray-200 dark:bg-neutral-700 rounded" />
          <div className="h-8 w-20 bg-gray-200 dark:bg-neutral-700 rounded" />
        </div>
      </div>
    </div>
  );

  // Render content based on state
  const renderContent = () => {
    // Loading state - T033: Use skeleton UI
    if (loading) {
      return <LoadingSkeleton />;
    }

    // Error state
    if (error && !factSummary) {
      return (
        <div className="text-center py-8">
          <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-500 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={fetchFactSummary}
            className="px-4 py-2 bg-gray-200 dark:bg-neutral-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-neutral-600 transition-colors"
          >
            다시 시도
          </button>
        </div>
      );
    }

    // Empty state - no summary yet
    if (!factSummary) {
      return (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
            <FileText className="w-8 h-8 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
            사실관계 요약
          </h3>
          <p className="text-[var(--color-text-secondary)] mb-6 max-w-md mx-auto">
            등록된 증거 자료를 기반으로 AI가 사건 전체의 사실관계를 시간순으로 정리합니다.
          </p>
          <button
            onClick={() => handleGenerate(false)}
            disabled={generating}
            className="inline-flex items-center px-6 py-3 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors disabled:opacity-50"
          >
            {generating ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                생성 중...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                사실관계 생성
              </>
            )}
          </button>
        </div>
      );
    }

    // Generating state (with existing summary)
    if (generating) {
      return (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-purple-600 dark:text-purple-400 animate-spin" />
          </div>
          <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
            사실관계 생성 중...
          </h3>
          <p className="text-[var(--color-text-secondary)]">
            AI가 증거를 분석하고 사실관계를 정리하고 있습니다.
          </p>
        </div>
      );
    }

    // Edit mode
    if (isEditing) {
      return (
        <div className="space-y-4">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full h-96 p-4 border border-gray-300 dark:border-neutral-600 rounded-lg
                       bg-white dark:bg-neutral-800 text-[var(--color-text-primary)]
                       focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent
                       resize-none"
            placeholder="사실관계를 입력하세요..."
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={handleCancelEdit}
              disabled={isSaving}
              className="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]
                         border border-gray-300 dark:border-neutral-600 rounded-lg transition-colors"
            >
              <X className="w-4 h-4 inline mr-1" />
              취소
            </button>
            <button
              onClick={handleSaveEdit}
              disabled={isSaving}
              className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg
                         hover:bg-[var(--color-primary-hover)] transition-colors disabled:opacity-50"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 inline mr-1 animate-spin" />
                  저장 중...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 inline mr-1" />
                  저장
                </>
              )}
            </button>
          </div>
        </div>
      );
    }

    // Display content
    return (
      <div className="space-y-4">
        {/* Content display */}
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <div className="whitespace-pre-wrap text-[var(--color-text-primary)] leading-relaxed">
            {displayContent}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-neutral-700">
          <div className="text-xs text-[var(--color-text-secondary)]">
            {isModified ? (
              <span>수정됨: {new Date(factSummary.modified_at!).toLocaleString('ko-KR')}</span>
            ) : (
              <span>생성됨: {new Date(factSummary.created_at).toLocaleString('ko-KR')}</span>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleStartEdit}
              className="px-3 py-1.5 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]
                         border border-gray-300 dark:border-neutral-600 rounded transition-colors"
            >
              <Edit3 className="w-4 h-4 inline mr-1" />
              수정
            </button>
            <button
              onClick={() => setShowRegenerateModal(true)}
              disabled={generating}
              className="px-3 py-1.5 text-sm text-[var(--color-primary)] hover:bg-[var(--color-primary)]/10
                         border border-[var(--color-primary)] rounded transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 inline mr-1 ${generating ? 'animate-spin' : ''}`} />
              재생성
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 ${className}`}>
      {/* Header */}
      {!hideHeader && (
        <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-800 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <h2 className="font-semibold text-gray-900 dark:text-gray-100">사실관계 요약</h2>
          </div>
          {factSummary && (
            <div className="flex items-center gap-2">
              {isModified && (
                <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                  수정됨
                </span>
              )}
              <span className="text-sm text-gray-500 dark:text-gray-400">
                증거 {factSummary.evidence_ids.length}건 기반
              </span>
            </div>
          )}
        </div>
      )}

      {/* Fault Types */}
      {factSummary && factSummary.fault_types.length > 0 && (
        <div className="px-4 py-2 bg-gray-50 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-800">
          <span className="text-xs text-gray-500 dark:text-gray-400">유책사유: </span>
          <span className="text-xs text-gray-700 dark:text-gray-300">
            {factSummary.fault_types.join(', ')}
          </span>
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        {renderContent()}
      </div>

      {/* T030: Regenerate Confirmation Modal */}
      {showRegenerateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-3">
              사실관계 재생성
            </h3>
            <p className="text-[var(--color-text-secondary)] mb-6">
              {isModified
                ? '기존 수정 내용이 백업되고 새로운 AI 요약이 생성됩니다. 계속하시겠습니까?'
                : '최신 증거를 반영하여 새로운 AI 요약이 생성됩니다. 계속하시겠습니까?'}
            </p>
            {isModified && (
              <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-700 dark:text-yellow-400">
                  현재 수정된 내용은 이전 버전으로 백업됩니다.
                </p>
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowRegenerateModal(false)}
                className="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]
                           border border-gray-300 dark:border-neutral-600 rounded-lg transition-colors"
              >
                취소
              </button>
              <button
                onClick={() => {
                  setShowRegenerateModal(false);
                  handleGenerate(true);
                }}
                className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg
                           hover:bg-[var(--color-primary-hover)] transition-colors"
              >
                재생성
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FactSummaryPanel;

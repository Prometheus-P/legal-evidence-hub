/**
 * Evidence DataTable Component
 * Shadcn/ui style with TanStack Table integration
 *
 * Responsibilities:
 * - Render table structure
 * - Display evidence data with sorting
 * - Integrate with useEvidenceTable hook for logic
 */

import { useState } from 'react';
import { logger } from '@/lib/logger';
import { flexRender } from '@tanstack/react-table';
import { ArrowUpDown, MoreVertical, Filter, Sparkles, X, FileText, Loader2, RefreshCw, Users } from 'lucide-react';
import { Evidence } from '@/types/evidence';
import type { PartyNode } from '@/types/party';
import { useEvidenceTable } from '@/hooks/useEvidenceTable';
import { EvidenceTypeIcon } from './EvidenceTypeIcon';
import { EvidenceStatusBadge } from './EvidenceStatusBadge';
import { SpeakerMappingBadge } from './SpeakerMappingBadge';
import { SpeakerMappingModal } from './SpeakerMappingModal';
import { DataTablePagination } from './DataTablePagination';
import { getEvidenceDetail, retryEvidence, updateSpeakerMapping } from '@/lib/api/evidence';
import type { SpeakerMapping } from '@/lib/api/evidence';

/**
 * AI Summary Modal Component
 */
function AISummaryModal({
  isOpen,
  onClose,
  evidence
}: {
  isOpen: boolean;
  onClose: () => void;
  evidence: Evidence | null;
}) {
  if (!isOpen || !evidence) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6 animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-bold text-gray-900">AI 요약</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-500 mb-1">파일명</p>
          <p className="text-sm font-medium text-gray-900">{evidence.filename}</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
            {evidence.summary || '요약이 아직 생성되지 않았습니다.'}
          </p>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Evidence Content Modal Component (원문 보기)
 * T016: 화자 매핑 버튼 추가
 */
function ContentModal({
  isOpen,
  onClose,
  evidence,
  content,
  isLoading,
  showSpeakerMappingButton,
  onOpenSpeakerMapping,
}: {
  isOpen: boolean;
  onClose: () => void;
  evidence: Evidence | null;
  content: string | null;
  isLoading: boolean;
  /** 015-evidence-speaker-mapping: 화자 매핑 버튼 표시 여부 */
  showSpeakerMappingButton?: boolean;
  /** 015-evidence-speaker-mapping: 화자 매핑 버튼 클릭 핸들러 */
  onOpenSpeakerMapping?: () => void;
}) {
  if (!isOpen || !evidence) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[80vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-start justify-between p-6 border-b border-gray-100">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-secondary" />
            <h3 className="text-lg font-bold text-gray-900">증거 원문</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="px-6 py-3 bg-gray-50 border-b border-gray-100">
          <p className="text-sm text-gray-500">파일명</p>
          <p className="text-sm font-medium text-gray-900">{evidence.filename}</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
              <span className="ml-2 text-gray-500">원문을 불러오는 중...</span>
            </div>
          ) : content ? (
            <pre className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap font-sans">
              {content}
            </pre>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>원문이 아직 추출되지 않았습니다.</p>
              <p className="text-xs mt-1">AI 분석이 완료되면 원문을 볼 수 있습니다.</p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-100 flex justify-between">
          {/* T016: 화자 매핑 버튼 */}
          <div>
            {showSpeakerMappingButton && content && (
              <button
                onClick={onOpenSpeakerMapping}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              >
                <Users className="w-4 h-4 mr-2" />
                화자 매핑
              </button>
            )}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}

interface EvidenceDataTableProps {
  items: Evidence[];
  onRetry?: (evidenceId: string) => void;
  /** 015-evidence-speaker-mapping: 인물관계도의 당사자 목록 */
  parties?: PartyNode[];
  /** 015-evidence-speaker-mapping: 화자 매핑 저장 후 콜백 */
  onSpeakerMappingUpdate?: (evidenceId: string) => void;
}

export function EvidenceDataTable({ items, onRetry, parties = [], onSpeakerMappingUpdate }: EvidenceDataTableProps) {
  const [typeFilter, setTypeFilterValue] = useState<string>('all');
  const [dateFilter, setDateFilterValue] = useState<string>('all');
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [isSummaryModalOpen, setIsSummaryModalOpen] = useState(false);
  const [isContentModalOpen, setIsContentModalOpen] = useState(false);
  const [evidenceContent, setEvidenceContent] = useState<string | null>(null);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [retryingIds, setRetryingIds] = useState<Set<string>>(new Set());

  // 015-evidence-speaker-mapping: 화자 매핑 모달 상태
  const [isSpeakerMappingModalOpen, setIsSpeakerMappingModalOpen] = useState(false);
  const [speakerMappingEvidence, setSpeakerMappingEvidence] = useState<Evidence | null>(null);

  const { table, setTypeFilter, setDateFilter } = useEvidenceTable(items);

  const handleRetry = async (evidenceId: string) => {
    setRetryingIds((prev) => new Set(prev).add(evidenceId));
    try {
      await retryEvidence(evidenceId);
      onRetry?.(evidenceId);
    } catch (err) {
      logger.error('Failed to retry evidence:', err);
    } finally {
      setRetryingIds((prev) => {
        const next = new Set(prev);
        next.delete(evidenceId);
        return next;
      });
    }
  };

  const handleOpenSummary = (evidence: Evidence) => {
    setSelectedEvidence(evidence);
    setIsSummaryModalOpen(true);
  };

  const handleCloseSummary = () => {
    setIsSummaryModalOpen(false);
    setSelectedEvidence(null);
  };

  const handleOpenContent = async (evidence: Evidence) => {
    setSelectedEvidence(evidence);
    setIsContentModalOpen(true);
    setIsLoadingContent(true);
    setEvidenceContent(null);

    try {
      const result = await getEvidenceDetail(evidence.id);
      if (result.data?.content) {
        setEvidenceContent(result.data.content);
      }
    } catch (err) {
      logger.error('Failed to fetch evidence content:', err);
    } finally {
      setIsLoadingContent(false);
    }
  };

  const handleCloseContent = () => {
    setIsContentModalOpen(false);
    setSelectedEvidence(null);
    setEvidenceContent(null);
  };

  // 015-evidence-speaker-mapping: 화자 매핑 모달 핸들러
  const handleOpenSpeakerMapping = (evidence: Evidence) => {
    setSpeakerMappingEvidence(evidence);
    setIsSpeakerMappingModalOpen(true);
  };

  const handleCloseSpeakerMapping = () => {
    setIsSpeakerMappingModalOpen(false);
    setSpeakerMappingEvidence(null);
  };

  const handleSaveSpeakerMapping = async (mapping: SpeakerMapping) => {
    if (!speakerMappingEvidence) return;

    const response = await updateSpeakerMapping(speakerMappingEvidence.id, {
      speaker_mapping: mapping,
    });

    if (response.error) {
      throw new Error(response.error);
    }

    // 매핑 업데이트 콜백 호출 (목록 새로고침용)
    onSpeakerMappingUpdate?.(speakerMappingEvidence.id);
  };

  const handleTypeFilterChange = (value: string) => {
    setTypeFilterValue(value);
    setTypeFilter(value);
  };

  const handleDateFilterChange = (value: string) => {
    setDateFilterValue(value);
    setDateFilter(value);
  };

  return (
    <div className="space-y-4">
      {/* Filter Controls - Calm Control UX */}
      <div className="flex items-center space-x-4 bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
        <Filter className="w-5 h-5 text-gray-400" />

        <div className="flex items-center space-x-2">
          <label htmlFor="type-filter" className="text-sm font-medium text-neutral-700">
            유형 필터:
          </label>
          <select
            id="type-filter"
            value={typeFilter}
            onChange={(e) => handleTypeFilterChange(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary transition-all"
          >
            <option value="all">전체</option>
            <option value="text">텍스트</option>
            <option value="image">이미지</option>
            <option value="audio">오디오</option>
            <option value="video">비디오</option>
            <option value="pdf">PDF</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label htmlFor="date-filter" className="text-sm font-medium text-neutral-700">
            날짜 필터:
          </label>
          <select
            id="date-filter"
            value={dateFilter}
            onChange={(e) => handleDateFilterChange(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary transition-all"
          >
            <option value="all">전체</option>
            <option value="today">오늘</option>
            <option value="week">최근 7일</option>
            <option value="month">최근 30일</option>
          </select>
        </div>

        <div className="text-sm text-gray-500 ml-auto">
          {table.getFilteredRowModel().rows.length}개 / 전체 {items.length}개
        </div>
      </div>

      {/* DataTable - Shadcn/ui style */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200" aria-label="증거 자료 목록">
            <caption className="sr-only">
              증거 자료 목록. 번호, 유형, 파일명, AI 요약, 업로드 날짜, 상태 열이 있습니다.
              파일명과 업로드 날짜는 정렬 가능합니다.
              번호는 사실관계 요약의 [증거N] 형식과 일치합니다.
            </caption>
            <thead className="bg-gray-50">
              <tr>
                {/* 증거 번호 열 - 사실관계 요약의 [증거N] 참조용 */}
                <th
                  scope="col"
                  className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20"
                >
                  번호
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  유형
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  aria-sort={
                    table.getColumn('filename')?.getIsSorted() === 'asc'
                      ? 'ascending'
                      : table.getColumn('filename')?.getIsSorted() === 'desc'
                        ? 'descending'
                        : 'none'
                  }
                >
                  <button
                    type="button"
                    onClick={() => table.getColumn('filename')?.toggleSorting()}
                    className="flex items-center space-x-1 hover:text-secondary transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded"
                    aria-label="파일명으로 정렬"
                  >
                    <span>파일명</span>
                    <ArrowUpDown className="w-4 h-4" aria-hidden="true" />
                  </button>
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  AI 요약
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  aria-sort={
                    table.getColumn('uploadDate')?.getIsSorted() === 'asc'
                      ? 'ascending'
                      : table.getColumn('uploadDate')?.getIsSorted() === 'desc'
                        ? 'descending'
                        : 'none'
                  }
                >
                  <button
                    type="button"
                    onClick={() => table.getColumn('uploadDate')?.toggleSorting()}
                    className="flex items-center space-x-1 hover:text-secondary transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded"
                    aria-label="업로드 날짜로 정렬"
                  >
                    <span>업로드 날짜</span>
                    <ArrowUpDown className="w-4 h-4" aria-hidden="true" />
                  </button>
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  상태
                </th>
                {/* 015-evidence-speaker-mapping: 화자 매핑 열 */}
                {parties.length > 0 && (
                  <th
                    scope="col"
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    화자
                  </th>
                )}
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {table.getRowModel().rows.map((row, index) => {
                const evidence = row.original;
                const zebraBackground = index % 2 === 0 ? 'bg-white' : 'bg-gray-50/70';
                // 전체 정렬된 데이터에서의 순서 번호 계산 (페이지네이션 고려)
                const pageIndex = table.getState().pagination.pageIndex;
                const pageSize = table.getState().pagination.pageSize;
                const evidenceNumber = pageIndex * pageSize + index + 1;

                return (
                  <tr
                    key={evidence.id}
                    className={`group transition-colors ${zebraBackground} hover:bg-primary-light/50`}
                  >
                    {/* 증거 번호 - 사실관계 요약의 [증거N] 참조용 */}
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 text-sm font-bold text-primary bg-primary-light rounded-full">
                        {evidenceNumber}
                      </span>
                    </td>

                    {/* Type Icon - 클릭하면 원문 보기 */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        type="button"
                        onClick={() => handleOpenContent(evidence)}
                        className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                        aria-label={`${evidence.filename} 원문 보기`}
                      >
                        <EvidenceTypeIcon type={evidence.type} />
                      </button>
                    </td>

                    {/* Filename */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {evidence.filename}
                      </div>
                      <div className="text-xs text-gray-500">
                        {(evidence.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                      <div className="text-[11px] text-gray-400 hidden group-hover:block mt-1">
                        클릭하여 상세 · 타임라인 연결 옵션 보기
                      </div>
                    </td>

                    {/* AI Summary */}
                    <td className="px-6 py-4">
                      {evidence.status === 'completed' && evidence.summary ? (
                        <button
                          type="button"
                          onClick={() => handleOpenSummary(evidence)}
                          className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-sm font-medium text-primary bg-primary-light hover:bg-primary-light/80 rounded-lg transition-colors"
                        >
                          <Sparkles className="w-4 h-4" />
                          <span>요약 보기</span>
                        </button>
                      ) : evidence.status === 'processing' || evidence.status === 'queued' ? (
                        <span className="text-sm text-gray-400">분석 중...</span>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>

                    {/* Upload Date */}
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(evidence.uploadDate).toLocaleDateString()}
                    </td>

                    {/* Status Badge */}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <EvidenceStatusBadge status={evidence.status} />
                        {evidence.status === 'failed' && (
                          <button
                            type="button"
                            onClick={() => handleRetry(evidence.id)}
                            disabled={retryingIds.has(evidence.id)}
                            className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors disabled:opacity-50"
                            title="재시도"
                          >
                            <RefreshCw className={`w-3 h-3 ${retryingIds.has(evidence.id) ? 'animate-spin' : ''}`} />
                            {retryingIds.has(evidence.id) ? '재시도 중...' : '재시도'}
                          </button>
                        )}
                      </div>
                    </td>

                    {/* 015-evidence-speaker-mapping: 화자 매핑 뱃지 (T027) */}
                    {parties.length > 0 && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <SpeakerMappingBadge
                          hasSpeakerMapping={evidence.hasSpeakerMapping}
                          speakerMapping={evidence.speakerMapping}
                          onClick={() => handleOpenSpeakerMapping(evidence)}
                        />
                      </td>
                    )}

                    {/* Actions */}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        type="button"
                        className="text-gray-400 hover:text-neutral-600 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
                        aria-label={`${evidence.filename} 추가 작업`}
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <DataTablePagination table={table} />
      </div>

      {/* AI Summary Modal */}
      <AISummaryModal
        isOpen={isSummaryModalOpen}
        onClose={handleCloseSummary}
        evidence={selectedEvidence}
      />

      {/* Content Modal (원문 보기) */}
      <ContentModal
        isOpen={isContentModalOpen}
        onClose={handleCloseContent}
        evidence={selectedEvidence}
        content={evidenceContent}
        isLoading={isLoadingContent}
        showSpeakerMappingButton={parties.length > 0}
        onOpenSpeakerMapping={() => {
          if (selectedEvidence) {
            handleCloseContent();
            handleOpenSpeakerMapping(selectedEvidence);
          }
        }}
      />

      {/* 015-evidence-speaker-mapping: 화자 매핑 모달 */}
      {speakerMappingEvidence && (
        <SpeakerMappingModal
          isOpen={isSpeakerMappingModalOpen}
          onClose={handleCloseSpeakerMapping}
          evidence={speakerMappingEvidence}
          parties={parties}
          onSave={handleSaveSpeakerMapping}
          onSaveSuccess={() => {
            // 목록 새로고침
            onSpeakerMappingUpdate?.(speakerMappingEvidence.id);
          }}
        />
      )}
    </div>
  );
}

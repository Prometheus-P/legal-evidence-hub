'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle2,
  XCircle,
  Edit3,
  ArrowRight,
  Filter,
  Loader2,
  RefreshCw,
  FileText,
  Tag,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import {
  getCandidates,
  updateCandidate,
  promoteCandidates,
  getPipelineStats,
  Candidate,
  PipelineStats,
  CandidateUpdateRequest,
} from '@/lib/api/lssp';
import { logger } from '@/lib/logger';

interface PipelinePanelProps {
  caseId: string;
  onRefresh?: () => void;
}

type StatusFilter = 'ALL' | 'CANDIDATE' | 'ACCEPTED' | 'REJECTED';

const STATUS_LABELS: Record<Candidate['status'], string> = {
  CANDIDATE: '검토 대기',
  ACCEPTED: '수락됨',
  REJECTED: '거절됨',
  MERGED: '병합됨',
};

const STATUS_COLORS: Record<Candidate['status'], string> = {
  CANDIDATE: 'bg-yellow-100 text-yellow-700',
  ACCEPTED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
  MERGED: 'bg-purple-100 text-purple-700',
};

const KIND_LABELS: Record<string, string> = {
  ADMISSION: '부정행위 인정',
  THREAT: '위협/폭력',
  SEPARATION: '별거/유기',
  SPENDING: '금전 지출',
  MEDICAL: '의료/진단',
  POLICE_CASE: '경찰 사건',
  DATE_EVENT: '날짜/일시',
  PERSON: '인물',
  LOCATION: '장소',
};

export function PipelinePanel({ caseId, onRefresh }: PipelinePanelProps) {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [stats, setStats] = useState<PipelineStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [processingIds, setProcessingIds] = useState<Set<number>>(new Set());
  const [isPromoting, setIsPromoting] = useState(false);

  // Load candidates and stats
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [candidatesRes, statsRes] = await Promise.all([
        getCandidates(caseId, {
          status: statusFilter === 'ALL' ? undefined : statusFilter,
          limit: 100,
        }),
        getPipelineStats(caseId),
      ]);

      if (candidatesRes.error) {
        throw new Error(typeof candidatesRes.error === 'string' ? candidatesRes.error : 'Failed to load candidates');
      }
      if (statsRes.error) {
        throw new Error(typeof statsRes.error === 'string' ? statsRes.error : 'Failed to load stats');
      }

      setCandidates(candidatesRes.data || []);
      setStats(statsRes.data || null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load data';
      setError(message);
      logger.error('Pipeline data load failed:', err);
    } finally {
      setIsLoading(false);
    }
  }, [caseId, statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle accept/reject
  const handleUpdateStatus = async (
    candidateId: number,
    newStatus: 'ACCEPTED' | 'REJECTED',
    rejectionReason?: string
  ) => {
    setProcessingIds((prev) => new Set(prev).add(candidateId));

    try {
      const data: CandidateUpdateRequest = { status: newStatus };
      if (newStatus === 'REJECTED' && rejectionReason) {
        data.rejection_reason = rejectionReason;
      }

      const response = await updateCandidate(caseId, candidateId, data);
      if (response.error) {
        throw new Error(typeof response.error === 'string' ? response.error : 'Failed to update candidate');
      }

      // Update local state
      setCandidates((prev) =>
        prev.map((c) =>
          c.candidate_id === candidateId
            ? { ...c, status: newStatus, rejection_reason: rejectionReason || null }
            : c
        )
      );

      // Update stats
      setStats((prev) => {
        if (!prev) return prev;
        const delta = newStatus === 'ACCEPTED' ? 1 : 0;
        return {
          ...prev,
          pending_candidates: prev.pending_candidates - 1,
          accepted_candidates: prev.accepted_candidates + delta,
          rejected_candidates: prev.rejected_candidates + (newStatus === 'REJECTED' ? 1 : 0),
        };
      });
    } catch (err) {
      logger.error('Failed to update candidate:', err);
    } finally {
      setProcessingIds((prev) => {
        const next = new Set(prev);
        next.delete(candidateId);
        return next;
      });
    }
  };

  // Handle promote
  const handlePromote = async () => {
    const acceptedIds = candidates
      .filter((c) => c.status === 'ACCEPTED')
      .map((c) => c.candidate_id);

    if (acceptedIds.length === 0) {
      return;
    }

    setIsPromoting(true);

    try {
      const response = await promoteCandidates(caseId, {
        candidate_ids: acceptedIds,
        merge_similar: false,
      });

      if (response.error) {
        throw new Error(typeof response.error === 'string' ? response.error : 'Failed to promote candidates');
      }

      // Reload data and notify parent
      await loadData();
      onRefresh?.();
    } catch (err) {
      logger.error('Failed to promote candidates:', err);
    } finally {
      setIsPromoting(false);
    }
  };

  // Toggle selection
  const toggleSelection = (candidateId: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(candidateId)) {
        next.delete(candidateId);
      } else {
        next.add(candidateId);
      }
      return next;
    });
  };

  // Get confidence color
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Stats summary
  const acceptedCount = candidates.filter((c) => c.status === 'ACCEPTED').length;
  const pendingCount = candidates.filter((c) => c.status === 'CANDIDATE').length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <span className="ml-3 text-gray-600">후보 데이터를 불러오는 중...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
          <AlertTriangle className="w-8 h-8 text-red-500" />
        </div>
        <h3 className="text-gray-900 font-medium mb-1">데이터 로드 실패</h3>
        <p className="text-sm text-gray-500 mb-4">{error}</p>
        <button
          onClick={loadData}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90"
        >
          <RefreshCw className="w-4 h-4" />
          다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Stats Bar */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {stats.total_candidates}
            </div>
            <div className="text-xs text-gray-500">총 후보</div>
          </div>
          <div className="bg-yellow-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-semibold text-yellow-700">
              {stats.pending_candidates}
            </div>
            <div className="text-xs text-yellow-600">검토 대기</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-semibold text-green-700">
              {stats.accepted_candidates}
            </div>
            <div className="text-xs text-green-600">수락됨</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <div className="text-2xl font-semibold text-blue-700">
              {stats.promoted_keypoints}
            </div>
            <div className="text-xs text-blue-600">정식 쟁점</div>
          </div>
        </div>
      )}

      {/* Filter & Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            <option value="ALL">전체 상태</option>
            <option value="CANDIDATE">검토 대기</option>
            <option value="ACCEPTED">수락됨</option>
            <option value="REJECTED">거절됨</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadData}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </button>
          <button
            onClick={handlePromote}
            disabled={acceptedCount === 0 || isPromoting}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isPromoting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ArrowRight className="w-4 h-4" />
            )}
            정식 승격 ({acceptedCount})
          </button>
        </div>
      </div>

      {/* Candidates List */}
      {candidates.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
            <FileText className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-gray-900 font-medium mb-1">후보가 없습니다</h3>
          <p className="text-sm text-gray-500">
            증거 파일에서 쟁점을 추출하면 여기에 후보가 표시됩니다.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {candidates.map((candidate) => {
            const isExpanded = expandedId === candidate.candidate_id;
            const isProcessing = processingIds.has(candidate.candidate_id);

            return (
              <div
                key={candidate.candidate_id}
                className={`border rounded-lg transition-all ${
                  candidate.status === 'ACCEPTED'
                    ? 'border-green-200 bg-green-50/50'
                    : candidate.status === 'REJECTED'
                    ? 'border-red-200 bg-red-50/50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                {/* Main Row */}
                <div className="p-4">
                  <div className="flex items-start gap-3">
                    {/* Expand Toggle */}
                    <button
                      onClick={() =>
                        setExpandedId(isExpanded ? null : candidate.candidate_id)
                      }
                      className="mt-0.5 text-gray-400 hover:text-gray-600"
                    >
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </button>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {/* Kind Badge */}
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                          <Tag className="w-3 h-3" />
                          {KIND_LABELS[candidate.kind] || candidate.kind}
                        </span>

                        {/* Status Badge */}
                        <span
                          className={`px-2 py-0.5 text-xs font-medium rounded ${
                            STATUS_COLORS[candidate.status]
                          }`}
                        >
                          {STATUS_LABELS[candidate.status]}
                        </span>

                        {/* Confidence */}
                        <span
                          className={`text-xs font-medium ${getConfidenceColor(
                            candidate.confidence
                          )}`}
                        >
                          {Math.round(candidate.confidence * 100)}%
                        </span>

                        {/* Ground Tags */}
                        {candidate.ground_tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-1.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>

                      {/* Content */}
                      <p className="text-sm text-gray-900">{candidate.content}</p>

                      {/* Rule Name */}
                      {candidate.rule_name && (
                        <p className="text-xs text-gray-500 mt-1">
                          <Sparkles className="w-3 h-3 inline mr-1" />
                          규칙: {candidate.rule_name}
                        </p>
                      )}
                    </div>

                    {/* Actions */}
                    {candidate.status === 'CANDIDATE' && (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() =>
                            handleUpdateStatus(candidate.candidate_id, 'ACCEPTED')
                          }
                          disabled={isProcessing}
                          className="p-1.5 text-green-600 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50"
                          title="수락"
                        >
                          {isProcessing ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <CheckCircle2 className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() =>
                            handleUpdateStatus(candidate.candidate_id, 'REJECTED')
                          }
                          disabled={isProcessing}
                          className="p-1.5 text-red-600 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
                          title="거절"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                        <button
                          className="p-1.5 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors"
                          title="수정"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t border-gray-100 px-4 py-3 bg-gray-50/50">
                    <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                      <div>
                        <dt className="text-gray-500">증거 ID</dt>
                        <dd className="text-gray-900 font-mono text-xs">
                          {candidate.evidence_id}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-gray-500">물리성</dt>
                        <dd className="text-gray-900">{candidate.materiality}%</dd>
                      </div>
                      {candidate.source_span && (
                        <div>
                          <dt className="text-gray-500">위치</dt>
                          <dd className="text-gray-900">
                            {candidate.source_span.start} - {candidate.source_span.end}
                          </dd>
                        </div>
                      )}
                      {candidate.rejection_reason && (
                        <div className="col-span-2">
                          <dt className="text-gray-500">거절 사유</dt>
                          <dd className="text-red-600">{candidate.rejection_reason}</dd>
                        </div>
                      )}
                      <div>
                        <dt className="text-gray-500">생성일</dt>
                        <dd className="text-gray-900">
                          {new Date(candidate.created_at).toLocaleString('ko-KR')}
                        </dd>
                      </div>
                    </dl>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

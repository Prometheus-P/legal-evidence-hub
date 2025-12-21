'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  FileText,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Plus,
  Sparkles,
  Scale,
  Loader2,
  ChevronRight,
  ChevronDown,
  GitBranch,
  BookOpen,
} from 'lucide-react';
import {
  getKeypoints,
  getLegalGrounds,
  getDraftTemplates,
  extractKeypoints,
  getPipelineStats,
  Keypoint,
  LegalGround,
  DraftTemplate,
  PipelineStats,
} from '@/lib/api/lssp';
import { KeypointList } from './KeypointList';
import { LegalGroundSummary } from './LegalGroundSummary';
import { PipelinePanel } from './PipelinePanel';
import { PrecedentPanel } from '../precedent/PrecedentPanel';
import { LSSPStatCard } from './LSSPStatCard';
import { logger } from '@/lib/logger';

interface LSSPPanelProps {
  caseId: string;
  evidenceCount: number;
  onDraftGenerate?: (templateId: string) => void;
}

export function LSSPPanel({ caseId, evidenceCount, onDraftGenerate }: LSSPPanelProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [keypoints, setKeypoints] = useState<Keypoint[]>([]);
  const [legalGrounds, setLegalGrounds] = useState<LegalGround[]>([]);
  const [templates, setTemplates] = useState<DraftTemplate[]>([]);
  const [pipelineStats, setPipelineStats] = useState<PipelineStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial data
  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [keypointsRes, groundsRes, templatesRes, pipelineRes] = await Promise.all([
        getKeypoints(caseId),
        getLegalGrounds(),
        getDraftTemplates({ active_only: true }),
        getPipelineStats(caseId),
      ]);

      if (keypointsRes.data) {
        setKeypoints(keypointsRes.data.keypoints);
      }
      if (groundsRes.data) {
        setLegalGrounds(groundsRes.data);
      }
      if (templatesRes.data) {
        setTemplates(templatesRes.data);
      }
      if (pipelineRes.data) {
        setPipelineStats(pipelineRes.data);
      }
    } catch (err) {
      logger.error('Failed to fetch LSSP data:', err);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Extract keypoints from evidence
  const handleExtractKeypoints = async () => {
    if (isExtracting) return;

    setIsExtracting(true);
    try {
      const response = await extractKeypoints(caseId);
      if (response.error) {
        setError(response.error);
      } else {
        // Refresh keypoints after extraction
        const keypointsRes = await getKeypoints(caseId);
        if (keypointsRes.data) {
          setKeypoints(keypointsRes.data.keypoints);
        }
      }
    } catch (err) {
      logger.error('Failed to extract keypoints:', err);
      setError('핵심 쟁점 추출에 실패했습니다.');
    } finally {
      setIsExtracting(false);
    }
  };

  // Keypoint verification handler
  const handleKeypointVerify = (keypointId: string, verified: boolean) => {
    setKeypoints((prev) =>
      prev.map((kp) =>
        kp.id === keypointId ? { ...kp, user_verified: verified } : kp
      )
    );
  };

  // Stats
  const verifiedCount = keypoints.filter((kp) => kp.user_verified).length;
  const aiExtractedCount = keypoints.filter((kp) => kp.source_type === 'ai_extracted').length;
  const pendingCandidates = pipelineStats?.pending_candidates ?? 0;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
          <span className="ml-2 text-gray-500 dark:text-gray-400">LSSP 데이터 로딩 중...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Compact Header with Stats */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">법률 전략 분석</h2>
          <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              검증 {verifiedCount}/{keypoints.length}
            </span>
            <span className="flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              AI {aiExtractedCount}
            </span>
          </div>
        </div>
        <button
          onClick={fetchData}
          disabled={isLoading}
          className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
          title="새로고침"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-red-500 dark:text-red-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
          >
            ×
          </button>
        </div>
      )}

      {/* Main Cards - Expandable */}
      <div className="space-y-3">
        {/* 핵심 쟁점 Card */}
        <LSSPStatCard
          icon={FileText}
          label="핵심 쟁점"
          count={keypoints.length}
          description={keypoints.length === 0 ? 'AI 추출로 쟁점을 추출하세요' : `${verifiedCount}개 검증됨`}
          iconColor="text-blue-600 dark:text-blue-400"
          bgColor="bg-blue-50 dark:bg-blue-900/30"
          defaultExpanded={false}
        >
          <div className="space-y-4">
            {/* Actions */}
            <div className="flex items-center justify-end gap-2">
              <button
                onClick={handleExtractKeypoints}
                disabled={isExtracting || evidenceCount === 0}
                className="flex items-center px-3 py-1.5 bg-primary text-white text-sm rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isExtracting ? (
                  <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4 mr-1.5" />
                )}
                AI 추출
              </button>
              <button className="flex items-center px-3 py-1.5 border border-gray-300 dark:border-neutral-600 text-gray-700 dark:text-gray-300 text-sm rounded-lg hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors">
                <Plus className="w-4 h-4 mr-1.5" />
                직접 추가
              </button>
            </div>
            {/* Keypoint list */}
            <KeypointList
              keypoints={keypoints}
              legalGrounds={legalGrounds}
              onVerify={handleKeypointVerify}
              caseId={caseId}
            />
          </div>
        </LSSPStatCard>

        {/* 법적 근거 Card */}
        <LSSPStatCard
          icon={Scale}
          label="법적 근거"
          count={legalGrounds.length}
          description="민법 제840조 기반 이혼 사유"
          iconColor="text-purple-600 dark:text-purple-400"
          bgColor="bg-purple-50 dark:bg-purple-900/30"
        >
          <LegalGroundSummary
            caseId={caseId}
            keypoints={keypoints}
            legalGrounds={legalGrounds}
          />
        </LSSPStatCard>

        {/* 유사 판례 Card */}
        <LSSPStatCard
          icon={BookOpen}
          label="유사 판례"
          count={undefined}
          description="유사한 이혼 사례 및 판결"
          iconColor="text-amber-600 dark:text-amber-400"
          bgColor="bg-amber-50 dark:bg-amber-900/30"
        >
          <PrecedentPanel caseId={caseId} className="border-none shadow-none !p-0" hideHeader={true} />
        </LSSPStatCard>
      </div>

      {/* Advanced Section - Collapsible */}
      <div className="border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-between p-4 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="font-medium text-neutral-700 dark:text-neutral-300">고급 기능</span>
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              문서 생성 ({templates.length}) · 후보 관리 ({pendingCandidates})
            </span>
          </div>
          <ChevronDown className={`w-5 h-5 text-neutral-400 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
        </button>

        {showAdvanced && (
          <div className="border-t border-neutral-200 dark:border-neutral-700 p-4 space-y-6">
            {/* 문서 생성 Section */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-primary" />
                <h4 className="font-medium text-neutral-900 dark:text-neutral-100">문서 생성</h4>
              </div>

              {templates.length === 0 ? (
                <div className="text-center py-6 text-gray-500 dark:text-gray-400">
                  <FileText className="w-10 h-10 mx-auto mb-2 text-gray-300 dark:text-neutral-600" />
                  <p className="text-sm">사용 가능한 템플릿이 없습니다</p>
                </div>
              ) : (
                <div className="grid gap-2">
                  {templates.map((template) => (
                    <button
                      key={template.id}
                      onClick={() => onDraftGenerate?.(template.id)}
                      disabled={verifiedCount === 0}
                      className="flex items-center justify-between p-3 border border-gray-200 dark:border-neutral-700 rounded-lg hover:border-primary dark:hover:border-primary hover:bg-primary-light/10 dark:hover:bg-primary/5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-left"
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-primary" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{template.name}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{template.description}</p>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </button>
                  ))}
                </div>
              )}

              {verifiedCount === 0 && templates.length > 0 && (
                <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                  ※ 문서 생성을 위해 최소 1개의 쟁점을 검증하세요
                </p>
              )}
            </div>

            {/* 후보 관리 Section */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <GitBranch className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                <h4 className="font-medium text-neutral-900 dark:text-neutral-100">후보 관리</h4>
                {pendingCandidates > 0 && (
                  <span className="px-1.5 py-0.5 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 text-xs rounded-full">
                    {pendingCandidates} 대기
                  </span>
                )}
              </div>
              <PipelinePanel caseId={caseId} onRefresh={fetchData} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

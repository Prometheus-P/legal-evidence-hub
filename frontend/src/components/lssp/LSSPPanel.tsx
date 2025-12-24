'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  AlertCircle,
  RefreshCw,
  Loader2,
  BookOpen,
  HelpCircle,
  CheckCircle2,
  Sparkles,
  Plus,
  Scale,
  FileText,
  ChevronDown,
  ChevronRight,
  GitBranch,
} from 'lucide-react';
import {
  getKeypoints,
  getLegalGrounds,
  getDraftTemplates,
  extractKeypoints,
  getPipelineStats,
  createKeypoint,
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
import { Modal } from '@/components/primitives';
import { logger } from '@/lib/logger';

interface LSSPPanelProps {
  caseId: string;
  evidenceCount: number;
  onDraftGenerate?: (templateId: string) => void;
}

export function LSSPPanel({ caseId, evidenceCount, onDraftGenerate }: LSSPPanelProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [keypoints, setKeypoints] = useState<Keypoint[]>([]);
  const [legalGrounds, setLegalGrounds] = useState<LegalGround[]>([]);
  const [templates, setTemplates] = useState<DraftTemplate[]>([]);
  const [pipelineStats, setPipelineStats] = useState<PipelineStats | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showGuideModal, setShowGuideModal] = useState(false);
  const [newKeypointContent, setNewKeypointContent] = useState('');
  const [isCreating, setIsCreating] = useState(false);

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

  // Create keypoint manually
  const handleCreateKeypoint = async () => {
    if (!newKeypointContent.trim() || isCreating) return;

    setIsCreating(true);
    try {
      const response = await createKeypoint(caseId, {
        content: newKeypointContent.trim(),
        source_type: 'user_added',
      });
      if (response.data) {
        setKeypoints((prev) => [...prev, response.data!]);
        setNewKeypointContent('');
        setShowAddModal(false);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      logger.error('Failed to create keypoint:', err);
      setError('쟁점 추가에 실패했습니다.');
    } finally {
      setIsCreating(false);
    }
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
          <span className="ml-2 text-gray-500 dark:text-gray-400">데이터 로딩 중...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
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
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowGuideModal(true)}
            className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
            title="사용방법 안내"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
            title="새로고침"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
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
              <button
                onClick={() => setShowAddModal(true)}
                className="flex items-center px-3 py-1.5 border border-gray-300 dark:border-neutral-600 text-gray-700 dark:text-gray-300 text-sm rounded-lg hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors"
              >
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

      {/* Add Keypoint Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => {
          setShowAddModal(false);
          setNewKeypointContent('');
        }}
        title="쟁점 직접 추가"
        size="md"
        footer={
          <div className="flex justify-end gap-2">
            <button
              onClick={() => {
                setShowAddModal(false);
                setNewKeypointContent('');
              }}
              className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleCreateKeypoint}
              disabled={!newKeypointContent.trim() || isCreating}
              className="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isCreating && <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />}
              추가
            </button>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              쟁점 내용
            </label>
            <textarea
              value={newKeypointContent}
              onChange={(e) => setNewKeypointContent(e.target.value)}
              placeholder="예: 2023년 3월부터 피고는 원고에게 지속적인 폭언을 행사함"
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 dark:border-neutral-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-neutral-800 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary focus:border-primary resize-none"
              autoFocus
            />
            <p className="mt-1.5 text-xs text-gray-500 dark:text-gray-400">
              사건의 핵심이 되는 쟁점을 구체적으로 입력하세요.
            </p>
          </div>
        </div>
      </Modal>

      {/* Usage Guide Modal */}
      <Modal
        isOpen={showGuideModal}
        onClose={() => setShowGuideModal(false)}
        title="사용방법 안내"
        size="lg"
      >
        <div className="space-y-6 text-sm">
          {/* 핵심 쟁점 Section */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">핵심 쟁점</h3>
            </div>
            <ul className="space-y-1.5 text-gray-600 dark:text-gray-400 ml-7">
              <li><span className="font-medium text-primary">AI 추출</span>: 업로드된 증거에서 AI가 자동으로 쟁점을 추출합니다.</li>
              <li><span className="font-medium text-gray-900 dark:text-gray-100">직접 추가</span>: 수동으로 쟁점을 입력할 수 있습니다.</li>
              <li><span className="font-medium text-green-600 dark:text-green-400">체크 표시</span>: 쟁점을 검토한 후 체크하여 검증 완료 표시를 합니다.</li>
            </ul>
          </div>

          {/* 법적 근거 Section */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Scale className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">법적 근거</h3>
            </div>
            <ul className="space-y-1.5 text-gray-600 dark:text-gray-400 ml-7">
              <li>민법 제840조에 따른 이혼 사유가 표시됩니다.</li>
              <li>각 쟁점은 해당하는 법적 근거와 자동으로 연결됩니다.</li>
              <li>근거별 증거 강도를 확인할 수 있습니다.</li>
            </ul>
          </div>

          {/* 유사 판례 Section */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-5 h-5 text-amber-600 dark:text-amber-400" />
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">유사 판례</h3>
            </div>
            <ul className="space-y-1.5 text-gray-600 dark:text-gray-400 ml-7">
              <li>키워드로 관련 판례를 검색할 수 있습니다.</li>
              <li>유사한 사례의 판결 내용을 참고하세요.</li>
            </ul>
          </div>

          {/* 팁 Section */}
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/50 rounded-lg">
            <p className="text-blue-700 dark:text-blue-300">
              <span className="font-medium">Tip:</span> 최소 1개 이상의 쟁점을 검증해야 초안 생성이 가능합니다.
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
}

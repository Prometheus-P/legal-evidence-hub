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
  GitBranch,
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
import { logger } from '@/lib/logger';

interface LSSPPanelProps {
  caseId: string;
  evidenceCount: number;
  onDraftGenerate?: (templateId: string) => void;
}

type LSSPTab = 'keypoints' | 'grounds' | 'drafts' | 'pipeline';

export function LSSPPanel({ caseId, evidenceCount, onDraftGenerate }: LSSPPanelProps) {
  const [activeTab, setActiveTab] = useState<LSSPTab>('keypoints');
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

  const tabs = [
    {
      id: 'keypoints' as const,
      label: '핵심 쟁점',
      count: keypoints.length,
      icon: FileText,
    },
    {
      id: 'grounds' as const,
      label: '법적 근거',
      count: legalGrounds.length,
      icon: Scale,
    },
    {
      id: 'drafts' as const,
      label: '문서 생성',
      count: templates.length,
      icon: Sparkles,
    },
    {
      id: 'pipeline' as const,
      label: '후보 관리',
      count: pipelineStats?.pending_candidates ?? 0,
      icon: GitBranch,
    },
  ];

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
          <span className="ml-2 text-gray-500">LSSP 데이터 로딩 중...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900">법률 전략 분석 (LSSP)</h2>
            <p className="text-sm text-gray-500">
              AI가 증거에서 핵심 쟁점을 추출하고 법적 근거와 연결합니다
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchData}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              title="새로고침"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Stats bar */}
        <div className="mt-4 flex items-center space-x-6 text-sm">
          <div className="flex items-center text-gray-600">
            <FileText className="w-4 h-4 mr-1.5 text-gray-400" />
            <span>쟁점 {keypoints.length}개</span>
          </div>
          <div className="flex items-center text-gray-600">
            <CheckCircle2 className="w-4 h-4 mr-1.5 text-green-500" />
            <span>검증됨 {verifiedCount}개</span>
          </div>
          <div className="flex items-center text-gray-600">
            <Sparkles className="w-4 h-4 mr-1.5 text-primary" />
            <span>AI 추출 {aiExtractedCount}개</span>
          </div>
        </div>
      </div>

      {/* Tab navigation */}
      <div className="flex border-b border-gray-100">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 text-sm font-medium transition-colors ${
                isActive
                  ? 'text-primary border-b-2 border-primary bg-primary-light/30'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              <span
                className={`px-1.5 py-0.5 rounded-full text-xs ${
                  isActive ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'
                }`}
              >
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Error state */}
      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-red-700">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}

      {/* Tab content */}
      <div className="p-6">
        {activeTab === 'keypoints' && (
          <div className="space-y-4">
            {/* Actions */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                {keypoints.length === 0
                  ? '아직 추출된 쟁점이 없습니다. AI 추출을 실행하거나 직접 추가하세요.'
                  : `총 ${keypoints.length}개의 핵심 쟁점이 있습니다.`}
              </p>
              <div className="flex items-center space-x-2">
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
                <button className="flex items-center px-3 py-1.5 border border-gray-300 text-gray-700 text-sm rounded-lg hover:bg-gray-50 transition-colors">
                  <Plus className="w-4 h-4 mr-1.5" />
                  직접 추가
                </button>
              </div>
            </div>

            {/* Keypoint list */}
            <KeypointList
              keypoints={keypoints}
              legalGrounds={legalGrounds}
              onVerify={handleKeypointVerify}
              caseId={caseId}
            />
          </div>
        )}

        {activeTab === 'grounds' && (
          <LegalGroundSummary
            caseId={caseId}
            keypoints={keypoints}
            legalGrounds={legalGrounds}
          />
        )}

        {activeTab === 'drafts' && (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              검증된 쟁점을 기반으로 법률 문서 초안을 생성합니다.
            </p>

            {templates.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>사용 가능한 템플릿이 없습니다.</p>
              </div>
            ) : (
              <div className="grid gap-3">
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => onDraftGenerate?.(template.id)}
                    disabled={verifiedCount === 0}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:border-primary hover:bg-primary-light/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-left"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-primary-light rounded-lg">
                        <FileText className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{template.name}</p>
                        <p className="text-sm text-gray-500">{template.description}</p>
                      </div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </button>
                ))}
              </div>
            )}

            {verifiedCount === 0 && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>안내:</strong> 문서를 생성하려면 최소 1개 이상의 쟁점을 검증해야 합니다.
                  핵심 쟁점 탭에서 쟁점을 검증해 주세요.
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'pipeline' && (
          <PipelinePanel caseId={caseId} onRefresh={fetchData} />
        )}
      </div>
    </div>
  );
}

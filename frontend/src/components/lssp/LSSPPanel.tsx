'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  AlertCircle,
  RefreshCw,
  Loader2,
  BookOpen,
} from 'lucide-react';
import { PrecedentPanel } from '../precedent/PrecedentPanel';
import { LSSPStatCard } from './LSSPStatCard';
import { logger } from '@/lib/logger';

interface LSSPPanelProps {
  caseId: string;
  evidenceCount: number;
  onDraftGenerate?: (templateId: string) => void;
}

export function LSSPPanel({ caseId }: LSSPPanelProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRefresh = useCallback(() => {
    setIsLoading(true);
    setError(null);
    // Simulate refresh - actual refresh happens within PrecedentPanel
    setTimeout(() => setIsLoading(false), 500);
  }, []);

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
        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">법률 분석</h2>
        <button
          onClick={handleRefresh}
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

      {/* 유사 판례 Card */}
      <LSSPStatCard
        icon={BookOpen}
        label="유사 판례"
        count={undefined}
        description="유사한 이혼 사례 및 판결"
        iconColor="text-amber-600 dark:text-amber-400"
        bgColor="bg-amber-50 dark:bg-amber-900/30"
        defaultExpanded={true}
      >
        <PrecedentPanel caseId={caseId} className="border-none shadow-none !p-0" hideHeader={true} />
      </LSSPStatCard>
    </div>
  );
}

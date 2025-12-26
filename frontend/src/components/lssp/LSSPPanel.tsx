'use client';

import { BookOpen } from 'lucide-react';
import { PrecedentPanel } from '../precedent/PrecedentPanel';
import { LSSPStatCard } from './LSSPStatCard';

interface LSSPPanelProps {
  caseId: string;
  evidenceCount: number;
  onDraftGenerate?: (templateId: string) => void;
}

export function LSSPPanel({ caseId }: LSSPPanelProps) {
  return (
    <div className="space-y-4">
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
  );
}

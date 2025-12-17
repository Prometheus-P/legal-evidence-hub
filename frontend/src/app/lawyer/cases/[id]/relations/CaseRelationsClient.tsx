/**
 * Case Relations Client Component
 * 009-calm-control-design-system
 *
 * Client-side party relations graph for a case using React Flow.
 */

'use client';

import Link from 'next/link';
import { CaseRelationsGraph } from '@/components/case/CaseRelationsGraph';
import { getCaseDetailPath, getLawyerCasePath } from '@/lib/portalPaths';

interface CaseRelationsClientProps {
  caseId: string;
}

export default function CaseRelationsClient({ caseId }: CaseRelationsClientProps) {
  const relationsPath = getLawyerCasePath('relations', caseId);
  const detailPath = getCaseDetailPath('lawyer', caseId, { returnUrl: relationsPath });
  const evidenceTabPath = getCaseDetailPath('lawyer', caseId, {
    tab: 'evidence',
    returnUrl: relationsPath,
  });
  const assetsPath = getLawyerCasePath('assets', caseId);
  const draftTabPath = getCaseDetailPath('lawyer', caseId, { tab: 'draft', returnUrl: relationsPath });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">당사자 관계도</h1>
          <p className="text-gray-500 mt-1">
            당사자 간의 관계를 시각적으로 확인하고 편집합니다.
          </p>
        </div>
        <Link
          href={detailPath}
          className="text-sm text-primary hover:text-primary-hover"
        >
          ← 케이스 상세로 돌아가기
        </Link>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          <Link
            href={detailPath}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            개요
          </Link>
          <Link
            href={evidenceTabPath}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            증거
          </Link>
          <span className="py-3 text-sm text-primary font-medium border-b-2 border-primary">
            관계도
          </span>
          <Link
            href={assetsPath}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            재산
          </Link>
          <Link
            href={draftTabPath}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            초안
          </Link>
        </nav>
      </div>

      {/* Relations Graph */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="mb-4">
          <h2 className="font-semibold text-gray-900">관계 그래프</h2>
          <p className="text-sm text-gray-500 mt-1">
            노드를 드래그하여 위치를 조정하고, 노드 사이를 연결하여 관계를 추가할 수 있습니다.
          </p>
        </div>
        <CaseRelationsGraph caseId={caseId} />
      </div>

      {/* Instructions */}
      <div className="bg-neutral-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-2">사용 방법</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• <strong>당사자 추가:</strong> 좌측 상단의 &quot;+ 당사자 추가&quot; 버튼 클릭</li>
          <li>• <strong>관계 연결:</strong> 한 노드의 핸들을 드래그하여 다른 노드에 연결</li>
          <li>• <strong>위치 조정:</strong> 노드를 드래그하여 원하는 위치로 이동 (자동 저장)</li>
          <li>• <strong>상세 보기:</strong> 노드 클릭 시 우측 패널에 상세 정보 표시</li>
          <li>• <strong>확대/축소:</strong> 마우스 휠 또는 좌측 하단 컨트롤 사용</li>
        </ul>
      </div>
    </div>
  );
}

/**
 * Case Assets Client Component
 * 009-calm-control-design-system
 *
 * Client-side asset division management for divorce cases.
 */

'use client';

import Link from 'next/link';
import { AssetDivisionForm } from '@/components/case/AssetDivisionForm';

interface CaseAssetsClientProps {
  caseId: string;
}

export default function CaseAssetsClient({ caseId }: CaseAssetsClientProps) {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">재산 분할</h1>
          <p className="text-gray-500 mt-1">
            사건에 관련된 재산을 등록하고 분할 비율을 설정합니다.
          </p>
        </div>
        <Link
          href={`/lawyer/cases/${caseId}`}
          className="text-sm text-teal-600 hover:text-teal-700"
        >
          ← 케이스 상세로 돌아가기
        </Link>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          <Link
            href={`/lawyer/cases/${caseId}`}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            개요
          </Link>
          <Link
            href={`/lawyer/cases/${caseId}/evidence`}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            증거
          </Link>
          <Link
            href={`/lawyer/cases/${caseId}/relations`}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            관계도
          </Link>
          <span className="py-3 text-sm text-teal-600 font-medium border-b-2 border-teal-600">
            재산
          </span>
          <Link
            href={`/lawyer/cases/${caseId}/draft`}
            className="py-3 text-sm text-gray-500 hover:text-gray-700 border-b-2 border-transparent"
          >
            초안
          </Link>
        </nav>
      </div>

      {/* Asset Division Form */}
      <AssetDivisionForm caseId={caseId} />

      {/* Instructions */}
      <div className="bg-neutral-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-2">사용 방법</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• <strong>재산 추가:</strong> &quot;+ 재산 추가&quot; 버튼을 클릭하여 새 재산 등록</li>
          <li>• <strong>분할 비율:</strong> 슬라이더를 조절하여 원고/피고 분할 비율 설정</li>
          <li>• <strong>부채 관리:</strong> 재산 유형에서 &quot;부채&quot;를 선택하여 부채 등록</li>
          <li>• <strong>결과 미리보기:</strong> 우측 패널에서 예상 분할 결과 확인</li>
        </ul>
      </div>
    </div>
  );
}

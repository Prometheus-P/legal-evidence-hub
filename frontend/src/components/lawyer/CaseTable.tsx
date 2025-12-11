'use client';

/**
 * CaseTable Component
 * 003-role-based-ui Feature - US3
 *
 * Table view for cases with sorting and selection.
 */

import Link from 'next/link';
import { useState } from 'react';

interface CaseItem {
  id: string;
  title: string;
  clientName?: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  evidenceCount: number;
  progress: number;
  ownerName?: string;
}

interface CaseTableProps {
  cases: CaseItem[];
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  onSort: (field: string) => void;
  onAction?: (caseId: string, action: 'procedure' | 'assets' | 'ai-analyze') => void;
}

const statusColors: Record<string, string> = {
  active: 'bg-blue-100 text-blue-800',
  open: 'bg-green-100 text-green-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  closed: 'bg-gray-100 text-gray-800',
};

const statusLabels: Record<string, string> = {
  active: '활성',
  open: '진행 중',
  in_progress: '검토 대기',
  closed: '종료',
};

export function CaseTable({
  cases,
  selectedIds,
  onSelectionChange,
  sortBy,
  sortOrder,
  onSort,
  onAction,
}: CaseTableProps) {
  const allSelected = cases.length > 0 && selectedIds.length === cases.length;
  const someSelected = selectedIds.length > 0 && selectedIds.length < cases.length;

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      onSelectionChange(cases.map((c) => c.id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedIds, id]);
    } else {
      onSelectionChange(selectedIds.filter((i) => i !== id));
    }
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortBy !== field) {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    return sortOrder === 'asc' ? (
      <svg className="w-4 h-4 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  const SortableHeader = ({ field, children }: { field: string; children: React.ReactNode }) => (
    <th
      className="px-4 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider cursor-pointer hover:bg-gray-100"
      onClick={() => onSort(field)}
    >
      <div className="flex items-center gap-1">
        {children}
        <SortIcon field={field} />
      </div>
    </th>
  );

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 w-10">
              <input
                type="checkbox"
                checked={allSelected}
                ref={(el) => {
                  if (el) el.indeterminate = someSelected;
                }}
                onChange={handleSelectAll}
                className="w-4 h-4 rounded border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
              />
            </th>
            <SortableHeader field="title">케이스명</SortableHeader>
            <SortableHeader field="client_name">의뢰인</SortableHeader>
            <SortableHeader field="status">상태</SortableHeader>
            <th className="px-4 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              증거
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              진행률
            </th>
            <SortableHeader field="updated_at">최근 업데이트</SortableHeader>
            <th className="px-4 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              담당자
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
              액션
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {cases.map((caseItem) => (
            <tr
              key={caseItem.id}
              className={`hover:bg-gray-50 ${selectedIds.includes(caseItem.id) ? 'bg-blue-50' : ''}`}
            >
              <td className="px-4 py-3">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(caseItem.id)}
                  onChange={(e) => handleSelectOne(caseItem.id, e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
                />
              </td>
              <td className="px-4 py-3">
                <Link
                  href={`/lawyer/cases/${caseItem.id}`}
                  className="font-medium text-[var(--color-text-primary)] hover:text-[var(--color-primary)]"
                >
                  {caseItem.title}
                </Link>
              </td>
              <td className="px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                {caseItem.clientName || '-'}
              </td>
              <td className="px-4 py-3">
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statusColors[caseItem.status] || statusColors.active}`}>
                  {statusLabels[caseItem.status] || caseItem.status}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                {caseItem.evidenceCount}건
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-[var(--color-primary)] rounded-full"
                      style={{ width: `${caseItem.progress}%` }}
                    />
                  </div>
                  <span className="text-xs text-[var(--color-text-secondary)]">
                    {caseItem.progress}%
                  </span>
                </div>
              </td>
              <td className="px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                {new Date(caseItem.updatedAt).toLocaleDateString('ko-KR')}
              </td>
              <td className="px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                {caseItem.ownerName || '-'}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1">
                  <Link
                    href={`/lawyer/cases/${caseItem.id}/procedure`}
                    className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="절차 진행"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  </Link>
                  <Link
                    href={`/lawyer/cases/${caseItem.id}/assets`}
                    className="p-1.5 text-green-600 hover:bg-green-50 rounded transition-colors"
                    title="재산분할"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </Link>
                  {onAction && (
                    <button
                      type="button"
                      onClick={() => onAction(caseItem.id, 'ai-analyze')}
                      className="p-1.5 text-purple-600 hover:bg-purple-50 rounded transition-colors"
                      title="AI 분석"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {cases.length === 0 && (
            <tr>
              <td colSpan={9} className="px-4 py-8 text-center text-[var(--color-text-secondary)]">
                케이스가 없습니다.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default CaseTable;

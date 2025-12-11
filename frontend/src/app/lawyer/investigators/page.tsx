/**
 * Lawyer Investigators Page
 * 005-lawyer-portal-pages Feature - US3 (T042)
 *
 * Investigator management page with search, filter, and pagination.
 */

'use client';

import { useState } from 'react';
import { useInvestigators, getAvailabilityStyle, getAvailabilityLabel } from '@/hooks/useInvestigators';
import type { InvestigatorAvailability, InvestigatorFilter } from '@/types/investigator';

export default function LawyerInvestigatorsPage() {
  const [searchValue, setSearchValue] = useState('');
  const [availabilityFilter, setAvailabilityFilter] = useState<InvestigatorAvailability | 'all'>('all');

  const {
    investigators,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    setFilters,
    setPage,
    refetch,
  } = useInvestigators();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const newFilters: InvestigatorFilter = {
      search: searchValue || undefined,
      availability: availabilityFilter,
    };
    setFilters(newFilters);
  };

  const handleAvailabilityChange = (availability: InvestigatorAvailability | 'all') => {
    setAvailabilityFilter(availability);
    setFilters({
      search: searchValue || undefined,
      availability,
    });
  };

  const handleClearFilters = () => {
    setSearchValue('');
    setAvailabilityFilter('all');
    setFilters({});
  };

  // Count by availability
  const availableCounts = investigators.reduce(
    (acc, inv) => {
      acc[inv.availability] = (acc[inv.availability] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">조사원/탐정 관리</h1>
          <p className="text-[var(--color-text-secondary)]">
            등록된 조사원 {total}명
            {availableCounts.available && ` · 배정 가능 ${availableCounts.available}명`}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={refetch}
            className="px-4 py-2 rounded-lg border border-[var(--color-border-default)] text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            새로고침
          </button>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white border border-[var(--color-border-default)] rounded-xl p-4 shadow-sm">
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="이름 또는 이메일로 검색..."
              className="w-full px-4 py-2 rounded-lg border border-[var(--color-border-default)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={availabilityFilter}
              onChange={(e) => handleAvailabilityChange(e.target.value as InvestigatorAvailability | 'all')}
              className="px-4 py-2 rounded-lg border border-[var(--color-border-default)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-white"
            >
              <option value="all">전체 상태</option>
              <option value="available">배정 가능</option>
              <option value="busy">바쁨</option>
              <option value="unavailable">배정 불가</option>
            </select>
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-hover)] transition-colors"
            >
              검색
            </button>
            <button
              type="button"
              onClick={handleClearFilters}
              className="px-4 py-2 rounded-lg border border-[var(--color-border-default)] text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              초기화
            </button>
          </div>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-lg border border-red-200 bg-red-50 text-red-700">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)]" />
        </div>
      )}

      {/* Investigator Table */}
      {!isLoading && !error && (
        <div className="bg-white border border-[var(--color-border-default)] rounded-xl overflow-hidden shadow-sm">
          <table className="min-w-full divide-y divide-[var(--color-border-default)]">
            <thead className="bg-[var(--color-bg-secondary)]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  조사원
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  전문 분야
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  배정 현황
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  상태
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  최근 활동
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-[var(--color-border-default)]">
              {investigators.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[var(--color-text-secondary)]">
                    {searchValue || availabilityFilter !== 'all'
                      ? '검색 결과가 없습니다.'
                      : '아직 등록된 조사원이 없습니다.'}
                  </td>
                </tr>
              )}
              {investigators.map((investigator) => (
                <tr
                  key={investigator.id}
                  className="hover:bg-[var(--color-bg-secondary)]/50 transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white font-medium">
                        {investigator.name.charAt(0)}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-[var(--color-text-primary)]">
                          {investigator.name}
                        </div>
                        <div className="text-xs text-[var(--color-text-secondary)]">
                          {investigator.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-[var(--color-text-primary)]">
                    {investigator.specialization || '-'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-[var(--color-text-primary)]">
                      진행 중 {investigator.active_assignments}건
                    </div>
                    <div className="text-xs text-[var(--color-text-secondary)]">
                      완료 {investigator.completed_assignments}건
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getAvailabilityStyle(
                        investigator.availability
                      )}`}
                    >
                      {getAvailabilityLabel(investigator.availability)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-[var(--color-text-secondary)]">
                    {investigator.last_activity
                      ? new Date(investigator.last_activity).toLocaleDateString('ko-KR')
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-[var(--color-border-default)] flex items-center justify-between">
              <div className="text-sm text-[var(--color-text-secondary)]">
                {total}명 중 {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, total)}명
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="px-3 py-1 rounded border border-[var(--color-border-default)] text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  이전
                </button>
                <span className="px-3 py-1 text-sm text-[var(--color-text-secondary)]">
                  {page} / {totalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                  className="px-3 py-1 rounded border border-[var(--color-border-default)] text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  다음
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Lawyer Clients Page
 * 005-lawyer-portal-pages Feature - US2 (T028)
 *
 * Client management page with search, filter, and pagination.
 */

'use client';

import { useState } from 'react';
import { useClients, getClientStatusStyle, getClientStatusLabel } from '@/hooks/useClients';
import type { ClientFilter } from '@/types/client';

export default function LawyerClientsPage() {
  const [searchValue, setSearchValue] = useState('');
  const [statusFilter, setStatusFilter] = useState<'active' | 'inactive' | 'all'>('all');

  const {
    clients,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    setFilters,
    setPage,
    refetch,
  } = useClients();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const newFilters: ClientFilter = {
      search: searchValue || undefined,
      status: statusFilter,
    };
    setFilters(newFilters);
  };

  const handleStatusChange = (status: 'active' | 'inactive' | 'all') => {
    setStatusFilter(status);
    setFilters({
      search: searchValue || undefined,
      status,
    });
  };

  const handleClearFilters = () => {
    setSearchValue('');
    setStatusFilter('all');
    setFilters({});
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">의뢰인 관리</h1>
          <p className="text-[var(--color-text-secondary)]">
            등록된 의뢰인 {total}명
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
              value={statusFilter}
              onChange={(e) => handleStatusChange(e.target.value as 'active' | 'inactive' | 'all')}
              className="px-4 py-2 rounded-lg border border-[var(--color-border-default)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] bg-white"
            >
              <option value="all">전체 상태</option>
              <option value="active">활성</option>
              <option value="inactive">비활성</option>
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

      {/* Client Table */}
      {!isLoading && !error && (
        <div className="bg-white border border-[var(--color-border-default)] rounded-xl overflow-hidden shadow-sm">
          <table className="min-w-full divide-y divide-[var(--color-border-default)]">
            <thead className="bg-[var(--color-bg-secondary)]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  의뢰인
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  연락처
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  케이스
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
              {clients.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[var(--color-text-secondary)]">
                    {searchValue || statusFilter !== 'all'
                      ? '검색 결과가 없습니다.'
                      : '아직 등록된 의뢰인이 없습니다.'}
                  </td>
                </tr>
              )}
              {clients.map((client) => (
                <tr
                  key={client.id}
                  className="hover:bg-[var(--color-bg-secondary)]/50 transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white font-medium">
                        {client.name.charAt(0)}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-[var(--color-text-primary)]">
                          {client.name}
                        </div>
                        <div className="text-xs text-[var(--color-text-secondary)]">
                          {client.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-[var(--color-text-primary)]">
                    {client.phone || '-'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-[var(--color-text-primary)]">
                      {client.case_count}건
                    </div>
                    <div className="text-xs text-[var(--color-text-secondary)]">
                      진행 중 {client.active_cases}건
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getClientStatusStyle(
                        client.status
                      )}`}
                    >
                      {getClientStatusLabel(client.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-[var(--color-text-secondary)]">
                    {client.last_activity
                      ? new Date(client.last_activity).toLocaleDateString('ko-KR')
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

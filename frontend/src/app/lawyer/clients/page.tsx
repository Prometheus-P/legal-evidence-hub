'use client';

import { useCallback, useEffect, useState } from 'react';
import { apiRequest, ApiResponse } from '@/lib/api/client';

interface CaseListItem {
  id: string;
  title: string;
  status: string;
  client_name?: string | null;
  updated_at: string;
}

interface LawyerCaseListResponse {
  items: CaseListItem[];
  total: number;
  status_counts?: Record<string, number>;
}

interface ClientSummary {
  name: string;
  caseCount: number;
  activeCount: number;
  statuses: Record<string, number>;
  lastUpdated?: string;
}

export default function LawyerClientsPage() {
  const [clients, setClients] = useState<ClientSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusCounts, setStatusCounts] = useState<Record<string, number>>({});

  const fetchClientData = useCallback(async () => {
    setLoading(true);
    setError(null);

    const response: ApiResponse<LawyerCaseListResponse> = await apiRequest(
      '/lawyer/cases?page_size=100',
      { method: 'GET' }
    );

    if (response.error) {
      setError(response.error);
      setClients([]);
      setLoading(false);
      return;
    }

    const caseItems = response.data?.items ?? [];
    const grouped = new Map<string, ClientSummary>();

    caseItems.forEach((item) => {
      const name = item.client_name || '미등록 의뢰인';
      const summary = grouped.get(name) ?? {
        name,
        caseCount: 0,
        activeCount: 0,
        statuses: {},
        lastUpdated: undefined,
      };

      summary.caseCount += 1;
      summary.statuses[item.status] = (summary.statuses[item.status] || 0) + 1;
      if (item.status !== 'closed') {
        summary.activeCount += 1;
      }

      if (
        !summary.lastUpdated ||
        new Date(item.updated_at) > new Date(summary.lastUpdated)
      ) {
        summary.lastUpdated = item.updated_at;
      }

      grouped.set(name, summary);
    });

    setClients(Array.from(grouped.values()).sort((a, b) => b.caseCount - a.caseCount));
    setStatusCounts(response.data?.status_counts ?? {});
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchClientData();
  }, [fetchClientData]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">의뢰인 관리</h1>
          <p className="text-[var(--color-text-secondary)]">
            등록된 의뢰인 {clients.length}명 · 진행 중 사건{' '}
            {statusCounts.active ?? 0}건
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={fetchClientData}
            className="px-4 py-2 rounded-lg border border-[var(--color-border-default)] text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            새로고침
          </button>
          <button
            type="button"
            className="px-4 py-2 rounded-lg bg-[var(--color-primary)] text-white text-sm font-medium hover:bg-[var(--color-primary-dark)] transition-colors"
          >
            새 의뢰인 등록
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg border border-red-200 bg-red-50 text-red-700">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)]" />
        </div>
      )}

      {!loading && !error && (
        <div className="bg-white border border-[var(--color-border-default)] rounded-xl overflow-hidden shadow-sm">
          <table className="min-w-full divide-y divide-[var(--color-border-default)]">
            <thead className="bg-[var(--color-bg-secondary)]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  의뢰인
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  전체 케이스
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  진행 중
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  상태 요약
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">
                  최근 업데이트
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-[var(--color-border-default)]">
              {clients.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-[var(--color-text-secondary)]">
                    아직 등록된 의뢰인이 없습니다.
                  </td>
                </tr>
              )}
              {clients.map((client) => (
                <tr key={client.name} className="hover:bg-[var(--color-bg-secondary)]/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-[var(--color-text-primary)]">
                      {client.name}
                    </div>
                    <div className="text-xs text-[var(--color-text-secondary)]">
                      {client.statuses.active ?? 0}건 진행 중
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-primary)]">
                    {client.caseCount}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-primary)]">
                    {client.activeCount}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(client.statuses).map(([status, count]) => (
                        <span
                          key={`${client.name}-${status}`}
                          className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800"
                        >
                          {status} · {count}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[var(--color-text-secondary)]">
                    {client.lastUpdated
                      ? new Date(client.lastUpdated).toLocaleDateString('ko-KR')
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

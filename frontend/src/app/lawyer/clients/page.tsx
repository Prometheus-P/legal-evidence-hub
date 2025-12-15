/**
 * Lawyer Clients Page
 * 005-lawyer-portal-pages Feature - US2 (T028)
 * Updated: 011-production-bug-fixes - US2 (T050)
 *
 * Client management with tabs for case clients and contact book.
 */

'use client';

import { useState } from 'react';
import { useClients, getClientStatusStyle, getClientStatusLabel } from '@/hooks/useClients';
import { useClientContacts } from '@/hooks/useClientContacts';
import { ClientList } from '@/components/lawyer/clients/ClientList';
import { ClientForm } from '@/components/lawyer/clients/ClientForm';
import type { ClientFilter, ClientContact, ClientContactCreate, ClientContactUpdate } from '@/types/client';

type TabType = 'cases' | 'contacts';

function CaseClientsSection() {
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
      {/* Search and Filter */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-4 shadow-sm">
        <form onSubmit={handleSearch} className="flex flex-col gap-4 md:flex-row">
          <div className="flex-1">
            <input
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="이름 또는 이메일로 검색..."
              className="w-full rounded-lg border border-[var(--color-border-default)] px-4 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => handleStatusChange(e.target.value as 'active' | 'inactive' | 'all')}
              className="rounded-lg border border-[var(--color-border-default)] bg-white px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="all">전체 상태</option>
              <option value="active">활성</option>
              <option value="inactive">비활성</option>
            </select>
            <button
              type="submit"
              className="rounded-lg bg-[var(--color-primary)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--color-primary-hover)]"
            >
              검색
            </button>
            <button
              type="button"
              onClick={handleClearFilters}
              className="rounded-lg border border-[var(--color-border-default)] px-4 py-2 text-sm font-medium transition-colors hover:bg-gray-50"
            >
              초기화
            </button>
          </div>
        </form>
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between">
        <p className="text-[var(--color-text-secondary)]">
          등록된 의뢰인 {total}명
        </p>
        <button
          type="button"
          onClick={refetch}
          className="rounded-lg border border-[var(--color-border-default)] px-4 py-2 text-sm font-medium transition-colors hover:bg-gray-50"
        >
          새로고침
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-[var(--color-primary)]" />
        </div>
      )}

      {/* Table */}
      {!isLoading && !error && (
        <div className="overflow-hidden rounded-xl border border-[var(--color-border-default)] bg-white shadow-sm">
          <table className="min-w-full divide-y divide-[var(--color-border-default)]">
            <thead className="bg-[var(--color-bg-secondary)]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                  의뢰인
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                  연락처
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                  케이스
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                  상태
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                  최근 활동
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-default)] bg-white">
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
                  className="cursor-pointer transition-colors hover:bg-[var(--color-bg-secondary)]/50"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--color-primary)] font-medium text-white">
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
            <div className="flex items-center justify-between border-t border-[var(--color-border-default)] px-6 py-4">
              <div className="text-sm text-[var(--color-text-secondary)]">
                {total}명 중 {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, total)}명
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="rounded border border-[var(--color-border-default)] px-3 py-1 text-sm hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
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
                  className="rounded border border-[var(--color-border-default)] px-3 py-1 text-sm hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
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

function ClientContactsSection() {
  const [showForm, setShowForm] = useState(false);
  const [editingClient, setEditingClient] = useState<ClientContact | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    contacts,
    total,
    page,
    isLoading,
    error,
    search,
    setSearch,
    setPage,
    create,
    update,
    remove,
  } = useClientContacts({ limit: 12 });

  const handleAdd = () => {
    setEditingClient(null);
    setShowForm(true);
  };

  const handleEdit = (client: ClientContact) => {
    setEditingClient(client);
    setShowForm(true);
  };

  const handleDelete = async (clientId: string) => {
    await remove(clientId);
  };

  const handleSubmit = async (data: ClientContactCreate | ClientContactUpdate) => {
    setIsSubmitting(true);
    try {
      if (editingClient) {
        await update(editingClient.id, data);
      } else {
        await create(data as ClientContactCreate);
      }
      setShowForm(false);
      setEditingClient(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingClient(null);
  };

  return (
    <>
      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      <ClientList
        clients={contacts}
        isLoading={isLoading}
        search={search}
        onSearchChange={setSearch}
        onAdd={handleAdd}
        onEdit={handleEdit}
        onDelete={handleDelete}
        page={page}
        total={total}
        limit={12}
        onPageChange={setPage}
      />

      {showForm && (
        <ClientForm
          client={editingClient}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={isSubmitting}
        />
      )}
    </>
  );
}

export default function LawyerClientsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('cases');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">의뢰인 관리</h1>
        <p className="text-[var(--color-text-secondary)]">
          케이스 의뢰인 및 연락처를 관리합니다
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          type="button"
          onClick={() => setActiveTab('cases')}
          className={`px-6 py-3 text-sm font-medium transition-colors ${
            activeTab === 'cases'
              ? 'border-b-2 border-[var(--color-primary)] text-[var(--color-primary)]'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          케이스 의뢰인
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('contacts')}
          className={`px-6 py-3 text-sm font-medium transition-colors ${
            activeTab === 'contacts'
              ? 'border-b-2 border-[var(--color-primary)] text-[var(--color-primary)]'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          연락처
        </button>
      </div>

      {/* Content */}
      {activeTab === 'cases' ? <CaseClientsSection /> : <ClientContactsSection />}
    </div>
  );
}

/**
 * ClientList Component
 * 011-production-bug-fixes Feature - US2 (T049)
 *
 * List of client contacts with search and pagination.
 */

'use client';

import React from 'react';
import { ClientCard } from './ClientCard';
import type { ClientContact } from '@/types/client';

interface ClientListProps {
  clients: ClientContact[];
  isLoading?: boolean;
  search: string;
  onSearchChange: (search: string) => void;
  onAdd: () => void;
  onEdit: (client: ClientContact) => void;
  onDelete: (clientId: string) => void;
  page: number;
  total: number;
  limit: number;
  onPageChange: (page: number) => void;
}

export function ClientList({
  clients,
  isLoading = false,
  search,
  onSearchChange,
  onAdd,
  onEdit,
  onDelete,
  page,
  total,
  limit,
  onPageChange,
}: ClientListProps) {
  const totalPages = Math.ceil(total / limit);
  const hasNext = page < totalPages;
  const hasPrev = page > 1;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">의뢰인 관리</h1>
          <p className="mt-1 text-sm text-gray-500">
            총 {total}명의 의뢰인
          </p>
        </div>
        <button
          type="button"
          onClick={onAdd}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          의뢰인 추가
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="이름, 전화번호, 이메일로 검색..."
          className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && clients.length === 0 && (
        <div className="rounded-lg border border-gray-200 bg-white py-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
            />
          </svg>
          <p className="mt-4 text-gray-500">
            {search ? '검색 결과가 없습니다' : '등록된 의뢰인이 없습니다'}
          </p>
          {!search && (
            <button
              type="button"
              onClick={onAdd}
              className="mt-4 text-sm text-blue-600 hover:text-blue-800"
            >
              첫 의뢰인을 추가하세요
            </button>
          )}
        </div>
      )}

      {/* Client Grid */}
      {!isLoading && clients.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {clients.map((client) => (
            <ClientCard
              key={client.id}
              client={client}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <button
            type="button"
            onClick={() => onPageChange(page - 1)}
            disabled={!hasPrev}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-50"
          >
            이전
          </button>
          <span className="text-sm text-gray-600">
            {page} / {totalPages}
          </span>
          <button
            type="button"
            onClick={() => onPageChange(page + 1)}
            disabled={!hasNext}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-50"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}

export default ClientList;

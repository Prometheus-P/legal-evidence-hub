/**
 * DetectiveList Component
 * 011-production-bug-fixes Feature - US2 (T053)
 *
 * List of detective contacts with search and pagination.
 */

'use client';

import React from 'react';
import { DetectiveCard } from './DetectiveCard';
import type { DetectiveContact } from '@/types/investigator';

interface DetectiveListProps {
  detectives: DetectiveContact[];
  isLoading?: boolean;
  search: string;
  onSearchChange: (search: string) => void;
  onAdd: () => void;
  onEdit: (detective: DetectiveContact) => void;
  onDelete: (detectiveId: string) => void;
  page: number;
  total: number;
  limit: number;
  onPageChange: (page: number) => void;
}

export function DetectiveList({
  detectives,
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
}: DetectiveListProps) {
  const totalPages = Math.ceil(total / limit);
  const hasNext = page < totalPages;
  const hasPrev = page > 1;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">탐정 관리</h1>
          <p className="mt-1 text-sm text-gray-500">
            총 {total}명의 탐정
          </p>
        </div>
        <button
          type="button"
          onClick={onAdd}
          className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          탐정 추가
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
          placeholder="이름, 전화번호, 전문분야로 검색..."
          className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
        />
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-purple-600 border-t-transparent" />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && detectives.length === 0 && (
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
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <p className="mt-4 text-gray-500">
            {search ? '검색 결과가 없습니다' : '등록된 탐정이 없습니다'}
          </p>
          {!search && (
            <button
              type="button"
              onClick={onAdd}
              className="mt-4 text-sm text-purple-600 hover:text-purple-800"
            >
              첫 탐정을 추가하세요
            </button>
          )}
        </div>
      )}

      {/* Detective Grid */}
      {!isLoading && detectives.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {detectives.map((detective) => (
            <DetectiveCard
              key={detective.id}
              detective={detective}
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

export default DetectiveList;

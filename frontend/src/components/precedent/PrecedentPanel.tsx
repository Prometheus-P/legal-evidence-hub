/**
 * Precedent Panel Component
 * 012-precedent-integration: T027, T030, T031
 */

'use client';

import { useState, useEffect } from 'react';
import type { PrecedentCase, PrecedentSearchResponse } from '@/types/precedent';
import { searchSimilarPrecedents } from '@/lib/api/precedent';
import { PrecedentCard } from './PrecedentCard';
import { PrecedentModal } from './PrecedentModal';

interface PrecedentPanelProps {
  caseId: string;
  className?: string;
  hideHeader?: boolean;
}

export function PrecedentPanel({ caseId, className = '', hideHeader = false }: PrecedentPanelProps) {
  const [data, setData] = useState<PrecedentSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPrecedent, setSelectedPrecedent] = useState<PrecedentCase | null>(null);
  const [isSearched, setIsSearched] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await searchSimilarPrecedents(caseId, { limit: 10, min_score: 0.3 });
      setData(result);
      setIsSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : '판례 검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // T031: Empty results handling
  const renderContent = () => {
    if (!isSearched) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400 mb-4">유사 판례를 검색하여 참고 자료를 확인하세요.</p>
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? '검색 중...' : '유사 판례 검색'}
          </button>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-8">
          <p className="text-red-500 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-gray-200 dark:bg-neutral-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-neutral-600 transition-colors"
          >
            다시 시도
          </button>
        </div>
      );
    }

    if (!data || data.precedents.length === 0) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">관련 판례를 찾을 수 없습니다.</p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
            검색 조건을 변경하거나 사건 정보를 추가해 보세요.
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {data.precedents.map((precedent, index) => (
          <PrecedentCard
            key={`${precedent.case_ref}-${index}`}
            precedent={precedent}
            onClick={() => setSelectedPrecedent(precedent)}
          />
        ))}
      </div>
    );
  };

  return (
    <div className={`bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 ${className}`}>
      {/* Header */}
      {!hideHeader && (
        <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-800 flex justify-between items-center">
          <h2 className="font-semibold text-gray-900 dark:text-gray-100">유사 판례</h2>
          {isSearched && data && (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {data.query_context.total_found}건 발견
            </span>
          )}
        </div>
      )}

      {/* Query Context */}
      {isSearched && data && data.query_context.fault_types.length > 0 && (
        <div className="px-4 py-2 bg-gray-50 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-800">
          <span className="text-xs text-gray-500 dark:text-gray-400">검색 키워드: </span>
          <span className="text-xs text-gray-700 dark:text-gray-300">
            {data.query_context.fault_types.join(', ')}
          </span>
        </div>
      )}

      {/* Content */}
      <div className="p-4">{renderContent()}</div>

      {/* Refresh Button */}
      {isSearched && (
        <div className="px-4 py-3 border-t border-neutral-200 dark:border-neutral-800">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full px-3 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded transition-colors disabled:opacity-50"
          >
            {loading ? '검색 중...' : '새로고침'}
          </button>
        </div>
      )}

      {/* Modal */}
      <PrecedentModal
        precedent={selectedPrecedent}
        isOpen={!!selectedPrecedent}
        onClose={() => setSelectedPrecedent(null)}
      />
    </div>
  );
}

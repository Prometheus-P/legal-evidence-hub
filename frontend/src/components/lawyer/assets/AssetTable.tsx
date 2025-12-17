/**
 * AssetTable Component
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Table display for assets with sorting and actions
 */

'use client';

import { useState, useMemo } from 'react';
import type { Asset, AssetCategory } from '@/types/asset';
import {
  ASSET_CATEGORY_LABELS,
  ASSET_OWNERSHIP_LABELS,
  ASSET_NATURE_LABELS,
  formatKoreanCurrency,
} from '@/types/asset';

interface AssetTableProps {
  assets: Asset[];
  onEdit?: (asset: Asset) => void;
  onDelete?: (asset: Asset) => void;
  onSelect?: (asset: Asset) => void;
  selectedId?: string;
  loading?: boolean;
  className?: string;
}

type SortField = 'name' | 'category' | 'ownership' | 'current_value' | 'created_at';
type SortDirection = 'asc' | 'desc';

const CATEGORY_FILTERS: { value: AssetCategory | 'all'; label: string }[] = [
  { value: 'all', label: '전체' },
  { value: 'real_estate', label: '부동산' },
  { value: 'savings', label: '예금/적금' },
  { value: 'stocks', label: '주식/증권' },
  { value: 'retirement', label: '퇴직금/연금' },
  { value: 'vehicle', label: '차량' },
  { value: 'insurance', label: '보험' },
  { value: 'debt', label: '부채' },
  { value: 'other', label: '기타' },
];

export default function AssetTable({
  assets,
  onEdit,
  onDelete,
  onSelect,
  selectedId,
  loading = false,
  className = '',
}: AssetTableProps) {
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [categoryFilter, setCategoryFilter] = useState<AssetCategory | 'all'>('all');

  // Filter and sort assets
  const filteredAssets = useMemo(() => {
    let result = [...assets];

    // Apply category filter
    if (categoryFilter !== 'all') {
      result = result.filter((a) => a.category === categoryFilter);
    }

    // Apply sorting
    result.sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'category':
          comparison = a.category.localeCompare(b.category);
          break;
        case 'ownership':
          comparison = a.ownership.localeCompare(b.ownership);
          break;
        case 'current_value':
          comparison = a.current_value - b.current_value;
          break;
        case 'created_at':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [assets, categoryFilter, sortField, sortDirection]);

  // Calculate totals
  const totals = useMemo(() => {
    const plaintiff = filteredAssets
      .filter((a) => a.ownership === 'plaintiff' && a.category !== 'debt')
      .reduce((sum, a) => sum + a.current_value, 0);
    const defendant = filteredAssets
      .filter((a) => a.ownership === 'defendant' && a.category !== 'debt')
      .reduce((sum, a) => sum + a.current_value, 0);
    const joint = filteredAssets
      .filter((a) => a.ownership === 'joint' && a.category !== 'debt')
      .reduce((sum, a) => sum + a.current_value, 0);
    const debts = filteredAssets
      .filter((a) => a.category === 'debt')
      .reduce((sum, a) => sum + a.current_value, 0);

    return { plaintiff, defendant, joint, debts, total: plaintiff + defendant + joint - debts };
  }, [filteredAssets]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <span className="text-neutral-400 ml-1">⇅</span>;
    }
    return <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>;
  };

  const thClass =
    'px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-700';
  const tdClass = 'px-4 py-3 whitespace-nowrap text-sm';

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-neutral-200 dark:bg-neutral-700 rounded mb-4" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 bg-neutral-100 dark:bg-neutral-800 rounded mb-2" />
        ))}
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Filter */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <label className="text-sm text-neutral-600 dark:text-neutral-400">분류:</label>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value as AssetCategory | 'all')}
            className="px-3 py-1.5 text-sm border border-neutral-300 dark:border-neutral-600 rounded-md bg-white dark:bg-neutral-800"
          >
            {CATEGORY_FILTERS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        <div className="text-sm text-neutral-500 dark:text-neutral-400">
          총 {filteredAssets.length}건
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-neutral-200 dark:border-neutral-700 rounded-lg">
        <table className="min-w-full divide-y divide-neutral-200 dark:divide-neutral-700">
          <thead className="bg-neutral-50 dark:bg-neutral-800">
            <tr>
              <th className={thClass} onClick={() => handleSort('category')}>
                분류 <SortIcon field="category" />
              </th>
              <th className={thClass} onClick={() => handleSort('name')}>
                명칭 <SortIcon field="name" />
              </th>
              <th className={thClass} onClick={() => handleSort('ownership')}>
                소유자 <SortIcon field="ownership" />
              </th>
              <th className={thClass}>성격</th>
              <th className={`${thClass} text-right`} onClick={() => handleSort('current_value')}>
                현재 가치 <SortIcon field="current_value" />
              </th>
              <th className={thClass}>비율</th>
              {(onEdit || onDelete) && <th className={thClass}>작업</th>}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-neutral-900 divide-y divide-neutral-200 dark:divide-neutral-700">
            {filteredAssets.length === 0 ? (
              <tr>
                <td
                  colSpan={7}
                  className="px-4 py-8 text-center text-neutral-500 dark:text-neutral-400"
                >
                  등록된 재산이 없습니다.
                </td>
              </tr>
            ) : (
              filteredAssets.map((asset) => (
                <tr
                  key={asset.id}
                  className={`hover:bg-neutral-50 dark:hover:bg-neutral-800 cursor-pointer transition-colors ${
                    selectedId === asset.id ? 'bg-primary-light dark:bg-primary/20' : ''
                  }`}
                  onClick={() => onSelect?.(asset)}
                >
                  <td className={tdClass}>
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        asset.category === 'debt'
                          ? 'bg-error-light text-error'
                          : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300'
                      }`}
                    >
                      {ASSET_CATEGORY_LABELS[asset.category]}
                    </span>
                  </td>
                  <td className={`${tdClass} font-medium text-neutral-900 dark:text-white`}>
                    {asset.name}
                  </td>
                  <td className={tdClass}>
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        asset.ownership === 'plaintiff'
                          ? 'bg-primary-light text-primary'
                          : asset.ownership === 'defendant'
                            ? 'bg-secondary-light text-secondary'
                            : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-400'
                      }`}
                    >
                      {ASSET_OWNERSHIP_LABELS[asset.ownership]}
                    </span>
                  </td>
                  <td className={`${tdClass} text-neutral-500 dark:text-neutral-400`}>
                    {ASSET_NATURE_LABELS[asset.nature]}
                  </td>
                  <td
                    className={`${tdClass} text-right font-mono ${
                      asset.category === 'debt' ? 'text-error' : 'text-neutral-900 dark:text-white'
                    }`}
                  >
                    {asset.category === 'debt' && '-'}
                    {formatKoreanCurrency(asset.current_value)}
                  </td>
                  <td className={`${tdClass} text-neutral-500 dark:text-neutral-400`}>
                    {asset.division_ratio_plaintiff}:{asset.division_ratio_defendant}
                  </td>
                  {(onEdit || onDelete) && (
                    <td className={tdClass}>
                      <div className="flex items-center space-x-2">
                        {onEdit && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onEdit(asset);
                            }}
                            className="text-primary hover:text-primary-hover text-sm"
                          >
                            수정
                          </button>
                        )}
                        {onDelete && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onDelete(asset);
                            }}
                            className="text-error hover:text-error-hover text-sm"
                          >
                            삭제
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
          {filteredAssets.length > 0 && (
            <tfoot className="bg-neutral-50 dark:bg-neutral-800">
              <tr>
                <td colSpan={4} className={`${tdClass} font-medium`}>
                  합계
                </td>
                <td className={`${tdClass} text-right font-mono font-medium`}>
                  {formatKoreanCurrency(totals.total)}
                </td>
                <td colSpan={2} />
              </tr>
              <tr className="text-xs text-neutral-500 dark:text-neutral-400">
                <td colSpan={4} className="px-4 py-2">
                  원고: {formatKoreanCurrency(totals.plaintiff)} / 피고:{' '}
                  {formatKoreanCurrency(totals.defendant)} / 공동:{' '}
                  {formatKoreanCurrency(totals.joint)} / 부채: -{formatKoreanCurrency(totals.debts)}
                </td>
                <td colSpan={3} />
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  );
}

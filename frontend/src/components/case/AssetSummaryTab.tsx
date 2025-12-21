/**
 * AssetSummaryTab Component
 *
 * Embedded asset division view for the case detail page.
 * Shows summary cards at top with expandable full asset table.
 */

'use client';

import { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, DollarSign, TrendingDown, Scale, Plus, AlertCircle } from 'lucide-react';
import { useAssets } from '@/hooks/useAssets';
import type { LegacyAsset as Asset, AssetType, CreateAssetRequest } from '@/types/asset';
import { ASSET_TYPE_CONFIG, OWNERSHIP_CONFIG } from '@/types/asset';

// Format currency in Korean Won
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    maximumFractionDigits: 0,
  }).format(value);
}

// Compact format for large numbers
function formatCompact(value: number): string {
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(1)}억`;
  }
  if (value >= 10000) {
    return `${(value / 10000).toFixed(0)}만`;
  }
  return formatCurrency(value);
}

interface SummaryCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  isNegative?: boolean;
  bgColor: string;
  iconColor: string;
}

function SummaryCard({ icon, label, value, isNegative, bgColor, iconColor }: SummaryCardProps) {
  return (
    <div className={`${bgColor} rounded-lg p-4`}>
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconColor}`}>
          {icon}
        </div>
        <div>
          <div className="text-sm text-neutral-600 dark:text-neutral-400">{label}</div>
          <div className={`text-lg font-bold ${isNegative ? 'text-red-600 dark:text-red-400' : 'text-neutral-900 dark:text-white'}`}>
            {isNegative && '-'}{formatCompact(Math.abs(value))}
          </div>
        </div>
      </div>
    </div>
  );
}

interface AssetSummaryTabProps {
  caseId: string;
}

export function AssetSummaryTab({ caseId }: AssetSummaryTabProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  const {
    assets,
    assetsByType,
    divisionSummary,
    isLoading,
    addAsset,
    removeAsset,
    updateDivisionRatio,
  } = useAssets({ caseId });

  const handleAddAsset = async (data: CreateAssetRequest) => {
    try {
      await addAsset(data);
      setShowAddForm(false);
    } catch {
      // Error handling
    }
  };

  const handleDeleteAsset = async (assetId: string) => {
    if (confirm('이 재산을 삭제하시겠습니까?')) {
      try {
        await removeAsset(assetId);
      } catch {
        // Error handling
      }
    }
  };

  const handleRatioChange = (assetId: string, plaintiffRatio: number) => {
    updateDivisionRatio(assetId, plaintiffRatio, 100 - plaintiffRatio);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SummaryCard
          icon={<DollarSign className="w-5 h-5" />}
          label="총 자산"
          value={divisionSummary.total_assets}
          bgColor="bg-emerald-50 dark:bg-emerald-900/20"
          iconColor="bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400"
        />
        <SummaryCard
          icon={<TrendingDown className="w-5 h-5" />}
          label="총 부채"
          value={divisionSummary.total_debts}
          isNegative
          bgColor="bg-red-50 dark:bg-red-900/20"
          iconColor="bg-red-100 dark:bg-red-900/50 text-red-600 dark:text-red-400"
        />
        <SummaryCard
          icon={<Scale className="w-5 h-5" />}
          label="순자산"
          value={divisionSummary.net_value}
          bgColor="bg-blue-50 dark:bg-blue-900/20"
          iconColor="bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400"
        />
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-400">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm text-neutral-600 dark:text-neutral-400">분할 비율</div>
              <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                50:50
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Division Result Preview */}
      <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-neutral-900 dark:text-white">분할 결과 예상</h3>
          {divisionSummary.settlement_needed !== 0 && (
            <span className="flex items-center gap-1 text-sm text-amber-600 dark:text-amber-400">
              <AlertCircle className="w-4 h-4" />
              정산 필요
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg text-center">
            <div className="text-sm text-teal-600 dark:text-teal-400 mb-1">원고 취득 예정</div>
            <div className="text-2xl font-bold text-teal-700 dark:text-teal-300">
              {formatCurrency(divisionSummary.plaintiff_share)}
            </div>
          </div>
          <div className="p-4 bg-slate-50 dark:bg-slate-900/20 rounded-lg text-center">
            <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">피고 취득 예정</div>
            <div className="text-2xl font-bold text-slate-700 dark:text-slate-300">
              {formatCurrency(divisionSummary.defendant_share)}
            </div>
          </div>
        </div>
        {divisionSummary.settlement_needed !== 0 && (
          <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-900/30 rounded-lg text-sm text-amber-700 dark:text-amber-300">
            {divisionSummary.settlement_needed > 0
              ? `피고가 원고에게 ${formatCurrency(Math.abs(divisionSummary.settlement_needed))} 정산 필요`
              : `원고가 피고에게 ${formatCurrency(Math.abs(divisionSummary.settlement_needed))} 정산 필요`}
          </div>
        )}
      </div>

      {/* Expandable Asset List */}
      <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors"
        >
          <div>
            <h3 className="font-semibold text-neutral-900 dark:text-white">
              재산 목록 ({assets.length}건)
            </h3>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">
              {isExpanded ? '클릭하여 접기' : '클릭하여 상세 보기'}
            </p>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-neutral-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-neutral-400" />
          )}
        </button>

        {isExpanded && (
          <div className="border-t border-neutral-200 dark:border-neutral-700 p-4 space-y-4">
            {/* Add Asset Button */}
            {!showAddForm && (
              <button
                onClick={() => setShowAddForm(true)}
                className="w-full p-3 border-2 border-dashed border-neutral-300 dark:border-neutral-700 rounded-lg text-neutral-500 dark:text-neutral-400 hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] transition-colors flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" />
                재산 추가
              </button>
            )}

            {showAddForm && (
              <AddAssetFormInline
                onSubmit={handleAddAsset}
                onCancel={() => setShowAddForm(false)}
              />
            )}

            {/* Asset List by Type */}
            {Object.entries(assetsByType).map(([type, typeAssets]) => {
              if (typeAssets.length === 0) return null;
              const config = ASSET_TYPE_CONFIG[type as AssetType] || ASSET_TYPE_CONFIG['other'];

              return (
                <div key={type} className="space-y-2">
                  <h4 className="font-medium text-neutral-700 dark:text-neutral-300 text-sm flex items-center gap-2">
                    {config.label}
                    <span className="text-xs text-neutral-400">({typeAssets.length})</span>
                  </h4>
                  {typeAssets.map((asset) => (
                    <AssetRowCompact
                      key={asset.id}
                      asset={asset}
                      onDelete={handleDeleteAsset}
                      onRatioChange={handleRatioChange}
                    />
                  ))}
                </div>
              );
            })}

            {assets.length === 0 && !showAddForm && (
              <div className="text-center py-8 text-neutral-500 dark:text-neutral-400">
                등록된 재산이 없습니다.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Legal Notice */}
      <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-sm text-blue-700 dark:text-blue-300">
        <strong>안내:</strong> 이 결과는 입력된 정보를 기준으로 한 예상치입니다.
        실제 분할 결과는 법원의 판단에 따라 달라질 수 있습니다.
      </div>
    </div>
  );
}

// Compact asset row for inline display
function AssetRowCompact({
  asset,
  onDelete,
  onRatioChange,
}: {
  asset: Asset;
  onDelete: (assetId: string) => void;
  onRatioChange: (assetId: string, plaintiffRatio: number) => void;
}) {
  const ownershipConfig = OWNERSHIP_CONFIG[asset.ownership] || OWNERSHIP_CONFIG['joint'];
  const isDebt = asset.asset_type === 'debt';

  return (
    <div className="flex items-center gap-4 p-3 bg-neutral-50 dark:bg-neutral-900 rounded-lg">
      <div className="flex-1 min-w-0">
        <div className="font-medium text-neutral-900 dark:text-neutral-100 truncate text-sm">
          {asset.name}
        </div>
        <div className="text-xs text-neutral-500 dark:text-neutral-400">
          <span style={{ color: ownershipConfig.color }}>{ownershipConfig.label}</span>
        </div>
      </div>

      <div className={`text-right ${isDebt ? 'text-red-600 dark:text-red-400' : 'text-neutral-900 dark:text-neutral-100'}`}>
        <div className="font-semibold text-sm">
          {isDebt ? '-' : ''}{formatCurrency(asset.current_value)}
        </div>
      </div>

      <div className="w-24">
        <div className="text-xs text-neutral-500 dark:text-neutral-400 text-center">
          {asset.division_ratio_plaintiff}:{asset.division_ratio_defendant}
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={asset.division_ratio_plaintiff}
          onChange={(e) => onRatioChange(asset.id, parseInt(e.target.value, 10))}
          className="w-full h-1.5 bg-neutral-200 dark:bg-neutral-700 rounded-lg appearance-none cursor-pointer"
        />
      </div>

      <button
        onClick={() => onDelete(asset.id)}
        className="p-1.5 text-neutral-400 hover:text-red-500 transition-colors"
        title="삭제"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  );
}

// Inline add asset form
function AddAssetFormInline({
  onSubmit,
  onCancel,
}: {
  onSubmit: (data: CreateAssetRequest) => void;
  onCancel: () => void;
}) {
  const [formData, setFormData] = useState<CreateAssetRequest>({
    asset_type: 'real_estate',
    name: '',
    current_value: 0,
    ownership: 'joint',
    division_ratio_plaintiff: 50,
    division_ratio_defendant: 50,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || formData.current_value <= 0) return;
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-neutral-50 dark:bg-neutral-900 rounded-lg p-4 space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-neutral-600 dark:text-neutral-400 mb-1">유형</label>
          <select
            value={formData.asset_type}
            onChange={(e) => setFormData({ ...formData, asset_type: e.target.value as AssetType })}
            className="w-full border border-neutral-200 dark:border-neutral-700 dark:bg-neutral-800 rounded-md px-2 py-1.5 text-sm"
          >
            {Object.entries(ASSET_TYPE_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-neutral-600 dark:text-neutral-400 mb-1">소유</label>
          <select
            value={formData.ownership}
            onChange={(e) => setFormData({ ...formData, ownership: e.target.value as 'plaintiff' | 'defendant' | 'joint' })}
            className="w-full border border-neutral-200 dark:border-neutral-700 dark:bg-neutral-800 rounded-md px-2 py-1.5 text-sm"
          >
            {Object.entries(OWNERSHIP_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-neutral-600 dark:text-neutral-400 mb-1">재산명</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="예: 강남 아파트"
            className="w-full border border-neutral-200 dark:border-neutral-700 dark:bg-neutral-800 rounded-md px-2 py-1.5 text-sm"
            required
          />
        </div>
        <div>
          <label className="block text-xs text-neutral-600 dark:text-neutral-400 mb-1">현재 가치 (원)</label>
          <input
            type="number"
            value={formData.current_value || ''}
            onChange={(e) => setFormData({ ...formData, current_value: parseInt(e.target.value, 10) || 0 })}
            className="w-full border border-neutral-200 dark:border-neutral-700 dark:bg-neutral-800 rounded-md px-2 py-1.5 text-sm"
            min="0"
            required
          />
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md"
        >
          취소
        </button>
        <button
          type="submit"
          className="px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded-md hover:bg-[var(--color-primary-hover)]"
        >
          추가
        </button>
      </div>
    </form>
  );
}

export default AssetSummaryTab;

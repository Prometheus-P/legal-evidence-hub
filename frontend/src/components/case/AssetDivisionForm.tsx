/**
 * Asset Division Form Component
 * 009-calm-control-design-system
 *
 * Form for managing divorce case asset division.
 */

'use client';

import { useState, useCallback } from 'react';
import { useAssets } from '@/hooks/useAssets';
import type { Asset, AssetType, OwnershipType, CreateAssetRequest } from '@/types/assets';
import { ASSET_TYPE_CONFIG, OWNERSHIP_CONFIG } from '@/types/assets';

// Format currency in Korean Won
function formatCurrency(value: number): string {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    maximumFractionDigits: 0,
  }).format(value);
}

// Asset type icons (SVG components)
const BuildingIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
  </svg>
);

const CarIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
  </svg>
);

const WalletIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
  </svg>
);

const BriefcaseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);

const PackageIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
  </svg>
);

const CreditCardIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
  </svg>
);

const getAssetIcon = (iconName: string) => {
  const icons: Record<string, React.FC<{ className?: string }>> = {
    Building: BuildingIcon,
    Car: CarIcon,
    Wallet: WalletIcon,
    Briefcase: BriefcaseIcon,
    Package: PackageIcon,
    CreditCard: CreditCardIcon,
  };
  return icons[iconName] || PackageIcon;
};

// Asset row component
function AssetRow({
  asset,
  onEdit,
  onDelete,
  onRatioChange,
}: {
  asset: Asset;
  onEdit: (asset: Asset) => void;
  onDelete: (assetId: string) => void;
  onRatioChange: (assetId: string, plaintiffRatio: number) => void;
}) {
  const config = ASSET_TYPE_CONFIG[asset.asset_type];
  const ownershipConfig = OWNERSHIP_CONFIG[asset.ownership];
  const IconComponent = getAssetIcon(config.icon);
  const isDebt = asset.asset_type === 'debt';

  return (
    <div className="flex items-center gap-4 p-4 bg-white rounded-lg border border-neutral-200 hover:border-neutral-300 transition-colors">
      <div className={`flex items-center justify-center w-10 h-10 rounded-lg ${isDebt ? 'bg-red-50' : 'bg-teal-50'}`}>
        <IconComponent className={`w-5 h-5 ${isDebt ? 'text-red-500' : 'text-teal-500'}`} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="font-medium text-gray-900 truncate">{asset.name}</div>
        <div className="text-sm text-gray-500 flex items-center gap-2">
          <span>{config.label}</span>
          <span className="text-neutral-300">|</span>
          <span style={{ color: ownershipConfig.color }}>{ownershipConfig.label}</span>
        </div>
      </div>

      <div className={`text-right ${isDebt ? 'text-red-600' : 'text-gray-900'}`}>
        <div className="font-semibold">
          {isDebt ? '-' : ''}{formatCurrency(asset.current_value)}
        </div>
      </div>

      <div className="w-32">
        <div className="text-xs text-gray-500 mb-1 text-center">
          원고 {asset.division_ratio_plaintiff}% : 피고 {asset.division_ratio_defendant}%
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={asset.division_ratio_plaintiff}
          onChange={(e) => onRatioChange(asset.id, parseInt(e.target.value, 10))}
          className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
        />
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => onEdit(asset)}
          className="p-2 text-neutral-400 hover:text-teal-500 transition-colors"
          title="편집"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          onClick={() => onDelete(asset.id)}
          className="p-2 text-neutral-400 hover:text-red-500 transition-colors"
          title="삭제"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  );
}

// Add asset form
function AddAssetForm({
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

  const handleRatioChange = (value: number) => {
    setFormData({
      ...formData,
      division_ratio_plaintiff: value,
      division_ratio_defendant: 100 - value,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-neutral-200 p-4 space-y-4">
      <h3 className="font-medium text-gray-900">새 재산 추가</h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-gray-600 mb-1">재산 유형</label>
          <select
            value={formData.asset_type}
            onChange={(e) => setFormData({ ...formData, asset_type: e.target.value as AssetType })}
            className="w-full border border-neutral-200 rounded-lg px-3 py-2 text-sm"
          >
            {Object.entries(ASSET_TYPE_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">소유 구분</label>
          <select
            value={formData.ownership}
            onChange={(e) => setFormData({ ...formData, ownership: e.target.value as OwnershipType })}
            className="w-full border border-neutral-200 rounded-lg px-3 py-2 text-sm"
          >
            {Object.entries(OWNERSHIP_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">재산명</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="예: 서울 강남구 아파트"
          className="w-full border border-neutral-200 rounded-lg px-3 py-2 text-sm"
          required
        />
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">현재 가치 (원)</label>
        <input
          type="number"
          value={formData.current_value || ''}
          onChange={(e) => setFormData({ ...formData, current_value: parseInt(e.target.value, 10) || 0 })}
          placeholder="0"
          className="w-full border border-neutral-200 rounded-lg px-3 py-2 text-sm"
          min="0"
          required
        />
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">
          분할 비율: 원고 {formData.division_ratio_plaintiff}% : 피고 {formData.division_ratio_defendant}%
        </label>
        <input
          type="range"
          min="0"
          max="100"
          value={formData.division_ratio_plaintiff}
          onChange={(e) => handleRatioChange(parseInt(e.target.value, 10))}
          className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer"
        />
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm text-gray-600 hover:bg-neutral-100 rounded-lg"
        >
          취소
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm bg-teal-500 text-white rounded-lg hover:bg-teal-600"
        >
          추가
        </button>
      </div>
    </form>
  );
}

// Division Summary Card
function DivisionSummaryCard({
  summary,
}: {
  summary: {
    total_assets: number;
    total_debts: number;
    net_value: number;
    plaintiff_share: number;
    defendant_share: number;
    settlement_needed: number;
  };
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-neutral-200 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">분할 결과 Preview</h3>

      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-600">총 자산</span>
          <span className="font-medium text-gray-900">{formatCurrency(summary.total_assets)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">총 부채</span>
          <span className="font-medium text-red-600">-{formatCurrency(summary.total_debts)}</span>
        </div>
        <div className="border-t border-neutral-200 pt-3 flex justify-between">
          <span className="text-gray-600">순자산</span>
          <span className="font-semibold text-gray-900">{formatCurrency(summary.net_value)}</span>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-neutral-200 space-y-3">
        <div className="flex justify-between">
          <span className="text-teal-600 font-medium">원고 취득 예정</span>
          <span className="font-semibold text-teal-600">{formatCurrency(summary.plaintiff_share)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-700 font-medium">피고 취득 예정</span>
          <span className="font-semibold text-slate-700">{formatCurrency(summary.defendant_share)}</span>
        </div>
      </div>

      {summary.settlement_needed !== 0 && (
        <div className="mt-4 p-3 bg-amber-50 rounded-lg">
          <div className="text-sm text-amber-800 font-medium">
            {summary.settlement_needed > 0
              ? `피고가 원고에게 ${formatCurrency(Math.abs(summary.settlement_needed))} 정산 필요`
              : `원고가 피고에게 ${formatCurrency(Math.abs(summary.settlement_needed))} 정산 필요`}
          </div>
        </div>
      )}
    </div>
  );
}

interface AssetDivisionFormProps {
  caseId: string;
}

export function AssetDivisionForm({ caseId }: AssetDivisionFormProps) {
  const {
    assets,
    assetsByType,
    divisionSummary,
    isLoading,
    addAsset,
    removeAsset,
    updateDivisionRatio,
  } = useAssets({ caseId });

  const [showAddForm, setShowAddForm] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);

  const handleAddAsset = useCallback(
    async (data: CreateAssetRequest) => {
      try {
        await addAsset(data);
        setShowAddForm(false);
      } catch (err) {
        console.error('Failed to add asset:', err);
      }
    },
    [addAsset]
  );

  const handleDeleteAsset = useCallback(
    async (assetId: string) => {
      if (confirm('이 재산을 삭제하시겠습니까?')) {
        try {
          await removeAsset(assetId);
        } catch (err) {
          console.error('Failed to delete asset:', err);
        }
      }
    },
    [removeAsset]
  );

  const handleRatioChange = useCallback(
    (assetId: string, plaintiffRatio: number) => {
      updateDivisionRatio(assetId, plaintiffRatio, 100 - plaintiffRatio);
    },
    [updateDivisionRatio]
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-neutral-500">재산 정보 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        {!showAddForm && (
          <button
            onClick={() => setShowAddForm(true)}
            className="w-full p-3 border-2 border-dashed border-neutral-300 rounded-lg text-neutral-500 hover:border-teal-500 hover:text-teal-500 transition-colors"
          >
            + 재산 추가
          </button>
        )}

        {showAddForm && (
          <AddAssetForm onSubmit={handleAddAsset} onCancel={() => setShowAddForm(false)} />
        )}

        {Object.entries(assetsByType).map(([type, typeAssets]) => {
          if (typeAssets.length === 0) return null;
          const config = ASSET_TYPE_CONFIG[type as AssetType];

          return (
            <div key={type} className="space-y-2">
              <h3 className="font-medium text-gray-700 flex items-center gap-2">
                {config.label}
                <span className="text-sm text-neutral-400">({typeAssets.length})</span>
              </h3>
              {typeAssets.map((asset) => (
                <AssetRow
                  key={asset.id}
                  asset={asset}
                  onEdit={setEditingAsset}
                  onDelete={handleDeleteAsset}
                  onRatioChange={handleRatioChange}
                />
              ))}
            </div>
          );
        })}

        {assets.length === 0 && !showAddForm && (
          <div className="text-center py-12 text-neutral-500">
            등록된 재산이 없습니다. 위 버튼을 클릭하여 재산을 추가하세요.
          </div>
        )}
      </div>

      <div className="lg:col-span-1">
        <div className="sticky top-6">
          <DivisionSummaryCard summary={divisionSummary} />

          <div className="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-700">
            <strong>안내:</strong> 이 결과는 입력된 정보를 기준으로 한 예상치입니다.
            실제 분할 결과는 법원의 판단에 따라 달라질 수 있습니다.
          </div>
        </div>
      </div>
    </div>
  );
}

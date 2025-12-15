/**
 * Asset Sheet Client Component
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Korean divorce property division calculation page
 * Based on Civil Code Article 839-2
 */

'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAssets } from '@/hooks/useAssets';
import { AssetForm, AssetTable, DivisionSummary } from '@/components/lawyer/assets';
// Note: Type mismatch between @/types/asset (components) and @/types/assets (hook)
// Using 'unknown' to bridge the gap until types are unified
import type { Asset as ComponentAsset, DivisionSummary as ComponentDivisionSummary } from '@/types/asset';
import type { Asset, CreateAssetRequest } from '@/types/assets';
import { getCaseDetailPath, getLawyerCasePath } from '@/lib/portalPaths';

type ViewMode = 'table' | 'form';

interface AssetSheetClientProps {
  caseId: string;
}

export default function AssetSheetClient({ caseId }: AssetSheetClientProps) {
  const router = useRouter();
  const assetsPath = getLawyerCasePath('assets', caseId);
  const detailPath = getCaseDetailPath('lawyer', caseId, { returnUrl: assetsPath });

  const {
    assets,
    divisionSummary,
    selectedAsset,
    isLoading,
    error,
    addAsset,
    updateAsset,
    removeAsset,
    setSelectedAsset,
  } = useAssets({ caseId });

  // Local error state for clearable errors
  const [localError, setLocalError] = useState<string | null>(null);
  const clearError = useCallback(() => setLocalError(null), []);
  const displayError = localError || error;

  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<Asset | null>(null);
  const [plaintiffRatio, setPlaintiffRatio] = useState(50);
  const [defendantRatio, setDefendantRatio] = useState(50);

  // Handle form submission
  const handleSubmit = useCallback(
    async (data: CreateAssetRequest | Partial<CreateAssetRequest>) => {
      if (editingAsset) {
        const result = await updateAsset(editingAsset.id, data as Partial<CreateAssetRequest>);
        if (result) {
          setEditingAsset(null);
          setViewMode('table');
        }
      } else {
        const result = await addAsset(data as CreateAssetRequest);
        if (result) {
          setViewMode('table');
        }
      }
    },
    [editingAsset, updateAsset, addAsset]
  );

  // Handle edit click
  const handleEdit = useCallback((asset: Asset) => {
    setEditingAsset(asset);
    setViewMode('form');
  }, []);

  // Handle delete click
  const handleDeleteClick = useCallback((asset: Asset) => {
    setShowDeleteConfirm(asset);
  }, []);

  // Confirm delete
  const handleDeleteConfirm = useCallback(async () => {
    if (showDeleteConfirm) {
      await removeAsset(showDeleteConfirm.id);
      setShowDeleteConfirm(null);
    }
  }, [showDeleteConfirm, removeAsset]);

  // Handle cancel
  const handleCancel = useCallback(() => {
    setEditingAsset(null);
    setViewMode('table');
  }, []);

  // Handle recalculate (now local-only since division is calculated from assets)
  const handleRecalculate = useCallback(
    (pRatio: number, _dRatio: number) => {
      setPlaintiffRatio(pRatio);
      setDefendantRatio(100 - pRatio);
      // Division summary is automatically calculated from assets
    },
    []
  );

  // Handle ratio change
  const handleRatioChange = useCallback((value: number) => {
    setPlaintiffRatio(value);
    setDefendantRatio(100 - value);
  }, []);

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900">
      {/* Header */}
      <header className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* T073 - FR-028: Back button to case detail */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push(detailPath)}
                className="text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200"
              >
                ← 뒤로
              </button>
              <div>
                <h1 className="text-xl font-semibold text-neutral-900 dark:text-white">
                  재산분할표
                </h1>
                <p className="text-sm text-neutral-500 dark:text-neutral-400">
                  민법 제839조의2에 따른 재산분할 계산
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {viewMode === 'table' && (
                <>
                  <button
                    onClick={() => {
                      // TODO: Implement CSV export
                      alert('CSV 내보내기 기능은 준비 중입니다.');
                    }}
                    className="px-4 py-2 text-sm border border-neutral-300 dark:border-neutral-600 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
                  >
                    CSV 내보내기
                  </button>
                  <button
                    onClick={() => {
                      setEditingAsset(null);
                      setViewMode('form');
                    }}
                    className="px-4 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary-hover transition-colors"
                  >
                    + 재산 추가
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Error Alert */}
      {displayError && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-error-light border border-error rounded-lg p-4 flex items-center justify-between">
            <span className="text-error">{displayError}</span>
            <button
              onClick={clearError}
              className="text-error hover:text-error-hover"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {viewMode === 'form' ? (
          <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-6">
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white mb-6">
              {editingAsset ? '재산 수정' : '재산 추가'}
            </h2>
            <AssetForm
              asset={editingAsset as unknown as ComponentAsset | null}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              loading={isLoading}
            />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Division Ratio Controls */}
            <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                    분할 비율 설정
                  </h3>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                    원고와 피고의 재산분할 비율을 설정합니다
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <label className="text-sm text-neutral-600 dark:text-neutral-400">
                      원고:
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={plaintiffRatio}
                      onChange={(e) => handleRatioChange(parseInt(e.target.value) || 0)}
                      className="w-16 px-2 py-1 text-center border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-800"
                    />
                    <span className="text-neutral-500">%</span>
                  </div>
                  <span className="text-neutral-400">:</span>
                  <div className="flex items-center space-x-2">
                    <label className="text-sm text-neutral-600 dark:text-neutral-400">
                      피고:
                    </label>
                    <input
                      type="number"
                      value={defendantRatio}
                      readOnly
                      className="w-16 px-2 py-1 text-center border border-neutral-300 dark:border-neutral-600 rounded-md bg-neutral-100 dark:bg-neutral-700"
                    />
                    <span className="text-neutral-500">%</span>
                  </div>
                  <button
                    onClick={() => handleRecalculate(plaintiffRatio, defendantRatio)}
                    disabled={isLoading}
                    className="px-4 py-1.5 text-sm bg-primary text-white rounded-md hover:bg-primary-hover disabled:opacity-50 transition-colors"
                  >
                    {isLoading ? '계산 중...' : '계산하기'}
                  </button>
                </div>
              </div>
            </div>

            {/* Division Summary */}
            <DivisionSummary
              summary={divisionSummary as unknown as ComponentDivisionSummary | null}
              plaintiffRatio={plaintiffRatio}
              defendantRatio={defendantRatio}
              onRecalculate={handleRecalculate}
              calculating={isLoading}
            />

            {/* Asset Table */}
            <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-4">
                재산 목록
              </h3>
              <AssetTable
                assets={assets as unknown as ComponentAsset[]}
                onEdit={handleEdit as unknown as (asset: ComponentAsset) => void}
                onDelete={handleDeleteClick as unknown as (asset: ComponentAsset) => void}
                onSelect={setSelectedAsset as unknown as (asset: ComponentAsset | null) => void}
                selectedId={selectedAsset?.id}
                loading={isLoading}
              />
            </div>
          </div>
        )}
      </main>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-6 max-w-md mx-4">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white mb-2">
              재산 삭제 확인
            </h3>
            <p className="text-neutral-600 dark:text-neutral-400 mb-4">
              &quot;{showDeleteConfirm.name}&quot; 항목을 삭제하시겠습니까?
              <br />
              <span className="text-sm text-error">이 작업은 되돌릴 수 없습니다.</span>
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-md transition-colors"
              >
                취소
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 bg-error text-white rounded-md hover:bg-error-hover transition-colors"
              >
                삭제
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

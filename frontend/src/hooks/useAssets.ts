/**
 * Hook for Asset Division
 * 009-calm-control-design-system
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import type { Asset, CreateAssetRequest, DivisionSummary, AssetType } from '@/types/assets';
import * as assetsApi from '@/lib/api/assets';

interface UseAssetsOptions {
  caseId: string;
}

export function useAssets({ caseId }: UseAssetsOptions) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

  // Calculate division summary locally
  const divisionSummary = useMemo((): DivisionSummary => {
    const totalAssets = assets
      .filter((a) => a.asset_type !== 'debt')
      .reduce((sum, a) => sum + a.current_value, 0);

    const totalDebts = assets
      .filter((a) => a.asset_type === 'debt')
      .reduce((sum, a) => sum + a.current_value, 0);

    const netValue = totalAssets - totalDebts;

    // Calculate each party's share based on division ratios
    let plaintiffShare = 0;
    let defendantShare = 0;

    assets.forEach((asset) => {
      const value = asset.current_value;
      const isDebt = asset.asset_type === 'debt';
      const plaintiffRatio = asset.division_ratio_plaintiff / 100;
      const defendantRatio = asset.division_ratio_defendant / 100;

      if (isDebt) {
        plaintiffShare -= value * plaintiffRatio;
        defendantShare -= value * defendantRatio;
      } else {
        plaintiffShare += value * plaintiffRatio;
        defendantShare += value * defendantRatio;
      }
    });

    const settlementNeeded = plaintiffShare - defendantShare;

    return {
      total_assets: totalAssets,
      total_debts: totalDebts,
      net_value: netValue,
      plaintiff_share: plaintiffShare,
      defendant_share: defendantShare,
      settlement_needed: settlementNeeded / 2,
    };
  }, [assets]);

  // Fetch assets
  const fetchAssets = useCallback(async () => {
    if (!caseId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await assetsApi.getAssets(caseId);
      setAssets(data);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
      setError('재산 데이터를 불러오는데 실패했습니다.');
      // Set mock data for development
      setAssets([
        {
          id: 'a1',
          case_id: caseId,
          asset_type: 'real_estate',
          name: '서울 강남구 아파트',
          current_value: 1200000000,
          ownership: 'joint',
          division_ratio_plaintiff: 50,
          division_ratio_defendant: 50,
          acquisition_date: '2018-05-15',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'a2',
          case_id: caseId,
          asset_type: 'vehicle',
          name: '벤츠 E클래스',
          current_value: 65000000,
          ownership: 'defendant',
          division_ratio_plaintiff: 0,
          division_ratio_defendant: 100,
          acquisition_date: '2022-03-10',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'a3',
          case_id: caseId,
          asset_type: 'financial',
          name: '정기예금 (국민은행)',
          current_value: 150000000,
          ownership: 'plaintiff',
          division_ratio_plaintiff: 100,
          division_ratio_defendant: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'a4',
          case_id: caseId,
          asset_type: 'debt',
          name: '주택담보대출',
          current_value: 500000000,
          ownership: 'joint',
          division_ratio_plaintiff: 50,
          division_ratio_defendant: 50,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  // CRUD operations
  const addAsset = useCallback(
    async (data: CreateAssetRequest) => {
      try {
        const newAsset = await assetsApi.createAsset(caseId, data);
        setAssets((prev) => [...prev, newAsset]);
        return newAsset;
      } catch (err) {
        console.error('Failed to create asset:', err);
        throw err;
      }
    },
    [caseId]
  );

  const updateAsset = useCallback(
    async (assetId: string, data: Partial<CreateAssetRequest>) => {
      try {
        const updated = await assetsApi.updateAsset(caseId, assetId, data);
        setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
        return updated;
      } catch (err) {
        console.error('Failed to update asset:', err);
        throw err;
      }
    },
    [caseId]
  );

  const removeAsset = useCallback(
    async (assetId: string) => {
      try {
        await assetsApi.deleteAsset(caseId, assetId);
        setAssets((prev) => prev.filter((a) => a.id !== assetId));
      } catch (err) {
        console.error('Failed to delete asset:', err);
        throw err;
      }
    },
    [caseId]
  );

  // Update division ratio locally (for preview)
  const updateDivisionRatio = useCallback(
    (assetId: string, plaintiffRatio: number, defendantRatio: number) => {
      setAssets((prev) =>
        prev.map((a) =>
          a.id === assetId
            ? {
                ...a,
                division_ratio_plaintiff: plaintiffRatio,
                division_ratio_defendant: defendantRatio,
              }
            : a
        )
      );
    },
    []
  );

  // Group assets by type
  const assetsByType = useMemo(() => {
    const grouped: Record<AssetType, Asset[]> = {
      real_estate: [],
      vehicle: [],
      financial: [],
      business: [],
      personal: [],
      debt: [],
      other: [],
    };

    assets.forEach((asset) => {
      grouped[asset.asset_type].push(asset);
    });

    return grouped;
  }, [assets]);

  return {
    assets,
    assetsByType,
    divisionSummary,
    isLoading,
    error,
    selectedAsset,
    setSelectedAsset,
    fetchAssets,
    addAsset,
    updateAsset,
    removeAsset,
    updateDivisionRatio,
  };
}

'use client';

/**
 * AssetModal - Modal for adding/editing assets
 * Task 5: 재산 추가 Modal + 분할 예측 제거
 *
 * Fixed division ratio input (manual), not AI-predicted.
 */

import { useState, useCallback, useEffect } from 'react';
import { Building, Car, Wallet, PiggyBank, CreditCard, FileText, HelpCircle } from 'lucide-react';
import { Modal, Button, Input } from '@/components/primitives';
import type { AssetType, CreateAssetRequest } from '@/types/asset';
import { ASSET_TYPE_CONFIG, OWNERSHIP_CONFIG } from '@/types/asset';

interface AssetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateAssetRequest) => Promise<void>;
  isLoading?: boolean;
}

const ASSET_TYPE_ICONS: Partial<Record<AssetType, typeof Building>> = {
  real_estate: Building,
  vehicle: Car,
  savings: PiggyBank,
  stocks: Wallet,
  retirement: Wallet,
  insurance: FileText,
  debt: CreditCard,
  financial: Wallet,
  business: Building,
  personal: HelpCircle,
  other: HelpCircle,
};

export function AssetModal({ isOpen, onClose, onSubmit, isLoading = false }: AssetModalProps) {
  const [formData, setFormData] = useState<CreateAssetRequest>({
    asset_type: 'real_estate',
    name: '',
    current_value: 0,
    ownership: 'joint',
    division_ratio_plaintiff: 50,
    division_ratio_defendant: 50,
    description: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData({
        asset_type: 'real_estate',
        name: '',
        current_value: 0,
        ownership: 'joint',
        division_ratio_plaintiff: 50,
        division_ratio_defendant: 50,
        description: '',
      });
      setErrors({});
    }
  }, [isOpen]);

  // Sync defendant ratio when plaintiff ratio changes
  const handlePlaintiffRatioChange = useCallback((value: number) => {
    const plaintiffRatio = Math.min(100, Math.max(0, value));
    setFormData(prev => ({
      ...prev,
      division_ratio_plaintiff: plaintiffRatio,
      division_ratio_defendant: 100 - plaintiffRatio,
    }));
  }, []);

  const validate = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = '재산명을 입력해주세요.';
    }

    if (formData.current_value <= 0) {
      newErrors.current_value = '현재 가치를 입력해주세요.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    try {
      await onSubmit(formData);
      onClose();
    } catch {
      // Error handling
    }
  }, [formData, validate, onSubmit, onClose]);

  const handleClose = useCallback(() => {
    if (!isLoading) {
      onClose();
    }
  }, [isLoading, onClose]);

  // Format number with comma separators
  const formatNumber = (num: number): string => {
    return num.toLocaleString('ko-KR');
  };

  // Parse formatted number back to number
  const parseFormattedNumber = (str: string): number => {
    return parseInt(str.replace(/,/g, ''), 10) || 0;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="재산 추가"
      description="재산 정보를 입력하고 분할 비율을 지정합니다."
      size="lg"
      footer={
        <>
          <Button variant="ghost" onClick={handleClose} disabled={isLoading}>
            취소
          </Button>
          <Button
            variant="secondary"
            onClick={handleSubmit}
            disabled={isLoading}
            isLoading={isLoading}
          >
            추가
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Asset Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            재산 유형
          </label>
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(ASSET_TYPE_CONFIG).map(([type, config]) => {
              const Icon = ASSET_TYPE_ICONS[type as AssetType] || HelpCircle;
              const isSelected = formData.asset_type === type;

              return (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, asset_type: type as AssetType }))}
                  className={`
                    flex flex-col items-center p-3 rounded-lg border-2 transition-all
                    ${isSelected
                      ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10'
                      : 'border-gray-200 dark:border-neutral-700 hover:border-gray-300 dark:hover:border-neutral-600'
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 mb-1 ${isSelected ? 'text-[var(--color-primary)]' : 'text-gray-500'}`} />
                  <span className={`text-xs ${isSelected ? 'text-[var(--color-primary)] font-medium' : 'text-gray-600 dark:text-gray-400'}`}>
                    {config.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Name and Value */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              재산명 <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="예: 강남 아파트"
              error={errors.name}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              현재 가치 (원) <span className="text-red-500">*</span>
            </label>
            <Input
              type="text"
              value={formData.current_value ? formatNumber(formData.current_value) : ''}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                current_value: parseFormattedNumber(e.target.value),
              }))}
              placeholder="500,000,000"
              error={errors.current_value}
            />
          </div>
        </div>

        {/* Ownership */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            소유 구분
          </label>
          <div className="flex gap-2">
            {Object.entries(OWNERSHIP_CONFIG).map(([key, config]) => (
              <button
                key={key}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, ownership: key as 'plaintiff' | 'defendant' | 'joint' }))}
                className={`
                  px-4 py-2 text-sm rounded-lg border transition-colors
                  ${formData.ownership === key
                    ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/10 text-[var(--color-primary)]'
                    : 'border-gray-200 dark:border-neutral-700 text-gray-600 dark:text-gray-400 hover:border-gray-300'
                  }
                `}
              >
                {config.label}
              </button>
            ))}
          </div>
        </div>

        {/* Division Ratio - Fixed Value Input (Not AI Predicted) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            분할 비율 (원고 : 피고)
          </label>
          <div className="bg-gray-50 dark:bg-neutral-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-teal-600 dark:text-teal-400">원고</span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {formData.division_ratio_plaintiff} : {formData.division_ratio_defendant}
              </span>
              <span className="text-sm text-slate-600 dark:text-slate-400">피고</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={formData.division_ratio_plaintiff}
              onChange={(e) => handlePlaintiffRatioChange(parseInt(e.target.value, 10))}
              className="w-full h-2 bg-gray-200 dark:bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-[var(--color-primary)]"
            />
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
            {/* Quick ratio buttons */}
            <div className="flex gap-2 mt-3">
              {[
                { label: '0:100', plaintiff: 0 },
                { label: '30:70', plaintiff: 30 },
                { label: '50:50', plaintiff: 50 },
                { label: '70:30', plaintiff: 70 },
                { label: '100:0', plaintiff: 100 },
              ].map(({ label, plaintiff }) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => handlePlaintiffRatioChange(plaintiff)}
                  className={`
                    px-2 py-1 text-xs rounded transition-colors
                    ${formData.division_ratio_plaintiff === plaintiff
                      ? 'bg-[var(--color-primary)] text-white'
                      : 'bg-gray-200 dark:bg-neutral-700 text-gray-600 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-neutral-600'
                    }
                  `}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            설명 (선택)
          </label>
          <textarea
            value={formData.description || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            placeholder="재산에 대한 추가 설명"
            rows={2}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] resize-none"
          />
        </div>
      </form>
    </Modal>
  );
}

export default AssetModal;

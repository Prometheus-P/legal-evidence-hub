/**
 * AssetForm Component
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Form for creating and editing assets
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import type {
  Asset,
  AssetCreateRequest,
  AssetUpdateRequest,
  AssetCategory,
  AssetOwnership,
  AssetNature,
} from '@/types/asset';
import {
  ASSET_CATEGORY_LABELS,
  ASSET_OWNERSHIP_LABELS,
  ASSET_NATURE_LABELS,
} from '@/types/asset';

interface AssetFormProps {
  asset?: Asset | null;
  onSubmit: (data: AssetCreateRequest | AssetUpdateRequest) => Promise<void>;
  onCancel?: () => void;
  loading?: boolean;
  className?: string;
}

interface FormData {
  category: AssetCategory;
  ownership: AssetOwnership;
  nature: AssetNature;
  name: string;
  description: string;
  acquisition_date: string;
  acquisition_value: string;
  current_value: string;
  valuation_date: string;
  valuation_source: string;
  division_ratio_plaintiff: string;
  division_ratio_defendant: string;
  notes: string;
}

interface FormErrors {
  name?: string;
  current_value?: string;
  division_ratio?: string;
}

const CATEGORIES: AssetCategory[] = [
  'real_estate',
  'savings',
  'stocks',
  'retirement',
  'vehicle',
  'insurance',
  'debt',
  'other',
];

const OWNERSHIPS: AssetOwnership[] = ['plaintiff', 'defendant', 'joint', 'third_party'];
const NATURES: AssetNature[] = ['marital', 'separate', 'mixed'];

export default function AssetForm({
  asset,
  onSubmit,
  onCancel,
  loading = false,
  className = '',
}: AssetFormProps) {
  const isEdit = !!asset;

  const [formData, setFormData] = useState<FormData>({
    category: asset?.category || 'real_estate',
    ownership: asset?.ownership || 'plaintiff',
    nature: asset?.nature || 'marital',
    name: asset?.name || '',
    description: asset?.description || '',
    acquisition_date: asset?.acquisition_date?.split('T')[0] || '',
    acquisition_value: asset?.acquisition_value?.toString() || '',
    current_value: asset?.current_value?.toString() || '',
    valuation_date: asset?.valuation_date?.split('T')[0] || '',
    valuation_source: asset?.valuation_source || '',
    division_ratio_plaintiff: asset?.division_ratio_plaintiff?.toString() || '50',
    division_ratio_defendant: asset?.division_ratio_defendant?.toString() || '50',
    notes: asset?.notes || '',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  // Sync defendant ratio when plaintiff ratio changes
  useEffect(() => {
    const plaintiffRatio = parseInt(formData.division_ratio_plaintiff) || 0;
    if (plaintiffRatio >= 0 && plaintiffRatio <= 100) {
      setFormData((prev) => ({
        ...prev,
        division_ratio_defendant: (100 - plaintiffRatio).toString(),
      }));
    }
  }, [formData.division_ratio_plaintiff]);

  const handleInputChange = useCallback(
    (field: keyof FormData) =>
      (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData((prev) => ({
          ...prev,
          [field]: e.target.value,
        }));
        // Clear error when user starts typing
        if (errors[field as keyof FormErrors]) {
          setErrors((prev) => ({
            ...prev,
            [field]: undefined,
          }));
        }
      },
    [errors]
  );

  const validate = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = '재산 명칭을 입력해 주세요.';
    }

    if (!formData.current_value.trim()) {
      newErrors.current_value = '현재 가치를 입력해 주세요.';
    } else if (!/^\d+$/.test(formData.current_value.trim())) {
      newErrors.current_value = '금액은 숫자만 입력해 주세요.';
    }

    const pRatio = parseInt(formData.division_ratio_plaintiff) || 0;
    const dRatio = parseInt(formData.division_ratio_defendant) || 0;
    if (pRatio < 0 || pRatio > 100 || dRatio < 0 || dRatio > 100) {
      newErrors.division_ratio = '분할 비율은 0~100 사이여야 합니다.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!validate()) {
        return;
      }

      const submitData: AssetCreateRequest = {
        category: formData.category,
        ownership: formData.ownership,
        nature: formData.nature,
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        acquisition_date: formData.acquisition_date || undefined,
        acquisition_value: formData.acquisition_value
          ? parseInt(formData.acquisition_value)
          : undefined,
        current_value: parseInt(formData.current_value),
        valuation_date: formData.valuation_date || undefined,
        valuation_source: formData.valuation_source.trim() || undefined,
        division_ratio_plaintiff: parseInt(formData.division_ratio_plaintiff),
        division_ratio_defendant: parseInt(formData.division_ratio_defendant),
        notes: formData.notes.trim() || undefined,
      };

      await onSubmit(submitData);
    },
    [formData, onSubmit, validate]
  );

  const inputClass =
    'w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent dark:bg-neutral-800 dark:border-neutral-600 dark:text-white';
  const labelClass = 'block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1';
  const errorClass = 'text-sm text-error mt-1';

  return (
    <form onSubmit={handleSubmit} className={`space-y-6 ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Category */}
        <div>
          <label className={labelClass}>분류 *</label>
          <select
            value={formData.category}
            onChange={handleInputChange('category')}
            className={inputClass}
            disabled={loading}
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {ASSET_CATEGORY_LABELS[cat]}
              </option>
            ))}
          </select>
        </div>

        {/* Ownership */}
        <div>
          <label className={labelClass}>소유자 *</label>
          <select
            value={formData.ownership}
            onChange={handleInputChange('ownership')}
            className={inputClass}
            disabled={loading}
          >
            {OWNERSHIPS.map((own) => (
              <option key={own} value={own}>
                {ASSET_OWNERSHIP_LABELS[own]}
              </option>
            ))}
          </select>
        </div>

        {/* Nature */}
        <div>
          <label className={labelClass}>재산 성격 *</label>
          <select
            value={formData.nature}
            onChange={handleInputChange('nature')}
            className={inputClass}
            disabled={loading}
          >
            {NATURES.map((nat) => (
              <option key={nat} value={nat}>
                {ASSET_NATURE_LABELS[nat]}
              </option>
            ))}
          </select>
        </div>

        {/* Name */}
        <div>
          <label className={labelClass}>재산 명칭 *</label>
          <input
            type="text"
            value={formData.name}
            onChange={handleInputChange('name')}
            className={inputClass}
            placeholder="예: 강남구 아파트"
            disabled={loading}
          />
          {errors.name && <p className={errorClass}>{errors.name}</p>}
        </div>

        {/* Current Value */}
        <div>
          <label className={labelClass}>현재 가치 (원) *</label>
          <input
            type="text"
            value={formData.current_value}
            onChange={handleInputChange('current_value')}
            className={inputClass}
            placeholder="500000000"
            disabled={loading}
          />
          {errors.current_value && <p className={errorClass}>{errors.current_value}</p>}
        </div>

        {/* Acquisition Value */}
        <div>
          <label className={labelClass}>취득 가액 (원)</label>
          <input
            type="text"
            value={formData.acquisition_value}
            onChange={handleInputChange('acquisition_value')}
            className={inputClass}
            placeholder="300000000"
            disabled={loading}
          />
        </div>

        {/* Acquisition Date */}
        <div>
          <label className={labelClass}>취득일</label>
          <input
            type="date"
            value={formData.acquisition_date}
            onChange={handleInputChange('acquisition_date')}
            className={inputClass}
            disabled={loading}
          />
        </div>

        {/* Valuation Date */}
        <div>
          <label className={labelClass}>감정일</label>
          <input
            type="date"
            value={formData.valuation_date}
            onChange={handleInputChange('valuation_date')}
            className={inputClass}
            disabled={loading}
          />
        </div>

        {/* Valuation Source */}
        <div>
          <label className={labelClass}>감정 기관</label>
          <input
            type="text"
            value={formData.valuation_source}
            onChange={handleInputChange('valuation_source')}
            className={inputClass}
            placeholder="예: KB시세, 한국감정원"
            disabled={loading}
          />
        </div>

        {/* Division Ratio */}
        <div>
          <label className={labelClass}>분할 비율 (원고:피고)</label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              min="0"
              max="100"
              value={formData.division_ratio_plaintiff}
              onChange={handleInputChange('division_ratio_plaintiff')}
              className={`${inputClass} w-20 text-center`}
              disabled={loading}
            />
            <span className="text-neutral-500">:</span>
            <input
              type="number"
              min="0"
              max="100"
              value={formData.division_ratio_defendant}
              readOnly
              className={`${inputClass} w-20 text-center bg-neutral-100 dark:bg-neutral-700`}
              disabled
            />
          </div>
          {errors.division_ratio && <p className={errorClass}>{errors.division_ratio}</p>}
        </div>
      </div>

      {/* Description */}
      <div>
        <label className={labelClass}>설명</label>
        <textarea
          value={formData.description}
          onChange={handleInputChange('description')}
          className={`${inputClass} h-20`}
          placeholder="재산에 대한 상세 설명"
          disabled={loading}
        />
      </div>

      {/* Notes */}
      <div>
        <label className={labelClass}>비고</label>
        <textarea
          value={formData.notes}
          onChange={handleInputChange('notes')}
          className={`${inputClass} h-20`}
          placeholder="추가 메모"
          disabled={loading}
        />
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-neutral-200 dark:border-neutral-700">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md transition-colors"
            disabled={loading}
          >
            취소
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          disabled={loading}
        >
          {loading ? '저장 중...' : isEdit ? '수정' : '추가'}
        </button>
      </div>
    </form>
  );
}

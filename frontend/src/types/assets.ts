/**
 * Types for Asset Division
 * 009-calm-control-design-system
 */

// Asset type enum
export type AssetType =
  | 'real_estate'  // 부동산
  | 'vehicle'      // 차량
  | 'financial'    // 금융자산
  | 'business'     // 사업자산
  | 'personal'     // 개인자산
  | 'debt'         // 부채
  | 'other';       // 기타

// Ownership type enum
export type OwnershipType = 'plaintiff' | 'defendant' | 'joint';

// Asset model
export interface Asset {
  id: string;
  case_id: string;
  asset_type: AssetType;
  name: string;
  description?: string;
  acquisition_date?: string;
  current_value: number;
  ownership: OwnershipType;
  division_ratio_plaintiff: number; // 0-100 percentage
  division_ratio_defendant: number; // 0-100 percentage
  notes?: string;
  evidence_ids?: string[];
  created_at: string;
  updated_at: string;
}

// Asset division summary
export interface DivisionSummary {
  total_assets: number;
  total_debts: number;
  net_value: number;
  plaintiff_share: number;
  defendant_share: number;
  settlement_needed: number; // positive = defendant pays plaintiff
}

// API Request types
export interface CreateAssetRequest {
  asset_type: AssetType;
  name: string;
  description?: string;
  acquisition_date?: string;
  current_value: number;
  ownership: OwnershipType;
  division_ratio_plaintiff?: number;
  division_ratio_defendant?: number;
  notes?: string;
  evidence_ids?: string[];
}

export interface UpdateAssetRequest extends Partial<CreateAssetRequest> {
  id: string;
}

export interface SimulateDivisionRequest {
  assets: Array<{
    id: string;
    division_ratio_plaintiff: number;
    division_ratio_defendant: number;
  }>;
}

// Asset type labels and icons
export const ASSET_TYPE_CONFIG: Record<AssetType, { label: string; icon: string }> = {
  real_estate: { label: '부동산', icon: 'Building' },
  vehicle: { label: '차량', icon: 'Car' },
  financial: { label: '금융자산', icon: 'Wallet' },
  business: { label: '사업자산', icon: 'Briefcase' },
  personal: { label: '개인자산', icon: 'Package' },
  debt: { label: '부채', icon: 'CreditCard' },
  other: { label: '기타', icon: 'Box' },
};

export const OWNERSHIP_CONFIG: Record<OwnershipType, { label: string; color: string }> = {
  plaintiff: { label: '원고 단독', color: '#1ABC9C' },
  defendant: { label: '피고 단독', color: '#2C3E50' },
  joint: { label: '공동 소유', color: '#F39C12' },
};

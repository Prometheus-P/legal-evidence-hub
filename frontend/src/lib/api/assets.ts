/**
 * API client for Assets
 * 009-calm-control-design-system
 */

import { apiClient } from './client';
import type {
  Asset,
  CreateAssetRequest,
  DivisionSummary,
  SimulateDivisionRequest,
} from '@/types/assets';

// Get all assets for a case
export async function getAssets(caseId: string): Promise<Asset[]> {
  const response = await apiClient.get<Asset[]>(`/cases/${caseId}/assets`);
  return response.data;
}

// Get single asset
export async function getAsset(caseId: string, assetId: string): Promise<Asset> {
  const response = await apiClient.get<Asset>(`/cases/${caseId}/assets/${assetId}`);
  return response.data;
}

// Create new asset
export async function createAsset(caseId: string, data: CreateAssetRequest): Promise<Asset> {
  const response = await apiClient.post<Asset>(`/cases/${caseId}/assets`, data);
  return response.data;
}

// Update asset
export async function updateAsset(
  caseId: string,
  assetId: string,
  data: Partial<CreateAssetRequest>
): Promise<Asset> {
  const response = await apiClient.put<Asset>(`/cases/${caseId}/assets/${assetId}`, data);
  return response.data;
}

// Delete asset
export async function deleteAsset(caseId: string, assetId: string): Promise<void> {
  await apiClient.delete(`/cases/${caseId}/assets/${assetId}`);
}

// Get division summary
export async function getDivisionSummary(caseId: string): Promise<DivisionSummary> {
  const response = await apiClient.get<DivisionSummary>(`/cases/${caseId}/assets/summary`);
  return response.data;
}

// Simulate division with custom ratios
export async function simulateDivision(
  caseId: string,
  data: SimulateDivisionRequest
): Promise<DivisionSummary> {
  const response = await apiClient.post<DivisionSummary>(
    `/cases/${caseId}/assets/simulate-division`,
    data
  );
  return response.data;
}

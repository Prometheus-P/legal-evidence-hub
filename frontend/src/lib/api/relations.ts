/**
 * API client for Case Relations (Parties & Relations)
 * 009-calm-control-design-system
 */

import { apiClient } from './client';
import type {
  Party,
  Relation,
  CreatePartyRequest,
  UpdatePartyRequest,
  CreateRelationRequest,
  UpdateRelationRequest,
  CaseGraphData,
} from '@/types/relations';

// ============ Parties API ============

export async function getParties(caseId: string): Promise<Party[]> {
  const response = await apiClient.get<Party[]>(`/cases/${caseId}/parties`);
  return response.data ?? [];
}

export async function createParty(caseId: string, data: CreatePartyRequest): Promise<Party> {
  const response = await apiClient.post<Party>(`/cases/${caseId}/parties`, data);
  if (!response.data) throw new Error('Failed to create party');
  return response.data;
}

export async function updateParty(
  caseId: string,
  partyId: string,
  data: Partial<CreatePartyRequest>
): Promise<Party> {
  const response = await apiClient.put<Party>(`/cases/${caseId}/parties/${partyId}`, data);
  if (!response.data) throw new Error('Failed to update party');
  return response.data;
}

export async function deleteParty(caseId: string, partyId: string): Promise<void> {
  await apiClient.delete(`/cases/${caseId}/parties/${partyId}`);
}

// ============ Relations API ============
// NOTE: Backend uses /relationships endpoint (not /relations)

export async function getRelations(caseId: string): Promise<Relation[]> {
  const response = await apiClient.get<Relation[]>(`/cases/${caseId}/relationships`);
  return response.data ?? [];
}

export async function createRelation(caseId: string, data: CreateRelationRequest): Promise<Relation> {
  const response = await apiClient.post<Relation>(`/cases/${caseId}/relationships`, data);
  if (!response.data) throw new Error('Failed to create relation');
  return response.data;
}

export async function updateRelation(
  caseId: string,
  relationId: string,
  data: Partial<CreateRelationRequest>
): Promise<Relation> {
  const response = await apiClient.put<Relation>(`/cases/${caseId}/relationships/${relationId}`, data);
  if (!response.data) throw new Error('Failed to update relation');
  return response.data;
}

export async function deleteRelation(caseId: string, relationId: string): Promise<void> {
  await apiClient.delete(`/cases/${caseId}/relationships/${relationId}`);
}

// ============ Combined Graph Data ============

export async function getCaseGraphData(caseId: string): Promise<CaseGraphData> {
  const [parties, relations] = await Promise.all([
    getParties(caseId),
    getRelations(caseId),
  ]);
  return { parties, relations };
}

// ============ Batch Position Update ============

export async function updatePartyPositions(
  caseId: string,
  positions: Array<{ id: string; position_x: number; position_y: number }>
): Promise<void> {
  await apiClient.put(`/cases/${caseId}/parties/positions`, { positions });
}

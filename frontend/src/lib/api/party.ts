/**
 * Party API client for LEH Lawyer Portal v1
 * User Story 1: Party Relationship Graph
 */

import { apiClient } from './client';
import type {
  PartyNode,
  PartyNodeCreate,
  PartyNodeUpdate,
  PartyRelationship,
  RelationshipCreate,
  RelationshipUpdate,
  PartyGraphData,
} from '@/types/party';

// ============================================================
// Party Node APIs
// ============================================================

interface PartyListResponse {
  items: PartyNode[];
  total: number;
}

/**
 * Get all parties for a case
 */
export async function getParties(caseId: string): Promise<PartyNode[]> {
  const response = await apiClient.get<PartyListResponse>(
    `/cases/${caseId}/parties`
  );
  if (!response.data) {
    throw new Error(response.error || '당사자 목록을 불러오는데 실패했습니다.');
  }
  return response.data.items;
}

/**
 * Get a single party by ID
 */
export async function getParty(caseId: string, partyId: string): Promise<PartyNode> {
  const response = await apiClient.get<PartyNode>(
    `/cases/${caseId}/parties/${partyId}`
  );
  if (!response.data) {
    throw new Error(response.error || '당사자 정보를 불러오는데 실패했습니다.');
  }
  return response.data;
}

/**
 * Create a new party
 */
export async function createParty(
  caseId: string,
  data: PartyNodeCreate
): Promise<PartyNode> {
  const response = await apiClient.post<PartyNode>(
    `/cases/${caseId}/parties`,
    data
  );
  if (!response.data) {
    throw new Error(response.error || '당사자를 추가하는데 실패했습니다.');
  }
  return response.data;
}

/**
 * Update a party
 */
export async function updateParty(
  caseId: string,
  partyId: string,
  data: PartyNodeUpdate
): Promise<PartyNode> {
  const response = await apiClient.patch<PartyNode>(
    `/cases/${caseId}/parties/${partyId}`,
    data
  );
  if (!response.data) {
    throw new Error(response.error || '당사자 정보를 수정하는데 실패했습니다.');
  }
  return response.data;
}

/**
 * Delete a party
 */
export async function deleteParty(caseId: string, partyId: string): Promise<void> {
  const response = await apiClient.delete(`/cases/${caseId}/parties/${partyId}`);
  if (response.error) {
    throw new Error(response.error || '당사자를 삭제하는데 실패했습니다.');
  }
}

// ============================================================
// Relationship APIs
// ============================================================

interface RelationshipListResponse {
  items: PartyRelationship[];
  total: number;
}

/**
 * Get all relationships for a case
 */
export async function getRelationships(caseId: string): Promise<PartyRelationship[]> {
  const response = await apiClient.get<RelationshipListResponse>(
    `/cases/${caseId}/relationships`
  );
  if (!response.data) {
    throw new Error(response.error || '관계 목록을 불러오는데 실패했습니다.');
  }
  return response.data.items;
}

/**
 * Create a new relationship
 */
export async function createRelationship(
  caseId: string,
  data: RelationshipCreate
): Promise<PartyRelationship> {
  const response = await apiClient.post<PartyRelationship>(
    `/cases/${caseId}/relationships`,
    data
  );
  if (!response.data) {
    throw new Error(response.error || '관계를 추가하는데 실패했습니다.');
  }
  return response.data;
}

/**
 * Update a relationship
 */
export async function updateRelationship(
  caseId: string,
  relationshipId: string,
  data: RelationshipUpdate
): Promise<PartyRelationship> {
  const response = await apiClient.patch<PartyRelationship>(
    `/cases/${caseId}/relationships/${relationshipId}`,
    data
  );
  if (!response.data) {
    throw new Error(response.error || '관계 정보를 수정하는데 실패했습니다.');
  }
  return response.data;
}

/**
 * Delete a relationship
 */
export async function deleteRelationship(
  caseId: string,
  relationshipId: string
): Promise<void> {
  const response = await apiClient.delete(
    `/cases/${caseId}/relationships/${relationshipId}`
  );
  if (response.error) {
    throw new Error(response.error || '관계를 삭제하는데 실패했습니다.');
  }
}

// ============================================================
// Graph API (combined data for React Flow)
// ============================================================

/**
 * Get the complete party graph for a case
 * Returns nodes and relationships in a single request
 */
export async function getPartyGraph(caseId: string): Promise<PartyGraphData> {
  const response = await apiClient.get<PartyGraphData>(
    `/cases/${caseId}/graph`
  );
  if (!response.data) {
    throw new Error(response.error || '관계도를 불러오는데 실패했습니다.');
  }
  return response.data;
}

// ============================================================
// Batch Position Update
// ============================================================

interface PositionUpdate {
  id: string;
  position: { x: number; y: number };
}

/**
 * Update multiple party positions in a single request
 * Used for persisting React Flow node positions
 */
export async function updatePartyPositions(
  caseId: string,
  positions: PositionUpdate[]
): Promise<void> {
  const response = await apiClient.put(
    `/cases/${caseId}/parties/positions`,
    { positions }
  );
  if (response.error) {
    throw new Error(response.error || '위치 저장에 실패했습니다.');
  }
}

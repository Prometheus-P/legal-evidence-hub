/**
 * Evidence Links API client for LEH Lawyer Portal v1
 * User Story 4: Evidence-Party Linking
 */

import { apiClient } from './client';
import type {
  EvidencePartyLink,
  EvidenceLinkCreate,
  LinkType,
} from '@/types/party';

interface EvidenceLinksResponse {
  items: EvidencePartyLink[];
  total: number;
}

/**
 * Get all evidence links for a case
 */
export async function getEvidenceLinks(
  caseId: string,
  filters?: {
    evidence_id?: string;
    party_id?: string;
    relationship_id?: string;
  }
): Promise<EvidencePartyLink[]> {
  const params = new URLSearchParams();
  if (filters?.evidence_id) params.append('evidence_id', filters.evidence_id);
  if (filters?.party_id) params.append('party_id', filters.party_id);
  if (filters?.relationship_id) params.append('relationship_id', filters.relationship_id);

  const queryString = params.toString();
  const url = `/cases/${caseId}/evidence-links${queryString ? `?${queryString}` : ''}`;

  const response = await apiClient.get<EvidenceLinksResponse>(url);
  if (!response.data) {
    throw new Error(response.error || '증거 연결 목록을 불러오는데 실패했습니다.');
  }
  return response.data.items;
}

/**
 * Get links for a specific evidence item
 */
export async function getLinksForEvidence(
  caseId: string,
  evidenceId: string
): Promise<EvidencePartyLink[]> {
  const response = await apiClient.get<EvidenceLinksResponse>(
    `/cases/${caseId}/evidence-links/by-evidence/${evidenceId}`
  );
  if (!response.data) {
    throw new Error(response.error || '증거 연결 목록을 불러오는데 실패했습니다.');
  }
  return response.data.items;
}

/**
 * Get links for a specific party
 */
export async function getLinksForParty(
  caseId: string,
  partyId: string
): Promise<EvidencePartyLink[]> {
  const response = await apiClient.get<EvidenceLinksResponse>(
    `/cases/${caseId}/evidence-links/by-party/${partyId}`
  );
  if (!response.data) {
    throw new Error(response.error || '증거 연결 목록을 불러오는데 실패했습니다.');
  }
  return response.data.items;
}

/**
 * Create a new evidence link
 */
export async function createEvidenceLink(
  caseId: string,
  data: EvidenceLinkCreate
): Promise<EvidencePartyLink> {
  const response = await apiClient.post<EvidencePartyLink>(
    `/cases/${caseId}/evidence-links`,
    data
  );
  if (!response.data) {
    throw new Error(response.error || '증거 연결을 추가하는데 실패했습니다.');
  }
  return response.data;
}

/**
 * Delete an evidence link
 */
export async function deleteEvidenceLink(
  caseId: string,
  linkId: string
): Promise<void> {
  const response = await apiClient.delete(
    `/cases/${caseId}/evidence-links/${linkId}`
  );
  if (response.error) {
    throw new Error(response.error || '증거 연결을 삭제하는데 실패했습니다.');
  }
}

/**
 * Link type labels
 */
export const LINK_TYPE_LABELS: Record<LinkType, string> = {
  mentions: '언급',
  proves: '증명',
  involves: '관련',
  contradicts: '반박',
};

export const LINK_TYPE_DESCRIPTIONS: Record<LinkType, string> = {
  mentions: '이 증거가 당사자를 언급합니다',
  proves: '이 증거가 관계를 증명합니다',
  involves: '이 증거가 당사자와 관련됩니다',
  contradicts: '이 증거가 주장을 반박합니다',
};

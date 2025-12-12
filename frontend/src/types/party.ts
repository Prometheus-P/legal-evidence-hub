/**
 * Party types for LEH Lawyer Portal v1
 * User Story 1: Party Relationship Graph
 */

export type PartyType =
  | 'plaintiff'
  | 'defendant'
  | 'third_party'
  | 'child'
  | 'family';

export type RelationshipType =
  | 'marriage'
  | 'affair'
  | 'parent_child'
  | 'sibling'
  | 'in_law'
  | 'cohabit';

export type LinkType = 'mentions' | 'proves' | 'involves' | 'contradicts';

export interface Position {
  x: number;
  y: number;
}

export interface PartyNode {
  id: string;
  case_id: string;
  type: PartyType;
  name: string;
  alias?: string;
  birth_year?: number;
  occupation?: string;
  position: Position;
  extra_data?: Record<string, unknown>;
  // 012-precedent-integration: T048-T050 자동 추출 필드
  is_auto_extracted?: boolean;
  extraction_confidence?: number;
  source_evidence_id?: string;
  created_at: string;
  updated_at: string;
}

export interface PartyNodeCreate {
  type: PartyType;
  name: string;
  alias?: string;
  birth_year?: number;
  occupation?: string;
  position?: Position;
  extra_data?: Record<string, unknown>;
}

export interface PartyNodeUpdate {
  name?: string;
  alias?: string;
  birth_year?: number;
  occupation?: string;
  position?: Position;
  extra_data?: Record<string, unknown>;
}

export interface PartyRelationship {
  id: string;
  case_id: string;
  source_party_id: string;
  target_party_id: string;
  type: RelationshipType;
  start_date?: string;
  end_date?: string;
  notes?: string;
  // 012-precedent-integration: T048-T050 자동 추출 필드
  is_auto_extracted?: boolean;
  extraction_confidence?: number;
  evidence_text?: string;
  created_at: string;
  updated_at: string;
}

export interface RelationshipCreate {
  source_party_id: string;
  target_party_id: string;
  type: RelationshipType;
  start_date?: string;
  end_date?: string;
  notes?: string;
}

export interface RelationshipUpdate {
  type?: RelationshipType;
  start_date?: string;
  end_date?: string;
  notes?: string;
}

export interface PartyGraphData {
  nodes: PartyNode[];
  relationships: PartyRelationship[];
}

export interface EvidencePartyLink {
  id: string;
  case_id: string;
  evidence_id: string;
  party_id?: string;
  relationship_id?: string;
  asset_id?: string;
  link_type: LinkType;
  created_at: string;
}

export interface EvidenceLinkCreate {
  evidence_id: string;
  party_id?: string;
  relationship_id?: string;
  asset_id?: string;
  link_type?: LinkType;
}

/**
 * React Flow node type mapping
 */
export const PARTY_TYPE_LABELS: Record<PartyType, string> = {
  plaintiff: '원고',
  defendant: '피고',
  third_party: '제3자',
  child: '자녀',
  family: '친족',
};

export const RELATIONSHIP_TYPE_LABELS: Record<RelationshipType, string> = {
  marriage: '혼인',
  affair: '불륜',
  parent_child: '부모-자녀',
  sibling: '형제자매',
  in_law: '인척',
  cohabit: '동거',
};

export const LINK_TYPE_LABELS: Record<LinkType, string> = {
  mentions: '언급',
  proves: '증명',
  involves: '관련',
  contradicts: '반박',
};

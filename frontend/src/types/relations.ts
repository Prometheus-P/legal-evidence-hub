/**
 * Types for Case Relations Graph
 * 009-calm-control-design-system - React Flow Integration
 */

// Party (Node) Types
export type PartyType = 'plaintiff' | 'defendant' | 'child' | 'third_party';

export interface Party {
  id: string;
  case_id: string;
  name: string;
  type: PartyType;
  description?: string;
  birth_date?: string;
  contact?: string;
  // Graph position (stored for persistence)
  position_x?: number;
  position_y?: number;
  created_at: string;
  updated_at: string;
}

// Relation (Edge) Types
export type RelationType = 'marriage' | 'parent_child' | 'affair' | 'relative' | 'other';

export interface Relation {
  id: string;
  case_id: string;
  source_party_id: string;
  target_party_id: string;
  relation_type: RelationType;
  label?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  // Evidence links
  evidence_ids?: string[];
  created_at: string;
  updated_at: string;
}

// API Request/Response types
export interface CreatePartyRequest {
  name: string;
  type: PartyType;
  description?: string;
  birth_date?: string;
  contact?: string;
  position_x?: number;
  position_y?: number;
}

export interface UpdatePartyRequest extends Partial<CreatePartyRequest> {
  id: string;
}

export interface CreateRelationRequest {
  source_party_id: string;
  target_party_id: string;
  relation_type: RelationType;
  label?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  evidence_ids?: string[];
}

export interface UpdateRelationRequest extends Partial<CreateRelationRequest> {
  id: string;
}

// Graph data for React Flow
export interface CaseGraphData {
  parties: Party[];
  relations: Relation[];
}

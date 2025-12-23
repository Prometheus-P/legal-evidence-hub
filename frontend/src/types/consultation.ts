/**
 * Consultation Types
 * Issue #399: 상담내역 API 타입 정의
 */

export type ConsultationType = 'phone' | 'in_person' | 'online';

export interface Consultation {
  id: string;
  case_id: string;
  date: string; // YYYY-MM-DD
  time: string | null; // HH:MM:SS
  type: ConsultationType;
  participants: string[];
  summary: string;
  notes: string | null;
  created_by: string;
  created_by_name: string | null;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  linked_evidence: string[];
}

export interface ConsultationCreate {
  date: string; // YYYY-MM-DD
  time?: string; // HH:MM:SS
  type: ConsultationType;
  participants: string[];
  summary: string;
  notes?: string;
}

export interface ConsultationUpdate {
  date?: string;
  time?: string;
  type?: ConsultationType;
  participants?: string[];
  summary?: string;
  notes?: string;
}

export interface ConsultationListResponse {
  consultations: Consultation[];
  total: number;
}

export interface LinkEvidenceRequest {
  evidence_ids: string[];
}

export interface LinkEvidenceResponse {
  consultation_id: string;
  linked_evidence_ids: string[];
  linked_at: string;
}

// UI helper constants
export const CONSULTATION_TYPE_LABELS: Record<ConsultationType, string> = {
  phone: '전화 상담',
  in_person: '대면 상담',
  online: '화상 상담',
};

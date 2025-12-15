/**
 * Client Types for Lawyer Portal
 * 005-lawyer-portal-pages Feature - US2
 */

export interface ClientItem {
  id: string;
  name: string;
  email: string;
  phone?: string;
  case_count: number;
  active_cases: number;
  last_activity?: string; // ISO datetime
  status: 'active' | 'inactive';
  created_at: string;
}

export interface ClientListResponse {
  items: ClientItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ClientFilter {
  search?: string;
  status?: 'active' | 'inactive' | 'all';
  sort_by?: 'name' | 'case_count' | 'last_activity' | 'created_at';
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export interface ClientDetail {
  id: string;
  name: string;
  email: string;
  phone?: string;
  created_at: string;
  linked_cases: LinkedCase[];
  recent_activity: ActivityItem[];
  stats: ClientStats;
}

export interface LinkedCase {
  id: string;
  title: string;
  status: string;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface ActivityItem {
  type: string;
  case_id: string;
  description: string;
  timestamp: string;
}

export interface ClientStats {
  total_cases: number;
  active_cases: number;
  completed_cases: number;
  total_evidence: number;
  total_messages: number;
}

// ============== Client CRUD Types (US2 - Lawyer Portal) ==============

/**
 * Client contact for lawyer's address book
 * Separate from User accounts - these are contacts managed by lawyers
 * NOTE: Field names must match backend ClientContactResponse schema (snake_case)
 */
export interface ClientContact {
  id: string;
  lawyer_id: string;
  name: string;
  phone?: string;
  email?: string;
  memo?: string;
  created_at: string; // ISO 8601
  updated_at: string;
}

export interface ClientContactCreate {
  name: string;
  phone?: string;
  email?: string;
  memo?: string;
}

export interface ClientContactUpdate {
  name?: string;
  phone?: string;
  email?: string;
  memo?: string;
}

export interface ClientContactListResponse {
  items: ClientContact[];  // NOTE: Backend uses 'items', not 'clients'
  total: number;
  page: number;
  limit: number;
}

export interface ClientContactQueryParams {
  search?: string;
  page?: number;
  limit?: number;
}

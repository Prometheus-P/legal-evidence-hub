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

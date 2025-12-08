import { apiClient, ApiResponse } from './client';

export interface FeedbackChecklistItem {
  item_id: string;
  title: string;
  status: string;
  description?: string;
  owner?: string;
  notes?: string;
  updated_by?: string;
  updated_at?: string;
}

export interface AssigneeInfo {
  id: string;
  name: string;
  email?: string;
}

export interface EvidenceCounts {
  pending: number;
  uploaded: number;
  processing: number;
  completed: number;
  failed: number;
}

export interface CaseProgressSummary {
  case_id: string;
  title: string;
  client_name?: string;
  status: string;
  assignee: AssigneeInfo;
  updated_at: string;
  evidence_counts: EvidenceCounts;
  ai_status: string;
  ai_last_updated?: string;
  outstanding_feedback_count: number;
  feedback_items: FeedbackChecklistItem[];
  is_blocked: boolean;
  blocked_reason?: string;
}

export interface StaffProgressFilters {
  blocked_only?: boolean;
  assignee_id?: string;
}

export interface ChecklistUpdatePayload {
  status: string;
  notes?: string;
}

export async function getStaffProgress(
  filters?: StaffProgressFilters
): Promise<ApiResponse<CaseProgressSummary[]>> {
  const params = new URLSearchParams();
  if (filters?.blocked_only) {
    params.append('blocked_only', 'true');
  }
  if (filters?.assignee_id) {
    params.append('assignee_id', filters.assignee_id);
  }

  const query = params.toString();
  const endpoint = query ? `/staff/progress?${query}` : '/staff/progress';
  return apiClient.get<CaseProgressSummary[]>(endpoint);
}

export async function updateChecklistItem(
  caseId: string,
  itemId: string,
  payload: ChecklistUpdatePayload
): Promise<ApiResponse<FeedbackChecklistItem>> {
  return apiClient.patch<FeedbackChecklistItem>(
    `/staff/progress/${caseId}/checklist/${itemId}`,
    payload
  );
}

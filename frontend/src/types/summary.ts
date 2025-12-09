/**
 * Summary Types
 * US8 - 진행 상태 요약 카드 (Progress Summary Cards)
 *
 * Types for case summary card generation and sharing
 */

/**
 * Completed procedure stage info
 */
export interface CompletedStageInfo {
  stage_label: string;
  completed_date: string | null;
}

/**
 * Next scheduled event info
 */
export interface NextSchedule {
  event_type: string;
  scheduled_date: string;
  location: string | null;
  notes: string | null;
}

/**
 * Evidence statistics by category
 */
export interface EvidenceStat {
  category: string;
  count: number;
}

/**
 * Lawyer contact information
 */
export interface LawyerInfo {
  name: string;
  phone: string | null;
  email: string | null;
}

/**
 * Full case summary response from API
 */
export interface CaseSummaryResponse {
  case_id: string;
  case_title: string;
  court_reference: string | null;
  client_name: string | null;
  current_stage: string | null;
  current_stage_status: string | null;
  progress_percent: number;
  completed_stages: CompletedStageInfo[];
  next_schedules: NextSchedule[];
  evidence_total: number;
  evidence_stats: EvidenceStat[];
  lawyer: LawyerInfo | null;
  generated_at: string;
}

/**
 * Request to share summary via email
 */
export interface ShareSummaryRequest {
  recipient_email: string;
  recipient_name?: string;
  message?: string;
  include_pdf: boolean;
}

/**
 * Response after sharing summary
 */
export interface ShareSummaryResponse {
  success: boolean;
  message: string;
  sent_at: string | null;
}

/**
 * Format date for display in summary card
 */
export function formatSummaryDate(dateString: string | null): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Format datetime for display in summary card
 */
export function formatSummaryDateTime(dateString: string | null): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

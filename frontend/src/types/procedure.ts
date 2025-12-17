/**
 * Procedure Stage types for US3 - 절차 단계 관리
 * Korean Family Litigation Act procedure tracking
 */

// Procedure stage types based on Korean family litigation
export type ProcedureStageType =
  | 'filed'           // 소장 접수
  | 'served'          // 송달
  | 'answered'        // 답변서
  | 'mediation'       // 조정 회부
  | 'mediation_closed' // 조정 종결
  | 'trial'           // 본안 이행
  | 'judgment'        // 판결 선고
  | 'appeal'          // 항소심
  | 'final';          // 확정

// Stage status types
export type StageStatus =
  | 'pending'         // 대기
  | 'in_progress'     // 진행중
  | 'completed'       // 완료
  | 'skipped';        // 건너뜀

// Document associated with a stage
export interface StageDocument {
  name: string;
  s3_key: string;
  uploaded_at: string;
}

// Procedure stage model
export interface ProcedureStage {
  id: string;
  case_id: string;
  stage: ProcedureStageType;
  status: StageStatus;
  scheduled_date?: string;
  completed_date?: string;
  court_reference?: string;
  judge_name?: string;
  court_room?: string;
  notes?: string;
  documents?: StageDocument[];
  outcome?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  // UI helper fields (added by API)
  stage_label?: string;
  status_label?: string;
}

// Create stage request
export interface ProcedureStageCreate {
  stage: ProcedureStageType;
  status?: StageStatus;
  scheduled_date?: string;
  completed_date?: string;
  court_reference?: string;
  judge_name?: string;
  court_room?: string;
  notes?: string;
  documents?: StageDocument[];
  outcome?: string;
}

// Update stage request (all fields optional)
export interface ProcedureStageUpdate {
  status?: StageStatus;
  scheduled_date?: string;
  completed_date?: string;
  court_reference?: string;
  judge_name?: string;
  court_room?: string;
  notes?: string;
  documents?: StageDocument[];
  outcome?: string;
}

// Transition to next stage request
export interface TransitionToNextStage {
  next_stage: ProcedureStageType;
  complete_current?: boolean;
  current_outcome?: string;
}

// Timeline response
export interface ProcedureTimelineResponse {
  case_id: string;
  stages: ProcedureStage[];
  current_stage?: ProcedureStage;
  progress_percent: number;
}

// Valid next stage option
export interface NextStageOption {
  stage: ProcedureStageType;
  label: string;
}

// Transition response
export interface TransitionResponse {
  success: boolean;
  message: string;
  next_stage: ProcedureStage;
  completed_stage?: ProcedureStage;
}

// Upcoming deadline
export interface UpcomingDeadline {
  case_id: string;
  case_title: string;
  stage: ProcedureStageType;
  stage_label: string;
  scheduled_date: string;
  days_until: number;
}

// Upcoming deadlines response
export interface UpcomingDeadlinesResponse {
  deadlines: UpcomingDeadline[];
  days_ahead: number;
}

// Korean labels for procedure stages
export const STAGE_LABELS: Record<ProcedureStageType, string> = {
  filed: '소장 접수',
  served: '송달',
  answered: '답변서',
  mediation: '조정 회부',
  mediation_closed: '조정 종결',
  trial: '본안 이행',
  judgment: '판결 선고',
  appeal: '항소심',
  final: '확정',
};

// Korean labels for stage status
export const STATUS_LABELS: Record<StageStatus, string> = {
  pending: '대기',
  in_progress: '진행중',
  completed: '완료',
  skipped: '건너뜀',
};

// Stage order for display
export const STAGE_ORDER: ProcedureStageType[] = [
  'filed',
  'served',
  'answered',
  'mediation',
  'mediation_closed',
  'trial',
  'judgment',
  'appeal',
  'final',
];

// Status colors for UI
export const STATUS_COLORS: Record<StageStatus, { bg: string; text: string; border: string }> = {
  pending: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' },
  in_progress: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-400' },
  completed: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-400' },
  skipped: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-400' },
};

// Helper function to get stage index
export function getStageIndex(stage: ProcedureStageType): number {
  return STAGE_ORDER.indexOf(stage);
}

// Helper function to check if stage is after another
export function isStageAfter(stage: ProcedureStageType, reference: ProcedureStageType): boolean {
  return getStageIndex(stage) > getStageIndex(reference);
}

// Helper function to format date for display
export function formatStageDate(dateString?: string): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

// Helper function to calculate days until deadline
export function calculateDaysUntil(dateString?: string): number | null {
  if (!dateString) return null;
  const date = new Date(dateString);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  date.setHours(0, 0, 0, 0);
  const diff = date.getTime() - today.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

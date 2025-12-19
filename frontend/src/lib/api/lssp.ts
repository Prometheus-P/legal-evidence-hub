/**
 * LSSP (Legal Strategy & Structured Pleading) API Client
 * Handles keypoint extraction, legal ground mapping, and draft generation
 */

import { apiRequest, ApiResponse, apiClient } from './client';

// =============================================================================
// Types: Legal Grounds
// =============================================================================

export interface LegalGround {
  id: string;
  code: string;
  name: string;
  description: string;
  civil_code_ref: string | null;
  typical_evidence_types: string[];
  created_at: string;
}

// =============================================================================
// Types: Keypoints
// =============================================================================

export interface Keypoint {
  id: string;
  case_id: string;
  content: string;
  source_type: 'ai_extracted' | 'user_added' | 'merged';
  confidence_score: number | null;
  temporal_order: number | null;
  is_disputed: boolean;
  user_verified: boolean;
  created_at: string;
  updated_at: string;
  legal_grounds?: LegalGround[];
  evidence_extracts?: EvidenceExtract[];
}

export interface KeypointCreateRequest {
  content: string;
  source_type?: 'ai_extracted' | 'user_added' | 'merged';
  confidence_score?: number;
  temporal_order?: number;
  is_disputed?: boolean;
  user_verified?: boolean;
  legal_ground_ids?: string[];
}

export interface KeypointUpdateRequest {
  content?: string;
  confidence_score?: number;
  temporal_order?: number;
  is_disputed?: boolean;
  user_verified?: boolean;
}

// =============================================================================
// Types: Evidence Extracts
// =============================================================================

export interface EvidenceExtract {
  id: string;
  evidence_id: string;
  chunk_index: number;
  content: string;
  embedding_id: string | null;
  page_number: number | null;
  timestamp_start: number | null;
  timestamp_end: number | null;
  created_at: string;
}

// =============================================================================
// Types: Draft Templates & Blocks
// =============================================================================

export interface DraftTemplate {
  id: string;
  template_code: string;
  name: string;
  description: string | null;
  document_type: string;
  version: string;
  is_active: boolean;
  created_at: string;
}

export interface DraftBlock {
  id: string;
  block_code: string;
  name: string;
  description: string | null;
  default_content: string;
  required_variables: string[];
  order_hint: number;
  created_at: string;
}

// =============================================================================
// Types: Drafts
// =============================================================================

export interface Draft {
  id: string;
  case_id: string;
  template_id: string;
  title: string;
  status: 'generating' | 'draft' | 'review' | 'final';
  version: number;
  created_at: string;
  updated_at: string;
  template?: DraftTemplate;
  block_instances?: DraftBlockInstance[];
}

export interface DraftBlockInstance {
  id: string;
  draft_id: string;
  block_id: string;
  content: string;
  order_index: number;
  is_modified: boolean;
  created_at: string;
  updated_at: string;
  block?: DraftBlock;
  citations?: DraftCitation[];
}

export interface DraftCitation {
  id: string;
  block_instance_id: string;
  keypoint_id: string | null;
  extract_id: string | null;
  citation_text: string;
  position_start: number;
  position_end: number;
  created_at: string;
}

export interface DraftCreateRequest {
  template_id: string;
  title: string;
}

export interface DraftBlockUpdateRequest {
  content: string;
}

// =============================================================================
// Types: AI Pipeline
// =============================================================================

export interface KeypointExtractionRequest {
  evidence_ids?: string[];
  force_reprocess?: boolean;
}

export interface KeypointExtractionResponse {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  keypoints_created: number;
  message: string;
}

export interface DraftGenerationRequest {
  template_id: string;
  title?: string;
  selected_keypoint_ids?: string[];
  selected_ground_ids?: string[];
}

export interface DraftGenerationResponse {
  draft_id: string;
  status: 'generating' | 'draft';
  message: string;
}

// =============================================================================
// API Functions: Legal Grounds (Reference Data)
// =============================================================================

/**
 * List all available legal grounds
 */
export async function getLegalGrounds(): Promise<ApiResponse<LegalGround[]>> {
  return apiClient.get<LegalGround[]>('/lssp/legal-grounds');
}

/**
 * Get a specific legal ground by ID
 */
export async function getLegalGround(groundId: string): Promise<ApiResponse<LegalGround>> {
  return apiClient.get<LegalGround>(`/lssp/legal-grounds/${groundId}`);
}

// =============================================================================
// API Functions: Keypoints
// =============================================================================

/**
 * List keypoints for a case
 */
export async function getKeypoints(
  caseId: string,
  params?: {
    verified_only?: boolean;
    ground_id?: string;
    limit?: number;
    offset?: number;
  }
): Promise<ApiResponse<{ keypoints: Keypoint[]; total: number }>> {
  const searchParams = new URLSearchParams();
  if (params?.verified_only) searchParams.set('verified_only', 'true');
  if (params?.ground_id) searchParams.set('ground_id', params.ground_id);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());

  const query = searchParams.toString();
  return apiClient.get<{ keypoints: Keypoint[]; total: number }>(
    `/lssp/cases/${caseId}/keypoints${query ? `?${query}` : ''}`
  );
}

/**
 * Get a specific keypoint
 */
export async function getKeypoint(
  caseId: string,
  keypointId: string
): Promise<ApiResponse<Keypoint>> {
  return apiClient.get<Keypoint>(`/lssp/cases/${caseId}/keypoints/${keypointId}`);
}

/**
 * Create a new keypoint (manual)
 */
export async function createKeypoint(
  caseId: string,
  data: KeypointCreateRequest
): Promise<ApiResponse<Keypoint>> {
  return apiClient.post<Keypoint>(`/lssp/cases/${caseId}/keypoints`, data);
}

/**
 * Update a keypoint
 */
export async function updateKeypoint(
  caseId: string,
  keypointId: string,
  data: KeypointUpdateRequest
): Promise<ApiResponse<Keypoint>> {
  return apiClient.patch<Keypoint>(`/lssp/cases/${caseId}/keypoints/${keypointId}`, data);
}

/**
 * Delete a keypoint
 */
export async function deleteKeypoint(
  caseId: string,
  keypointId: string
): Promise<ApiResponse<void>> {
  return apiClient.delete<void>(`/lssp/cases/${caseId}/keypoints/${keypointId}`);
}

/**
 * Verify/unverify a keypoint
 */
export async function verifyKeypoint(
  caseId: string,
  keypointId: string,
  verified: boolean
): Promise<ApiResponse<Keypoint>> {
  return apiClient.post<Keypoint>(
    `/lssp/cases/${caseId}/keypoints/${keypointId}/verify`,
    { verified }
  );
}

/**
 * Link a keypoint to legal grounds
 */
export async function linkKeypointToGrounds(
  caseId: string,
  keypointId: string,
  groundIds: string[]
): Promise<ApiResponse<Keypoint>> {
  return apiClient.post<Keypoint>(
    `/lssp/cases/${caseId}/keypoints/${keypointId}/grounds`,
    { ground_ids: groundIds }
  );
}

// =============================================================================
// API Functions: Draft Templates (Reference Data)
// =============================================================================

/**
 * List available draft templates
 */
export async function getDraftTemplates(
  params?: { document_type?: string; active_only?: boolean }
): Promise<ApiResponse<DraftTemplate[]>> {
  const searchParams = new URLSearchParams();
  if (params?.document_type) searchParams.set('document_type', params.document_type);
  if (params?.active_only !== undefined) searchParams.set('active_only', params.active_only.toString());

  const query = searchParams.toString();
  return apiClient.get<DraftTemplate[]>(`/lssp/templates${query ? `?${query}` : ''}`);
}

/**
 * Get a specific template with its blocks
 */
export async function getDraftTemplate(templateId: string): Promise<ApiResponse<DraftTemplate & { blocks: DraftBlock[] }>> {
  return apiClient.get<DraftTemplate & { blocks: DraftBlock[] }>(`/lssp/templates/${templateId}`);
}

// =============================================================================
// API Functions: Drafts
// =============================================================================

/**
 * List drafts for a case
 */
export async function getDrafts(
  caseId: string,
  params?: { status?: string; limit?: number; offset?: number }
): Promise<ApiResponse<{ drafts: Draft[]; total: number }>> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());

  const query = searchParams.toString();
  return apiClient.get<{ drafts: Draft[]; total: number }>(
    `/lssp/cases/${caseId}/drafts${query ? `?${query}` : ''}`
  );
}

/**
 * Get a specific draft with all block instances
 */
export async function getDraft(caseId: string, draftId: string): Promise<ApiResponse<Draft>> {
  return apiClient.get<Draft>(`/lssp/cases/${caseId}/drafts/${draftId}`);
}

/**
 * Create a new draft (manual)
 */
export async function createDraft(
  caseId: string,
  data: DraftCreateRequest
): Promise<ApiResponse<Draft>> {
  return apiClient.post<Draft>(`/lssp/cases/${caseId}/drafts`, data);
}

/**
 * Update a draft block instance content
 */
export async function updateDraftBlock(
  caseId: string,
  draftId: string,
  blockInstanceId: string,
  data: DraftBlockUpdateRequest
): Promise<ApiResponse<DraftBlockInstance>> {
  return apiClient.patch<DraftBlockInstance>(
    `/lssp/cases/${caseId}/drafts/${draftId}/blocks/${blockInstanceId}`,
    data
  );
}

/**
 * Update draft status
 */
export async function updateDraftStatus(
  caseId: string,
  draftId: string,
  status: 'draft' | 'review' | 'final'
): Promise<ApiResponse<Draft>> {
  return apiClient.patch<Draft>(`/lssp/cases/${caseId}/drafts/${draftId}/status`, { status });
}

/**
 * Delete a draft
 */
export async function deleteDraft(caseId: string, draftId: string): Promise<ApiResponse<void>> {
  return apiClient.delete<void>(`/lssp/cases/${caseId}/drafts/${draftId}`);
}

// =============================================================================
// API Functions: AI Pipeline
// =============================================================================

/**
 * Trigger keypoint extraction from evidence
 */
export async function extractKeypoints(
  caseId: string,
  data?: KeypointExtractionRequest
): Promise<ApiResponse<KeypointExtractionResponse>> {
  return apiClient.post<KeypointExtractionResponse>(
    `/lssp/cases/${caseId}/extract-keypoints`,
    data || {}
  );
}

/**
 * Generate a draft using AI
 */
export async function generateDraft(
  caseId: string,
  data: DraftGenerationRequest
): Promise<ApiResponse<DraftGenerationResponse>> {
  return apiClient.post<DraftGenerationResponse>(
    `/lssp/cases/${caseId}/generate-draft`,
    data
  );
}

// =============================================================================
// API Functions: Case Legal Ground Summary
// =============================================================================

/**
 * Get legal ground analysis for a case
 */
export async function getCaseLegalGroundSummary(
  caseId: string
): Promise<ApiResponse<{
  grounds: Array<{
    ground: LegalGround;
    keypoint_count: number;
    verified_count: number;
    evidence_strength: 'strong' | 'moderate' | 'weak' | 'none';
  }>;
  total_keypoints: number;
  verified_keypoints: number;
}>> {
  return apiClient.get(`/lssp/cases/${caseId}/legal-ground-summary`);
}

// =============================================================================
// Types: Pipeline (v2.10)
// =============================================================================

export interface PipelineRule {
  rule_id: number;
  version: string;
  evidence_type: string;
  kind: string;
  name: string;
  pattern: string;
  flags: string;
  value_template: Record<string, unknown>;
  ground_tags: string[];
  base_confidence: number;
  base_materiality: number;
  is_enabled: boolean;
  created_at: string;
}

export interface Candidate {
  candidate_id: number;
  case_id: string;
  evidence_id: string;
  extract_id: string | null;
  run_id: number | null;
  rule_id: number | null;
  kind: string;
  content: string;
  value: Record<string, unknown>;
  ground_tags: string[];
  confidence: number;
  materiality: number;
  source_span: { start: number; end: number } | null;
  status: 'CANDIDATE' | 'ACCEPTED' | 'REJECTED' | 'MERGED';
  reviewer_id: string | null;
  reviewed_at: string | null;
  rejection_reason: string | null;
  created_at: string;
  rule_name?: string;
}

export interface ExtractionRun {
  run_id: number;
  case_id: string;
  evidence_id: string;
  extractor: string;
  version: string;
  status: 'PENDING' | 'RUNNING' | 'DONE' | 'ERROR';
  started_at: string;
  finished_at: string | null;
  candidate_count: number;
  error_message: string | null;
}

export interface PipelineStats {
  total_runs: number;
  total_candidates: number;
  pending_candidates: number;
  accepted_candidates: number;
  rejected_candidates: number;
  promoted_keypoints: number;
}

export interface CandidateUpdateRequest {
  status?: 'CANDIDATE' | 'ACCEPTED' | 'REJECTED';
  content?: string;
  kind?: string;
  ground_tags?: string[];
  rejection_reason?: string;
}

export interface PromoteCandidatesRequest {
  candidate_ids: number[];
  merge_similar?: boolean;
}

export interface PromoteCandidatesResponse {
  promoted_count: number;
  keypoint_ids: string[];
  merged_groups: number[];
}

export interface ExtractCandidatesRequest {
  mode?: 'rule_based' | 'ai_based' | 'hybrid';
  evidence_type?: string;
  text_content?: string;
}

// =============================================================================
// API Functions: Pipeline (v2.10)
// =============================================================================

/**
 * List all pipeline extraction rules
 */
export async function getPipelineRules(
  params?: {
    evidence_type?: string;
    kind?: string;
    enabled_only?: boolean;
  }
): Promise<ApiResponse<PipelineRule[]>> {
  const searchParams = new URLSearchParams();
  if (params?.evidence_type) searchParams.set('evidence_type', params.evidence_type);
  if (params?.kind) searchParams.set('kind', params.kind);
  if (params?.enabled_only !== undefined) searchParams.set('enabled_only', params.enabled_only.toString());

  const query = searchParams.toString();
  return apiClient.get<PipelineRule[]>(`/lssp/pipeline/rules${query ? `?${query}` : ''}`);
}

/**
 * List candidates for a case
 */
export async function getCandidates(
  caseId: string,
  params?: {
    evidence_id?: string;
    status?: string;
    kind?: string;
    limit?: number;
    offset?: number;
  }
): Promise<ApiResponse<Candidate[]>> {
  const searchParams = new URLSearchParams();
  if (params?.evidence_id) searchParams.set('evidence_id', params.evidence_id);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.kind) searchParams.set('kind', params.kind);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());

  const query = searchParams.toString();
  return apiClient.get<Candidate[]>(`/lssp/pipeline/cases/${caseId}/candidates${query ? `?${query}` : ''}`);
}

/**
 * Update a candidate (accept/reject/edit)
 */
export async function updateCandidate(
  caseId: string,
  candidateId: number,
  data: CandidateUpdateRequest
): Promise<ApiResponse<Candidate>> {
  return apiClient.patch<Candidate>(
    `/lssp/pipeline/cases/${caseId}/candidates/${candidateId}`,
    data
  );
}

/**
 * Promote accepted candidates to keypoints
 */
export async function promoteCandidates(
  caseId: string,
  data: PromoteCandidatesRequest
): Promise<ApiResponse<PromoteCandidatesResponse>> {
  return apiClient.post<PromoteCandidatesResponse>(
    `/lssp/pipeline/cases/${caseId}/promote`,
    data
  );
}

/**
 * Extract candidates from evidence
 */
export async function extractCandidates(
  caseId: string,
  evidenceId: string,
  data?: ExtractCandidatesRequest
): Promise<ApiResponse<ExtractionRun>> {
  return apiClient.post<ExtractionRun>(
    `/lssp/pipeline/cases/${caseId}/evidences/${evidenceId}/extract`,
    data || {}
  );
}

/**
 * Get pipeline statistics for a case
 */
export async function getPipelineStats(
  caseId: string
): Promise<ApiResponse<PipelineStats>> {
  return apiClient.get<PipelineStats>(`/lssp/pipeline/cases/${caseId}/stats`);
}

/**
 * Get extraction runs for a case
 */
export async function getExtractionRuns(
  caseId: string,
  params?: {
    evidence_id?: string;
    status?: string;
    limit?: number;
  }
): Promise<ApiResponse<ExtractionRun[]>> {
  const searchParams = new URLSearchParams();
  if (params?.evidence_id) searchParams.set('evidence_id', params.evidence_id);
  if (params?.status) searchParams.set('status', params.status);
  if (params?.limit) searchParams.set('limit', params.limit.toString());

  const query = searchParams.toString();
  return apiClient.get<ExtractionRun[]>(`/lssp/pipeline/cases/${caseId}/extraction-runs${query ? `?${query}` : ''}`);
}

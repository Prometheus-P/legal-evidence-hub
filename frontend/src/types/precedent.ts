/**
 * Precedent Search Types
 * 012-precedent-integration: T011
 */

export interface DivisionRatio {
  plaintiff: number;
  defendant: number;
}

export interface PrecedentCase {
  case_ref: string;
  court: string;
  decision_date: string;
  summary: string;
  division_ratio?: DivisionRatio;
  key_factors: string[];
  similarity_score: number;
}

export interface QueryContext {
  fault_types: string[];
  total_found: number;
}

export interface PrecedentSearchResponse {
  precedents: PrecedentCase[];
  query_context: QueryContext;
}

export interface PrecedentSearchOptions {
  limit?: number;
  min_score?: number;
}

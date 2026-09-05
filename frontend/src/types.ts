export interface ProductData {
  title: string;
  rawDetails: string;
  url?: string;
  category?: string;
  price?: string;
  description?: string;
  features?: string[];
  imageUrl: string | null;
  imageFile?: File | null;
  dimensions?: string;
  sku?: string;
}

export type AnalysisStage = 
  | 'idle'
  | 'analyzing'
  | 'pipeline'
  | 'result';

export type SystemStatusStep = 
  | 'PARSING PRODUCT'
  | 'BUILDING PRODUCT VECTOR'
  | 'FINDING COMPETITORS'
  | 'SIMULATING AI BUYER';

export interface AIModelResult {
  name: string;
  code: string;
  percentage: number;
  reasoning: string;
  preferenceRank: string;
  confidence: number;
}

export interface CompetitorComparison {
  name: string;
  percentage: number;
  isUserProduct: boolean;
  delta: string;
  strengths: string;
}

export interface PipelineStageInfo {
  id: string;
  title: string;
  subhead: string;
  status: 'pending' | 'active' | 'completed';
  models?: string[];
}

export interface AuditResponse {
  times_rank1?: number;
  times_shown?: number;
  win_rate?: number;
}

export interface ScoreResponse {
  overall_score?: number;
}
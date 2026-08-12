import { apiRequest } from "./api";
import type { ParsedResume } from "./resume";

export type AnalysisSummary = {
  id: string;
  resume_name: string;
  job_title: string | null;
  ats_score: number | null;
  match_score: number | null;
  created_at: string;
};

export type AnalysisDetail = AnalysisSummary & {
  parsed_resume: ParsedResume | Record<string, never>;
  keyword_score: number | null;
  skills_score: number | null;
  structure_score: number | null;
  experience_score: number | null;
  project_score: number | null;
  formatting_score: number | null;
  matching_skills: string[];
  missing_skills: string[];
  matching_keywords: string[];
  missing_keywords: string[];
  experience_relevance: number | null;
  project_relevance: number | null;
  strengths: string[];
  weaknesses: string[];
  priority_improvements: string[];
  recommendations: string[];
};

export type DashboardStats = {
  total_analyses: number;
  best_ats_score: number | null;
  avg_match_score: number | null;
  unique_skills_count: number;
  recent_analyses: AnalysisSummary[];
};

export type SaveAnalysisPayload = {
  resume_name: string;
  job_title?: string | null;
  parsed_resume?: unknown;
  ats_score?: number | null;
  keyword_score?: number | null;
  skills_score?: number | null;
  structure_score?: number | null;
  experience_score?: number | null;
  project_score?: number | null;
  formatting_score?: number | null;
  match_score?: number | null;
  matching_skills?: string[];
  missing_skills?: string[];
  matching_keywords?: string[];
  missing_keywords?: string[];
  experience_relevance?: number | null;
  project_relevance?: number | null;
  strengths?: string[];
  weaknesses?: string[];
  priority_improvements?: string[];
  recommendations?: string[];
};

export async function saveAnalysis(payload: SaveAnalysisPayload): Promise<AnalysisDetail> {
  return apiRequest<AnalysisDetail>("/analysis/save", { method: "POST", body: payload });
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return apiRequest<DashboardStats>("/dashboard/stats");
}

export async function getAnalysisHistory(): Promise<AnalysisSummary[]> {
  return apiRequest<AnalysisSummary[]>("/analysis/history");
}

export async function getAnalysis(id: string): Promise<AnalysisDetail> {
  return apiRequest<AnalysisDetail>(`/analysis/${id}`);
}

export async function deleteAnalysis(id: string): Promise<void> {
  await apiRequest<void>(`/analysis/${id}`, { method: "DELETE" });
}

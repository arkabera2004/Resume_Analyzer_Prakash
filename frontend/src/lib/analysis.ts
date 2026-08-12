import { apiRequest, downloadFile } from "./api";
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

export type CompareResult = {
  analysis_a: AnalysisSummary;
  analysis_b: AnalysisSummary;
  ats_score_change: number | null;
  match_score_change: number | null;
  new_skills: string[];
  removed_skills: string[];
  new_keywords: string[];
  removed_keywords: string[];
  improved_sections: string[];
  regressed_sections: string[];
};

export async function compareAnalyses(idA: string, idB: string): Promise<CompareResult> {
  return apiRequest<CompareResult>("/analysis/compare", {
    method: "POST",
    body: { analysis_id_a: idA, analysis_id_b: idB },
  });
}

export async function downloadAnalysisReport(id: string, resumeName: string): Promise<void> {
  const fallbackName = `${resumeName.replace(/\.(pdf|docx?)$/i, "")}-analysis-report.pdf`;
  await downloadFile(`/analysis/${id}/report`, fallbackName);
}

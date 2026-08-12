import { apiRequest } from "./api";

export type SectionScore = {
  score: number;
  strengths: string[];
  problems: string[];
  recommendations: string[];
};

export type RecommendedRole = {
  role: string;
  match_percentage: number;
  reason: string;
};

export type AIRecommendations = {
  section_scores: Record<string, SectionScore>;
  strengths: string[];
  weaknesses: string[];
  priority_improvements: string[];
  recommended_roles: RecommendedRole[];
};

export const SECTION_SCORE_LABELS: Record<string, string> = {
  summary: "Summary",
  education: "Education",
  skills: "Skills",
  experience: "Experience",
  projects: "Projects",
  certifications: "Certifications",
  achievements: "Achievements",
};

export async function getAIRecommendations(resumeText: string): Promise<AIRecommendations> {
  return apiRequest<AIRecommendations>("/ai/recommendations", {
    method: "POST",
    body: { resume_text: resumeText },
  });
}

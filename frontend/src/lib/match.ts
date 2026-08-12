import { apiRequest } from "./api";
import type { JobDescriptionAnalysis } from "./job";
import type { ParsedResume } from "./resume";

export type MatchResult = {
  overall_match: number;
  matching_skills: string[];
  missing_skills: string[];
  matching_keywords: string[];
  missing_keywords: string[];
  experience_relevance: number;
  project_relevance: number;
  explanation: string[];
  parsed_resume: ParsedResume;
  parsed_job: JobDescriptionAnalysis;
};

export async function matchResumeToJob(
  resumeText: string,
  jobDescription: string,
): Promise<MatchResult> {
  return apiRequest<MatchResult>("/match/analyze", {
    method: "POST",
    body: { resume_text: resumeText, job_description: jobDescription },
  });
}

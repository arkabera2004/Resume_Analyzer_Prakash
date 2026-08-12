import { apiRequest } from "./api";

export type JobDescriptionAnalysis = {
  job_title: string | null;
  required_skills: string[];
  preferred_skills: string[];
  technologies: string[];
  keywords: string[];
  experience_requirements: string[];
  education_requirements: string[];
  responsibilities: string[];
};

export async function analyzeJobDescription(
  jobDescription: string,
): Promise<JobDescriptionAnalysis> {
  return apiRequest<JobDescriptionAnalysis>("/job/analyze", {
    method: "POST",
    body: { job_description: jobDescription },
  });
}

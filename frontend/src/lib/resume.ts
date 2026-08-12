import { apiRequest } from "./api";

export type ContactInfo = {
  name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
};

export type ParsedResume = {
  contact: ContactInfo;
  skills: Record<string, string[]>;
  education: string[];
  experience: string[];
  internships: string[];
  projects: string[];
  certifications: string[];
  achievements: string[];
  summary: string | null;
};

export type ResumeUploadResult = {
  filename: string;
  file_type: "pdf" | "docx";
  character_count: number;
  word_count: number;
  extracted_text: string;
  parsed: ParsedResume;
};

export const SKILL_CATEGORY_LABELS: Record<string, string> = {
  programming: "Programming Languages",
  frontend: "Frontend",
  backend: "Backend",
  database: "Database",
  tools: "Tools",
};

export const ACCEPTED_RESUME_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];
export const ACCEPTED_RESUME_EXTENSIONS = [".pdf", ".docx"];
export const MAX_RESUME_SIZE_MB = 5;

export function isAcceptedResumeFile(file: File): boolean {
  if (ACCEPTED_RESUME_TYPES.includes(file.type)) return true;
  const lowerName = file.name.toLowerCase();
  return ACCEPTED_RESUME_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
}

export async function uploadResume(file: File): Promise<ResumeUploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<ResumeUploadResult>("/resume/upload", {
    method: "POST",
    body: formData,
  });
}

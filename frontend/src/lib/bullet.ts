import { apiRequest } from "./api";

export type ImproveBulletResult = {
  original: string;
  improved: string;
  why_better: string[];
};

export async function improveBullet(
  bulletText: string,
  context?: string,
): Promise<ImproveBulletResult> {
  return apiRequest<ImproveBulletResult>("/ai/improve-bullet", {
    method: "POST",
    body: { bullet_text: bulletText, context: context || undefined },
  });
}

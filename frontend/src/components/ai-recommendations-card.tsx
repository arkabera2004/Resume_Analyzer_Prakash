import { useState } from "react";
import { Sparkles, RotateCcw, ThumbsUp, ThumbsDown, ListOrdered, Briefcase } from "lucide-react";
import { toast } from "sonner";

import { scoreColor } from "@/components/score-ring";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ApiError } from "@/lib/api";
import { getAIRecommendations, SECTION_SCORE_LABELS, type AIRecommendations } from "@/lib/ai";

function scoreOutOf10Color(score: number): string {
  return scoreColor(score * 10);
}

export function AiRecommendationsCard({ resumeText }: { resumeText: string }) {
  const [result, setResult] = useState<AIRecommendations | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const hasResume = resumeText.trim().length > 0;

  async function handleGenerate() {
    if (!hasResume) {
      toast.error("Upload a resume first", {
        description: "Upload and extract a resume above before generating recommendations.",
      });
      return;
    }

    setIsLoading(true);
    try {
      const recommendations = await getAIRecommendations(resumeText);
      setResult(recommendations);
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unexpected error. Please try again.";
      toast.error("Couldn't generate recommendations", { description: message });
    } finally {
      setIsLoading(false);
    }
  }

  function reset() {
    setResult(null);
  }

  return (
    <Card className="border-border shadow-none">
      <CardHeader>
        <CardTitle>AI recommendations</CardTitle>
        <CardDescription>
          {!hasResume
            ? "Upload a resume above to generate AI-backed recommendations."
            : result
              ? "Grounded in your resume — nothing here is invented."
              : "Get section-by-section feedback, strengths/weaknesses, and role suggestions."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {result ? (
          <div className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  <ThumbsUp className="size-3.5" /> Strengths
                </p>
                <ul className="list-inside list-disc space-y-1 text-sm text-foreground/80">
                  {result.strengths.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  <ThumbsDown className="size-3.5" /> Weaknesses
                </p>
                <ul className="list-inside list-disc space-y-1 text-sm text-foreground/80">
                  {result.weaknesses.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div>
              <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                <ListOrdered className="size-3.5" /> Priority Improvements
              </p>
              <ol className="list-inside list-decimal space-y-1 text-sm text-foreground/80">
                {result.priority_improvements.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ol>
            </div>

            <div>
              <p className="mb-2 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                <Briefcase className="size-3.5" /> Recommended Roles
              </p>
              <div className="space-y-2">
                {result.recommended_roles.map((role) => (
                  <div key={role.role} className="rounded-lg border border-border p-3">
                    <div className="mb-1 flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">{role.role}</span>
                      <span className={`font-mono text-sm font-semibold ${scoreColor(role.match_percentage)}`}>
                        {role.match_percentage}%
                      </span>
                    </div>
                    <Progress value={role.match_percentage} className="mb-2 h-1.5" />
                    <p className="text-xs text-muted-foreground">{role.reason}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Section-by-Section Analysis
              </p>
              <Accordion type="single" collapsible className="w-full">
                {Object.entries(result.section_scores).map(([key, section]) => (
                  <AccordionItem key={key} value={key}>
                    <AccordionTrigger className="text-sm">
                      <span className="flex items-center gap-2">
                        {SECTION_SCORE_LABELS[key] ?? key}
                        <Badge variant="outline" className={`font-mono font-normal ${scoreOutOf10Color(section.score)}`}>
                          {section.score}/10
                        </Badge>
                      </span>
                    </AccordionTrigger>
                    <AccordionContent className="space-y-2 text-sm">
                      {section.strengths.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-emerald-600 dark:text-emerald-400">Strengths</p>
                          <ul className="list-inside list-disc text-foreground/80">
                            {section.strengths.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {section.problems.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-red-600 dark:text-red-400">Problems</p>
                          <ul className="list-inside list-disc text-foreground/80">
                            {section.problems.map((p, i) => (
                              <li key={i}>{p}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {section.recommendations.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-muted-foreground">Recommendations</p>
                          <ul className="list-inside list-disc text-foreground/80">
                            {section.recommendations.map((r, i) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </div>

            <Button variant="outline" size="sm" onClick={reset}>
              <RotateCcw className="size-4" /> Regenerate
            </Button>
          </div>
        ) : (
          <Button onClick={() => void handleGenerate()} disabled={isLoading || !hasResume} className="w-full">
            <Sparkles className="size-4" />
            {isLoading ? "Generating…" : "Generate AI Recommendations"}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

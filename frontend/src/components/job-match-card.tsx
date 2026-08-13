import { useState } from "react";
import { Scale, RotateCcw } from "lucide-react";
import { toast } from "sonner";

import { ScoreRing, scoreColor } from "@/components/score-ring";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { matchResumeToJob, type MatchResult } from "@/lib/match";

const MIN_LENGTH = 30;

function SkillBadges({
  skills,
  emptyLabel,
  variant,
}: {
  skills: string[];
  emptyLabel: string;
  variant: "matching" | "missing";
}) {
  if (skills.length === 0) {
    return <p className="text-sm text-muted-foreground">{emptyLabel}</p>;
  }
  return (
    <div className="flex flex-wrap gap-1.5">
      {skills.map((skill) => (
        <Badge
          key={skill}
          variant="outline"
          className={
            variant === "matching"
              ? "border-emerald-500/40 bg-emerald-500/10 font-normal text-emerald-700 dark:text-emerald-400"
              : "border-red-500/40 bg-red-500/10 font-normal text-red-700 dark:text-red-400"
          }
        >
          {skill}
        </Badge>
      ))}
    </div>
  );
}

type JobMatchCardProps = {
  resumeText: string;
  /** Shared with JobDescriptionCard — see that component for why. */
  jobDescription: string;
  onJobDescriptionChange: (value: string) => void;
  /** Called whenever a match completes, so the dashboard can offer to save it
   * alongside the ATS score. */
  onMatchResult?: (jobTitle: string | null, result: MatchResult) => void;
};

export function JobMatchCard({
  resumeText,
  jobDescription,
  onJobDescriptionChange,
  onMatchResult,
}: JobMatchCardProps) {
  const [result, setResult] = useState<MatchResult | null>(null);
  const [isMatching, setIsMatching] = useState(false);

  const hasResume = resumeText.trim().length > 0;

  async function handleMatch() {
    if (!hasResume) {
      toast.error("Upload a resume first", {
        description: "Upload and extract a resume above before comparing it to a job.",
      });
      return;
    }
    if (jobDescription.trim().length < MIN_LENGTH) {
      toast.error("Paste a fuller job description", {
        description: `At least ${MIN_LENGTH} characters, so there's enough to compare.`,
      });
      return;
    }

    setIsMatching(true);
    try {
      const match = await matchResumeToJob(resumeText, jobDescription);
      setResult(match);
      onMatchResult?.(match.parsed_job.job_title, match);
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unexpected error. Please try again.";
      toast.error("Match failed", { description: message });
    } finally {
      setIsMatching(false);
    }
  }

  function reset() {
    setResult(null);
  }

  return (
    <Card className="border-border shadow-none">
      <CardHeader>
        <CardTitle>Match your resume to a job</CardTitle>
        <CardDescription>
          {!hasResume
            ? "Upload a resume above, then paste a job description to see how well they match."
            : result
              ? "Comparison between your uploaded resume and this job description."
              : "Paste a job description to compare it against your uploaded resume."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {result ? (
          <div className="space-y-5">
            <div className="rounded-lg border border-border bg-muted/20 p-4">
              <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
                <ScoreRing score={result.overall_match} label="Overall Match" />
                <div className="w-full flex-1 space-y-3">
                  <div>
                    <div className="mb-1 flex items-baseline justify-between text-xs">
                      <span className="text-foreground/80">Experience Relevance</span>
                      <span className={`font-mono font-medium ${scoreColor(result.experience_relevance)}`}>
                        {result.experience_relevance}
                      </span>
                    </div>
                    <Progress value={result.experience_relevance} className="h-1.5" />
                  </div>
                  <div>
                    <div className="mb-1 flex items-baseline justify-between text-xs">
                      <span className="text-foreground/80">Project Relevance</span>
                      <span className={`font-mono font-medium ${scoreColor(result.project_relevance)}`}>
                        {result.project_relevance}
                      </span>
                    </div>
                    <Progress value={result.project_relevance} className="h-1.5" />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Matching Skills
                </p>
                <SkillBadges skills={result.matching_skills} emptyLabel="No overlap detected." variant="matching" />
              </div>
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Missing Skills
                </p>
                <SkillBadges skills={result.missing_skills} emptyLabel="Nothing missing." variant="missing" />
              </div>
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Matching Keywords
                </p>
                <SkillBadges skills={result.matching_keywords} emptyLabel="No overlap detected." variant="matching" />
              </div>
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Missing Keywords
                </p>
                <SkillBadges skills={result.missing_keywords} emptyLabel="Nothing missing." variant="missing" />
              </div>
            </div>

            <div className="rounded-lg border border-border bg-muted/20 p-4">
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Why this score
              </p>
              <ul className="list-inside list-disc space-y-1 text-sm text-foreground/80">
                {result.explanation.map((line, index) => (
                  <li key={index}>{line}</li>
                ))}
              </ul>
            </div>

            <Button variant="outline" size="sm" onClick={reset}>
              <RotateCcw className="size-4" /> Compare a different job
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <Textarea
              value={jobDescription}
              onChange={(event) => onJobDescriptionChange(event.target.value)}
              placeholder={
                hasResume
                  ? "Paste the job description here…"
                  : "Upload a resume above first…"
              }
              disabled={!hasResume}
              className="min-h-40 resize-y"
            />
            <Button
              onClick={() => void handleMatch()}
              disabled={isMatching || !hasResume}
              className="w-full"
            >
              <Scale className="size-4" />
              {isMatching ? "Comparing…" : "Compare Resume to Job"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

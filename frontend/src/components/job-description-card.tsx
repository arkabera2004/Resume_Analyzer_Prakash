import { useState } from "react";
import { Briefcase, ClipboardList, RotateCcw } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { analyzeJobDescription, type JobDescriptionAnalysis } from "@/lib/job";

const MIN_LENGTH = 30;

function SkillList({ title, skills, emptyLabel }: { title: string; skills: string[]; emptyLabel: string }) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {title}
      </p>
      {skills.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {skills.map((skill) => (
            <Badge key={skill} variant="secondary" className="font-normal">
              {skill}
            </Badge>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">{emptyLabel}</p>
      )}
    </div>
  );
}

function LineList({ title, lines, emptyLabel }: { title: string; lines: string[]; emptyLabel: string }) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {title}
      </p>
      {lines.length > 0 ? (
        <ul className="list-inside list-disc space-y-1 text-sm text-foreground/80">
          {lines.map((line, index) => (
            <li key={index}>{line}</li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted-foreground">{emptyLabel}</p>
      )}
    </div>
  );
}

export function JobDescriptionCard() {
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<JobDescriptionAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  async function handleAnalyze() {
    if (jobDescription.trim().length < MIN_LENGTH) {
      toast.error("Paste a fuller job description", {
        description: `At least ${MIN_LENGTH} characters, so there's enough to analyze.`,
      });
      return;
    }

    setIsAnalyzing(true);
    try {
      const analysis = await analyzeJobDescription(jobDescription);
      setResult(analysis);
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unexpected error. Please try again.";
      toast.error("Analysis failed", { description: message });
    } finally {
      setIsAnalyzing(false);
    }
  }

  function reset() {
    setResult(null);
    setJobDescription("");
  }

  return (
    <Card className="border-border shadow-none">
      <CardHeader>
        <CardTitle>Analyze a job description</CardTitle>
        <CardDescription>
          {result
            ? "Extracted from the pasted job description."
            : "Paste a job posting to extract required/preferred skills, experience, and education requirements."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {result ? (
          <div className="space-y-4">
            <div className="flex items-start gap-3 rounded-lg border border-border bg-muted/30 px-4 py-3">
              <Briefcase className="mt-0.5 size-5 shrink-0 text-primary" />
              <p className="font-medium text-foreground">{result.job_title ?? "Job title not detected"}</p>
            </div>

            <SkillList title="Required Skills" skills={result.required_skills} emptyLabel="None detected." />
            <SkillList title="Preferred Skills" skills={result.preferred_skills} emptyLabel="None detected." />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Experience
                </p>
                {result.experience_requirements.length > 0 ? (
                  result.experience_requirements.map((req) => (
                    <Badge key={req} variant="outline" className="mr-1 mb-1 font-normal">
                      {req}
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">Not specified.</p>
                )}
              </div>
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Education
                </p>
                {result.education_requirements.length > 0 ? (
                  result.education_requirements.map((req) => (
                    <Badge key={req} variant="outline" className="mr-1 mb-1 font-normal">
                      {req}
                    </Badge>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">Not specified.</p>
                )}
              </div>
            </div>

            <LineList
              title="Responsibilities"
              lines={result.responsibilities}
              emptyLabel="None detected."
            />

            <Button variant="outline" size="sm" onClick={reset}>
              <RotateCcw className="size-4" /> Analyze a different posting
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <Textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste the full job description here…"
              className="min-h-40 resize-y"
            />
            <Button
              onClick={() => void handleAnalyze()}
              disabled={isAnalyzing}
              className="w-full"
            >
              <ClipboardList className="size-4" />
              {isAnalyzing ? "Analyzing…" : "Analyze Job Description"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

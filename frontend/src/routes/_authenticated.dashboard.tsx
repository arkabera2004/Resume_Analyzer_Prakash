import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Award, FileUp, Percent, Save, Tags, Trash2 } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { AiRecommendationsCard } from "@/components/ai-recommendations-card";
import { BulletImproverCard } from "@/components/bullet-improver-card";
import { JobDescriptionCard } from "@/components/job-description-card";
import { JobMatchCard } from "@/components/job-match-card";
import { ResumeUploadCard } from "@/components/resume-upload-card";
import { ScoreTrendChart } from "@/components/score-trend-chart";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";
import { deleteAnalysis, getDashboardStats, saveAnalysis } from "@/lib/analysis";
import { useAuth } from "@/lib/auth";
import type { MatchResult } from "@/lib/match";
import type { ATSScoreResult } from "@/lib/resume";

export const Route = createFileRoute("/_authenticated/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — ResumeIQ" },
      {
        name: "description",
        content: "Track your ATS scores, job match results, and resume analysis history.",
      },
      { property: "og:title", content: "Dashboard — ResumeIQ" },
      { property: "og:description", content: "Your resume analysis overview." },
    ],
  }),
  component: DashboardPage,
});

type Stat = {
  label: string;
  icon: LucideIcon;
  hint: string;
  value: (stats: { total_analyses: number; best_ats_score: number | null; avg_match_score: number | null; unique_skills_count: number }) => string;
};

const stats: Stat[] = [
  {
    label: "Analyses Completed",
    icon: FileUp,
    hint: "Across all resumes",
    value: (s) => String(s.total_analyses),
  },
  {
    label: "Best ATS Score",
    icon: Award,
    hint: "Highest score recorded",
    value: (s) => (s.best_ats_score === null ? "—" : String(s.best_ats_score)),
  },
  {
    label: "Avg Job Match",
    icon: Percent,
    hint: "Average across matches",
    value: (s) => (s.avg_match_score === null ? "—" : `${s.avg_match_score}%`),
  },
  {
    label: "Skills Detected",
    icon: Tags,
    hint: "Unique skills parsed",
    value: (s) => String(s.unique_skills_count),
  },
];

function DashboardPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [resumeText, setResumeText] = useState("");
  const [resumeFileName, setResumeFileName] = useState("");
  const [atsResult, setAtsResult] = useState<ATSScoreResult | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [jobTitle, setJobTitle] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  // Shared between JobDescriptionCard and JobMatchCard so pasting a job
  // description once feeds both — they used to hold independent copies,
  // which meant "Analyze" and "Match" could silently run against different
  // text if you'd typed into one and not the other.
  const [jobDescriptionText, setJobDescriptionText] = useState("");

  const statsQuery = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: getDashboardStats,
  });

  async function handleSave() {
    if (!atsResult) return;
    setIsSaving(true);
    try {
      await saveAnalysis({
        resume_name: resumeFileName || "resume",
        job_title: jobTitle,
        parsed_resume: atsResult.parsed,
        ats_score: atsResult.overall_score,
        keyword_score: atsResult.keyword_score,
        skills_score: atsResult.skills_score,
        structure_score: atsResult.structure_score,
        experience_score: atsResult.experience_score,
        project_score: atsResult.project_score,
        formatting_score: atsResult.formatting_score,
        match_score: matchResult?.overall_match ?? null,
        matching_skills: matchResult?.matching_skills ?? [],
        missing_skills: matchResult?.missing_skills ?? [],
        matching_keywords: matchResult?.matching_keywords ?? [],
        missing_keywords: matchResult?.missing_keywords ?? [],
        experience_relevance: matchResult?.experience_relevance ?? null,
        project_relevance: matchResult?.project_relevance ?? null,
      });
      toast.success("Analysis saved");
      await queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unexpected error. Please try again.";
      toast.error("Couldn't save analysis", { description: message });
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteAnalysis(id);
      toast.success("Analysis deleted");
      await queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unexpected error. Please try again.";
      toast.error("Couldn't delete analysis", { description: message });
    }
  }

  const data = statsQuery.data;

  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-12">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Welcome back{user ? `, ${user.name.split(" ")[0]}` : ""}
          </h1>
          <p className="mt-2 text-muted-foreground">
            Upload a resume to generate your first ATS score and job match report.
          </p>
        </div>
        {atsResult && (
          <Button onClick={() => void handleSave()} disabled={isSaving}>
            <Save className="size-4" />
            {isSaving ? "Saving…" : "Save this analysis"}
          </Button>
        )}
      </header>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="border-border shadow-none">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                <stat.icon className="size-4 text-muted-foreground" />
              </div>
              <p className="mt-3 font-mono text-3xl font-semibold text-foreground">
                {statsQuery.isPending ? (
                  <Skeleton className="h-8 w-12" />
                ) : data ? (
                  stat.value(data)
                ) : (
                  "—"
                )}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{stat.hint}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-3">
        <ResumeUploadCard
          onTextExtracted={(text) => setResumeText(text)}
          onScoreResult={(filename, score) => {
            setResumeFileName(filename);
            setAtsResult(score);
          }}
        />

        <Card className="border-border shadow-none">
          <CardHeader>
            <CardTitle>Recent analyses</CardTitle>
            <CardDescription>Your latest saved reports.</CardDescription>
          </CardHeader>
          <CardContent>
            {statsQuery.isPending ? (
              <div className="space-y-2">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : data && data.recent_analyses.length > 0 ? (
              <ul className="space-y-2">
                {data.recent_analyses.map((analysis) => (
                  <li
                    key={analysis.id}
                    className="flex items-center justify-between rounded-lg border border-border px-3 py-2"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-foreground">
                        {analysis.resume_name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {analysis.ats_score !== null ? `ATS ${analysis.ats_score}` : ""}
                        {analysis.match_score !== null ? ` · Match ${analysis.match_score}%` : ""}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-8 shrink-0 text-muted-foreground hover:text-destructive"
                      onClick={() => void handleDelete(analysis.id)}
                      aria-label="Delete analysis"
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="rounded-lg border border-dashed border-border px-4 py-12 text-center">
                <p className="text-sm text-muted-foreground">No analyses yet.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      {data && data.recent_analyses.length > 0 && (
        <section className="mt-8">
          <Card className="border-border shadow-none">
            <CardHeader>
              <CardTitle>Score trend</CardTitle>
              <CardDescription>ATS score and job match across your recent analyses.</CardDescription>
            </CardHeader>
            <CardContent>
              <ScoreTrendChart analyses={data.recent_analyses} />
            </CardContent>
          </Card>
        </section>
      )}

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <JobDescriptionCard
          jobDescription={jobDescriptionText}
          onJobDescriptionChange={setJobDescriptionText}
        />
        <JobMatchCard
          resumeText={resumeText}
          jobDescription={jobDescriptionText}
          onJobDescriptionChange={setJobDescriptionText}
          onMatchResult={(title, result) => {
            setJobTitle(title);
            setMatchResult(result);
          }}
        />
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <AiRecommendationsCard resumeText={resumeText} />
        <BulletImproverCard resumeText={resumeText} />
      </section>
    </div>
  );
}

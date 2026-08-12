import { createFileRoute } from "@tanstack/react-router";
import { Award, FileUp, Percent, Tags } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState } from "react";

import { JobDescriptionCard } from "@/components/job-description-card";
import { JobMatchCard } from "@/components/job-match-card";
import { ResumeUploadCard } from "@/components/resume-upload-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/lib/auth";

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
};

const stats: Stat[] = [
  { label: "Analyses Completed", icon: FileUp, hint: "Across all resumes" },
  { label: "Best ATS Score", icon: Award, hint: "Highest score recorded" },
  { label: "Avg Job Match", icon: Percent, hint: "Average across matches" },
  { label: "Skills Detected", icon: Tags, hint: "Unique skills parsed" },
];

function DashboardPage() {
  const { user } = useAuth();
  const [resumeText, setResumeText] = useState("");

  return (
    <div className="mx-auto w-full max-w-6xl px-5 py-12">
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Welcome back{user ? `, ${user.name.split(" ")[0]}` : ""}
        </h1>
        <p className="mt-2 text-muted-foreground">
          Upload a resume to generate your first ATS score and job match report.
        </p>
      </header>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="border-border shadow-none">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                <stat.icon className="size-4 text-muted-foreground" />
              </div>
              <p className="mt-3 font-mono text-3xl font-semibold text-foreground">—</p>
              <p className="mt-1 text-xs text-muted-foreground">{stat.hint}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-3">
        <ResumeUploadCard onTextExtracted={setResumeText} />

        <Card className="border-border shadow-none">
          <CardHeader>
            <CardTitle>Recent analyses</CardTitle>
            <CardDescription>Your latest reports will be listed here.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-dashed border-border px-4 py-12 text-center">
              <p className="text-sm text-muted-foreground">No analyses yet.</p>
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <JobDescriptionCard />
        <JobMatchCard resumeText={resumeText} />
      </section>
    </div>
  );
}

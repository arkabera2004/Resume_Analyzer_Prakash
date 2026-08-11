import { createFileRoute } from "@tanstack/react-router";
import { Award, FileUp, Percent, Tags, UploadCloud } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
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
        <Card className="border-border shadow-none lg:col-span-2">
          <CardHeader>
            <CardTitle>Start an analysis</CardTitle>
            <CardDescription>
              Resume upload and analysis are not connected yet. Once the analysis service is live,
              your report will appear here.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-muted/30 px-6 py-14 text-center">
              <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                <UploadCloud className="size-6" />
              </span>
              <h3 className="mt-4 font-semibold text-foreground">No resume uploaded yet</h3>
              <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                Upload a PDF or DOCX resume to receive an ATS score, keyword breakdown, and job
                match analysis.
              </p>
              <Button className="mt-6" disabled>
                Upload resume — coming soon
              </Button>
            </div>
          </CardContent>
        </Card>

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
    </div>
  );
}

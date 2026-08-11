import { Link, createFileRoute } from "@tanstack/react-router";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  FileUp,
  ShieldCheck,
  Sparkles,
  Target,
} from "lucide-react";

import { Footer } from "@/components/footer";
import { Navbar } from "@/components/navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ResumeIQ — AI Resume Analyzer & Job Match Platform" },
      {
        name: "description",
        content:
          "Upload your resume, get an ATS score, match against any job description, and receive AI recommendations that get you shortlisted.",
      },
      { property: "og:title", content: "ResumeIQ — AI Resume Analyzer & Job Match Platform" },
      {
        property: "og:description",
        content:
          "ATS scoring, job-description matching, and AI recommendations for your resume in one place.",
      },
    ],
  }),
  component: LandingPage,
});

const features = [
  {
    icon: ShieldCheck,
    title: "ATS Scoring Engine",
    description:
      "Your resume is parsed the way applicant tracking systems parse it — formatting, sections, keywords and readability all scored against real screening criteria.",
  },
  {
    icon: Target,
    title: "Job Match Analysis",
    description:
      "Paste any job description and see a match percentage, the skills you already prove, and the requirements your resume never mentions.",
  },
  {
    icon: BrainCircuit,
    title: "AI Recommendations",
    description:
      "Specific, line-level suggestions — stronger action verbs, missing metrics, and the keywords worth adding for the role you actually want.",
  },
];

const steps = [
  {
    icon: FileUp,
    title: "Upload your resume",
    description: "Drop in a PDF or DOCX. Parsing and section detection happen in seconds.",
  },
  {
    icon: BarChart3,
    title: "Get your ATS score",
    description: "A breakdown by category shows exactly where screening filters drop you.",
  },
  {
    icon: Sparkles,
    title: "Match and improve",
    description: "Compare against a job description and apply the recommendations that matter.",
  },
];

const techStack = ["React", "TypeScript", "Tailwind CSS", "FastAPI", "MongoDB", "JWT Auth"];

function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />

      <main className="flex-1">
        <section className="border-b border-border">
          <div className="mx-auto max-w-6xl px-5 py-20 md:py-28">
            <div className="max-w-3xl">
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground">
                <Sparkles className="size-3.5" /> ATS scoring · Job matching · AI feedback
              </span>
              <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl md:text-6xl">
                Know how your resume scores{" "}
                <span className="text-primary">before a recruiter sees it.</span>
              </h1>
              <p className="mt-6 max-w-2xl text-lg text-muted-foreground">
                ResumeIQ analyzes your resume against applicant tracking criteria, matches it to the
                jobs you are targeting, and tells you precisely what to change.
              </p>
              <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                <Button size="lg" asChild>
                  <Link to="/register">
                    Analyze My Resume <ArrowRight className="size-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <a href="#how-it-works">See how it works</a>
                </Button>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">
                Free to start · No credit card required
              </p>
            </div>
          </div>
        </section>

        <section className="border-b border-border">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">
              Everything you need to pass the first filter
            </h2>
            <p className="mt-3 max-w-2xl text-muted-foreground">
              Three analysis layers, one report — built for candidates who apply seriously.
            </p>
            <div className="mt-10 grid gap-6 md:grid-cols-3">
              {features.map((feature) => (
                <Card key={feature.title} className="border-border shadow-none">
                  <CardHeader>
                    <span className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <feature.icon className="size-5" />
                    </span>
                    <CardTitle className="pt-3 text-lg">{feature.title}</CardTitle>
                    <CardDescription className="leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section id="how-it-works" className="border-b border-border bg-muted/30">
          <div className="mx-auto max-w-6xl px-5 py-20">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">How it works</h2>
            <div className="mt-10 grid gap-6 md:grid-cols-3">
              {steps.map((step, index) => (
                <Card key={step.title} className="border-border bg-background shadow-none">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <span className="flex size-10 items-center justify-center rounded-lg border border-border bg-muted/50 text-foreground">
                        <step.icon className="size-5" />
                      </span>
                      <span className="font-mono text-sm text-muted-foreground">
                        0{index + 1}
                      </span>
                    </div>
                    <h3 className="mt-4 font-semibold text-foreground">{step.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                      {step.description}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section className="border-b border-border">
          <div className="mx-auto flex max-w-6xl flex-col gap-5 px-5 py-12 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm font-medium text-muted-foreground">Built with</p>
            <ul className="flex flex-wrap gap-x-8 gap-y-3">
              {techStack.map((tech) => (
                <li key={tech} className="font-mono text-sm text-foreground/80">
                  {tech}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section>
          <div className="mx-auto max-w-6xl px-5 py-20 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">
              Ready to score your resume?
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-muted-foreground">
              Create an account and run your first analysis in under a minute.
            </p>
            <Button size="lg" className="mt-8" asChild>
              <Link to="/register">
                Analyze My Resume <ArrowRight className="size-4" />
              </Link>
            </Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

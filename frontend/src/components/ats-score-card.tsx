import { Progress } from "@/components/ui/progress";
import { ATS_SCORE_BREAKDOWN, type ATSScoreResult } from "@/lib/resume";

function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-600 dark:text-emerald-400";
  if (score >= 60) return "text-amber-600 dark:text-amber-400";
  return "text-red-600 dark:text-red-400";
}

function ringColor(score: number): string {
  if (score >= 80) return "stroke-emerald-500";
  if (score >= 60) return "stroke-amber-500";
  return "stroke-red-500";
}

function ScoreRing({ score }: { score: number }) {
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="relative flex size-28 items-center justify-center">
      <svg viewBox="0 0 100 100" className="size-28 -rotate-90">
        <circle cx="50" cy="50" r={radius} className="stroke-muted" strokeWidth="8" fill="none" />
        <circle
          cx="50"
          cy="50"
          r={radius}
          className={`${ringColor(score)} transition-all duration-500`}
          strokeWidth="8"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className={`absolute font-mono text-2xl font-bold ${scoreColor(score)}`}>{score}</span>
    </div>
  );
}

export function AtsScoreCard({ result }: { result: ATSScoreResult }) {
  return (
    <div className="rounded-lg border border-border bg-muted/20 p-4">
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
        <div className="flex flex-col items-center gap-1">
          <ScoreRing score={result.overall_score} />
          <p className="text-xs font-medium text-muted-foreground">ATS Score</p>
        </div>

        <div className="w-full flex-1 space-y-3">
          {ATS_SCORE_BREAKDOWN.map(({ key, label, weight }) => {
            const value = result[key] as number;
            return (
              <div key={key}>
                <div className="mb-1 flex items-baseline justify-between text-xs">
                  <span className="text-foreground/80">
                    {label} <span className="text-muted-foreground">({weight})</span>
                  </span>
                  <span className={`font-mono font-medium ${scoreColor(value)}`}>{value}</span>
                </div>
                <Progress value={value} className="h-1.5" />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

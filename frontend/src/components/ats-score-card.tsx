import { ScoreRing, scoreColor } from "@/components/score-ring";
import { Progress } from "@/components/ui/progress";
import { ATS_SCORE_BREAKDOWN, type ATSScoreResult } from "@/lib/resume";

export function AtsScoreCard({ result }: { result: ATSScoreResult }) {
  return (
    <div className="rounded-lg border border-border bg-muted/20 p-4">
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
        <ScoreRing score={result.overall_score} label="ATS Score" />

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

import { useState } from "react";
import { ArrowRight, RotateCcw, Wand2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { improveBullet, type ImproveBulletResult } from "@/lib/bullet";

const MAX_BULLET_LENGTH = 500;

export function BulletImproverCard({ resumeText }: { resumeText: string }) {
  const [bulletText, setBulletText] = useState("");
  const [result, setResult] = useState<ImproveBulletResult | null>(null);
  const [isImproving, setIsImproving] = useState(false);

  async function handleImprove() {
    const trimmed = bulletText.trim();
    if (!trimmed) {
      toast.error("Paste a bullet point first", {
        description: "Enter a single resume bullet to improve.",
      });
      return;
    }
    if (trimmed.length > MAX_BULLET_LENGTH) {
      toast.error("Bullet is too long", {
        description: `Keep it under ${MAX_BULLET_LENGTH} characters — one bullet at a time.`,
      });
      return;
    }

    setIsImproving(true);
    try {
      // Use the uploaded resume as grounding context when available, so the AI can
      // pull in real specifics (tech stack, project names) already in the resume
      // instead of inventing anything.
      const improved = await improveBullet(trimmed, resumeText || undefined);
      setResult(improved);
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Unexpected error. Please try again.";
      toast.error("Couldn't improve this bullet", { description: message });
    } finally {
      setIsImproving(false);
    }
  }

  function reset() {
    setResult(null);
    setBulletText("");
  }

  return (
    <Card className="border-border shadow-none">
      <CardHeader>
        <CardTitle>Improve a bullet point</CardTitle>
        <CardDescription>
          {result
            ? "Preserves your original facts — nothing is invented."
            : "Paste one resume bullet and get a stronger rewrite with clear reasoning."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {result ? (
          <div className="space-y-4">
            <div className="space-y-3">
              <div className="rounded-lg border border-border bg-muted/20 p-3">
                <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Before
                </p>
                <p className="text-sm text-foreground/80">{result.original}</p>
              </div>
              <div className="flex justify-center text-muted-foreground">
                <ArrowRight className="size-4" />
              </div>
              <div className="rounded-lg border border-primary/30 bg-primary/5 p-3">
                <p className="mb-1 text-xs font-medium uppercase tracking-wide text-primary">
                  After
                </p>
                <p className="text-sm text-foreground">{result.improved}</p>
              </div>
            </div>

            {result.why_better.length > 0 && (
              <div>
                <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Why this is better
                </p>
                <ul className="list-inside list-disc space-y-1 text-sm text-foreground/80">
                  {result.why_better.map((reason, i) => (
                    <li key={i}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            <Button variant="outline" size="sm" onClick={reset}>
              <RotateCcw className="size-4" /> Improve another bullet
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <Textarea
              value={bulletText}
              onChange={(event) => setBulletText(event.target.value)}
              placeholder="e.g. Created an e-commerce website using React."
              className="min-h-24 resize-y"
              maxLength={MAX_BULLET_LENGTH}
            />
            <p className="text-right text-xs text-muted-foreground">
              {bulletText.length}/{MAX_BULLET_LENGTH}
            </p>
            <Button onClick={() => void handleImprove()} disabled={isImproving} className="w-full">
              <Wand2 className="size-4" />
              {isImproving ? "Improving…" : "Improve with AI"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

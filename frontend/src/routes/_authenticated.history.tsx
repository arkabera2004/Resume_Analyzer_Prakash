import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { Download, Eye, GitCompareArrows, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ApiError } from "@/lib/api";
import {
  compareAnalyses,
  deleteAnalysis,
  downloadAnalysisReport,
  getAnalysis,
  getAnalysisHistory,
  type AnalysisDetail,
  type CompareResult,
} from "@/lib/analysis";

export const Route = createFileRoute("/_authenticated/history")({
  head: () => ({
    meta: [
      { title: "Analysis History — ResumeIQ" },
      { name: "description", content: "Browse, compare, and manage your saved resume analyses." },
    ],
  }),
  component: HistoryPage,
});

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function ScoreChange({ value }: { value: number | null }) {
  if (value === null) return <span className="text-muted-foreground">—</span>;
  if (value === 0) return <span className="text-muted-foreground">No change</span>;
  const color = value > 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400";
  return (
    <span className={`font-mono font-medium ${color}`}>
      {value > 0 ? "+" : ""}
      {value}
    </span>
  );
}

function DiffList({ title, items, variant }: { title: string; items: string[]; variant: "positive" | "negative" }) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">{title}</p>
      {items.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {items.map((item) => (
            <Badge
              key={item}
              variant="outline"
              className={
                variant === "positive"
                  ? "border-emerald-500/40 bg-emerald-500/10 font-normal text-emerald-700 dark:text-emerald-400"
                  : "border-red-500/40 bg-red-500/10 font-normal text-red-700 dark:text-red-400"
              }
            >
              {item}
            </Badge>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">None.</p>
      )}
    </div>
  );
}

function AnalysisDetailView({ analysis }: { analysis: AnalysisDetail }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
        <div>
          <p className="text-xs text-muted-foreground">ATS Score</p>
          <p className="font-mono text-lg font-semibold">{analysis.ats_score ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Job Match</p>
          <p className="font-mono text-lg font-semibold">
            {analysis.match_score !== null ? `${analysis.match_score}%` : "—"}
          </p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Saved</p>
          <p className="text-sm">{formatDate(analysis.created_at)}</p>
        </div>
      </div>

      {analysis.strengths.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Strengths
          </p>
          <ul className="list-inside list-disc space-y-1 text-sm text-foreground/80">
            {analysis.strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.weaknesses.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Weaknesses
          </p>
          <ul className="list-inside list-disc space-y-1 text-sm text-foreground/80">
            {analysis.weaknesses.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {(analysis.matching_skills.length > 0 || analysis.missing_skills.length > 0) && (
        <div className="grid gap-4 sm:grid-cols-2">
          <DiffList title="Matching skills" items={analysis.matching_skills} variant="positive" />
          <DiffList title="Missing skills" items={analysis.missing_skills} variant="negative" />
        </div>
      )}
    </div>
  );
}

function HistoryPage() {
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<string[]>([]);
  const [viewingId, setViewingId] = useState<string | null>(null);
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const historyQuery = useQuery({
    queryKey: ["analysis", "history"],
    queryFn: getAnalysisHistory,
  });

  const detailQuery = useQuery({
    queryKey: ["analysis", viewingId],
    queryFn: () => getAnalysis(viewingId as string),
    enabled: viewingId !== null,
  });

  function toggleSelected(id: string) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((existing) => existing !== id) : [...prev, id].slice(-2),
    );
  }

  async function handleDelete(id: string) {
    try {
      await deleteAnalysis(id);
      toast.success("Analysis deleted");
      setSelected((prev) => prev.filter((existing) => existing !== id));
      await queryClient.invalidateQueries({ queryKey: ["analysis", "history"] });
      await queryClient.invalidateQueries({ queryKey: ["dashboard", "stats"] });
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Unexpected error.";
      toast.error("Couldn't delete analysis", { description: message });
    }
  }

  async function handleDownload(id: string, resumeName: string) {
    setDownloadingId(id);
    try {
      await downloadAnalysisReport(id, resumeName);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Unexpected error.";
      toast.error("Couldn't download report", { description: message });
    } finally {
      setDownloadingId(null);
    }
  }

  async function handleCompare() {
    const [idA, idB] = selected;
    if (!idA || !idB) return;
    setIsComparing(true);
    try {
      const result = await compareAnalyses(idA, idB);
      setCompareResult(result);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Unexpected error.";
      toast.error("Couldn't compare analyses", { description: message });
    } finally {
      setIsComparing(false);
    }
  }

  const analyses = historyQuery.data ?? [];

  return (
    <div className="mx-auto w-full max-w-5xl px-5 py-12">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Analysis History</h1>
          <p className="mt-2 text-muted-foreground">
            All your saved analyses. Select two to compare.
          </p>
        </div>
        <Button onClick={() => void handleCompare()} disabled={selected.length !== 2 || isComparing}>
          <GitCompareArrows className="size-4" />
          {isComparing ? "Comparing…" : `Compare Selected (${selected.length}/2)`}
        </Button>
      </div>

      <div className="mt-8 overflow-x-auto rounded-lg border border-border">
        {historyQuery.isPending ? (
          <div className="space-y-2 p-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : analyses.length === 0 ? (
          <div className="px-4 py-16 text-center">
            <p className="text-sm text-muted-foreground">
              No saved analyses yet. Run one from the dashboard and save it.
            </p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-10" />
                <TableHead>Resume</TableHead>
                <TableHead>Job Title</TableHead>
                <TableHead>ATS Score</TableHead>
                <TableHead>Job Match</TableHead>
                <TableHead>Saved</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {analyses.map((analysis) => (
                <TableRow key={analysis.id}>
                  <TableCell>
                    <Checkbox
                      checked={selected.includes(analysis.id)}
                      onCheckedChange={() => toggleSelected(analysis.id)}
                      aria-label={`Select ${analysis.resume_name}`}
                    />
                  </TableCell>
                  <TableCell className="max-w-40 truncate font-medium">
                    {analysis.resume_name}
                  </TableCell>
                  <TableCell className="max-w-40 truncate text-muted-foreground">
                    {analysis.job_title ?? "—"}
                  </TableCell>
                  <TableCell className="font-mono">{analysis.ats_score ?? "—"}</TableCell>
                  <TableCell className="font-mono">
                    {analysis.match_score !== null ? `${analysis.match_score}%` : "—"}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDate(analysis.created_at)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-8"
                      onClick={() => setViewingId(analysis.id)}
                      aria-label="View analysis"
                    >
                      <Eye className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-8"
                      onClick={() => void handleDownload(analysis.id, analysis.resume_name)}
                      disabled={downloadingId === analysis.id}
                      aria-label="Download report"
                    >
                      <Download className="size-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-8 text-muted-foreground hover:text-destructive"
                      onClick={() => void handleDelete(analysis.id)}
                      aria-label="Delete analysis"
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      {/* View analysis dialog */}
      <Dialog open={viewingId !== null} onOpenChange={(open) => !open && setViewingId(null)}>
        <DialogContent className="max-h-[85vh] max-w-lg overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{detailQuery.data?.resume_name ?? "Analysis"}</DialogTitle>
            <DialogDescription>Full detail for this saved analysis.</DialogDescription>
          </DialogHeader>
          {detailQuery.isPending ? (
            <Skeleton className="h-40 w-full" />
          ) : detailQuery.data ? (
            <>
              <AnalysisDetailView analysis={detailQuery.data} />
              <Button
                variant="outline"
                size="sm"
                onClick={() => void handleDownload(detailQuery.data.id, detailQuery.data.resume_name)}
                disabled={downloadingId === detailQuery.data.id}
              >
                <Download className="size-4" />
                {downloadingId === detailQuery.data.id ? "Downloading…" : "Download Report"}
              </Button>
            </>
          ) : null}
        </DialogContent>
      </Dialog>

      {/* Compare dialog */}
      <Dialog open={compareResult !== null} onOpenChange={(open) => !open && setCompareResult(null)}>
        <DialogContent className="max-h-[85vh] max-w-lg overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Comparison</DialogTitle>
            <DialogDescription>
              {compareResult
                ? `${compareResult.analysis_a.resume_name} → ${compareResult.analysis_b.resume_name}`
                : ""}
            </DialogDescription>
          </DialogHeader>
          {compareResult && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-xs text-muted-foreground">ATS Score Change</p>
                  <ScoreChange value={compareResult.ats_score_change} />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Job Match Change</p>
                  <ScoreChange value={compareResult.match_score_change} />
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <DiffList title="New skills" items={compareResult.new_skills} variant="positive" />
                <DiffList title="Removed skills" items={compareResult.removed_skills} variant="negative" />
                <DiffList title="New keywords" items={compareResult.new_keywords} variant="positive" />
                <DiffList
                  title="Removed keywords"
                  items={compareResult.removed_keywords}
                  variant="negative"
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <DiffList
                  title="Improved sections"
                  items={compareResult.improved_sections}
                  variant="positive"
                />
                <DiffList
                  title="Regressed sections"
                  items={compareResult.regressed_sections}
                  variant="negative"
                />
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

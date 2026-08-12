import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { AnalysisSummary } from "@/lib/analysis";

export function ScoreTrendChart({ analyses }: { analyses: AnalysisSummary[] }) {
  // Chart oldest -> newest (left to right), matching how a trend is normally read.
  const data = [...analyses].reverse().map((a) => ({
    name: a.resume_name.length > 14 ? `${a.resume_name.slice(0, 12)}…` : a.resume_name,
    "ATS Score": a.ats_score ?? 0,
    "Job Match": a.match_score ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="currentColor" className="text-muted-foreground" />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="currentColor" className="text-muted-foreground" />
        <Tooltip
          contentStyle={{
            fontSize: 12,
            borderRadius: 8,
            border: "1px solid var(--border)",
            background: "var(--popover)",
            color: "var(--popover-foreground)",
          }}
        />
        <Bar dataKey="ATS Score" fill="var(--primary)" radius={[4, 4, 0, 0]} />
        <Bar dataKey="Job Match" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

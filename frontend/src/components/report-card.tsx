"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Target } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { InvestmentReport } from "@/lib/types";

interface ReportCardProps {
  data: InvestmentReport;
  currency?: string;
}

const REC_STYLES: Record<string, string> = {
  "Strong Buy": "text-emerald-300 bg-emerald-400/15 hover:bg-emerald-400/15 border-emerald-400/20",
  Buy: "text-emerald-400 bg-emerald-400/10 hover:bg-emerald-400/10",
  Hold: "text-amber-400 bg-amber-400/10 hover:bg-amber-400/10",
  Sell: "text-red-400 bg-red-400/10 hover:bg-red-400/10",
  "Strong Sell": "text-red-300 bg-red-400/15 hover:bg-red-400/15 border-red-400/20",
};

export function ReportCard({ data, currency = "USD" }: ReportCardProps) {
  const pct = Math.round(data.confidence_score * 100);
  const recStyle = REC_STYLES[data.recommendation] || REC_STYLES["Hold"];
  const sym = currency === "INR" ? "₹" : "$";
  const hasTarget = data.target_price !== null && data.target_price > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <Card className="border-primary/20 bg-card/50 backdrop-blur-sm">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">
                Investment Report
              </h3>
              <p className="text-lg font-bold mt-0.5">
                {data.company_name} ({data.ticker})
              </p>
            </div>
            <div className="flex flex-col items-end gap-2">
              <Badge variant="secondary" className={`text-sm px-3 py-1 ${recStyle}`}>
                {data.recommendation}
              </Badge>
              <div className="flex items-center gap-2">
                <div className="w-20 h-1.5 rounded-full bg-muted overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
                    className="h-full rounded-full bg-primary"
                  />
                </div>
                <span className="text-xs font-mono text-muted-foreground">
                  {pct}%
                </span>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          {hasTarget && (
            <div className="flex items-center gap-4 p-3 rounded-lg bg-background/50 border border-border/30">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-primary" />
                <span className="text-xs text-muted-foreground">12M Target</span>
              </div>
              <span className="text-xl font-bold font-mono">
                {sym}{data.target_price!.toLocaleString(currency === "INR" ? "en-IN" : "en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              {data.target_upside !== null && (
                <span className={`flex items-center gap-0.5 text-sm font-mono font-semibold ${data.target_upside >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {data.target_upside >= 0 ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                  {data.target_upside >= 0 ? "+" : ""}{data.target_upside.toFixed(1)}%
                </span>
              )}
              {data.target_methodology && (
                <span className="text-[10px] text-muted-foreground/60 ml-auto hidden sm:block max-w-48 line-clamp-2">
                  {data.target_methodology}
                </span>
              )}
            </div>
          )}

          <p className="text-sm leading-relaxed text-muted-foreground">
            {data.summary}
          </p>

          <div className="grid gap-4 sm:grid-cols-3">
            {data.strengths.length > 0 && (
              <Section title="Strengths" color="emerald" items={data.strengths} />
            )}
            {data.weaknesses.length > 0 && (
              <Section title="Weaknesses" color="amber" items={data.weaknesses} />
            )}
            {data.risks.length > 0 && (
              <Section title="Risks" color="red" items={data.risks} />
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function Section({
  title,
  color,
  items,
}: {
  title: string;
  color: "emerald" | "amber" | "red";
  items: string[];
}) {
  const titleColor =
    color === "emerald"
      ? "text-emerald-400"
      : color === "amber"
        ? "text-amber-400"
        : "text-red-400";

  const dotColor =
    color === "emerald"
      ? "bg-emerald-400/60"
      : color === "amber"
        ? "bg-amber-400/60"
        : "bg-red-400/60";

  return (
    <div>
      <p className={`text-xs font-medium ${titleColor} mb-2`}>{title}</p>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2 text-xs text-muted-foreground leading-relaxed">
            <span className={`mt-1.5 h-1 w-1 shrink-0 rounded-full ${dotColor}`} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

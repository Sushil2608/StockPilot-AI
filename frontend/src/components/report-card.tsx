"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import type { InvestmentReport } from "@/lib/types";

interface ReportCardProps {
  data: InvestmentReport;
}

const RECOMMENDATION_COLORS: Record<string, string> = {
  "Strong Buy": "bg-green-600 hover:bg-green-600 text-white",
  Buy: "bg-green-100 text-green-800 hover:bg-green-100",
  Hold: "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
  Sell: "bg-red-100 text-red-800 hover:bg-red-100",
  "Strong Sell": "bg-red-600 hover:bg-red-600 text-white",
};

export function ReportCard({ data }: ReportCardProps) {
  const confidencePercent = Math.round(data.confidence_score * 100);
  const colorClass =
    RECOMMENDATION_COLORS[data.recommendation] ||
    RECOMMENDATION_COLORS["Hold"];

  return (
    <Card className="border-2 border-primary/20">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Investment Report</span>
          <Badge className={`text-sm px-3 py-1 ${colorClass}`}>
            {data.recommendation}
          </Badge>
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          {data.company_name} ({data.ticker})
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium">Confidence Score</span>
            <span className="text-sm font-bold">{confidencePercent}%</span>
          </div>
          <Progress value={confidencePercent} className="h-3" />
        </div>

        <Separator />

        <div>
          <h4 className="mb-2 font-semibold">Summary</h4>
          <p className="text-sm leading-relaxed text-muted-foreground">
            {data.summary}
          </p>
        </div>

        {data.strengths.length > 0 && (
          <div>
            <h4 className="mb-2 font-semibold text-green-600">Strengths</h4>
            <ul className="space-y-1">
              {data.strengths.map((item, i) => (
                <li key={i} className="flex gap-2 text-sm text-muted-foreground">
                  <span className="text-green-500 shrink-0">+</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {data.weaknesses.length > 0 && (
          <div>
            <h4 className="mb-2 font-semibold text-amber-600">Weaknesses</h4>
            <ul className="space-y-1">
              {data.weaknesses.map((item, i) => (
                <li key={i} className="flex gap-2 text-sm text-muted-foreground">
                  <span className="text-amber-500 shrink-0">!</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {data.risks.length > 0 && (
          <div>
            <h4 className="mb-2 font-semibold text-red-600">Risks</h4>
            <ul className="space-y-1">
              {data.risks.map((item, i) => (
                <li key={i} className="flex gap-2 text-sm text-muted-foreground">
                  <span className="text-red-500 shrink-0">-</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

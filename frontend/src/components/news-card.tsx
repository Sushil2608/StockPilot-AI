"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { NewsAnalysis } from "@/lib/types";

interface NewsCardProps {
  data: NewsAnalysis;
}

const SENTIMENT_CONFIG = {
  bullish: {
    icon: <TrendingUp className="h-4 w-4" />,
    variant: "default" as const,
    className: "bg-green-100 text-green-800 hover:bg-green-100",
  },
  bearish: {
    icon: <TrendingDown className="h-4 w-4" />,
    variant: "destructive" as const,
    className: "",
  },
  neutral: {
    icon: <Minus className="h-4 w-4" />,
    variant: "secondary" as const,
    className: "",
  },
};

export function NewsCard({ data }: NewsCardProps) {
  const sentiment = data.overall_sentiment.toLowerCase();
  const config =
    SENTIMENT_CONFIG[sentiment as keyof typeof SENTIMENT_CONFIG] ||
    SENTIMENT_CONFIG.neutral;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>News Sentiment</span>
          <Badge variant={config.variant} className={config.className}>
            {config.icon}
            <span className="ml-1 capitalize">{data.overall_sentiment}</span>
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {data.positive_developments.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-semibold text-green-600">
              Positive Developments
            </h4>
            <ul className="space-y-1">
              {data.positive_developments.map((item, i) => (
                <li key={i} className="text-sm text-muted-foreground flex gap-2">
                  <span className="text-green-500 shrink-0">+</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
        {data.negative_developments.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-semibold text-red-600">
              Negative Developments
            </h4>
            <ul className="space-y-1">
              {data.negative_developments.map((item, i) => (
                <li key={i} className="text-sm text-muted-foreground flex gap-2">
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

"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { NewsAnalysis } from "@/lib/types";

interface NewsCardProps {
  data: NewsAnalysis;
}

const SENTIMENT_CONFIG = {
  bullish: {
    icon: <TrendingUp className="h-3.5 w-3.5" />,
    className: "text-emerald-400 bg-emerald-400/10 hover:bg-emerald-400/10",
  },
  bearish: {
    icon: <TrendingDown className="h-3.5 w-3.5" />,
    className: "text-red-400 bg-red-400/10 hover:bg-red-400/10",
  },
  neutral: {
    icon: <Minus className="h-3.5 w-3.5" />,
    className: "text-muted-foreground bg-muted hover:bg-muted",
  },
};

export function NewsCard({ data }: NewsCardProps) {
  const sentiment = data.overall_sentiment.toLowerCase();
  const config =
    SENTIMENT_CONFIG[sentiment as keyof typeof SENTIMENT_CONFIG] ||
    SENTIMENT_CONFIG.neutral;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm h-full flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-muted-foreground">
              News Sentiment
            </h3>
            <Badge variant="secondary" className={`text-xs ${config.className}`}>
              {config.icon}
              <span className="ml-1 capitalize">{data.overall_sentiment}</span>
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4 flex-1">
          {data.positive_developments.length > 0 && (
            <div>
              <p className="text-xs font-medium text-emerald-400 mb-2">Positive</p>
              <ul className="space-y-1.5">
                {data.positive_developments.map((item, i) => (
                  <li key={i} className="text-xs text-muted-foreground leading-relaxed flex gap-2">
                    <span className="text-emerald-400/60 shrink-0 mt-0.5">+</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {data.negative_developments.length > 0 && (
            <div>
              <p className="text-xs font-medium text-red-400 mb-2">Negative</p>
              <ul className="space-y-1.5">
                {data.negative_developments.map((item, i) => (
                  <li key={i} className="text-xs text-muted-foreground leading-relaxed flex gap-2">
                    <span className="text-red-400/60 shrink-0 mt-0.5">−</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {data.evidence.length > 0 && (
            <div className="pt-2 border-t border-border/30">
              <p className="text-[10px] font-medium text-muted-foreground mb-2 uppercase tracking-wider">
                Sources
              </p>
              <ul className="space-y-1">
                {data.evidence.slice(0, 5).map((item, i) => (
                  <li key={i}>
                    {item.url ? (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[11px] text-muted-foreground hover:text-foreground transition-colors flex items-start gap-1 group"
                      >
                        <ExternalLink className="h-3 w-3 mt-0.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                        <span className="line-clamp-1">{item.title}</span>
                      </a>
                    ) : (
                      <span className="text-[11px] text-muted-foreground line-clamp-1">
                        {item.title}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

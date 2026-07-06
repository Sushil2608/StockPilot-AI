"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { TechnicalIndicators } from "@/lib/types";
import { formatNumber } from "@/lib/format";

interface TechnicalCardProps {
  data: TechnicalIndicators;
}

function Indicator({
  label,
  value,
  signal,
}: {
  label: string;
  value: string;
  signal?: string;
}) {
  return (
    <div>
      <p className="text-xs text-muted-foreground mb-0.5">{label}</p>
      <p className="text-sm font-semibold font-mono">{value}</p>
      {signal && (
        <p
          className={`text-[10px] mt-0.5 ${
            signal === "Overbought" || signal === "Bearish" || signal === "High volume"
              ? "text-red-400"
              : signal === "Oversold" || signal === "Bullish"
                ? "text-emerald-400"
                : "text-muted-foreground"
          }`}
        >
          {signal}
        </p>
      )}
    </div>
  );
}

function formatVolume(v: number | null): string {
  if (v === null) return "—";
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)}K`;
  return v.toFixed(0);
}

export function TechnicalCard({ data }: TechnicalCardProps) {
  const trendClass =
    data.trend === "bullish"
      ? "text-emerald-400 bg-emerald-400/10 hover:bg-emerald-400/10"
      : data.trend === "bearish"
        ? "text-red-400 bg-red-400/10 hover:bg-red-400/10"
        : "text-muted-foreground bg-muted hover:bg-muted";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.25 }}
    >
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-muted-foreground">
              Technical Analysis
            </h3>
            <Badge variant="secondary" className={`text-xs ${trendClass}`}>
              <span className="capitalize">{data.trend}</span>
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-3 rounded-lg bg-background/50 border border-border/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-muted-foreground">Technical Score</span>
              <span className="text-lg font-bold font-mono">{data.technical_score}/100</span>
            </div>
            <div className="w-full h-2 rounded-full bg-border/30 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${data.technical_score}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className={`h-full rounded-full ${
                  data.technical_score >= 65
                    ? "bg-emerald-400"
                    : data.technical_score >= 40
                      ? "bg-amber-400"
                      : "bg-red-400"
                }`}
              />
            </div>
            <div className="flex justify-between mt-1.5 text-[10px] text-muted-foreground/60">
              <span>Strong Sell</span>
              <span>Neutral</span>
              <span>Strong Buy</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-x-4 gap-y-3">
            <Indicator
              label="RSI (14)"
              value={formatNumber(data.rsi)}
              signal={rsiSignal(data.rsi)}
            />
            <Indicator
              label="MACD"
              value={formatNumber(data.macd, 4)}
              signal={macdSignal(data.macd, data.macd_signal)}
            />
            <Indicator label="ATR" value={formatNumber(data.atr)} />
          </div>

          <div className="h-px bg-border/30" />

          <div className="grid grid-cols-3 gap-x-4 gap-y-3">
            <Indicator
              label="EMA 20"
              value={data.ema_20 !== null ? `$${formatNumber(data.ema_20)}` : "—"}
            />
            <Indicator
              label="SMA 50"
              value={data.sma_50 !== null ? `$${formatNumber(data.sma_50)}` : "—"}
            />
            <Indicator
              label="SMA 200"
              value={data.sma_200 !== null ? `$${formatNumber(data.sma_200)}` : "—"}
            />
          </div>

          <div className="h-px bg-border/30" />

          <div className="grid grid-cols-3 gap-x-4 gap-y-3">
            <Indicator
              label="BB Upper"
              value={data.bollinger_upper !== null ? `$${formatNumber(data.bollinger_upper)}` : "—"}
            />
            <Indicator
              label="BB Mid"
              value={data.bollinger_middle !== null ? `$${formatNumber(data.bollinger_middle)}` : "—"}
            />
            <Indicator
              label="BB Lower"
              value={data.bollinger_lower !== null ? `$${formatNumber(data.bollinger_lower)}` : "—"}
            />
          </div>

          <div className="h-px bg-border/30" />

          <div className="grid grid-cols-2 gap-x-4">
            <Indicator label="Volume" value={formatVolume(data.volume_current)} />
            <Indicator
              label="Avg Vol (20d)"
              value={formatVolume(data.volume_avg)}
              signal={volumeSignal(data.volume_current, data.volume_avg)}
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function rsiSignal(rsi: number | null): string | undefined {
  if (rsi === null) return undefined;
  if (rsi > 70) return "Overbought";
  if (rsi < 30) return "Oversold";
  return "Neutral";
}

function macdSignal(macd: number | null, signal: number | null): string | undefined {
  if (macd === null || signal === null) return undefined;
  return macd > signal ? "Bullish" : "Bearish";
}

function volumeSignal(current: number | null, avg: number | null): string | undefined {
  if (current === null || avg === null || avg === 0) return undefined;
  const ratio = current / avg;
  if (ratio > 1.5) return "High volume";
  if (ratio < 0.5) return "Low volume";
  return "Normal";
}

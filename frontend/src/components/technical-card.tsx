"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { IndicatorInfo } from "@/components/indicator-info";
import type { TechnicalIndicators } from "@/lib/types";
import { formatNumber } from "@/lib/format";

interface TechnicalCardProps {
  data: TechnicalIndicators;
  currency: string;
}

function Indicator({
  label,
  value,
  signal,
  description,
}: {
  label: string;
  value: string;
  signal?: string;
  description: string;
}) {
  return (
    <div className="min-w-0">
      <IndicatorInfo label={label} description={description} />
      <p className="break-words text-sm font-semibold font-mono">{value}</p>
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

export function TechnicalCard({ data, currency }: TechnicalCardProps) {
  const currencySymbol = currency === "INR" ? "₹" : "$";
  const trendClass =
    data.trend === "bullish"
      ? "text-emerald-400 bg-emerald-400/10 hover:bg-emerald-400/10"
      : data.trend === "bearish"
        ? "text-red-400 bg-red-400/10 hover:bg-red-400/10"
        : "text-muted-foreground bg-muted hover:bg-muted";

  return (
    <motion.div
      layout
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
            <IndicatorInfo
              label={
                <Badge variant="secondary" className={`text-xs ${trendClass}`}>
                  <span className="capitalize">{data.trend}</span>
                </Badge>
              }
              description="This trend label comes from the combined technical score: scores of 65 or higher are bullish, 35 or lower are bearish, and scores in between are neutral. It summarizes these indicators and is not a forecast."
            />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-3 rounded-lg bg-background/50 border border-border/30">
            <div className="flex items-center justify-between mb-2">
              <IndicatorInfo
                label="Technical Score"
                description="A 0–100 score combining RSI, MACD, moving averages, Bollinger Bands, and trading volume. Higher scores reflect more bullish signals in this scoring model; the score is not a price target or a guarantee."
              />
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

          <div className="grid grid-cols-3 gap-x-2 gap-y-3 sm:gap-x-4">
            <Indicator
              label="RSI (14)"
              value={formatNumber(data.rsi)}
              signal={rsiSignal(data.rsi)}
              description="The 14-period Relative Strength Index measures recent price momentum on a 0–100 scale. Readings above 70 are often called overbought and below 30 oversold, but either can persist during a strong trend."
            />
            <Indicator
              label="MACD"
              value={formatNumber(data.macd, 4)}
              signal={macdSignal(data.macd, data.macd_signal)}
              description="Moving Average Convergence Divergence compares faster and slower exponential moving averages to track momentum. The displayed MACD line above its signal line is treated as bullish here; MACD can lag because it is based on past prices."
            />
            <Indicator
              label="ATR"
              value={formatNumber(data.atr)}
              description="The 14-period Average True Range estimates typical price movement, including gaps. A larger ATR means greater volatility; it does not indicate whether the price is moving up or down."
            />
          </div>

          <div className="h-px bg-border/30" />

          <div className="grid grid-cols-3 gap-x-2 gap-y-3 sm:gap-x-4">
            <Indicator
              label="EMA 20"
              value={data.ema_20 !== null ? `${currencySymbol}${formatNumber(data.ema_20)}` : "—"}
              description="The 20-day Exponential Moving Average gives more weight to recent closing prices. Comparing price with this average can show short-term direction, but crossings are not guarantees of future moves."
            />
            <Indicator
              label="SMA 50"
              value={data.sma_50 !== null ? `${currencySymbol}${formatNumber(data.sma_50)}` : "—"}
              description="The 50-day Simple Moving Average is the average closing price over the latest 50 trading days. It is a medium-term trend reference; prices above or below it can change quickly."
            />
            <Indicator
              label="SMA 200"
              value={data.sma_200 !== null ? `${currencySymbol}${formatNumber(data.sma_200)}` : "—"}
              description="The 200-day Simple Moving Average is the average closing price over the latest 200 trading days. It is commonly used as a long-term trend reference, not as a standalone buy or sell signal."
            />
          </div>

          <div className="h-px bg-border/30" />

          <div className="grid grid-cols-3 gap-x-2 gap-y-3 sm:gap-x-4">
            <Indicator
              label="BB Upper"
              value={data.bollinger_upper !== null ? `${currencySymbol}${formatNumber(data.bollinger_upper)}` : "—"}
              description="The upper Bollinger Band is typically two standard deviations above the 20-day average. The bands widen as recent volatility rises; reaching the upper band alone does not mean a reversal is due."
            />
            <Indicator
              label="BB Mid"
              value={data.bollinger_middle !== null ? `${currencySymbol}${formatNumber(data.bollinger_middle)}` : "—"}
              description="The middle Bollinger Band is the 20-day Simple Moving Average. It is the center line for the upper and lower bands and can serve as a short-term trend reference."
            />
            <Indicator
              label="BB Lower"
              value={data.bollinger_lower !== null ? `${currencySymbol}${formatNumber(data.bollinger_lower)}` : "—"}
              description="The lower Bollinger Band is typically two standard deviations below the 20-day average. It reflects the recent price range; touching it does not guarantee a bounce."
            />
          </div>

          <div className="h-px bg-border/30" />

          <div className="grid grid-cols-2 gap-x-4">
            <Indicator
              label="Volume"
              value={formatVolume(data.volume_current)}
              description="The number of shares traded in the latest available session. Comparing it with average volume helps show whether recent price activity has unusually high or low participation."
            />
            <Indicator
              label="Avg Vol (20d)"
              value={formatVolume(data.volume_avg)}
              signal={volumeSignal(data.volume_current, data.volume_avg)}
              description="The average daily number of shares traded over the last 20 sessions. Current volume above this baseline is labeled high in this view when it exceeds 1.5 times the average."
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

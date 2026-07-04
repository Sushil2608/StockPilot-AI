"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { TechnicalIndicators } from "@/lib/types";
import { formatNumber } from "@/lib/format";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

interface TechnicalCardProps {
  data: TechnicalIndicators;
}

export function TechnicalCard({ data }: TechnicalCardProps) {
  const trendVariant =
    data.trend === "bullish"
      ? "default"
      : data.trend === "bearish"
        ? "destructive"
        : "secondary";

  const trendClassName =
    data.trend === "bullish" ? "bg-green-100 text-green-800 hover:bg-green-100" : "";

  const gaugeData = [
    {
      name: "RSI",
      value: data.rsi,
      color: data.rsi !== null && data.rsi > 70 ? "#ef4444" : data.rsi !== null && data.rsi < 30 ? "#22c55e" : "#3b82f6",
    },
  ];

  const indicatorData = [
    { name: "SMA 50", value: data.sma_50 },
    { name: "SMA 200", value: data.sma_200 },
    { name: "Price", value: data.current_price },
  ].filter((d) => d.value !== null);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Technical Analysis</span>
          <Badge variant={trendVariant} className={trendClassName}>
            <span className="capitalize">{data.trend}</span>
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          <IndicatorItem
            label="RSI (14)"
            value={formatNumber(data.rsi)}
            signal={rsiSignal(data.rsi)}
          />
          <IndicatorItem
            label="MACD"
            value={formatNumber(data.macd, 4)}
            signal={macdSignal(data.macd, data.macd_signal)}
          />
          <IndicatorItem
            label="MACD Signal"
            value={formatNumber(data.macd_signal, 4)}
          />
          <IndicatorItem
            label="SMA 50"
            value={data.sma_50 !== null ? `$${formatNumber(data.sma_50)}` : "N/A"}
          />
          <IndicatorItem
            label="SMA 200"
            value={data.sma_200 !== null ? `$${formatNumber(data.sma_200)}` : "N/A"}
          />
          <IndicatorItem
            label="Price"
            value={
              data.current_price !== null
                ? `$${formatNumber(data.current_price)}`
                : "N/A"
            }
          />
        </div>

        {indicatorData.length > 0 && (
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={indicatorData} layout="vertical">
                <XAxis type="number" tickFormatter={(v) => `$${v.toFixed(0)}`} />
                <YAxis type="category" dataKey="name" width={60} />
                <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}`} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {indicatorData.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={entry.name === "Price" ? "#3b82f6" : "#94a3b8"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function IndicatorItem({
  label,
  value,
  signal,
}: {
  label: string;
  value: string;
  signal?: string;
}) {
  return (
    <div className="space-y-1">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="font-semibold">{value}</p>
      {signal && (
        <p
          className={`text-xs ${signal === "Overbought" || signal === "Bearish" ? "text-red-500" : signal === "Oversold" || signal === "Bullish" ? "text-green-500" : "text-muted-foreground"}`}
        >
          {signal}
        </p>
      )}
    </div>
  );
}

function rsiSignal(rsi: number | null): string | undefined {
  if (rsi === null) return undefined;
  if (rsi > 70) return "Overbought";
  if (rsi < 30) return "Oversold";
  return "Neutral";
}

function macdSignal(
  macd: number | null,
  signal: number | null
): string | undefined {
  if (macd === null || signal === null) return undefined;
  return macd > signal ? "Bullish" : "Bearish";
}

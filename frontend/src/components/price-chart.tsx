"use client";

import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { fetchPriceHistory } from "@/lib/api";
import type {
  PricePoint,
  ChartPeriod,
  ChartType,
  MarketType,
} from "@/lib/types";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  ComposedChart,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface PriceChartProps {
  initialData: PricePoint[];
  ticker: string;
  currency?: string;
  market?: MarketType;
}

const PERIODS: { value: ChartPeriod; label: string }[] = [
  { value: "5d", label: "5D" },
  { value: "1mo", label: "1M" },
  { value: "3mo", label: "3M" },
  { value: "6mo", label: "6M" },
  { value: "1y", label: "1Y" },
  { value: "5y", label: "5Y" },
];

const CHART_TYPES: { value: ChartType; label: string }[] = [
  { value: "area", label: "Area" },
  { value: "line", label: "Line" },
  { value: "candle", label: "Candle" },
];

export function PriceChart({
  initialData,
  ticker,
  currency = "USD",
  market = "US",
}: PriceChartProps) {
  const [period, setPeriod] = useState<ChartPeriod>("1mo");
  const [chartType, setChartType] = useState<ChartType>("area");
  const [data, setData] = useState<PricePoint[]>(initialData);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(
    async (p: ChartPeriod) => {
      if (p === "1mo" && initialData.length > 0) {
        setData(initialData);
        return;
      }
      setLoading(true);
      try {
        const res = await fetchPriceHistory(ticker, p, market);
        setData(res.data);
      } catch {
        // keep current data on error
      } finally {
        setLoading(false);
      }
    },
    [ticker, market, initialData]
  );

  useEffect(() => {
    if (period !== "1mo") loadData(period);
  }, [period, loadData]);

  if (data.length === 0) return null;

  const prices = data.map((d) => d.close);
  const first = prices[0];
  const last = prices[prices.length - 1];
  const change = last - first;
  const changePct = ((change / first) * 100).toFixed(2);
  const isPositive = change >= 0;
  const sym = currency === "INR" ? "₹" : "$";
  const strokeColor = isPositive ? "#34d399" : "#f87171";

  const min = Math.min(...data.map((d) => d.low));
  const max = Math.max(...data.map((d) => d.high));
  const padding = (max - min) * 0.05;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader className="pb-2">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-medium text-muted-foreground">
                {ticker}
              </h3>
              <span className="text-lg font-bold font-mono">
                {sym}{last.toFixed(2)}
              </span>
              <span
                className={`text-sm font-mono font-semibold ${isPositive ? "text-emerald-400" : "text-red-400"}`}
              >
                {isPositive ? "+" : ""}{changePct}%
              </span>
              {loading && (
                <span className="text-xs text-muted-foreground animate-pulse">
                  Loading...
                </span>
              )}
            </div>
            <div className="flex gap-1">
              <div className="flex rounded-md border border-border/50 overflow-hidden mr-2">
                {CHART_TYPES.map((ct) => (
                  <button
                    key={ct.value}
                    onClick={() => setChartType(ct.value)}
                    className={`px-2.5 py-1 text-[11px] font-medium transition-colors ${
                      chartType === ct.value
                        ? "bg-primary/20 text-primary"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {ct.label}
                  </button>
                ))}
              </div>
              <div className="flex rounded-md border border-border/50 overflow-hidden">
                {PERIODS.map((p) => (
                  <button
                    key={p.value}
                    onClick={() => setPeriod(p.value)}
                    className={`px-2.5 py-1 text-[11px] font-medium transition-colors ${
                      period === p.value
                        ? "bg-primary/20 text-primary"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === "candle" ? (
                <CandlestickChart
                  data={data}
                  min={min - padding}
                  max={max + padding}
                  sym={sym}
                />
              ) : chartType === "line" ? (
                <LineChart data={data}>
                  <XAxis {...xAxisProps(period)} />
                  <YAxis {...yAxisProps(sym, min - padding, max + padding)} />
                  <Tooltip {...tooltipProps(sym)} />
                  <Line
                    type="monotone"
                    dataKey="close"
                    stroke={strokeColor}
                    strokeWidth={1.5}
                    dot={false}
                  />
                </LineChart>
              ) : (
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={strokeColor} stopOpacity={0.2} />
                      <stop offset="100%" stopColor={strokeColor} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis {...xAxisProps(period)} />
                  <YAxis {...yAxisProps(sym, min - padding, max + padding)} />
                  <Tooltip {...tooltipProps(sym)} />
                  <Area
                    type="monotone"
                    dataKey="close"
                    stroke={strokeColor}
                    strokeWidth={1.5}
                    fill="url(#areaGrad)"
                  />
                </AreaChart>
              )}
            </ResponsiveContainer>
          </div>

          <div className="h-20 mt-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <XAxis dataKey="date" hide />
                <YAxis hide />
                <Tooltip
                  contentStyle={tooltipStyle}
                  formatter={(v) => [Number(v).toLocaleString(), "Volume"]}
                  labelFormatter={() => ""}
                />
                <Bar dataKey="volume" radius={[1, 1, 0, 0]}>
                  {data.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={
                        entry.close >= entry.open
                          ? "rgba(52, 211, 153, 0.3)"
                          : "rgba(248, 113, 113, 0.3)"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

const tooltipStyle = {
  backgroundColor: "rgba(20, 20, 30, 0.95)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: "8px",
  fontSize: "11px",
  padding: "8px 12px",
};

function xAxisProps(period: ChartPeriod) {
  return {
    dataKey: "date",
    tickFormatter: (d: string) =>
      period === "5d" ? d.slice(11, 16) : d.slice(5),
    tick: { fontSize: 10, fill: "#6b7280" },
    axisLine: false,
    tickLine: false,
    interval: "preserveStartEnd" as const,
  };
}

function yAxisProps(sym: string, min: number, max: number) {
  return {
    domain: [min, max] as [number, number],
    tickFormatter: (v: number) => `${sym}${v.toFixed(0)}`,
    tick: { fontSize: 10, fill: "#6b7280" },
    axisLine: false,
    tickLine: false,
    width: 55,
  };
}

function tooltipProps(sym: string) {
  return {
    contentStyle: tooltipStyle,
    formatter: (v: unknown) => [`${sym}${Number(v).toFixed(2)}`, "Close"],
    labelFormatter: (label: unknown) => `${label}`,
  };
}

function CandlestickChart({
  data,
  min,
  max,
  sym,
}: {
  data: PricePoint[];
  min: number;
  max: number;
  sym: string;
}) {
  const candles = data.map((d) => ({
    ...d,
    body: [Math.min(d.open, d.close), Math.max(d.open, d.close)] as [number, number],
    isUp: d.close >= d.open,
  }));

  return (
    <ComposedChart data={candles}>
      <XAxis
        dataKey="date"
        tickFormatter={(d: string) => d.slice(5)}
        tick={{ fontSize: 10, fill: "#6b7280" }}
        axisLine={false}
        tickLine={false}
        interval="preserveStartEnd"
      />
      <YAxis
        domain={[min, max]}
        tickFormatter={(v: number) => `${sym}${v.toFixed(0)}`}
        tick={{ fontSize: 10, fill: "#6b7280" }}
        axisLine={false}
        tickLine={false}
        width={55}
      />
      <Tooltip
        contentStyle={tooltipStyle}
        formatter={(v: unknown, name: unknown) => [
          `${sym}${Number(v).toFixed(2)}`,
          String(name),
        ]}
        labelFormatter={(label) => `${label}`}
      />
      <Bar dataKey="body" radius={[1, 1, 1, 1]} barSize={6}>
        {candles.map((entry, i) => (
          <Cell
            key={i}
            fill={entry.isUp ? "#34d399" : "#f87171"}
          />
        ))}
      </Bar>
      <Line
        type="monotone"
        dataKey="high"
        stroke="rgba(255,255,255,0.15)"
        strokeWidth={0.5}
        dot={false}
      />
      <Line
        type="monotone"
        dataKey="low"
        stroke="rgba(255,255,255,0.15)"
        strokeWidth={0.5}
        dot={false}
      />
    </ComposedChart>
  );
}

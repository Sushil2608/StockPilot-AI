"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { FinancialData } from "@/lib/types";
import { formatCurrency, formatPrice, formatNumber, formatPercent } from "@/lib/format";

interface FinancialCardProps {
  data: FinancialData;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground mb-0.5">{label}</p>
      <p className="text-sm font-semibold font-mono">{value}</p>
    </div>
  );
}

function GrowthBadge({ value }: { value: number | null }) {
  if (value === null) return <span className="text-xs text-muted-foreground">—</span>;
  const pos = value >= 0;
  return (
    <Badge
      variant="secondary"
      className={`text-xs font-mono ${pos ? "text-emerald-400 bg-emerald-400/10 hover:bg-emerald-400/10" : "text-red-400 bg-red-400/10 hover:bg-red-400/10"}`}
    >
      {pos ? "+" : ""}{value.toFixed(1)}%
    </Badge>
  );
}

export function FinancialCard({ data }: FinancialCardProps) {
  const c = data.currency || "USD";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-medium text-muted-foreground">Fundamentals</h3>
              <p className="text-xl font-bold mt-0.5">{data.company_name}</p>
              {data.sector && (
                <p className="text-xs text-muted-foreground mt-0.5">
                  {data.sector} · {data.industry}
                </p>
              )}
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold font-mono">
                {formatPrice(data.current_price, c)}
              </p>
              <div className="mt-1">
                <GrowthBadge value={data.revenue_growth} />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {data.piotroski_score !== null && (
            <div className="mb-4 p-3 rounded-lg bg-background/50 border border-border/30">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-muted-foreground">Piotroski F-Score</span>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold font-mono">{data.piotroski_score}/9</span>
                  <Badge
                    variant="secondary"
                    className={`text-[10px] ${
                      data.fundamental_signal === "strong" || data.fundamental_signal === "healthy"
                        ? "text-emerald-400 bg-emerald-400/10 hover:bg-emerald-400/10"
                        : data.fundamental_signal === "weak" || data.fundamental_signal === "distressed"
                          ? "text-red-400 bg-red-400/10 hover:bg-red-400/10"
                          : "text-muted-foreground"
                    }`}
                  >
                    {data.fundamental_signal}
                  </Badge>
                </div>
              </div>
              <div className="flex gap-0.5">
                {Array.from({ length: 9 }, (_, i) => (
                  <div
                    key={i}
                    className={`h-1.5 flex-1 rounded-full ${
                      i < (data.piotroski_score ?? 0)
                        ? (data.piotroski_score ?? 0) >= 7
                          ? "bg-emerald-400"
                          : (data.piotroski_score ?? 0) >= 4
                            ? "bg-amber-400"
                            : "bg-red-400"
                        : "bg-border/30"
                    }`}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-x-8 gap-y-3 sm:grid-cols-4">
            <Metric label="Market Cap" value={formatCurrency(data.market_cap, c)} />
            <Metric label="Revenue" value={formatCurrency(data.revenue, c)} />
            <Metric label="P/E Ratio" value={formatNumber(data.pe_ratio)} />
            <Metric label="EPS" value={formatPrice(data.eps, c)} />
            <Metric label="Profit Margin" value={formatPercent(data.profit_margin)} />
            <Metric label="ROE" value={formatPercent(data.roe)} />
            <Metric label="Debt/Equity" value={formatNumber(data.debt_to_equity)} />
            <Metric label="Free Cash Flow" value={formatCurrency(data.free_cash_flow, c)} />
            <Metric label="Cash" value={formatCurrency(data.cash, c)} />
            <Metric label="Debt" value={formatCurrency(data.debt, c)} />
            <Metric label="P/B Ratio" value={formatNumber(data.price_to_book)} />
            <Metric
              label="52W Range"
              value={
                data.fifty_two_week_low !== null && data.fifty_two_week_high !== null
                  ? `${formatPrice(data.fifty_two_week_low, c)} – ${formatPrice(data.fifty_two_week_high, c)}`
                  : "—"
              }
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

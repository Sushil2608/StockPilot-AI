"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { IndicatorInfo } from "@/components/indicator-info";
import type { FinancialData } from "@/lib/types";
import { formatCurrency, formatPrice, formatNumber, formatPercent } from "@/lib/format";

interface FinancialCardProps {
  data: FinancialData;
}

function Metric({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description: string;
}) {
  return (
    <div className="min-w-0">
      <IndicatorInfo label={label} description={description} />
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
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <h3 className="text-sm font-medium text-muted-foreground">Fundamentals</h3>
              <p className="mt-0.5 break-words text-lg font-bold sm:text-xl">{data.company_name}</p>
              {data.sector && (
                <p className="text-xs text-muted-foreground mt-0.5">
                  {data.sector} · {data.industry}
                </p>
              )}
            </div>
            <div className="flex items-baseline justify-between gap-3 sm:block sm:text-right">
              <p className="text-xl font-bold font-mono sm:text-2xl">
                {formatPrice(data.current_price, c)}
              </p>
              <div className="mt-1 flex shrink-0 items-center gap-2">
                <IndicatorInfo
                  label="Revenue growth"
                  description="The year-over-year percentage change in the company’s revenue. Positive growth means sales increased; compare it with the company’s past growth and industry peers."
                />
                <GrowthBadge value={data.revenue_growth} />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {data.piotroski_score !== null && (
            <div className="mb-4 p-3 rounded-lg bg-background/50 border border-border/30">
              <div className="flex items-center justify-between mb-2">
                <IndicatorInfo
                  label="Piotroski F-Score"
                  description="A score from 0 to 9 based on nine accounting checks for profitability, liquidity, leverage, and operating efficiency. Higher scores indicate stronger financial signals in the latest reports; it does not predict future returns."
                />
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

          <div className="grid grid-cols-2 gap-x-4 gap-y-3 sm:grid-cols-4 sm:gap-x-8">
            <Metric
              label="Market Cap"
              value={formatCurrency(data.market_cap, c)}
              description="The market value of all outstanding shares, calculated as share price times shares outstanding. It describes company size, not whether the stock is cheap or expensive."
            />
            <Metric
              label="Revenue"
              value={formatCurrency(data.revenue, c)}
              description="The company’s reported sales before operating costs and other expenses are deducted. Compare revenue over time to see whether the business is growing."
            />
            <Metric
              label="P/E Ratio"
              value={formatNumber(data.pe_ratio)}
              description="Price-to-earnings compares a share price with earnings per share. A higher ratio can reflect stronger growth expectations, but comparisons are most useful among similar companies. It is less meaningful when earnings are negative."
            />
            <Metric
              label="EPS"
              value={formatPrice(data.eps, c)}
              description="Earnings per share is the company’s profit allocated to each share. It helps compare profitability across periods, though share buybacks and accounting changes can also affect it."
            />
            <Metric
              label="Profit Margin"
              value={formatPercent(data.profit_margin)}
              description="The percentage of revenue left as net profit. Higher or improving margins can indicate stronger profitability; typical margins vary widely by industry."
            />
            <Metric
              label="ROE"
              value={formatPercent(data.roe)}
              description="Return on equity measures net income relative to shareholders’ equity. It indicates how effectively equity is generating profit, but high debt can make ROE look unusually strong."
            />
            <Metric
              label="Debt/Equity"
              value={formatNumber(data.debt_to_equity)}
              description="A leverage measure comparing debt with shareholders’ equity. Higher values can mean more financial risk; appropriate levels depend on the industry and business model."
            />
            <Metric
              label="Free Cash Flow"
              value={formatCurrency(data.free_cash_flow, c)}
              description="Cash generated after the company pays for operating needs and capital investment. Positive free cash flow can support debt repayment, dividends, or reinvestment."
            />
            <Metric
              label="Cash"
              value={formatCurrency(data.cash, c)}
              description="Cash and cash equivalents reported on the balance sheet. This is a snapshot of available liquidity and should be considered alongside debt and cash needs."
            />
            <Metric
              label="Debt"
              value={formatCurrency(data.debt, c)}
              description="Borrowings reported for the company. The amount is more informative when compared with cash, earnings, and the company’s ability to make interest and principal payments."
            />
            <Metric
              label="P/B Ratio"
              value={formatNumber(data.price_to_book)}
              description="Price-to-book compares the market value of equity with its accounting book value. It is often more useful for asset-heavy businesses and less useful when valuable intangible assets dominate."
            />
            <Metric
              label="52W Range"
              value={
                data.fifty_two_week_low !== null && data.fifty_two_week_high !== null
                  ? `${formatPrice(data.fifty_two_week_low, c)} – ${formatPrice(data.fifty_two_week_high, c)}`
                  : "—"
              }
              description="The lowest and highest recorded share prices over the past 52 weeks. It gives recent historical context, but does not indicate where the price will go next."
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { FinancialData } from "@/lib/types";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/format";

interface FinancialCardProps {
  data: FinancialData;
}

interface MetricProps {
  label: string;
  value: string;
}

function Metric({ label, value }: MetricProps) {
  return (
    <div className="space-y-1">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}

export function FinancialCard({ data }: FinancialCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Financial Overview</span>
          <span className="text-2xl font-bold">
            {data.current_price !== null
              ? `$${formatNumber(data.current_price)}`
              : "N/A"}
          </span>
        </CardTitle>
        <p className="text-sm text-muted-foreground">{data.company_name}</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Metric label="Market Cap" value={formatCurrency(data.market_cap)} />
          <Metric label="Revenue" value={formatCurrency(data.revenue)} />
          <Metric label="P/E Ratio" value={formatNumber(data.pe_ratio)} />
          <Metric label="EPS" value={data.eps !== null ? `$${formatNumber(data.eps)}` : "N/A"} />
          <Metric label="Cash" value={formatCurrency(data.cash)} />
          <Metric label="Debt" value={formatCurrency(data.debt)} />
          <Metric label="ROE" value={formatPercent(data.roe)} />
          <Metric
            label="52W Range"
            value={
              data.fifty_two_week_low !== null && data.fifty_two_week_high !== null
                ? `$${formatNumber(data.fifty_two_week_low)} - $${formatNumber(data.fifty_two_week_high)}`
                : "N/A"
            }
          />
        </div>
      </CardContent>
    </Card>
  );
}

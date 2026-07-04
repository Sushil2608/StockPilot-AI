export function formatCurrency(value: number | null): string {
  if (value === null) return "N/A";
  if (value >= 1_000_000_000_000) return `$${(value / 1_000_000_000_000).toFixed(2)}T`;
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(2)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  return `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatNumber(value: number | null, decimals = 2): string {
  if (value === null) return "N/A";
  return value.toFixed(decimals);
}

export function formatPercent(value: number | null): string {
  if (value === null) return "N/A";
  return `${value.toFixed(2)}%`;
}

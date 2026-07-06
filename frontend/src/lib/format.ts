export function formatCurrency(value: number | null, currency = "USD"): string {
  if (value === null) return "—";
  const sym = currency === "INR" ? "₹" : "$";
  if (currency === "INR") return `${sym}${formatIndian(value)}`;
  return `${sym}${formatWestern(value)}`;
}

function formatWestern(value: number): string {
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  if (abs >= 1_000_000_000_000) return `${sign}${(value / 1_000_000_000_000).toFixed(2)}T`;
  if (abs >= 1_000_000_000) return `${sign}${(value / 1_000_000_000).toFixed(2)}B`;
  if (abs >= 1_000_000) return `${sign}${(value / 1_000_000).toFixed(2)}M`;
  return `${sign}${abs.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatIndian(value: number): string {
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  if (abs >= 10_000_000_000_000) return `${sign}${(value / 10_000_000_000_000).toFixed(2)}L Cr`;
  if (abs >= 10_000_000) return `${sign}${(value / 10_000_000).toFixed(2)} Cr`;
  if (abs >= 100_000) return `${sign}${(value / 100_000).toFixed(2)}L`;
  if (abs >= 1_000) return `${sign}${(value / 1_000).toFixed(2)}K`;
  return `${sign}${abs.toFixed(2)}`;
}

export function formatPrice(value: number | null, currency = "USD"): string {
  if (value === null) return "—";
  const sym = currency === "INR" ? "₹" : "$";
  return `${sym}${value.toLocaleString(currency === "INR" ? "en-IN" : "en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatNumber(value: number | null, decimals = 2): string {
  if (value === null) return "—";
  return value.toFixed(decimals);
}

export function formatPercent(value: number | null): string {
  if (value === null) return "—";
  return `${value.toFixed(2)}%`;
}

import type {
  AgentStatus,
  AnalysisResponse,
  ChartPeriod,
  FinancialData,
  MarketType,
  NewsAnalysis,
  PriceHistoryResponse,
  TechnicalIndicators,
  ResearchPlan,
  InvestmentReport,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type StreamEvent =
  | { type: "agent_status"; data: AgentStatus }
  | { type: "result_planner"; data: ResearchPlan }
  | { type: "result_financial"; data: FinancialData }
  | { type: "result_news"; data: NewsAnalysis }
  | { type: "result_technical"; data: TechnicalIndicators }
  | { type: "result_report"; data: InvestmentReport }
  | { type: "complete"; data: AnalysisResponse }
  | { type: "error"; data: string };

export async function streamAnalysis(
  ticker: string,
  market: MarketType,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch(`${API_BASE}/analyze/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker, market }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:") && currentEvent) {
        const rawData = line.slice(5).trim();
        try {
          const parsed = JSON.parse(rawData);
          onEvent({ type: currentEvent, data: parsed } as StreamEvent);
        } catch {
          // skip malformed data
        }
        currentEvent = "";
      }
    }
  }
}

export async function fetchPriceHistory(
  ticker: string,
  period: ChartPeriod,
  market: MarketType
): Promise<PriceHistoryResponse> {
  const params = new URLSearchParams({ period, market });
  const response = await fetch(
    `${API_BASE}/price-history/${ticker}?${params}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch price history: ${response.statusText}`);
  }
  return response.json();
}

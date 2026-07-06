export type MarketType = "US" | "IN";

export interface FinancialData {
  ticker: string;
  market: string;
  currency: string;
  company_name: string;
  sector: string;
  industry: string;
  current_price: number | null;
  market_cap: number | null;
  revenue: number | null;
  revenue_growth: number | null;
  net_income: number | null;
  profit_margin: number | null;
  pe_ratio: number | null;
  eps: number | null;
  cash: number | null;
  debt: number | null;
  debt_to_equity: number | null;
  free_cash_flow: number | null;
  roe: number | null;
  dividend_yield: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  price_to_book: number | null;
  piotroski_score: number | null;
  piotroski_details: string[];
  fundamental_signal: string;
}

export interface NewsItem {
  title: string;
  source: string;
  url: string;
  published: string;
}

export interface NewsAnalysis {
  ticker: string;
  positive_developments: string[];
  negative_developments: string[];
  overall_sentiment: string;
  evidence: NewsItem[];
}

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export type ChartPeriod = "5d" | "1mo" | "3mo" | "6mo" | "1y" | "5y";
export type ChartType = "area" | "line" | "candle";

export interface PriceHistoryResponse {
  ticker: string;
  period: string;
  currency: string;
  data: PricePoint[];
}

export interface TechnicalIndicators {
  ticker: string;
  current_price: number | null;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  sma_50: number | null;
  sma_200: number | null;
  ema_20: number | null;
  bollinger_upper: number | null;
  bollinger_middle: number | null;
  bollinger_lower: number | null;
  atr: number | null;
  volume_current: number | null;
  volume_avg: number | null;
  trend: string;
  technical_score: number;
  score_breakdown: Record<string, number>;
  price_history: PricePoint[];
}

export interface ResearchPlan {
  ticker: string;
  company_name: string;
  steps: string[];
}

export interface InvestmentReport {
  ticker: string;
  company_name: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  risks: string[];
  recommendation: string;
  confidence_score: number;
  target_price: number | null;
  target_upside: number | null;
  target_methodology: string;
}

export interface AnalysisResponse {
  ticker: string;
  market: string;
  currency: string;
  planner: ResearchPlan | null;
  financial: FinancialData | null;
  news: NewsAnalysis | null;
  technical: TechnicalIndicators | null;
  report: InvestmentReport | null;
}

export type AgentStatusValue = "pending" | "running" | "completed" | "error";

export interface AgentStatus {
  agent: string;
  status: AgentStatusValue;
  message: string;
}

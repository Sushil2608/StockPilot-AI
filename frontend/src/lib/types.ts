export interface FinancialData {
  ticker: string;
  company_name: string;
  revenue: number | null;
  market_cap: number | null;
  pe_ratio: number | null;
  eps: number | null;
  cash: number | null;
  debt: number | null;
  roe: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  current_price: number | null;
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

export interface TechnicalIndicators {
  ticker: string;
  current_price: number | null;
  rsi: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  sma_50: number | null;
  sma_200: number | null;
  trend: string;
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
}

export interface AnalysisResponse {
  ticker: string;
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

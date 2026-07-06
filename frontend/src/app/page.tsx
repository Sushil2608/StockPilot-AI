"use client";

import { useCallback, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/navbar";
import { SearchBar } from "@/components/search-bar";
import { ProgressTracker } from "@/components/progress-tracker";
import { FinancialCard } from "@/components/financial-card";
import { NewsCard } from "@/components/news-card";
import { TechnicalCard } from "@/components/technical-card";
import { ReportCard } from "@/components/report-card";
import { PriceChart } from "@/components/price-chart";
import { streamAnalysis, type StreamEvent } from "@/lib/api";
import type {
  AgentStatusValue,
  FinancialData,
  MarketType,
  NewsAnalysis,
  TechnicalIndicators,
  InvestmentReport,
} from "@/lib/types";

interface AgentStep {
  name: string;
  status: AgentStatusValue;
}

const INITIAL_STEPS: AgentStep[] = [
  { name: "Planner", status: "pending" },
  { name: "Financial Agent", status: "pending" },
  { name: "News Agent", status: "pending" },
  { name: "Technical Agent", status: "pending" },
  { name: "Report Writer", status: "pending" },
];

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [steps, setSteps] = useState<AgentStep[]>(INITIAL_STEPS);
  const [financial, setFinancial] = useState<FinancialData | null>(null);
  const [news, setNews] = useState<NewsAnalysis | null>(null);
  const [technical, setTechnical] = useState<TechnicalIndicators | null>(null);
  const [report, setReport] = useState<InvestmentReport | null>(null);
  const [currency, setCurrency] = useState("USD");
  const [currentMarket, setCurrentMarket] = useState<MarketType>("US");
  const [currentTicker, setCurrentTicker] = useState("");
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const updateStep = useCallback(
    (name: string, status: AgentStatusValue) => {
      setSteps((prev) =>
        prev.map((s) => (s.name === name ? { ...s, status } : s))
      );
    },
    []
  );

  const handleEvent = useCallback(
    (event: StreamEvent) => {
      switch (event.type) {
        case "agent_status":
          updateStep(event.data.agent, event.data.status);
          break;
        case "result_financial":
          setFinancial(event.data);
          break;
        case "result_news":
          setNews(event.data);
          break;
        case "result_technical":
          setTechnical(event.data);
          break;
        case "result_report":
          setReport(event.data);
          break;
        case "complete":
          if (event.data.financial) setFinancial(event.data.financial);
          if (event.data.news) setNews(event.data.news);
          if (event.data.technical) setTechnical(event.data.technical);
          if (event.data.report) setReport(event.data.report);
          break;
      }
    },
    [updateStep]
  );

  async function handleAnalyze(ticker: string, market: MarketType) {
    setCurrency(market === "IN" ? "INR" : "USD");
    setCurrentMarket(market);
    setCurrentTicker(ticker);
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setError(null);
    setFinancial(null);
    setNews(null);
    setTechnical(null);
    setReport(null);
    setSteps(
      INITIAL_STEPS.map((s) => ({
        ...s,
        status: "pending" as AgentStatusValue,
      }))
    );

    try {
      await streamAnalysis(ticker, market, handleEvent, controller.signal);
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  }

  const hasResults = financial || news || technical || report;

  return (
    <>
      <Navbar />
      <main className="container mx-auto max-w-5xl flex flex-col gap-8 px-4 py-12">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center gap-4"
        >
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">
              Stock Research
            </h1>
            <p className="text-sm text-muted-foreground">
              AI-powered analysis across financials, news, and technicals
            </p>
          </div>
          <SearchBar onAnalyze={handleAnalyze} isLoading={isLoading} />
        </motion.div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="rounded-lg border border-red-400/20 bg-red-400/5 p-3 text-sm text-red-400"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        <ProgressTracker steps={steps} />

        {hasResults && (
          <div className="space-y-6">
            {financial && <FinancialCard data={financial} />}

            {technical && technical.price_history.length > 0 && (
              <PriceChart
                initialData={technical.price_history}
                ticker={currentTicker}
                currency={currency}
                market={currentMarket}
              />
            )}

            <div className="grid gap-6 md:grid-cols-2">
              {news && <NewsCard data={news} />}
              {technical && <TechnicalCard data={technical} />}
            </div>

            {report && <ReportCard data={report} currency={currency} />}
          </div>
        )}

        {!hasResults && !isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-center py-16"
          >
            <p className="text-sm text-muted-foreground/50">
              Enter a ticker to begin
            </p>
          </motion.div>
        )}
      </main>
    </>
  );
}

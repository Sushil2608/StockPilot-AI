"use client";

import { useCallback, useRef, useState } from "react";
import { Navbar } from "@/components/navbar";
import { SearchBar } from "@/components/search-bar";
import { ProgressTracker } from "@/components/progress-tracker";
import { FinancialCard } from "@/components/financial-card";
import { NewsCard } from "@/components/news-card";
import { TechnicalCard } from "@/components/technical-card";
import { ReportCard } from "@/components/report-card";
import { streamAnalysis, type StreamEvent } from "@/lib/api";
import type {
  AgentStatusValue,
  FinancialData,
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

  async function handleAnalyze(ticker: string) {
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
      await streamAnalysis(ticker, handleEvent, controller.signal);
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
      <main className="container mx-auto flex flex-col gap-6 px-4 py-8">
        <div className="flex flex-col items-center gap-2">
          <h1 className="text-3xl font-bold">Stock Research</h1>
          <p className="text-muted-foreground">
            Enter a ticker symbol to generate an AI-powered investment report
          </p>
          <div className="mt-4">
            <SearchBar onAnalyze={handleAnalyze} isLoading={isLoading} />
          </div>
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        <ProgressTracker steps={steps} />

        {hasResults && (
          <div className="space-y-6">
            {financial && <FinancialCard data={financial} />}

            <div className="grid gap-6 md:grid-cols-2">
              {news && <NewsCard data={news} />}
              {technical && <TechnicalCard data={technical} />}
            </div>

            {report && <ReportCard data={report} />}
          </div>
        )}
      </main>
    </>
  );
}

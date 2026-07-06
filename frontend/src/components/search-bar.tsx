"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { MarketType } from "@/lib/types";

interface SearchBarProps {
  onAnalyze: (ticker: string, market: MarketType) => void;
  isLoading: boolean;
}

const PLACEHOLDERS: Record<MarketType, string> = {
  US: "AAPL, NVDA, MSFT...",
  IN: "RELIANCE, TCS, INFY...",
};

export function SearchBar({ onAnalyze, isLoading }: SearchBarProps) {
  const [ticker, setTicker] = useState("");
  const [market, setMarket] = useState<MarketType>("US");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleaned = ticker.trim().toUpperCase();
    if (cleaned) onAnalyze(cleaned, market);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 w-full max-w-lg items-center">
      <div className="flex rounded-lg border border-border/50 bg-card overflow-hidden">
        <button
          type="button"
          onClick={() => setMarket("US")}
          className={`px-3 py-2 text-xs font-medium transition-colors ${
            market === "US"
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          US
        </button>
        <button
          type="button"
          onClick={() => setMarket("IN")}
          className={`px-3 py-2 text-xs font-medium transition-colors ${
            market === "IN"
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          IN
        </button>
      </div>
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={PLACEHOLDERS[market]}
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          disabled={isLoading}
          className="pl-9 h-11 bg-card border-border/50 font-mono text-sm tracking-wider"
        />
      </div>
      <Button
        type="submit"
        disabled={isLoading || !ticker.trim()}
        className="h-11 px-6"
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          "Analyze"
        )}
      </Button>
    </form>
  );
}

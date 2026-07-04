"use client";

import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchBarProps {
  onAnalyze: (ticker: string) => void;
  isLoading: boolean;
}

export function SearchBar({ onAnalyze, isLoading }: SearchBarProps) {
  const [ticker, setTicker] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleaned = ticker.trim().toUpperCase();
    if (cleaned) onAnalyze(cleaned);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 w-full max-w-lg">
      <Input
        placeholder="Enter ticker (e.g., NVDA, AAPL, MSFT)"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        disabled={isLoading}
        className="text-lg h-12"
      />
      <Button type="submit" disabled={isLoading || !ticker.trim()} size="lg">
        {isLoading ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <Search className="h-5 w-5" />
        )}
        <span className="ml-2">{isLoading ? "Analyzing..." : "Analyze"}</span>
      </Button>
    </form>
  );
}

"use client";

import { TrendingUp } from "lucide-react";

export function Navbar() {
  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center px-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">StockPilot AI</span>
        </div>
        <span className="ml-3 text-sm text-muted-foreground">
          Agentic Stock Research Assistant
        </span>
      </div>
    </nav>
  );
}

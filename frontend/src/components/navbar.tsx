"use client";

import { TrendingUp } from "lucide-react";

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto flex h-14 items-center px-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <TrendingUp className="h-4 w-4 text-primary" />
          </div>
          <span className="text-lg font-semibold tracking-tight">
            StockPilot
            <span className="text-primary"> AI</span>
          </span>
        </div>
      </div>
    </nav>
  );
}

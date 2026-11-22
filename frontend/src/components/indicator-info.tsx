import { CircleHelp } from "lucide-react";
import type { ReactNode } from "react";

interface IndicatorInfoProps {
  label: ReactNode;
  description: string;
  className?: string;
}

export function IndicatorInfo({
  label,
  description,
  className = "",
}: IndicatorInfoProps) {
  return (
    <details className={`min-w-0 ${className}`}>
      <summary className="inline-flex cursor-pointer list-none items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground focus-visible:rounded-sm focus-visible:outline-2 focus-visible:outline-ring [&::-webkit-details-marker]:hidden">
        <span>{label}</span>
        <CircleHelp aria-hidden="true" className="h-3 w-3 shrink-0 opacity-70" />
      </summary>
      <p className="mt-1 rounded-md border border-border/50 bg-background/80 p-2 text-[11px] leading-relaxed text-muted-foreground">
        {description}
      </p>
    </details>
  );
}

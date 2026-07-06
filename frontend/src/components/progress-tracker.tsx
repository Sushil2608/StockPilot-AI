"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Loader2, Circle, AlertCircle } from "lucide-react";
import type { AgentStatusValue } from "@/lib/types";

interface AgentStep {
  name: string;
  status: AgentStatusValue;
}

interface ProgressTrackerProps {
  steps: AgentStep[];
}

const STATUS_ICON: Record<AgentStatusValue, React.ReactNode> = {
  pending: <Circle className="h-3.5 w-3.5" />,
  running: <Loader2 className="h-3.5 w-3.5 animate-spin" />,
  completed: <CheckCircle2 className="h-3.5 w-3.5" />,
  error: <AlertCircle className="h-3.5 w-3.5" />,
};

const STATUS_COLOR: Record<AgentStatusValue, string> = {
  pending: "text-muted-foreground/40",
  running: "text-primary",
  completed: "text-emerald-400",
  error: "text-red-400",
};

export function ProgressTracker({ steps }: ProgressTrackerProps) {
  const allPending = steps.every((s) => s.status === "pending");
  const allDone = steps.every(
    (s) => s.status === "completed" || s.status === "error"
  );
  const completedCount = steps.filter((s) => s.status === "completed").length;
  const startTime = useRef<number | null>(null);
  const elapsedRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (steps.some((s) => s.status === "running") && !startTime.current) {
      startTime.current = Date.now();
    }
    if (allDone && startTime.current) {
      const elapsed = ((Date.now() - startTime.current) / 1000).toFixed(1);
      if (elapsedRef.current) elapsedRef.current.textContent = `${elapsed}s`;
    }
    if (allPending) startTime.current = null;
  }, [steps, allDone, allPending]);

  if (allPending) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center gap-2"
    >
      <div className="flex items-center gap-1 flex-wrap justify-center">
        {steps.map((step, i) => (
          <div key={step.name} className="flex items-center">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: i * 0.05 }}
              className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all ${STATUS_COLOR[step.status]} ${
                step.status === "running"
                  ? "bg-primary/10 ring-1 ring-primary/30"
                  : step.status === "completed"
                    ? "bg-emerald-400/10"
                    : step.status === "error"
                      ? "bg-red-400/10"
                      : "bg-transparent"
              }`}
            >
              {STATUS_ICON[step.status]}
              <span className="hidden sm:inline">{step.name}</span>
            </motion.div>
            {i < steps.length - 1 && (
              <div
                className={`mx-0.5 h-px w-3 transition-colors ${
                  step.status === "completed"
                    ? "bg-emerald-400/30"
                    : "bg-border/30"
                }`}
              />
            )}
          </div>
        ))}
      </div>
      <div className="text-[11px] text-muted-foreground">
        {allDone ? (
          <span>
            {completedCount}/{steps.length} completed in{" "}
            <span ref={elapsedRef} className="font-mono" />
          </span>
        ) : (
          <span className="animate-pulse">
            {completedCount}/{steps.length} completed
          </span>
        )}
      </div>
    </motion.div>
  );
}

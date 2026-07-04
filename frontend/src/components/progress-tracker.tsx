"use client";

import {
  CheckCircle2,
  Loader2,
  Circle,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentStatusValue } from "@/lib/types";

interface AgentStep {
  name: string;
  status: AgentStatusValue;
}

interface ProgressTrackerProps {
  steps: AgentStep[];
}

const STATUS_CONFIG: Record<
  AgentStatusValue,
  { icon: React.ReactNode; className: string }
> = {
  pending: {
    icon: <Circle className="h-5 w-5" />,
    className: "text-muted-foreground",
  },
  running: {
    icon: <Loader2 className="h-5 w-5 animate-spin" />,
    className: "text-blue-500",
  },
  completed: {
    icon: <CheckCircle2 className="h-5 w-5" />,
    className: "text-green-500",
  },
  error: {
    icon: <AlertCircle className="h-5 w-5" />,
    className: "text-red-500",
  },
};

export function ProgressTracker({ steps }: ProgressTrackerProps) {
  if (steps.every((s) => s.status === "pending")) return null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Research Progress</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {steps.map((step) => {
            const config = STATUS_CONFIG[step.status];
            return (
              <div key={step.name} className="flex items-center gap-3">
                <span className={config.className}>{config.icon}</span>
                <span
                  className={
                    step.status === "pending"
                      ? "text-muted-foreground"
                      : "font-medium"
                  }
                >
                  {step.name}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

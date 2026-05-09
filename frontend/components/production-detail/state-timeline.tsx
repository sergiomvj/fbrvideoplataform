"use client";

import type { StateVariant } from "@/lib/design-system/tokens";

interface StateEntry {
  from_state: string | null;
  to_state: string;
  occurred_at: string;
  reason: string;
  triggered_by: string;
}

interface StateTimelineProps {
  entries: StateEntry[];
}

function inferVariant(state: string): StateVariant {
  const s = state.toLowerCase();
  if (s.includes("complet") || s.includes("done") || s.includes("success") || s === "finished")
    return "success";
  if (s.includes("fail") || s.includes("error") || s === "failed") return "danger";
  if (s.includes("process") || s.includes("render") || s.includes("progress") || s === "rendering")
    return "warning";
  return "info";
}

const dotColors: Record<StateVariant, string> = {
  success: "bg-green-500",
  warning: "bg-amber-500",
  danger: "bg-red-500",
  info: "bg-cyan-500",
};

const lineColors: Record<StateVariant, string> = {
  success: "bg-green-200",
  warning: "bg-amber-200",
  danger: "bg-red-200",
  info: "bg-cyan-200",
};

function formatTimestamp(ts: string): string {
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return ts;
  }
}

export function StateTimeline({ entries }: StateTimelineProps) {
  if (entries.length === 0) {
    return (
      <div className="py-4 text-sm text-gray-400">No state history available.</div>
    );
  }

  return (
    <div className="relative flex flex-col">
      {entries.map((entry, idx) => {
        const variant = inferVariant(entry.to_state);
        const isLast = idx === entries.length - 1;

        return (
          <div key={`${entry.to_state}-${entry.occurred_at}-${idx}`} className="relative flex gap-4 pb-6 last:pb-0">
            <div className="flex flex-col items-center">
              <div className={`h-3 w-3 shrink-0 rounded-full ${dotColors[variant]}`} />
              {!isLast && (
                <div className={`w-0.5 flex-1 ${lineColors[variant]}`} />
              )}
            </div>
            <div className="flex-1 pt-0">
              <p className="text-sm font-medium text-gray-900">
                {entry.from_state ? `${entry.from_state} → ${entry.to_state}` : entry.to_state}
              </p>
              <p className="text-xs text-gray-500">{formatTimestamp(entry.occurred_at)}</p>
              {entry.reason && (
                <p className="text-xs text-gray-400">{entry.reason}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

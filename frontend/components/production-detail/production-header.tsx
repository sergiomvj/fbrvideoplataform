"use client";

import { Badge } from "@/components/ui/badge";
import { StatusIndicator } from "@/components/ui/status-indicator";
import type { StateVariant } from "@/lib/design-system/tokens";

interface ProductionHeaderProps {
  title: string;
  mode: string;
  templateName: string;
  variationName?: string | null;
  state: string;
  stateVariant: StateVariant;
}

function mapModeToVariant(mode: string): "info" | "warning" | "success" {
  if (mode === "editorial") return "info";
  if (mode === "automated") return "warning";
  return "success";
}

export function ProductionHeader({
  title,
  mode,
  templateName,
  variationName,
  state,
  stateVariant,
}: ProductionHeaderProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        <StatusIndicator state={stateVariant} label={state} pulse={state === "processing" || state === "rendering"} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={mapModeToVariant(mode)}>{mode}</Badge>
        <Badge variant="neutral">{templateName}</Badge>
        {variationName && <Badge variant="neutral">{variationName}</Badge>}
      </div>
    </div>
  );
}

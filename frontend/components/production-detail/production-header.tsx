"use client";

import { Badge } from "@/components/ui/badge";
import { StatusIndicator } from "@/components/ui/status-indicator";
import type { StateVariant } from "@/lib/design-system/tokens";

interface ProductionHeaderProps {
  title: string;
  mode: string;
  templateTypeId: string;
  variationId: string;
  currentState: string;
  stateVariant: StateVariant;
}

function mapModeToVariant(mode: string): "info" | "warning" | "success" {
  if (mode === "editorial" || mode === "manual") return "info";
  if (mode === "automated" || mode === "automatic") return "warning";
  return "success";
}

export function ProductionHeader({
  title,
  mode,
  templateTypeId,
  variationId,
  currentState,
  stateVariant,
}: ProductionHeaderProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        <StatusIndicator state={stateVariant} label={currentState} pulse={currentState === "processing" || currentState === "rendering"} />
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={mapModeToVariant(mode)}>{mode}</Badge>
        <Badge variant="neutral">{templateTypeId}</Badge>
        {variationId && <Badge variant="neutral">{variationId}</Badge>}
      </div>
    </div>
  );
}

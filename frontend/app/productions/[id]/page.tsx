"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ProductionHeader } from "@/components/production-detail/production-header";
import { StateTimeline } from "@/components/production-detail/state-timeline";
import { CompositionPreview } from "@/components/production-detail/composition-preview";
import { RenderStatus } from "@/components/production-detail/render-status";
import type { StateVariant } from "@/lib/design-system/tokens";

interface StateHistoryEntry {
  from_state: string | null;
  to_state: string;
  occurred_at: string;
  reason: string;
  triggered_by: string;
}

interface CompositionSlot {
  slot_index: number;
  slot_type: string;
  duration_seconds: number;
  content_reference: string;
  asset_url: string | null;
}

interface CompositionSummary {
  id: string;
  template_type_id: string;
  variation_id: string;
  total_duration_seconds: number;
  slots: CompositionSlot[];
}

interface RenderJobSummary {
  id: string;
  status: string;
  provider: string;
  created_at: string;
  updated_at: string;
  error_message: string | null;
}

interface ProductionDetail {
  id: string;
  title: string;
  mode: string;
  template_type_id: string;
  variation_id: string;
  current_state: string;
  base_content: string;
  editorial_context: string;
  restrictions: string[];
  created_at: string;
  updated_at: string;
  operator_user_id: string;
  organization_id: string;
  state_history: StateHistoryEntry[];
  composition: CompositionSummary | null;
  render_job: RenderJobSummary | null;
}

function inferStateVariant(state: string): StateVariant {
  const s = state.toLowerCase();
  if (s === "completed" || s === "done" || s === "success" || s === "finished") return "success";
  if (s === "failed" || s === "error") return "danger";
  if (s === "processing" || s === "rendering" || s === "queued") return "warning";
  return "info";
}

export default function ProductionDetailPage() {
  const params = useParams<{ id: string }>();
  const [production, setProduction] = useState<ProductionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProduction() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/productions/${params.id}`);
        if (!res.ok) throw new Error(`Failed to load production (${res.status})`);
        const data = await res.json();
        setProduction(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    if (params.id) fetchProduction();
  }, [params.id]);

  if (loading) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">Loading production...</div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {error}
      </div>
    );
  }

  if (!production) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">Production not found.</div>
    );
  }

  const stateVariant = inferStateVariant(production.current_state);

  return (
    <div className="space-y-6">
      <ProductionHeader
        title={production.title}
        mode={production.mode}
        templateTypeId={production.template_type_id}
        variationId={production.variation_id}
        currentState={production.current_state}
        stateVariant={stateVariant}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>State History</CardTitle>
          </CardHeader>
          <CardContent>
            <StateTimeline entries={production.state_history ?? []} />
          </CardContent>
        </Card>

        <RenderStatus job={production.render_job} />
      </div>

      <CompositionPreview composition={production.composition} />
    </div>
  );
}

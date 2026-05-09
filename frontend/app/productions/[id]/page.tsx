"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ProductionHeader } from "@/components/production-detail/production-header";
import { StateTimeline } from "@/components/production-detail/state-timeline";
import { CompositionPreview } from "@/components/production-detail/composition-preview";
import { RenderStatus } from "@/components/production-detail/render-status";
import type { StateVariant } from "@/lib/design-system/tokens";

interface ProductionData {
  id: string;
  title: string;
  mode: string;
  template_name: string;
  variation_name?: string | null;
  state: string;
  state_history: Array<{ state: string; entered_at: string; variant?: StateVariant }>;
  composition_slots: Array<{ slot_type: string; duration: number; content: string }>;
  render_job: {
    id: string;
    status: string;
    progress: number;
    output_url?: string | null;
    error_message?: string | null;
  } | null;
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
  const [production, setProduction] = useState<ProductionData | null>(null);
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

  const stateVariant = inferStateVariant(production.state);

  return (
    <div className="space-y-6">
      <ProductionHeader
        title={production.title}
        mode={production.mode}
        templateName={production.template_name}
        variationName={production.variation_name}
        state={production.state}
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

      <CompositionPreview slots={production.composition_slots ?? []} />
    </div>
  );
}

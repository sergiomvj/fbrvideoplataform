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

interface NarrativeBlock {
  id: string;
  role: string;
  text: string;
  estimated_duration_seconds: number;
  scene_index: number;
}

interface NarrativeSummary {
  production_id: string;
  template_type_id: string;
  variation_id: string;
  objective: string;
  target_duration_seconds: number;
  total_duration: number;
  blocks: NarrativeBlock[];
}

interface BriefSummary {
  id: string;
  scene_id: string;
  scene_index: number;
  tema: string;
  funcao_visual: string;
  assunto_visivel: string;
  contexto_geografico_cultural: string;
  periodo: string;
  tom_editorial: string;
  nivel_literalidade: string;
  permitidos: string[];
  proibidos: string[];
  tipo_ativo_preferido: string;
  template_type_id: string;
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
  narrative: NarrativeSummary | null;
  briefs: BriefSummary[];
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

      {production.narrative && production.narrative.blocks.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Narrative Structure</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-3 text-sm text-gray-600">
              <span className="font-medium">Objective:</span> {production.narrative.objective}
            </div>
            <div className="mb-3 flex gap-4 text-xs text-gray-500">
              <span>Target: {production.narrative.target_duration_seconds}s</span>
              <span>Total: {production.narrative.total_duration.toFixed(1)}s</span>
            </div>
            <div className="space-y-2">
              {production.narrative.blocks.map((block) => (
                <div
                  key={block.id}
                  className="rounded-lg border border-gray-100 p-3"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium uppercase tracking-wider text-gray-500">
                      {block.role}
                    </span>
                    <span className="text-xs text-gray-400">
                      Scene {block.scene_index} · {block.estimated_duration_seconds}s
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{block.text}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {production.briefs && production.briefs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Visual Briefs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {production.briefs.map((brief) => (
                <div
                  key={brief.id}
                  className="rounded-lg border border-gray-100 p-3"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">
                      Scene {brief.scene_index}: {brief.tema}
                    </span>
                    <span className="text-xs text-gray-400">{brief.funcao_visual}</span>
                  </div>
                  <p className="text-xs text-gray-600 mb-1">{brief.assunto_visivel}</p>
                  <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                    <span>Tom: {brief.tom_editorial}</span>
                    <span>Literalidade: {brief.nivel_literalidade}</span>
                    <span>Tipo: {brief.tipo_ativo_preferido}</span>
                  </div>
                </div>
              ))}
            </div>
         </CardContent>
        </Card>
      )}
    </div>
  );
}

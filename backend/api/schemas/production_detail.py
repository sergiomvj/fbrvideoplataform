from __future__ import annotations

from pydantic import BaseModel, Field


class CompositionSlotResponse(BaseModel):
    slot_index: int
    slot_type: str
    duration_seconds: float
    content_reference: str
    asset_url: str | None = None


class CompositionSummaryResponse(BaseModel):
    id: str
    template_type_id: str
    variation_id: str
    total_duration_seconds: float
    slots: list[CompositionSlotResponse] = Field(default_factory=list)


class RenderJobSummaryResponse(BaseModel):
    id: str
    status: str
    provider: str
    created_at: str
    updated_at: str
    error_message: str | None = None


class StateHistoryEntry(BaseModel):
    from_state: str | None
    to_state: str
    occurred_at: str
    reason: str
    triggered_by: str


class ProductionDetailResponse(BaseModel):
    id: str
    title: str
    mode: str
    template_type_id: str
    variation_id: str
    current_state: str
    base_content: str
    editorial_context: str
    restrictions: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    operator_user_id: str
    organization_id: str
    state_history: list[StateHistoryEntry] = Field(default_factory=list)
    composition: CompositionSummaryResponse | None = None
    render_job: RenderJobSummaryResponse | None = None
    narrative: NarrativeResponse | None = None
    briefs: list[BriefResponse] = Field(default_factory=list)


class NarrativeBlockResponse(BaseModel):
    id: str
    role: str
    text: str
    estimated_duration_seconds: float
    scene_index: int


class NarrativeResponse(BaseModel):
    production_id: str
    template_type_id: str
    variation_id: str
    objective: str
    target_duration_seconds: float
    total_duration: float
    blocks: list[NarrativeBlockResponse] = Field(default_factory=list)


class BriefResponse(BaseModel):
    id: str
    scene_id: str
    scene_index: int
    tema: str
    funcao_visual: str
    assunto_visivel: str
    contexto_geografico_cultural: str
    periodo: str
    tom_editorial: str
    nivel_literalidade: str
    permitidos: list[str]
    proibidos: list[str]
    tipo_ativo_preferido: str
    template_type_id: str

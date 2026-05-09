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

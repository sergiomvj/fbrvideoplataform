from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )


class TemplateModel(Base):
    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )


class NarrativeBlockModel(Base):
    __tablename__ = "narrative_blocks"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    narrative_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("structured_narratives.id", ondelete="SET NULL"), nullable=True
    )
    scene_index: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str | None] = mapped_column(String(30), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_duration_seconds: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)

    narrative: Mapped["StructuredNarrativeModel | None"] = relationship(
        "StructuredNarrativeModel", back_populates="blocks"
    )


class ProductionModel(Base):
    __tablename__ = "productions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    operator_user_id: Mapped[str] = mapped_column(String, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    template_type_id: Mapped[str] = mapped_column(String(50), nullable=False)
    variation_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    base_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    editorial_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_state: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    restrictions: Mapped[list[ProductionRestrictionModel]] = relationship(
        "ProductionRestrictionModel",
        back_populates="production",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    state_transitions: Mapped[list[ProductionStateTransitionModel]] = relationship(
        "ProductionStateTransitionModel",
        back_populates="production",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ProductionStateTransitionModel.occurred_at",
    )


class ProductionRestrictionModel(Base):
    __tablename__ = "production_restrictions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    restriction: Mapped[str] = mapped_column(Text, nullable=False)

    production: Mapped[ProductionModel] = relationship(
        "ProductionModel", back_populates="restrictions"
    )


class ProductionStateTransitionModel(Base):
    __tablename__ = "production_state_transitions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    from_state: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_state: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str] = mapped_column(String(50), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    production: Mapped[ProductionModel] = relationship(
        "ProductionModel", back_populates="state_transitions"
    )


class AssetCandidateModel(Base):
    __tablename__ = "asset_candidates"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    scene_id: Mapped[str] = mapped_column(
        String, ForeignKey("narrative_blocks.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    asset_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")


class VerificationScoreModel(Base):
    __tablename__ = "verification_scores"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    asset_id: Mapped[str] = mapped_column(
        String, ForeignKey("asset_candidates.id", ondelete="CASCADE"), nullable=False
    )
    scene_id: Mapped[str] = mapped_column(
        String, ForeignKey("narrative_blocks.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )


class ReviewQueueItemModel(Base):
    __tablename__ = "review_queue_items"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    scene_id: Mapped[str] = mapped_column(
        String, ForeignKey("narrative_blocks.id", ondelete="CASCADE"), nullable=False
    )
    asset_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("asset_candidates.id"), nullable=True
    )
    score_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("verification_scores.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    reviewed_by: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    scene_index: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    scene_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    asset_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preview_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    brief_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    candidate_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    flags_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class ManualBindingModel(Base):
    __tablename__ = "manual_bindings"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    scene_id: Mapped[str] = mapped_column(
        String, ForeignKey("narrative_blocks.id", ondelete="CASCADE"), nullable=False
    )
    asset_reference: Mapped[str] = mapped_column(Text, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(20), nullable=False)
    bound_by: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )


class CompositionModel(Base):
    __tablename__ = "compositions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    template_type_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("templates.id"), nullable=True
    )
    variation_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    total_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )

    slots: Mapped[list[CompositionSlotModel]] = relationship(
        "CompositionSlotModel",
        back_populates="composition",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CompositionSlotModel.slot_index",
    )


class CompositionSlotModel(Base):
    __tablename__ = "composition_slots"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    composition_id: Mapped[str] = mapped_column(
        String, ForeignKey("compositions.id", ondelete="CASCADE"), nullable=False
    )
    slot_index: Mapped[int] = mapped_column(Integer, nullable=False)
    slot_type: Mapped[str] = mapped_column(String(30), nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    content_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    manual_binding_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("manual_bindings.id"), nullable=True
    )

    composition: Mapped[CompositionModel] = relationship(
        "CompositionModel", back_populates="slots"
    )


class RenderJobModel(Base):
    __tablename__ = "render_jobs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    composition_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("compositions.id"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    external_job_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )

    events: Mapped[list[RenderJobEventModel]] = relationship(
        "RenderJobEventModel",
        back_populates="render_job",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RenderJobEventModel.occurred_at",
    )


class RenderJobEventModel(Base):
    __tablename__ = "render_job_events"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    render_job_id: Mapped[str] = mapped_column(
        String, ForeignKey("render_jobs.id", ondelete="CASCADE"), nullable=False
    )
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )

    render_job: Mapped[RenderJobModel] = relationship(
        "RenderJobModel", back_populates="events"
    )


class StructuredNarrativeModel(Base):
    __tablename__ = "structured_narratives"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    template_type_id: Mapped[str] = mapped_column(String(50), nullable=False)
    variation_id: Mapped[str] = mapped_column(String(10), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    target_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )

    blocks: Mapped[list[NarrativeBlockModel]] = relationship(
        "NarrativeBlockModel",
        back_populates="narrative",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="NarrativeBlockModel.scene_index",
        foreign_keys="[NarrativeBlockModel.narrative_id]",
    )




class VisualBriefModel(Base):
    __tablename__ = "visual_briefs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    scene_id: Mapped[str] = mapped_column(String, nullable=False)
    scene_index: Mapped[int] = mapped_column(Integer, nullable=False)
    tema: Mapped[str] = mapped_column(Text, nullable=False, default="")
    funcao_visual: Mapped[str] = mapped_column(String(30), nullable=False, default="contexto_ambiental")
    assunto_visivel: Mapped[str] = mapped_column(Text, nullable=False, default="")
    contexto_geografico_cultural: Mapped[str] = mapped_column(Text, nullable=True, default="")
    periodo: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    tom_editorial: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    nivel_literalidade: Mapped[str] = mapped_column(String(20), nullable=True, default="media")
    permitidos: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    proibidos: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    tipo_ativo_preferido: Mapped[str] = mapped_column(String(20), nullable=True, default="any")
    template_type_id: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )


class MediaProviderModel(Base):
    __tablename__ = "media_providers"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    provider_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    provider_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    base_url: Mapped[str] = mapped_column(Text, nullable=True, default="")
    api_version: Mapped[str] = mapped_column(String(10), nullable=True, default="v1")
    auth_config: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    operational_config: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, nullable=True, default=60)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=True, default=30)
    disabled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )


class RenderSubmissionModel(Base):
    __tablename__ = "render_submissions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    outcome: Mapped[str | None] = mapped_column(String(30), nullable=True)
    external_job_id: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    provider_response_json: Mapped[str] = mapped_column(Text, nullable=True, default="{}")
    job_states_json: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )


class QueryAttemptModel(Base):
    __tablename__ = "query_attempts"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid4())
    )
    production_id: Mapped[str] = mapped_column(
        String, ForeignKey("productions.id", ondelete="CASCADE"), nullable=False
    )
    scene_id: Mapped[str] = mapped_column(String, nullable=False)
    brief_id: Mapped[str] = mapped_column(String, nullable=False)
    strategy_type: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_key: Mapped[str] = mapped_column(String(50), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    query_params: Mapped[str | None] = mapped_column(Text, nullable=True)
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    diagnostic: Mapped[str | None] = mapped_column(String(30), nullable=True)
    diagnostic_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_attempt_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("query_attempts.id"), nullable=True
    )
    reformulation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

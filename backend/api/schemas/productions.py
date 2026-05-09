from pydantic import BaseModel, Field


class ProductionIntakeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    template_type_id: str = Field(min_length=1)
    variation_id: str = Field(min_length=1)
    mode: str = Field(pattern="^(automatic|manual)$")
    base_content: str = Field(default="")
    editorial_context: str = Field(default="")
    restrictions: list[str] = Field(default_factory=list)


class StateTransitionResponse(BaseModel):
    from_state: str | None
    to_state: str
    occurred_at: str
    reason: str
    triggered_by: str


class ProductionResponse(BaseModel):
    id: str
    title: str
    mode: str
    template_type_id: str
    variation_id: str
    current_state: str
    base_content: str
    editorial_context: str
    restrictions: list[str]
    created_at: str
    updated_at: str
    state_history: list[StateTransitionResponse]
    operator_user_id: str

from pydantic import BaseModel, Field


class ManualBindingCreateRequest(BaseModel):
    production_id: str = Field(min_length=1)
    scene_index: int = Field(ge=0)
    asset_reference: str = Field(min_length=1)
    asset_type: str = Field(pattern="^(image|video)$")
    restrictions: list[str] = Field(default_factory=list)


class ManualBindingResponse(BaseModel):
    id: str
    production_id: str
    scene_index: int
    asset_reference: str
    asset_type: str
    bound_by: str
    created_at: str

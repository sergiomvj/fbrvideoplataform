from pydantic import BaseModel, Field


class VariationResponse(BaseModel):
    id: str
    label: str
    description: str


class TemplateResponse(BaseModel):
    type_id: str
    name: str
    description: str
    aspect_ratio: str
    resolution: str
    max_duration_seconds: int
    max_scenes: int
    min_scenes: int
    supports_broll: bool
    supported_asset_types: list[str]
    variations: list[VariationResponse]


class TemplateListResponse(BaseModel):
    templates: list[TemplateResponse]

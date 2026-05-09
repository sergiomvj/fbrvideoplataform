from pydantic import BaseModel, Field


class ReviewQueueItemResponse(BaseModel):
    id: str
    production_id: str
    scene_id: str
    scene_index: int
    scene_label: str
    asset_id: str
    asset_url: str
    asset_type: str
    source: str
    score: float
    justification: str
    decision: str
    status: str
    preview_url: str


class ReviewActionRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject|requery)$")
    reason: str | None = None


class ReviewListResponse(BaseModel):
    items: list[ReviewQueueItemResponse]
    total_count: int

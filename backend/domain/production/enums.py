from enum import Enum


class ProductionMode(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class TemplateType(str, Enum):
    PRESENTER_SHORT = "presenter_short"
    VIDEODOC_NARRATED = "videodoc_narrated"


class WorkflowState(str, Enum):
    INTAKE = "intake"
    STRUCTURING = "structuring"
    VISUAL_PLANNING = "visual_planning"
    MEDIA_SOURCING = "media_sourcing"
    CONTEXT_VERIFICATION = "context_verification"
    HUMAN_REVIEW = "human_review"
    REQUERY = "requery"
    COMPOSITION = "composition"
    RENDER_PENDING = "render_pending"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"

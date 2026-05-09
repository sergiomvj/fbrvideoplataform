from fastapi import APIRouter
from pydantic import BaseModel

from application.security.auth import CurrentUser
from domain.templates import list_templates, get_template, TEMPLATE_REGISTRY
from api.schemas.templates import TemplateResponse, TemplateListResponse, VariationResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=TemplateListResponse)
async def get_templates(user: CurrentUser) -> TemplateListResponse:
    templates = []
    for t in list_templates():
        templates.append(_to_template_response(t))
    return TemplateListResponse(templates=templates)


@router.get("/{template_type_id}", response_model=TemplateResponse)
async def get_template_detail(
    template_type_id: str, user: CurrentUser
) -> TemplateResponse:
    template = get_template(template_type_id)
    if not template:
        from application.errors import AppError
        raise AppError(message="Template not found", status_code=404)
    return _to_template_response(template)


def _to_template_response(t: "TemplateContract") -> TemplateResponse:
    from domain.templates import TemplateContract
    return TemplateResponse(
        type_id=t.type_id,
        name=t.name,
        description=t.description,
        aspect_ratio=t.aspect_ratio.value,
        resolution=t.resolution.value,
        max_duration_seconds=t.duration_constraint.max_seconds,
        max_scenes=t.composition_constraints.max_scenes,
        min_scenes=t.composition_constraints.min_scenes,
        supports_broll=t.composition_constraints.supports_broll,
        supported_asset_types=[at.value for at in t.supported_asset_types],
        variations=[
            VariationResponse(id=v.id, label=v.label, description=v.description)
            for v in t.variations
        ],
    )

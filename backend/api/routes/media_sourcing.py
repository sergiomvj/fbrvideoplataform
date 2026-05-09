from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from domain.visual_planning import VisualBrief
from domain.media_sourcing import MediaSourceType, SourcingResult
from application.services.media_sourcing import media_sourcing_service
from integrations.stock_media import stock_media_adapter
from integrations.archive_media import archive_media_adapter

router = APIRouter(prefix="/media-sourcing", tags=["media-sourcing"])


class SourceCandidatesRequest(BaseModel):
    production_id: UUID
    scene_id: UUID
    tema: str
    funcao_visual: str
    assunto_visivel: str
    contexto_geografico_cultural: str = ""
    periodo: str = ""
    tom_editorial: str = ""
    permitidos: list[str] = []
    proibidos: list[str] = []
    tipo_ativo_preferido: str = "any"
    source_types: Optional[list[str]] = None
    max_results: int = 10


class SourceCandidatesResponse(BaseModel):
    production_id: UUID
    results: list[dict]


class GetAssetRequest(BaseModel):
    production_id: UUID
    source_type: str
    external_id: str


@router.post("/source", response_model=SourceCandidatesResponse)
async def source_candidates(request: SourceCandidatesRequest):
    brief = VisualBrief(
        scene_id=request.scene_id,
        tema=request.tema,
        funcao_visual=request.funcao_visual,
        assunto_visivel=request.assunto_visivel,
        contexto_geografico_cultural=request.contexto_geografico_cultural,
        periodo=request.periodo,
        tom_editorial=request.tom_editorial,
        permitidos=request.permitidos,
        proibidos=request.proibidos,
        tipo_ativo_preferido=request.tipo_ativo_preferido,
    )

    source_types = None
    if request.source_types:
        source_types = [MediaSourceType(st) for st in request.source_types]

    results = await media_sourcing_service.source_candidates(
        brief=brief,
        production_id=request.production_id,
        source_types=source_types,
        max_results_per_source=request.max_results,
    )

    return SourceCandidatesResponse(
        production_id=request.production_id,
        results=[
            {
                "source_type": r.provider,
                "outcome": r.outcome.value,
                "candidates": [
                    {
                        "id": c.id.hex,
                        "url": c.url,
                        "thumbnail_url": c.thumbnail_url,
                        "media_type": c.media_type.value,
                        "title": c.title,
                    }
                    for c in r.candidates
                ],
                "error": r.error_message,
                "duration_ms": r.duration_ms,
            }
            for r in results
        ],
    )


@router.post("/asset")
async def get_asset(request: GetAssetRequest):
    try:
        source_type = MediaSourceType(request.source_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid source_type")

    result = await media_sourcing_service.get_asset_by_source(
        source_type=source_type,
        external_id=request.external_id,
        production_id=request.production_id,
    )

    if not result:
        raise HTTPException(status_code=404, detail="Source adapter not found")

    return {
        "outcome": result.outcome.value,
        "candidates": [
            {
                "id": c.id.hex,
                "url": c.url,
                "thumbnail_url": c.thumbnail_url,
                "media_type": c.media_type.value,
                "title": c.title,
                "description": c.description,
            }
            for c in result.candidates
        ],
        "error": result.error_message,
    }


def register_adapters(service: media_sourcing_service.__class__):
    service.register_adapter(stock_media_adapter)
    service.register_adapter(archive_media_adapter)
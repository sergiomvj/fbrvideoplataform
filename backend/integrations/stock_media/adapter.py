from datetime import datetime
from uuid import UUID
import time

from domain.media_sourcing import (
    VisualBrief,
    SourcingResult,
    SourcingOutcome,
    MediaCandidate,
    MediaType,
)
from domain.media_sourcing.adapters import StockMediaAdapter


class StockMediaSourceAdapter(StockMediaAdapter):
    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = api_key
        self.base_url = base_url

    async def search(
        self,
        brief: VisualBrief,
        production_id: UUID,
        max_results: int = 10,
    ) -> SourcingResult:
        start_time = time.time()

        try:
            query_params = self._build_query_from_brief(brief)
            candidates = await self._query_provider(query_params, max_results)

            return SourcingResult(
                outcome=SourcingOutcome.SUCCESS,
                candidates=candidates,
                provider="stock_media",
                duration_ms=(time.time() - start_time) * 1000,
                query_parameters=query_params,
            )

        except TimeoutError:
            return SourcingResult(
                outcome=SourcingOutcome.TIMEOUT,
                error_message="Provider timeout",
                provider="stock_media",
                duration_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            return SourcingResult(
                outcome=SourcingOutcome.PROVIDER_ERROR,
                error_message=str(e),
                provider="stock_media",
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def get_asset(self, external_id: str) -> SourcingResult:
        start_time = time.time()

        try:
            asset = await self._fetch_asset_by_id(external_id)
            if asset:
                return SourcingResult(
                    outcome=SourcingOutcome.SUCCESS,
                    candidates=[asset],
                    provider="stock_media",
                    duration_ms=(time.time() - start_time) * 1000,
                )
            else:
                return SourcingResult(
                    outcome=SourcingOutcome.NO_RESULTS,
                    error_message=f"Asset {external_id} not found",
                    provider="stock_media",
                    duration_ms=(time.time() - start_time) * 1000,
                )
        except Exception as e:
            return SourcingResult(
                outcome=SourcingOutcome.PROVIDER_ERROR,
                error_message=str(e),
                provider="stock_media",
                duration_ms=(time.time() - start_time) * 1000,
            )

    def _build_query_from_brief(self, brief: VisualBrief) -> dict:
        keywords = []

        if brief.tema:
            keywords.append(brief.tema)
        if brief.assunto_visivel:
            keywords.append(brief.assunto_visivel)
        if brief.contexto_geografico_cultural:
            keywords.append(brief.contexto_geografico_cultural)

        for term in brief.permitidos[:3]:
            if term not in keywords:
                keywords.append(term)

        return {
            "keywords": " ".join(keywords),
            "aspect_ratio": self._map_aspect_ratio(brief),
            "media_type": brief.tipo_ativo_preferido.value,
            "orientation": self._map_orientation(brief.funcao_visual.value),
        }

    def _map_aspect_ratio(self, brief: VisualBrief) -> str:
        return "16:9"

    def _map_orientation(self, funcao: str) -> str:
        if funcao in ["evidencia_literal", "prova_documental"]:
            return "landscape"
        elif funcao == "metafora_controlada":
            return "square"
        return "any"

    async def _query_provider(self, query: dict, max_results: int) -> list[MediaCandidate]:
        return []

    async def _fetch_asset_by_id(self, external_id: str) -> MediaCandidate | None:
        return None


stock_media_adapter = StockMediaSourceAdapter()
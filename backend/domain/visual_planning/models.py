from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4


class VisualFunction(str, Enum):
    EVIDENCIA_LITERAL = "evidencia_literal"
    CONTEXTO_AMBIENTAL = "contexto_ambiental"
    COBERTURA_BROLL = "cobertura_broll"
    PROVA_DOCUMENTAL = "prova_documental"
    METAFORA_CONTROLADA = "metafora_controlada"


class LiteralidadeLevel(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class AssetTypePreference(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    ANY = "any"


@dataclass(frozen=True)
class VisualBrief:
    id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    scene_index: int = 0
    tema: str = ""
    funcao_visual: VisualFunction = VisualFunction.CONTEXTO_AMBIENTAL
    assunto_visivel: str = ""
    contexto_geografico_cultural: str = ""
    periodo: str = ""
    tom_editorial: str = ""
    nivel_literalidade: LiteralidadeLevel = LiteralidadeLevel.MEDIA
    permitidos: list[str] = field(default_factory=list)
    proibidos: list[str] = field(default_factory=list)
    tipo_ativo_preferido: AssetTypePreference = AssetTypePreference.ANY
    template_type_id: str = ""


@dataclass
class VisualBriefSet:
    production_id: UUID = field(default_factory=uuid4)
    briefs: list[VisualBrief] = field(default_factory=list)

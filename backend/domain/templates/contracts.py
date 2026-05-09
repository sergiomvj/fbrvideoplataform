from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from domain.production.enums import ProductionMode


class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class Resolution(str, Enum):
    HD = "hd"
    TWO_K = "2k"


class AspectRatio(str, Enum):
    NINE_BY_SIXTEEN = "9:16"
    SIXTEEN_BY_NINE = "16:9"


@dataclass(frozen=True)
class DurationConstraint:
    max_seconds: int


@dataclass(frozen=True)
class CompositionConstraints:
    max_scenes: int
    min_scenes: int
    supports_broll: bool
    supports_narration: bool
    supports_presenter: bool


@dataclass(frozen=True)
class VariationContract:
    id: str
    label: str
    description: str
    compatible_modes: list[ProductionMode] = field(
        default_factory=lambda: [ProductionMode.AUTOMATIC, ProductionMode.MANUAL]
    )


@dataclass(frozen=True)
class TemplateContract:
    type_id: str
    name: str
    description: str
    aspect_ratio: AspectRatio
    resolution: Resolution
    duration_constraint: DurationConstraint
    composition_constraints: CompositionConstraints
    supported_asset_types: list[AssetType]
    variations: list[VariationContract]
    compatible_modes: list[ProductionMode] = field(
        default_factory=lambda: [ProductionMode.AUTOMATIC, ProductionMode.MANUAL]
    )

    def get_variation(self, variation_id: str) -> VariationContract | None:
        for variation in self.variations:
            if variation.id == variation_id:
                return variation
        return None

    def validate_mode(self, mode: ProductionMode) -> bool:
        return mode in self.compatible_modes

    def validate_variation(self, variation_id: str) -> bool:
        return self.get_variation(variation_id) is not None

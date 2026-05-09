from domain.templates.contracts import (
    TemplateContract,
    VariationContract,
    DurationConstraint,
    CompositionConstraints,
    AspectRatio,
    Resolution,
    AssetType,
)
from domain.production.enums import ProductionMode


PRESENTER_SHORT = TemplateContract(
    type_id="presenter_short",
    name="Presenter Short",
    description="Short video with avatar presenting the text over institutional background.",
    aspect_ratio=AspectRatio.NINE_BY_SIXTEEN,
    resolution=Resolution.HD,
    duration_constraint=DurationConstraint(max_seconds=60),
    composition_constraints=CompositionConstraints(
        max_scenes=5,
        min_scenes=1,
        supports_broll=False,
        supports_narration=True,
        supports_presenter=True,
    ),
    supported_asset_types=[AssetType.IMAGE],
    variations=[
        VariationContract(
            id="1",
            label="Variation 1",
            description="Standard opening with institutional background.",
        ),
        VariationContract(
            id="2",
            label="Variation 2",
            description="Alternative framing with dynamic background.",
        ),
        VariationContract(
            id="3",
            label="Variation 3",
            description="Compact layout with text overlay emphasis.",
        ),
    ],
)

VIDEODOC_NARRATED = TemplateContract(
    type_id="videodoc_narrated",
    name="VideoDoc Narrated",
    description="Longer video with narration and/or presenter, supporting images and video clips.",
    aspect_ratio=AspectRatio.SIXTEEN_BY_NINE,
    resolution=Resolution.TWO_K,
    duration_constraint=DurationConstraint(max_seconds=180),
    composition_constraints=CompositionConstraints(
        max_scenes=12,
        min_scenes=2,
        supports_broll=True,
        supports_narration=True,
        supports_presenter=True,
    ),
    supported_asset_types=[AssetType.IMAGE, AssetType.VIDEO],
    variations=[
        VariationContract(
            id="1",
            label="Variation 1",
            description="Narrator-led with B-roll cuts.",
        ),
        VariationContract(
            id="2",
            label="Variation 2",
            description="Presenter-focused with supporting imagery.",
        ),
        VariationContract(
            id="3",
            label="Variation 3",
            description="Documentary style with mixed media collage.",
        ),
    ],
)

TEMPLATE_REGISTRY: list[TemplateContract] = [PRESENTER_SHORT, VIDEODOC_NARRATED]

REGISTRY_BY_TYPE_ID: dict[str, TemplateContract] = {
    t.type_id: t for t in TEMPLATE_REGISTRY
}


def get_template(template_type_id: str) -> TemplateContract | None:
    return REGISTRY_BY_TYPE_ID.get(template_type_id)


def list_templates() -> list[TemplateContract]:
    return TEMPLATE_REGISTRY

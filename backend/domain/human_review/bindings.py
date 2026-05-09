from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class ManualBinding:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    asset_reference: str = ""
    asset_type: str = ""
    bound_by: str = ""


class AssetBindingStore:
    def __init__(self) -> None:
        self._bindings: dict[UUID, ManualBinding] = {}

    async def add_binding(
        self,
        production_id: UUID,
        scene_id: UUID,
        asset_reference: str,
        asset_type: str,
        bound_by: str,
    ) -> ManualBinding:
        binding = ManualBinding(
            production_id=production_id,
            scene_id=scene_id,
            asset_reference=asset_reference,
            asset_type=asset_type,
            bound_by=bound_by,
        )
        self._bindings[binding.id] = binding
        return binding

    async def get_bindings(self, production_id: UUID) -> list[ManualBinding]:
        return [
            b for b in self._bindings.values()
            if b.production_id == production_id
        ]


asset_binding_store = AssetBindingStore()

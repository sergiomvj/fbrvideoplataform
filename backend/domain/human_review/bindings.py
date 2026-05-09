from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional


class BindingType(str, Enum):
    REQUIRED = "required"
    FIXED = "fixed"
    PROHIBITED = "prohibited"
    PREFERRED = "preferred"


class AssetBindingStatus(str, Enum):
    ACTIVE = "active"
    OVERRIDDEN = "overridden"
    REMOVED = "removed"


@dataclass
class ManualBinding:
    production_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    asset_reference: str = ""
    asset_type: str = ""
    bound_by: str = ""


@dataclass
class AssetBinding:
    id: UUID = field(default_factory=uuid4)
    production_id: UUID = field(default_factory=uuid4)
    scene_id: UUID = field(default_factory=uuid4)
    block_id: Optional[UUID] = None
    candidate_id: Optional[UUID] = None
    binding_type: BindingType = BindingType.PREFERRED
    asset_url: str = ""
    asset_title: str = ""
    bound_by: str = ""
    bound_at: datetime = field(default_factory=datetime.utcnow)
    status: AssetBindingStatus = AssetBindingStatus.ACTIVE
    template_type_id: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id.hex,
            "production_id": self.production_id.hex,
            "scene_id": self.scene_id.hex,
            "block_id": self.block_id.hex if self.block_id else None,
            "candidate_id": self.candidate_id.hex if self.candidate_id else None,
            "binding_type": self.binding_type.value,
            "asset_url": self.asset_url,
            "asset_title": self.asset_title,
            "bound_by": self.bound_by,
            "bound_at": self.bound_at.isoformat(),
            "status": self.status.value,
            "template_type_id": self.template_type_id,
        }


class AssetBindingManager:
    def __init__(self):
        self._bindings: dict[UUID, AssetBinding] = {}

    async def create_binding(
        self,
        production_id: UUID,
        scene_id: UUID,
        candidate_id: UUID,
        binding_type: BindingType,
        asset_url: str,
        asset_title: str,
        bound_by: str,
        block_id: Optional[UUID] = None,
        template_type_id: str = "",
        metadata: Optional[dict] = None,
    ) -> AssetBinding:
        binding = AssetBinding(
            production_id=production_id,
            scene_id=scene_id,
            block_id=block_id,
            candidate_id=candidate_id,
            binding_type=binding_type,
            asset_url=asset_url,
            asset_title=asset_title,
            bound_by=bound_by,
            template_type_id=template_type_id,
            metadata=metadata or {},
        )
        self._bindings[binding.id] = binding
        return binding

    def get_binding(self, binding_id: UUID) -> Optional[AssetBinding]:
        return self._bindings.get(binding_id)

    def get_bindings_for_scene(
        self, production_id: UUID, scene_id: UUID
    ) -> list[AssetBinding]:
        return [
            b
            for b in self._bindings.values()
            if b.production_id == production_id
            and b.scene_id == scene_id
            and b.status == AssetBindingStatus.ACTIVE
        ]

    def get_bindings_for_production(
        self, production_id: UUID
    ) -> list[AssetBinding]:
        return [
            b
            for b in self._bindings.values()
            if b.production_id == production_id
            and b.status == AssetBindingStatus.ACTIVE
        ]

    def get_authoritative_binding(
        self, production_id: UUID, scene_id: UUID, block_id: Optional[UUID] = None
    ) -> Optional[AssetBinding]:
        bindings = self.get_bindings_for_scene(production_id, scene_id)
        if block_id:
            bindings = [b for b in bindings if b.block_id == block_id]

        required = [b for b in bindings if b.binding_type == BindingType.REQUIRED]
        if required:
            return required[0]

        fixed = [b for b in bindings if b.binding_type == BindingType.FIXED]
        if fixed:
            return fixed[0]

        preferred = [b for b in bindings if b.binding_type == BindingType.PREFERRED]
        if preferred:
            return preferred[0]

        return None

    def remove_binding(self, binding_id: UUID) -> Optional[AssetBinding]:
        binding = self._bindings.get(binding_id)
        if binding:
            binding.status = AssetBindingStatus.REMOVED
            return binding
        return None


binding_manager = AssetBindingManager()

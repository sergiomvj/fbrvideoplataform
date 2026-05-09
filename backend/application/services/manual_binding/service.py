from uuid import UUID
from typing import Optional

from domain.human_review import (
    AssetBinding,
    BindingType,
    AssetBindingStatus,
    binding_manager,
)
from domain.audit import audit_service, AuditEventType
from infrastructure.logging import get_logger, LoggingContext

logger = get_logger(__name__)


class ManualBindingService:
    def __init__(self):
        self._binding_manager = binding_manager

    async def bind_asset(
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
    ) -> AssetBinding:
        with LoggingContext(
            production_id=production_id.hex,
            scene_id=scene_id.hex,
            asset_id=candidate_id.hex,
        ):
            if template_type_id:
                self._validate_template_compatibility(
                    template_type_id, binding_type, scene_id
                )

            binding = await self._binding_manager.create_binding(
                production_id=production_id,
                scene_id=scene_id,
                candidate_id=candidate_id,
                binding_type=binding_type,
                asset_url=asset_url,
                asset_title=asset_title,
                bound_by=bound_by,
                block_id=block_id,
                template_type_id=template_type_id,
            )

            logger.info(
                "asset_bound",
                binding_id=binding.id.hex,
                binding_type=binding_type.value,
                scene_id=scene_id.hex,
            )

            self._emit_audit_event(binding, "created")

            return binding

    def _validate_template_compatibility(
        self, template_type_id: str, binding_type: BindingType, scene_id: UUID
    ) -> None:
        if binding_type == BindingType.PROHIBITED:
            logger.warning(
                "prohibited_binding_may_impact_template",
                template_type_id=template_type_id,
                scene_id=scene_id.hex,
            )

        logger.debug(
            "template_compatibility_validated",
            template_type_id=template_type_id,
            binding_type=binding_type.value,
        )

    async def get_bindings_for_scene(
        self, production_id: UUID, scene_id: UUID
    ) -> list[AssetBinding]:
        return self._binding_manager.get_bindings_for_scene(production_id, scene_id)

    async def get_bindings_for_production(
        self, production_id: UUID
    ) -> list[AssetBinding]:
        return self._binding_manager.get_bindings_for_production(production_id)

    async def get_authoritative_binding(
        self, production_id: UUID, scene_id: UUID, block_id: Optional[UUID] = None
    ) -> Optional[AssetBinding]:
        return self._binding_manager.get_authoritative_binding(
            production_id, scene_id, block_id
        )

    async def remove_binding(
        self, binding_id: UUID, removed_by: str
    ) -> Optional[AssetBinding]:
        binding = self._binding_manager.remove_binding(binding_id)
        if binding:
            logger.info(
                "binding_removed",
                binding_id=binding_id.hex,
                removed_by=removed_by,
            )
            self._emit_audit_event(binding, "removed")
        return binding

    def _emit_audit_event(self, binding: AssetBinding, action: str) -> None:
        audit_service.emit(
            event_type=AuditEventType.ASSET_PROCESSED,
            entity_type="manual_binding",
            entity_id=binding.id.hex,
            actor_id=binding.bound_by,
            actor_type="operator",
            before_state=None,
            after_state={
                "binding_type": binding.binding_type.value,
                "scene_id": binding.scene_id.hex,
                "asset_url": binding.asset_url,
            },
            metadata={
                "action": action,
                "template_type_id": binding.template_type_id,
            },
        )


manual_binding_service = ManualBindingService()
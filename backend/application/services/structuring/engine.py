from __future__ import annotations

import re
from math import ceil

from domain.production.aggregate import Production
from domain.production.enums import TemplateType
from domain.structuring.errors import StructuringError, StructuringReason
from domain.structuring.models import (
    NarrativeBase,
    NarrativeBlock,
    NarrativeRole,
)
from domain.templates.registry import get_template

WORDS_PER_SECOND = 2.5
MIN_SENTENCE_LENGTH = 10


class StructuringEngine:
    async def structure(self, production: Production) -> NarrativeBase:
        if not production.template_selection:
            raise StructuringError(
                message="Production has no template selection",
                template_type_id="",
                reason=StructuringReason.TEMPLATE_INCOMPATIBLE,
            )

        template_type_id = production.template_selection.template_type.value
        variation_id = production.template_selection.variation_id
        template = get_template(template_type_id)

        if template is None:
            raise StructuringError(
                message=f"Template '{template_type_id}' not found in registry",
                template_type_id=template_type_id,
                reason=StructuringReason.TEMPLATE_INCOMPATIBLE,
            )

        content = production.base_content
        if not content or len(content.strip()) < MIN_SENTENCE_LENGTH:
            raise StructuringError(
                message="Content is empty or too short to structure",
                template_type_id=template_type_id,
                reason=StructuringReason.INSUFFICIENT_CONTENT,
            )

        sentences = self._split_into_sentences(content)
        if not sentences:
            raise StructuringError(
                message="Could not extract sentences from content",
                template_type_id=template_type_id,
                reason=StructuringReason.INSUFFICIENT_CONTENT,
            )

        constraints = template.composition_constraints
        duration_constraint = template.duration_constraint

        if template_type_id == TemplateType.PRESENTER_SHORT.value:
            blocks = self._structure_presenter_short(
                sentences, constraints.max_scenes, duration_constraint.max_seconds
            )
        elif template_type_id == TemplateType.VIDEODOC_NARRATED.value:
            blocks = self._structure_videodoc_narrated(
                sentences, constraints.max_scenes, duration_constraint.max_seconds
            )
        else:
            raise StructuringError(
                message=f"No structuring strategy for template '{template_type_id}'",
                template_type_id=template_type_id,
                reason=StructuringReason.TEMPLATE_INCOMPATIBLE,
            )

        if len(blocks) < constraints.min_scenes:
            raise StructuringError(
                message=f"Content produced {len(blocks)} blocks, minimum is {constraints.min_scenes}",
                template_type_id=template_type_id,
                reason=StructuringReason.CONTENT_TOO_SHORT,
            )

        total_duration = sum(b.estimated_duration_seconds for b in blocks)
        if total_duration > duration_constraint.max_seconds:
            blocks = self._scale_durations(blocks, duration_constraint.max_seconds)

        objective = self._derive_objective(production)

        return NarrativeBase(
            production_id=production.id,
            template_type_id=template_type_id,
            variation_id=variation_id,
            objective=objective,
            target_duration_seconds=duration_constraint.max_seconds,
            blocks=blocks,
        )

    def _split_into_sentences(self, text: str) -> list[str]:
        parts = re.split(r'(?<=[.!?])\s+', text.strip())
        return [p.strip() for p in parts if len(p.strip()) >= MIN_SENTENCE_LENGTH]

    def _estimate_duration(self, text: str) -> float:
        word_count = len(text.split())
        return word_count / WORDS_PER_SECOND

    def _structure_presenter_short(
        self,
        sentences: list[str],
        max_scenes: int,
        max_duration: int,
    ) -> list[NarrativeBlock]:
        num_blocks = min(max(1, len(sentences)), max_scenes)
        chunk_size = max(1, ceil(len(sentences) / num_blocks))

        blocks: list[NarrativeBlock] = []
        for i in range(num_blocks):
            start = i * chunk_size
            end = min(start + chunk_size, len(sentences))
            chunk = sentences[start:end]

            if not chunk:
                break

            text = " ".join(chunk)
            duration = self._estimate_duration(text)

            if i == 0:
                role = NarrativeRole.OPENING
            elif i == num_blocks - 1:
                role = NarrativeRole.CLOSING
            else:
                role = NarrativeRole.DEVELOPMENT

            blocks.append(NarrativeBlock(
                role=role,
                text=text,
                estimated_duration_seconds=duration,
                scene_index=i,
            ))

        total = sum(b.estimated_duration_seconds for b in blocks)
        if total > max_duration:
            blocks = self._scale_durations(blocks, max_duration)

        return blocks

    def _structure_videodoc_narrated(
        self,
        sentences: list[str],
        max_scenes: int,
        max_duration: int,
    ) -> list[NarrativeBlock]:
        num_blocks = min(max(2, len(sentences)), max_scenes)
        chunk_size = max(1, ceil(len(sentences) / num_blocks))

        blocks: list[NarrativeBlock] = []
        for i in range(num_blocks):
            start = i * chunk_size
            end = min(start + chunk_size, len(sentences))
            chunk = sentences[start:end]

            if not chunk:
                break

            text = " ".join(chunk)
            duration = self._estimate_duration(text)

            if i == 0:
                role = NarrativeRole.OPENING
            elif i == 1:
                role = NarrativeRole.CONTEXT
            elif i == num_blocks - 1:
                role = NarrativeRole.CLOSING
            elif i == num_blocks - 2:
                role = NarrativeRole.CLIMAX
            elif i % 3 == 0 and i < num_blocks - 2:
                role = NarrativeRole.TRANSITION
            else:
                role = NarrativeRole.DEVELOPMENT

            blocks.append(NarrativeBlock(
                role=role,
                text=text,
                estimated_duration_seconds=duration,
                scene_index=i,
            ))

        total = sum(b.estimated_duration_seconds for b in blocks)
        if total > max_duration:
            blocks = self._scale_durations(blocks, max_duration)

        return blocks

    def _scale_durations(
        self, blocks: list[NarrativeBlock], max_duration: int
    ) -> list[NarrativeBlock]:
        total = sum(b.estimated_duration_seconds for b in blocks)
        if total == 0:
            return blocks
        ratio = max_duration / total
        return [
            NarrativeBlock(
                id=b.id,
                role=b.role,
                text=b.text,
                estimated_duration_seconds=round(b.estimated_duration_seconds * ratio, 2),
                scene_index=b.scene_index,
            )
            for b in blocks
        ]

    def _derive_objective(self, production: Production) -> str:
        parts: list[str] = []
        if production.title:
            parts.append(production.title)
        if production.editorial_context:
            parts.append(production.editorial_context)
        return " - ".join(parts) if parts else "Produce video content"

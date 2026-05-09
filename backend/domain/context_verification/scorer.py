from uuid import UUID

from domain.visual_planning.models import VisualBrief, VisualFunction
from domain.media_sourcing import MediaCandidate
from .contracts import VerificationResult, ScoreBreakdown, VerificationFlag


class ContextScorer:
    WEIGHTS = {
        "theme_relevance": 0.20,
        "scene_alignment": 0.25,
        "geographic_coherence": 0.10,
        "temporal_coherence": 0.10,
        "editorial_coherence": 0.15,
        "visual_adequacy": 0.15,
        "conflict_absence": 0.05,
    }

    def score(
        self,
        candidate: MediaCandidate,
        brief: VisualBrief,
        production_id: UUID,
    ) -> VerificationResult:
        breakdown = self._compute_breakdown(candidate, brief)
        score = self._compute_weighted_score(breakdown)
        flags = self._extract_flags(breakdown, brief, candidate)
        rationale = self._generate_rationale(breakdown, flags)

        result = VerificationResult(
            candidate_id=candidate.id,
            brief_id=brief.id,
            production_id=production_id,
            score=round(score, 2),
            breakdown=breakdown,
            flags=flags,
            rationale=rationale,
            details={
                "candidate_title": candidate.title,
                "brief_tema": brief.tema,
                "funcao_visual": brief.funcao_visual.value,
            },
        )

        return result

    def _compute_breakdown(
        self,
        candidate: MediaCandidate,
        brief: VisualBrief,
    ) -> ScoreBreakdown:
        theme_score = self._score_theme_relevance(candidate, brief)
        scene_score = self._score_scene_alignment(candidate, brief)
        geo_score = self._score_geographic_coherence(candidate, brief)
        temporal_score = self._score_temporal_coherence(candidate, brief)
        editorial_score = self._score_editorial_coherence(candidate, brief)
        visual_score = self._score_visual_adequacy(candidate, brief)
        conflict_score = self._score_conflict_absence(candidate, brief)

        return ScoreBreakdown(
            theme_relevance=theme_score,
            scene_alignment=scene_score,
            geographic_coherence=geo_score,
            temporal_coherence=temporal_score,
            editorial_coherence=editorial_score,
            visual_adequacy=visual_score,
            conflict_absence=conflict_score,
        )

    def _compute_weighted_score(self, breakdown: ScoreBreakdown) -> float:
        score = 0.0
        for criterion, weight in self.WEIGHTS.items():
            value = getattr(breakdown, criterion)
            score += value * weight
        return score * 100

    def _score_theme_relevance(self, candidate: MediaCandidate, brief: VisualBrief) -> float:
        if not brief.tema:
            return 0.5

        candidate_text = f"{candidate.title} {candidate.description}".lower()
        brief_terms = brief.tema.lower().split()

        matches = sum(1 for term in brief_terms if term in candidate_text)
        return min(matches / max(len(brief_terms), 1), 1.0)

    def _score_scene_alignment(self, candidate: MediaCandidate, brief: VisualBrief) -> float:
        if not brief.assunto_visivel:
            return 0.5

        candidate_text = f"{candidate.title} {candidate.description}".lower()
        subject_terms = brief.assunto_visivel.lower().split()

        matches = sum(1 for term in subject_terms if term in candidate_text)
        return min(matches / max(len(subject_terms), 1), 1.0)

    def _score_geographic_coherence(
        self, candidate: MediaCandidate, brief: VisualBrief
    ) -> float:
        if not brief.contexto_geografico_cultural:
            return 0.5

        candidate_text = f"{candidate.title} {candidate.description}".lower()
        location = brief.contexto_geografico_cultural.lower()

        if location in candidate_text:
            return 1.0

        location_terms = location.split()
        matches = sum(1 for term in location_terms if term in candidate_text)
        return min(matches / max(len(location_terms), 1), 0.7)

    def _score_temporal_coherence(self, candidate: MediaCandidate, brief: VisualBrief) -> float:
        if not brief.periodo:
            return 0.5

        candidate_text = f"{candidate.title} {candidate.description}".lower()
        period = brief.periodo.lower()

        if period in candidate_text:
            return 1.0

        return 0.3

    def _score_editorial_coherence(self, candidate: MediaCandidate, brief: VisualBrief) -> float:
        if not brief.tom_editorial:
            return 0.5

        candidate_text = f"{candidate.title} {candidate.description}".lower()
        tone = brief.tom_editorial.lower()

        positive_indicators = ["professional", "clean", "modern", "corporate", "business"]
        negative_indicators = ["casual", "party", "informal"]

        if tone in ["formal", "corporate", "profissional"]:
            if any(ind in candidate_text for ind in positive_indicators):
                return 0.9
            if any(ind in candidate_text for ind in negative_indicators):
                return 0.3
        elif tone in ["casual", "informal"]:
            if any(ind in candidate_text for ind in negative_indicators):
                return 0.9
            if any(ind in candidate_text for ind in positive_indicators):
                return 0.6

        return 0.5

    def _score_visual_adequacy(self, candidate: MediaCandidate, brief: VisualBrief) -> float:
        function = brief.funcao_visual

        if function == VisualFunction.EVIDENCIA_LITERAL:
            if candidate.metadata.get("type") == "photo":
                return 0.9
            return 0.6
        elif function == VisualFunction.CONTEXTO_AMBIENTAL:
            if candidate.metadata.get("type") in ["photo", "video"]:
                return 0.8
            return 0.4
        elif function == VisualFunction.COBERTURA_BROLL:
            if candidate.media_type.value == "video":
                return 0.9
            return 0.5

        return 0.5

    def _score_conflict_absence(
        self, candidate: MediaCandidate, brief: VisualBrief
    ) -> float:
        if not brief.proibidos:
            return 1.0

        candidate_text = f"{candidate.title} {candidate.description}".lower()
        conflicts = [term.lower() for term in brief.proibidos]

        conflicts_found = sum(1 for term in conflicts if term in candidate_text)
        return max(1.0 - (conflicts_found * 0.3), 0.0)

    def _extract_flags(
        self, breakdown: ScoreBreakdown, brief: VisualBrief, candidate: MediaCandidate
    ) -> list[VerificationFlag]:
        flags = []

        if breakdown.theme_relevance < 0.4:
            flags.append(VerificationFlag.THEME_MISMATCH)
        if breakdown.scene_alignment < 0.4:
            flags.append(VerificationFlag.SCENE_MISMATCH)
        if breakdown.geographic_coherence < 0.3:
            flags.append(VerificationFlag.GEOGRAPHIC_MISMATCH)
        if breakdown.temporal_coherence < 0.3:
            flags.append(VerificationFlag.TEMPORAL_MISMATCH)
        if breakdown.editorial_coherence < 0.4:
            flags.append(VerificationFlag.EDITORIAL_MISMATCH)
        if breakdown.visual_adequacy < 0.4:
            flags.append(VerificationFlag.VISUAL_INADEQUATE)
        if breakdown.conflict_absence < 0.7:
            flags.append(VerificationFlag.CONFLICT_DETECTED)

        if breakdown.theme_relevance > 0.6 and breakdown.scene_alignment > 0.6:
            pass

        return flags

    def _generate_rationale(
        self, breakdown: ScoreBreakdown, flags: list[VerificationFlag]
    ) -> str:
        if not flags:
            return "All criteria passed with high confidence."

        reasons = []
        for flag in flags[:3]:
            reason = {
                VerificationFlag.THEME_MISMATCH: "Theme relevance below threshold",
                VerificationFlag.SCENE_MISMATCH: "Scene alignment insufficient",
                VerificationFlag.GEOGRAPHIC_MISMATCH: "Geographic context mismatch",
                VerificationFlag.TEMPORAL_MISMATCH: "Temporal coherence unclear",
                VerificationFlag.EDITORIAL_MISMATCH: "Editorial tone inconsistent",
                VerificationFlag.VISUAL_INADEQUATE: "Visual type inadequate for function",
                VerificationFlag.CONFLICT_DETECTED: "Prohibited content detected",
                VerificationFlag.AMBIGUITY_DETECTED: "Ambiguous assessment",
            }.get(flag, "Unknown issue")
            reasons.append(reason)

        return "; ".join(reasons)


context_scorer = ContextScorer()
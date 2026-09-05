from __future__ import annotations

from green_river.scoring.models import (
    Recommendation,
)


MAX_MODELED_ESTIMATE = 0.20

DISCLAIMER = (
    "heuristic estimate, not a guaranteed outcome"
)


def apply_guardrails(
    recommendations: list[Recommendation],
) -> list[Recommendation]:
    guarded = []

    for recommendation in recommendations:
        estimate = min(
            max(
                recommendation.modeled_estimate,
                0.0,
            ),
            MAX_MODELED_ESTIMATE,
        )

        evidence_count = len(
            recommendation.evidence
        )

        confidence = recommendation.confidence

        if evidence_count < 2:
            confidence = "low"

        guarded.append(
            recommendation.model_copy(
                update={
                    "modeled_estimate": estimate,
                    "disclaimer": DISCLAIMER,
                    "confidence": confidence,
                }
            )
        )

    return guarded

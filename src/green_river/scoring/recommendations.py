from __future__ import annotations

from green_river.scoring.models import (
    Recommendation,
)


DISCLAIMER = (
    "heuristic estimate, not a guaranteed outcome"
)


def generate_recommendations(
    *,
    spec_completeness: float,
    is_overpriced: bool,
    price_percentile: float,
    feature_count_gap: float,
) -> list[Recommendation]:
    recommendations = []

    if spec_completeness < 0.70:
        recommendations.append(
            Recommendation(
                title="Complete your product spec sheet",
                priority="high",
                reasoning=(
                    "The merchant listing has less than 70% "
                    "of the defined product fields populated."
                ),
                modeled_estimate=0.10,
                disclaimer=DISCLAIMER,
                confidence="high",
                evidence={
                    "spec_completeness": round(
                        spec_completeness,
                        4,
                    ),
                    "threshold": 0.70,
                },
            )
        )

    if is_overpriced:
        recommendations.append(
            Recommendation(
                title="Reduce price or justify premium",
                priority="high",
                reasoning=(
                    "The merchant price is at or above "
                    "the 75th percentile of comparable "
                    "competitor prices."
                ),
                modeled_estimate=0.08,
                disclaimer=DISCLAIMER,
                confidence="medium",
                evidence={
                    "price_percentile": round(
                        price_percentile,
                        4,
                    ),
                    "threshold": 0.75,
                },
            )
        )

    if feature_count_gap < -2:
        recommendations.append(
            Recommendation(
                title="Add missing features to listing",
                priority="medium",
                reasoning=(
                    "The merchant listing contains more "
                    "than two fewer features than the "
                    "competitor average."
                ),
                modeled_estimate=0.06,
                disclaimer=DISCLAIMER,
                confidence="high",
                evidence={
                    "feature_count_gap": round(
                        feature_count_gap,
                        2,
                    ),
                    "threshold": -2,
                },
            )
        )

    return recommendations

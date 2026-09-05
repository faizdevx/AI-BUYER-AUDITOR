from __future__ import annotations

from green_river.audit.service import (
    compute_audit_trail,
)

from green_river.competitors.graph import (
    discover_competitors,
)

from green_river.db import (
    get_product,
    save_score_report,
)

from green_river.models import (
    StructuredProduct,
)

from green_river.scoring.calculations import (
    compute_feature_gap,
    compute_price_percentile,
    compute_spec_completeness,
)

from green_river.scoring.guardrails import (
    apply_guardrails,
)

from green_river.scoring.models import (
    GapAnalysis,
    ScoreReport,
)

from green_river.scoring.recommendations import (
    generate_recommendations,
)


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(
        minimum,
        min(value, maximum),
    )


async def compute_score_report(
    merchant_id: int,
) -> ScoreReport:
    merchant = get_product(
        merchant_id
    )

    if merchant is None:
        raise ValueError(
            f"Merchant product {merchant_id} was not found."
        )

    merchant_product = (
        StructuredProduct.model_validate(
            merchant["product_json"]
        )
    )

    merchant_product_id = merchant_product.product_id

    if not merchant_product_id:
        raise ValueError(
            f"Merchant {merchant_id} has no product_id."
        )

    audit = compute_audit_trail(
        merchant_id=merchant_id,
        merchant_product_id=merchant_product_id,
    )

    competitor_result = await discover_competitors(
        merchant_id
    )

    competitors = [
        StructuredProduct.model_validate(
            item["product"]
        )
        for item in competitor_result[
            "competitors"
        ]
    ]

    comparable_prices = [
        (
            competitor.price,
            competitor.currency,
        )
        for competitor in competitors
    ]

    price_percentile = (
        compute_price_percentile(
            merchant_product.price,
            merchant_product.currency,
            comparable_prices,
        )
    )

    spec_completeness = (
        compute_spec_completeness(
            merchant_product,
            competitors,
        )
    )

    feature_gap = compute_feature_gap(
        merchant_product.features,
        [
            competitor.features
            for competitor in competitors
        ],
    )

    is_overpriced = (
        price_percentile >= 0.75
    )

    recommendations = (
        generate_recommendations(
            spec_completeness=spec_completeness,
            is_overpriced=is_overpriced,
            price_percentile=price_percentile,
            feature_count_gap=feature_gap,
        )
    )

    recommendations = apply_guardrails(
        recommendations
    )

    price_score = (
        1.0 - price_percentile
    )

    feature_score = _clamp(
        0.5 + (feature_gap / 10.0)
    )

    overall_score = (
        0.50 * audit.win_rate
        + 0.20 * spec_completeness
        + 0.15 * price_score
        + 0.15 * feature_score
    )

    report = ScoreReport(
        merchant_id=merchant_id,
        current_win_rate=audit.win_rate,
        overall_score=round(
            overall_score,
            4,
        ),
        gap_analysis=GapAnalysis(
            price_percentile=round(
                price_percentile,
                4,
            ),
            is_overpriced=is_overpriced,
            spec_completeness_score=round(
                spec_completeness,
                4,
            ),
            feature_count_vs_competitor_avg=round(
                feature_gap,
                2,
            ),
        ),
        recommendations=recommendations,
    )

    save_score_report(
        merchant_id,
        report.model_dump(),
    )

    return report

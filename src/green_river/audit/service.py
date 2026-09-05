from __future__ import annotations

from green_river.audit.models import (
    AuditTrail,
    PromptResult,
)
from green_river.audit.reasoning import (
    extract_loss_reasons,
)
from green_river.db import (
    get_buyer_simulations,
)


def compute_audit_trail(
    merchant_id: int,
    merchant_product_id: str,
) -> AuditTrail:
    simulations = get_buyer_simulations(
        merchant_id,
    )

    if not simulations:
        raise ValueError(
            f"No buyer simulations found for merchant {merchant_id}."
        )

    total_simulations = len(simulations)

    times_shown = 0
    times_chosen_top3 = 0
    times_rank1 = 0

    per_prompt_results: list[PromptResult] = []
    losses: list[dict] = []

    for simulation in simulations:
        if simulation["status"] != "completed":
            continue

        ranked_products = (
            simulation["ranked_products"]
            or []
        )

        merchant_rank = None
        merchant_reasoning = None

        for item in ranked_products:
            product_id = str(
                item.get("product_id", "")
            )

            if product_id == str(merchant_product_id):
                merchant_rank = item.get("rank")
                merchant_reasoning = item.get(
                    "reasoning"
                )
                break

        if merchant_rank is not None:
            times_shown += 1

            if merchant_rank <= 3:
                times_chosen_top3 += 1

            if merchant_rank == 1:
                times_rank1 += 1
            else:
                losses.append(
                    {
                        "prompt": simulation["prompt"],
                        "merchant_rank": merchant_rank,
                        "reasoning": merchant_reasoning,
                    }
                )

        per_prompt_results.append(
            PromptResult(
                prompt=simulation["prompt"],
                merchant_rank=merchant_rank,
                reasoning_for_merchant=merchant_reasoning,
            )
        )

    win_rate = (
        times_rank1 / times_shown
        if times_shown
        else 0.0
    )

    top3_rate = (
        times_chosen_top3 / times_shown
        if times_shown
        else 0.0
    )

    loss_reasons = extract_loss_reasons(
        losses
    )

    return AuditTrail(
        merchant_id=merchant_id,
        total_simulations=total_simulations,
        times_shown=times_shown,
        times_chosen_top3=times_chosen_top3,
        times_rank1=times_rank1,
        win_rate=round(win_rate, 4),
        top3_rate=round(top3_rate, 4),
        loss_reasons=loss_reasons,
        per_prompt_results=per_prompt_results,
    )

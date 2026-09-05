from __future__ import annotations

from pydantic import BaseModel

from green_river.models import StructuredProduct


class SimulationCandidate(BaseModel):
    product_id: str
    product: StructuredProduct


def build_candidate_payload(
    candidates: list[SimulationCandidate],
) -> list[dict]:
    return [
        {
            "product_id": candidate.product_id,
            "product": candidate.product.model_dump(
                exclude_none=True,
            ),
        }
        for candidate in candidates
    ]
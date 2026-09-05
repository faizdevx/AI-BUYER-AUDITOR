from __future__ import annotations

from pydantic import BaseModel, Field


class PromptResult(BaseModel):
    prompt: str
    merchant_rank: int | None
    reasoning_for_merchant: str | None


class AuditTrail(BaseModel):
    merchant_id: int

    total_simulations: int

    times_shown: int
    times_chosen_top3: int
    times_rank1: int

    win_rate: float
    top3_rate: float

    loss_reasons: list[str] = Field(
        default_factory=list
    )

    per_prompt_results: list[PromptResult] = Field(
        default_factory=list
    )

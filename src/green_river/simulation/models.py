from __future__ import annotations

from pydantic import BaseModel, Field


class RankedProduct(BaseModel):
    product_id: str
    rank: int = Field(ge=1)
    reasoning: str = Field(min_length=1)


class BuyerDecision(BaseModel):
    prompt: str
    llm_provider: str
    ranked_products: list[RankedProduct]
    chosen: bool
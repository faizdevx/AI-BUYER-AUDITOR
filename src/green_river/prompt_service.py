from __future__ import annotations

from green_river.db import (
    get_product,
    save_buyer_prompts,
)
from green_river.llm.prompt_generator import (
    generate_buyer_prompts,
)
from green_river.models import StructuredProduct


def generate_and_store_buyer_prompts(
    merchant_id: int,
) -> list[dict]:
    merchant = get_product(merchant_id)

    if merchant is None:
        raise ValueError(
            f"Merchant product {merchant_id} was not found."
        )

    product = StructuredProduct.model_validate(
        merchant["product_json"]
    )

    prompts = generate_buyer_prompts(product)

    if len(prompts) != 10:
        raise ValueError(
            f"Prompt generator returned {len(prompts)} prompts; expected 10."
        )

    return save_buyer_prompts(
        merchant_id,
        prompts,
    )
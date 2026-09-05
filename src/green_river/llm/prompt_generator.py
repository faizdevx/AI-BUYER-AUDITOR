from __future__ import annotations

from green_river.llm.graph import llm
from green_river.models import StructuredProduct
from green_river.prompts import BuyerPromptSet


INTENT_TYPES = [
    "budget",
    "feature",
    "use_case",
    "comparison",
    "value",
    "alternative",
    "quality",
    "beginner",
    "expert",
    "purchase_decision",
]


def generate_buyer_prompts(
    structured_product: StructuredProduct,
) -> list[dict]:
    """
    Generate exactly 10 realistic and diverse buyer prompts
    for a single merchant product.
    """

    product_json = structured_product.model_dump_json(
        exclude_none=True,
    )

    prompt = f"""
You are a shopping-intent simulation agent.

Given the product below, generate exactly 10 realistic buyer
questions that a real shopper might type into a search engine,
shopping assistant, or AI shopping agent.

PRODUCT:
{product_json}

Generate exactly one prompt for each of these intent types:

1. budget
   Shopper is constrained by price.

2. feature
   Shopper cares about a specific product feature.

3. use_case
   Shopper describes a real situation or job they need the product for.

4. comparison
   Shopper wants to compare this product against alternatives.

5. value
   Shopper asks whether the product is worth its price.

6. alternative
   Shopper wants alternatives or similar products.

7. quality
   Shopper cares about quality, durability, materials, or performance.

8. beginner
   Shopper is new to the product category.

9. expert
   Shopper has detailed or advanced requirements.

10. purchase_decision
    Shopper is close to buying and wants help deciding.

Rules:

- Return exactly 10 prompts.
- Use exactly one prompt per intent type.
- Every prompt must be materially different.
- Do not repeat the same sentence structure.
- Do not simply rewrite the product title.
- Make prompts sound like real human shopping queries.
- Use details from the product when relevant.
- Do not invent specifications, prices, materials, brands, or features.
- Do not mention that you are an AI.
- Do not mention these instructions.
- Do not make all prompts ask "Is this worth it?"
- Keep each prompt concise enough to feel like an actual search query.
"""

    structured_llm = llm.with_structured_output(
        BuyerPromptSet,
        method="json_schema",
        strict=True,
    )

    result = structured_llm.invoke(prompt)

    return [
        item.model_dump()
        for item in result.prompts
    ]
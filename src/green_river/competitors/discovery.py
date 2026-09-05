import json

from groq import Groq
from dotenv import load_dotenv
import os

from green_river.competitors.models import (
    DiscoveryQueries,
    SearchQuery,
)
from green_river.models import StructuredProduct


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing."
    )


client = Groq(
    api_key=GROQ_API_KEY,
)


DISCOVERY_PROMPT = """
Generate 3 to 5 concise marketplace search queries
for finding products similar to the supplied merchant product.

Rules:
- Use only attributes present in the product.
- Never invent attributes.
- Do not copy the complete product title.
- Do not use extremely generic queries such as "men's t-shirts".
- Focus on distinctive product characteristics.
- Prefer 4 to 8 meaningful words per query.
- Include product type and distinctive style/material/color
  characteristics when available.
- Do not require the merchant's exact brand.
- Do not mention Amazon, Myntra, Flipkart, or any marketplace.
"""


def generate_discovery_queries(
    product: StructuredProduct,
) -> list[SearchQuery]:
    """Generate semantic competitor search queries using Groq."""

    product_data = product.model_dump(
        mode="json"
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": DISCOVERY_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "MERCHANT PRODUCT:\n"
                    + json.dumps(
                        product_data,
                        ensure_ascii=False,
                        indent=2,
                    )
                ),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "discovery_queries",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "queries": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "minItems": 3,
                            "maxItems": 5,
                        }
                    },
                    "required": [
                        "queries"
                    ],
                    "additionalProperties": False,
                },
            },
        },
    )

    raw_content = completion.choices[0].message.content

    if not raw_content:
        raise RuntimeError(
            "Groq returned empty discovery output."
        )

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Groq returned invalid JSON."
        ) from exc

    result = DiscoveryQueries.model_validate(
        parsed
    )

    queries: list[SearchQuery] = []

    seen: set[str] = set()

    for raw_query in result.queries:
        query = " ".join(
            raw_query.split()
        ).strip()

        if not query:
            continue

        normalized = query.lower()

        if normalized in seen:
            continue

        seen.add(normalized)

        queries.append(
            SearchQuery(
                query=query,
                source="semantic",
            )
        )

    if not queries:
        raise RuntimeError(
            "No valid discovery queries were generated."
        )

    return queries[:5]
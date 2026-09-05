from __future__ import annotations

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from green_river.models import StructuredProduct


class DiscoveryQueries(BaseModel):
    queries: list[str] = Field(
        min_length=3,
        max_length=5,
    )


def generate_discovery_queries(
    product: StructuredProduct,
) -> list[str]:
    """
    Generate semantic competitor-search queries from the product.
    """

    product_text = product.to_embedding_text()

    prompt = f"""
You are generating web search queries for competitor discovery.

Given the structured product representation below, generate
3 to 5 distinct semantic search queries that could find similar
products sold by other merchants.

Rules:
- Use only information present in the product representation.
- Do not invent brands, materials, specifications, or features.
- Do not create retailer-specific queries.
- Do not force Amazon, Myntra, Flipkart, etc.
- Prefer natural product concepts and distinctive attributes.
- Queries should be useful for general web search.
- Make the queries meaningfully different from each other.
- Do not return URLs.
- Do not explain the queries.

Product:
{product_text}
"""

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        max_retries=2,
    )

    structured_llm = llm.with_structured_output(
        DiscoveryQueries,
        method="json_schema",
        strict=True,
    )

    result = structured_llm.invoke(prompt)

    return result.queries
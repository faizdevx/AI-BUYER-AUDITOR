from __future__ import annotations

from typing import Any

from green_river.competitors.discovery import (
    generate_discovery_queries,
)
from green_river.competitors.models import (
    CandidateURL,
    CompetitorProduct,
    SearchQuery,
)
from green_river.competitors.search import search_candidates
from green_river.db import get_product
from green_river.scraper import fetch_page


def _dedupe_candidates(
    candidates: list[CandidateURL],
) -> list[CandidateURL]:
    seen: set[str] = set()
    unique: list[CandidateURL] = []

    for candidate in candidates:
        url = candidate.url.strip()

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)
        unique.append(
            CandidateURL(
                url=url,
                source=candidate.source,
            )
        )

    return unique


def discover_candidates(
    product,
    *,
    results_per_query: int = 10,
) -> tuple[list[SearchQuery], list[CandidateURL]]:
    """
    Generate semantic queries and search the web for candidate URLs.
    """

    query_strings = generate_discovery_queries(product)

    queries = [
        SearchQuery(
            query=query,
            source="semantic",
        )
        for query in query_strings
    ]

    candidates: list[CandidateURL] = []

    for query in queries:
        results = search_candidates(
            query.query,
            num=results_per_query,
        )

        candidates.extend(results)

    candidates = _dedupe_candidates(candidates)

    return queries, candidates




def discover_competitors(
    merchant_id: int,
    *,
    results_per_query: int = 10,
) -> dict[str, Any]:
    """
    Full first-stage competitor discovery pipeline.

    Merchant:
        Supabase
        ↓
    semantic queries
        ↓
    Serper
        ↓
    candidate URLs
        ↓
    Scrapling
        ↓
    StructuredProduct
    """

    merchant = get_product(merchant_id)

    if merchant is None:
        raise ValueError(
            f"Merchant product {merchant_id} was not found."
        )

    product_data = merchant["product_json"]

    from green_river.models import StructuredProduct

    merchant_product = StructuredProduct.model_validate(
        product_data
    )

    queries, candidates = discover_candidates(
        merchant_product,
        results_per_query=results_per_query,
    )

    competitors: list[CompetitorProduct] = []

    for candidate in candidates:
        try:
            product = fetch_candidate_product(candidate)
        except Exception:
            continue

        if product is None:
            continue

        competitors.append(
            CompetitorProduct(
                source=candidate.source,
                source_url=candidate.url,
                product=product,
            )
        )

    return {
        "merchant_id": merchant_id,
        "queries": queries,
        "candidates": candidates,
        "competitors": competitors,
    }
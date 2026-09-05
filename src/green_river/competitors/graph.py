from __future__ import annotations

from typing import Any

from green_river.competitors.discovery import (
    generate_discovery_queries,
)
from green_river.competitors.models import (
    CandidateURL,
    CompetitorFetchResponse,
    CompetitorProduct,
    SearchQuery,
)
from green_river.competitors.search import search_candidates
from green_river.db import get_product
from green_river.llm.extractor import extract_product
from green_river.models import StructuredProduct
from green_river.parser import parse_text
from green_river.scraper import fetch_page


def fetch_candidate_product(
    candidate: CandidateURL,
) -> StructuredProduct | None:
    """
    Fetch a candidate URL with Scrapling, convert the page into
    the same intermediate structured text used by Phase 1, then
    run the existing Groq product extractor.
    """

    try:
        # ---------------------------------------------------------
        # 1. Fetch webpage
        # ---------------------------------------------------------
        page = fetch_page(candidate.url)

        if page is None:
            return None

        # ---------------------------------------------------------
        # 2. Convert webpage to raw text
        # ---------------------------------------------------------
        raw_text = page.markdown(
            main_content_only=True,
        ).strip()

        if not raw_text:
            return None

        # ---------------------------------------------------------
        # 3. Use the existing generic parser
        # ---------------------------------------------------------
        webpage = parse_text(
            raw_text,
            candidate.url,
        )

        # ---------------------------------------------------------
        # 4. Convert to the same structured text used by Phase 1
        # ---------------------------------------------------------
        structured_text = webpage.to_structured_text(
            max_chars=10_000,
        )
        
        structured_text = structured_text[:8_000]
        if not structured_text.strip():
            return None

        # ---------------------------------------------------------
        # 5. Reuse the existing Groq extractor
        # ---------------------------------------------------------
        product_data = extract_product(
            structured_text,
        )

        # ---------------------------------------------------------
        # 6. Validate through StructuredProduct
        # ---------------------------------------------------------
        product = StructuredProduct.model_validate(
            product_data,
        )

        # Make sure the candidate URL is retained.
        if not product.url:
            product.url = candidate.url

        return product

    except Exception as exc:
        print(
            f"Failed to process competitor candidate "
            f"{candidate.url}: {exc}"
        )
        return None


def is_buyable_product(
    product: StructuredProduct,
) -> bool:
    """
    Conservative validation after the actual product page
    has been fetched and interpreted.

    This is intentionally separate from URL filtering.
    """

    # Must have a product identity.
    if not product.product_name:
        return False

    # Must have a source URL.
    if not product.url:
        return False

    # A price is strong evidence that this is a sellable listing.
    if not product.price:
        return False

    availability = (
        product.availability or ""
    ).strip().casefold()

    unavailable_phrases = (
        "out of stock",
        "currently unavailable",
        "sold out",
        "discontinued",
        "not available",
        "unavailable",
    )

    if any(
        phrase in availability
        for phrase in unavailable_phrases
    ):
        return False

    return True


def discover_candidates(
    product: StructuredProduct,
    *,
    results_per_query: int = 10,
) -> tuple[
    list[SearchQuery],
    list[CandidateURL],
]:
    """
    Generate semantic search queries and collect candidate URLs.
    """

    query_strings = generate_discovery_queries(
        product,
    )

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

    # Global deduplication across all generated queries.
    seen: set[str] = set()
    unique_candidates: list[CandidateURL] = []

    for candidate in candidates:
        if candidate.url in seen:
            continue

        seen.add(candidate.url)
        unique_candidates.append(candidate)

    return queries, unique_candidates


def discover_competitors(
    merchant_id: int,
    *,
    results_per_query: int = 10,
) -> dict[str, Any]:
    """
    Complete competitor discovery pipeline.

    Merchant from Supabase
        ↓
    Groq semantic queries
        ↓
    SerpApi
        ↓
    Candidate URL filtering
        ↓
    Scrapling
        ↓
    Generic parser
        ↓
    Existing Groq extractor
        ↓
    StructuredProduct
        ↓
    Buyability validation
    """

    # -------------------------------------------------------------
    # 1. Load merchant from Supabase
    # -------------------------------------------------------------
    merchant = get_product(
        merchant_id,
    )

    if merchant is None:
        raise ValueError(
            f"Merchant product {merchant_id} was not found."
        )

    # -------------------------------------------------------------
    # 2. Restore StructuredProduct
    # -------------------------------------------------------------
    merchant_product = StructuredProduct.model_validate(
        merchant["product_json"],
    )

    # -------------------------------------------------------------
    # 3. Discover candidate URLs
    # -------------------------------------------------------------
    queries, candidates = discover_candidates(
        merchant_product,
        results_per_query=3,
    )

    # -------------------------------------------------------------
    # 4. Fetch and extract candidates
    # -------------------------------------------------------------
    competitors: list[CompetitorProduct] = []

    for candidate in candidates[:3]:

        product = fetch_candidate_product(
            candidate,
        )

        if product is None:
            continue

        # ---------------------------------------------------------
        # 5. Check whether this is an actual sellable product
        # ---------------------------------------------------------
        if not is_buyable_product(product):
            continue

        # ---------------------------------------------------------
        # 6. Keep valid competitor
        # ---------------------------------------------------------
        competitors.append(
            CompetitorProduct(
                source=candidate.source,
                source_url=candidate.url,
                product=product,
            )
        )

    # -------------------------------------------------------------
    # 7. Return discovery result
    # -------------------------------------------------------------
    response = CompetitorFetchResponse(
        merchant_id=merchant_id,
        queries=queries,
        candidates=candidates,
        competitors=competitors,
    )

    return response.model_dump()
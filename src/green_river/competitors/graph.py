from __future__ import annotations

import json
from typing import Any

from starlette.concurrency import run_in_threadpool

from green_river.competitors.discovery import (
    generate_discovery_queries,
)
from green_river.competitors.fetcher import (
    fetch_candidate_pages,
)
from green_river.competitors.models import (
    CandidateURL,
    CompetitorFetchResponse,
    CompetitorProduct,
    SearchQuery,
)
from green_river.competitors.page_filter import (
    assess_product_page,
)
from green_river.competitors.reranker import (
    cosine_similarity,
    rank_competitors,
)
from green_river.competitors.search import (
    search_candidates,
)
from green_river.db import get_product
from green_river.embeddings.jina import (
    embed_image_url,
    embed_text,
)
from green_river.llm.extractor import extract_product
from green_river.models import StructuredProduct
from green_river.parser import parse_text


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_RESULTS_PER_QUERY = 5
DEFAULT_MAX_CANDIDATE_PAGES = 10
DEFAULT_TOP_K = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _coerce_vector(
    value: Any,
) -> list[float] | None:
    """
    Convert a Postgres/pgvector value into a Python float list.

    Supported:
    - list
    - tuple
    - pgvector string such as "[0.1,0.2,...]"
    """

    if value is None:
        return None

    if isinstance(value, list):
        try:
            return [float(item) for item in value]
        except (TypeError, ValueError):
            return None

    if isinstance(value, tuple):
        try:
            return [float(item) for item in value]
        except (TypeError, ValueError):
            return None

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return [float(item) for item in parsed]

        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        # Fallback for pgvector-style strings.
        if value.startswith("[") and value.endswith("]"):
            try:
                return [
                    float(item.strip())
                    for item in value[1:-1].split(",")
                    if item.strip()
                ]
            except (TypeError, ValueError):
                return None

    return None


# ---------------------------------------------------------------------------
# Product validation
# ---------------------------------------------------------------------------

def is_buyable_product(
    product: StructuredProduct,
) -> bool:
    """
    Conservative validation after Groq has extracted the product.

    The page must represent a product with:
    - product name
    - URL
    - price
    - no obvious unavailable status
    """

    if not product.product_name:
        return False

    if not product.url:
        return False

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


# ---------------------------------------------------------------------------
# Candidate discovery
# ---------------------------------------------------------------------------

def discover_candidates(
    product: StructuredProduct,
    *,
    results_per_query: int = DEFAULT_RESULTS_PER_QUERY,
) -> tuple[
    list[SearchQuery],
    list[CandidateURL],
]:
    """
    Generate semantic queries with Groq and collect unique candidate URLs
    through SerpApi.
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
        try:
            results = search_candidates(
                query.query,
                num=results_per_query,
            )

            candidates.extend(results)

        except Exception as exc:
            print(
                f"SEARCH FAILED: {query.query}: {exc}"
            )

    # Global deduplication.
    seen: set[str] = set()
    unique_candidates: list[CandidateURL] = []

    for candidate in candidates:
        if not candidate.url:
            continue

        if candidate.url in seen:
            continue

        seen.add(candidate.url)
        unique_candidates.append(candidate)

    return queries, unique_candidates


# ---------------------------------------------------------------------------
# Concurrent page fetching + deterministic filtering
# ---------------------------------------------------------------------------

async def process_candidate_pages(
    candidates: list[CandidateURL],
    *,
    max_pages: int = DEFAULT_MAX_CANDIDATE_PAGES,
) -> list[
    tuple[
        CandidateURL,
        dict[str, Any],
    ]
]:
    """
    Fetch candidate pages concurrently.

    Only pages that pass the deterministic product-page filter are returned.
    """

    if not candidates:
        return []

    candidates_to_fetch = candidates[:max_pages]

    print(
        f"Fetching {len(candidates_to_fetch)} candidate pages..."
    )

    # fetch_candidate_pages is synchronous and internally uses a
    # ThreadPoolExecutor. Run it away from FastAPI's event loop.
    fetched_pages = await run_in_threadpool(
        lambda: fetch_candidate_pages(
            [
                candidate.url
                for candidate in candidates_to_fetch
            ],
            max_pages=max_pages,
        )
    )

    candidate_map = {
        candidate.url: candidate
        for candidate in candidates_to_fetch
    }

    accepted: list[
        tuple[
            CandidateURL,
            dict[str, Any],
        ]
    ] = []

    for url, page in fetched_pages:
        candidate = candidate_map.get(url)

        if candidate is None:
            continue

        if page is None:
            print(
                f"FETCH FAILED: {url}"
            )
            continue

        try:
            assessment = assess_product_page(
                page,
            )

            print(
                f"PAGE FILTER | "
                f"score={assessment['score']} | "
                f"product={assessment['is_likely_product']} | "
                f"{url}"
            )

            if not assessment["is_likely_product"]:
                continue

            accepted.append(
                (
                    candidate,
                    assessment,
                )
            )

        except Exception as exc:
            print(
                f"PAGE FILTER FAILED: "
                f"{url}: {exc}"
            )

    print(
        f"Accepted product pages: {len(accepted)}"
    )

    return accepted


# ---------------------------------------------------------------------------
# Groq extraction
# ---------------------------------------------------------------------------

def extract_candidate_product(
    candidate: CandidateURL,
    assessment: dict[str, Any],
) -> StructuredProduct | None:
    """
    Run the existing generic parser + Groq product extraction pipeline
    on an already accepted product page.
    """

    try:
        raw_text = assessment.get(
            "text",
            "",
        )

        if not isinstance(
            raw_text,
            str,
        ):
            return None

        if not raw_text.strip():
            return None

        # -------------------------------------------------------------
        # Generic parser
        # -------------------------------------------------------------

        webpage = parse_text(
            raw_text,
            candidate.url,
        )

        # -------------------------------------------------------------
        # Compact Groq input
        # -------------------------------------------------------------

        structured_text = webpage.to_structured_text(
            max_chars=8_000,
        )

        if not structured_text.strip():
            return None

        structured_text = structured_text[:8_000]

        # -------------------------------------------------------------
        # Existing Groq extractor
        # -------------------------------------------------------------

        product_data = extract_product(
            structured_text,
        )

        product = StructuredProduct.model_validate(
            product_data,
        )

        # Always keep the actual candidate URL.
        product.url = candidate.url

        return product

    except Exception as exc:
        print(
            f"GROQ EXTRACTION FAILED: "
            f"{candidate.url}: {exc}"
        )
        return None


# ---------------------------------------------------------------------------
# Image similarity
# ---------------------------------------------------------------------------

def add_image_similarities(
    merchant_image_embedding: list[float] | None,
    competitors: list[CompetitorProduct],
    image_urls: dict[str, str],
) -> None:
    """
    Create competitor image embeddings and calculate image similarity.

    Image failures do not reject the competitor. The reranker will fall
    back to text similarity for candidates without an image score.
    """

    if not merchant_image_embedding:
        print(
            "Merchant image embedding unavailable. "
            "Using text similarity only."
        )
        return

    for competitor in competitors:
        image_url = image_urls.get(
            competitor.source_url
        )

        if not image_url:
            print(
                f"IMAGE SKIPPED: "
                f"no product image for {competitor.source_url}"
            )
            continue

        try:
            candidate_image_embedding = embed_image_url(
                image_url,
            )

            competitor.image_similarity = round(
                cosine_similarity(
                    merchant_image_embedding,
                    candidate_image_embedding,
                ),
                6,
            )

            print(
                f"IMAGE SCORE | "
                f"{competitor.image_similarity} | "
                f"{competitor.source_url}"
            )

        except Exception as exc:
            print(
                f"IMAGE EMBEDDING FAILED: "
                f"{competitor.source_url}: {exc}"
            )


# ---------------------------------------------------------------------------
# Complete competitor engine
# ---------------------------------------------------------------------------

async def discover_competitors(
    merchant_id: int,
    *,
    results_per_query: int = DEFAULT_RESULTS_PER_QUERY,
    max_candidate_pages: int = DEFAULT_MAX_CANDIDATE_PAGES,
    top_k: int = DEFAULT_TOP_K,
) -> dict[str, Any]:
    """
    Complete Green River competitor discovery engine.

    Merchant
        ↓
    Supabase
        ↓
    StructuredProduct
        ↓
    Groq semantic discovery queries
        ↓
    SerpApi
        ↓
    Candidate URLs
        ↓
    Concurrent Scrapling
        ↓
    Deterministic product-page filter
        ↓
    Generic parser
        ↓
    Groq StructuredProduct
        ↓
    Buyability validation
        ↓
    Jina text + image embeddings
        ↓
    Similarity
        ↓
    Reranking
        ↓
    Top K competitors
    """

    # ------------------------------------------------------------------
    # 1. Load merchant
    # ------------------------------------------------------------------

    merchant = get_product(
        merchant_id,
    )

    if merchant is None:
        raise ValueError(
            f"Merchant product {merchant_id} was not found."
        )

    # ------------------------------------------------------------------
    # 2. Restore merchant product
    # ------------------------------------------------------------------

    merchant_product = StructuredProduct.model_validate(
        merchant["product_json"],
    )

    print(
        f"Merchant loaded: {merchant_product.product_name}"
    )

    # ------------------------------------------------------------------
    # 3. Merchant text embedding
    # ------------------------------------------------------------------

    merchant_text = merchant_product.to_embedding_text()

    if not merchant_text.strip():
        raise ValueError(
            "Merchant product has no embeddable text."
        )

    print(
        "Creating merchant text embedding..."
    )

    merchant_text_embedding = embed_text(
        merchant_text,
    )

    # ------------------------------------------------------------------
    # 4. Merchant image embedding
    # ------------------------------------------------------------------

    merchant_image_embedding = _coerce_vector(
        merchant.get("image_embedding")
    )

    if merchant_image_embedding:
        print(
            "Merchant image embedding loaded."
        )
    else:
        print(
            "Merchant image embedding unavailable."
        )

    # ------------------------------------------------------------------
    # 5. Generate semantic queries + search
    # ------------------------------------------------------------------

    queries, candidates = discover_candidates(
        merchant_product,
        results_per_query=results_per_query,
    )

    print(
        f"Generated {len(queries)} search queries."
    )

    print(
        f"Found {len(candidates)} unique candidate URLs."
    )

    # ------------------------------------------------------------------
    # 6. Concurrent fetch + deterministic filtering
    # ------------------------------------------------------------------

    accepted_pages = await process_candidate_pages(
        candidates,
        max_pages=max_candidate_pages,
    )

    # ------------------------------------------------------------------
    # 7. Extract valid competitor products
    # ------------------------------------------------------------------

    competitors: list[CompetitorProduct] = []

    candidate_image_urls: dict[str, str] = {}

    for candidate, assessment in accepted_pages:

        product = extract_candidate_product(
            candidate,
            assessment,
        )

        if product is None:
            continue

        # --------------------------------------------------------------
        # Buyability validation
        # --------------------------------------------------------------

        if not is_buyable_product(product):
            print(
                f"REJECTED AS NOT BUYABLE: "
                f"{candidate.url}"
            )
            continue

        # --------------------------------------------------------------
        # Build competitor object
        # --------------------------------------------------------------

        competitor = CompetitorProduct(
            source=candidate.source,
            source_url=candidate.url,
            product=product,
        )

        competitors.append(
            competitor
        )

        # --------------------------------------------------------------
        # Preserve candidate product image URL
        # --------------------------------------------------------------

        image_url = assessment.get(
            "image_url"
        )

        if isinstance(
            image_url,
            str,
        ) and image_url.strip():
            candidate_image_urls[
                candidate.url
            ] = image_url.strip()

        print(
            f"COMPETITOR ACCEPTED: "
            f"{candidate.url}"
        )

    print(
        f"Valid competitors before ranking: "
        f"{len(competitors)}"
    )

    # ------------------------------------------------------------------
    # 8. Image similarity
    # ------------------------------------------------------------------

    add_image_similarities(
        merchant_image_embedding,
        competitors,
        candidate_image_urls,
    )

    # ------------------------------------------------------------------
    # 9. Text similarity + final ranking
    # ------------------------------------------------------------------

    ranked_competitors = rank_competitors(
        merchant_text_embedding,
        competitors,
    )

    # ------------------------------------------------------------------
    # 10. Top K
    # ------------------------------------------------------------------

    ranked_competitors = ranked_competitors[:top_k]

    print(
        f"Returning top {len(ranked_competitors)} competitors."
    )

    for index, competitor in enumerate(
        ranked_competitors,
        start=1,
    ):
        print(
            f"RANK {index} | "
            f"text={competitor.text_similarity} | "
            f"image={competitor.image_similarity} | "
            f"final={competitor.final_score} | "
            f"{competitor.source_url}"
        )

    # ------------------------------------------------------------------
    # 11. Response
    # ------------------------------------------------------------------

    response = CompetitorFetchResponse(
        merchant_id=merchant_id,
        queries=queries,
        candidates=candidates,
        competitors=ranked_competitors,
    )

    return response.model_dump()
from __future__ import annotations

import html
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
    urlunparse,
)

import serpapi
from dotenv import load_dotenv

from green_river.competitors.models import CandidateURL, RawListing


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not SERPAPI_KEY:
    raise RuntimeError("SERPAPI_KEY is missing.")


client = serpapi.Client(
    api_key=SERPAPI_KEY,
)


# ---------------------------------------------------------------------------
# Search-result filtering
# ---------------------------------------------------------------------------

BLOCKED_DOMAINS = {
    "pinterest.com",
    "instagram.com",
    "facebook.com",
    "youtube.com",
    "x.com",
    "twitter.com",
}


BLOCKED_PATH_PARTS = (
    "/search",
    "/collections/",
    "/collection/",
    "/category/",
    "/categories/",
    "/lookalike/",
    "/ideas/",
    "/boards/",
    "/reels/",
)


# ---------------------------------------------------------------------------
# URL cleaning
# ---------------------------------------------------------------------------

def clean_search_url(url: str) -> str:
    """
    Normalize a search result URL.

    - Remove accidental Markdown wrapping.
    - Decode HTML entities.
    - Decode escaped unicode-style equals signs.
    - Remove common search-engine tracking parameters.
    - Remove URL fragments.
    """

    url = url.strip()

    # Handle accidental Markdown:
    # [https://example.com/product](https://example.com/product)
    match = re.fullmatch(
        r"\[.*?\]\((https?://[^)]+)\)",
        url,
    )

    if match:
        url = match.group(1)

    # Decode HTML entities such as &amp;
    url = html.unescape(url)

    # Handle escaped equals signs.
    url = url.replace(r"\u003d", "=")
    url = url.replace("%5Cu003d", "=")

    parsed = urlparse(url)

    # Remove common tracking parameters.
    tracking_parameters = {
        "srsltid",
        "ved",
        "usg",
    }

    filtered_query = [
        (key, value)
        for key, value in parse_qsl(
            parsed.query,
            keep_blank_values=True,
        )
        if key.lower() not in tracking_parameters
    ]

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(filtered_query),
            "",
        )
    )


# ---------------------------------------------------------------------------
# Candidate URL validation
# ---------------------------------------------------------------------------

def is_candidate_url(url: str) -> bool:
    """
    Reject only obvious non-product pages.

    This deliberately does NOT try to determine whether a URL is
    definitely a product page. That decision is made later after
    Scrapling fetches the page and Groq extracts StructuredProduct.
    """

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    if not parsed.netloc:
        return False

    domain = parsed.netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    # Reject obvious social/media sites.
    for blocked_domain in BLOCKED_DOMAINS:
        if domain == blocked_domain:
            return False

        if domain.endswith("." + blocked_domain):
            return False

    path = parsed.path.lower()

    # Reject obvious search/category/collection pages.
    for blocked_path in BLOCKED_PATH_PARTS:
        if blocked_path in path:
            return False

    # Explicit search path check.
    if path.rstrip("/") in {
        "/search",
        "/s",
    }:
        return False

    return True


# ---------------------------------------------------------------------------
# Google search through SerpApi
# ---------------------------------------------------------------------------

def search_google(
    query: str,
    *,
    num: int = 10,
    country: str = "in",
    language: str = "en",
) -> dict[str, Any]:
    """
    Search Google through SerpApi.

    Returns the structured SerpApi response.
    """

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    results = client.search(
        {
            "engine": "google",
            "q": query,
            "num": num,
            "gl": country,
            "hl": language,
        }
    )

    return dict(results)


# ---------------------------------------------------------------------------
# Candidate URL discovery
# ---------------------------------------------------------------------------

def search_candidates(
    query: str,
    *,
    num: int = 10,
) -> list[CandidateURL]:
    """
    Search the web and return cleaned candidate URLs.

    The function:
        1. Calls SerpApi.
        2. Reads organic_results.
        3. Extracts result links.
        4. Cleans URLs.
        5. Removes duplicates.
        6. Removes obvious non-product pages.

    Product validity is checked later after scraping the page.
    """

    data = search_google(
        query,
        num=num,
    )

    organic_results = data.get(
        "organic_results",
        [],
    )

    if not isinstance(organic_results, list):
        return []

    candidates: list[CandidateURL] = []
    seen: set[str] = set()

    for result in organic_results:
        if not isinstance(result, dict):
            continue

        url = result.get("link")

        if not isinstance(url, str):
            continue

        url = clean_search_url(url)

        if not url:
            continue

        if url in seen:
            continue

        if not is_candidate_url(url):
            continue

        seen.add(url)

        candidates.append(
            CandidateURL(
                url=url,
                source="google",
            )
        )

    return candidates


# ---------------------------------------------------------------------------
# Raw search listings
# ---------------------------------------------------------------------------

def search_raw_listings(
    query: str,
    *,
    num: int = 10,
) -> list[RawListing]:
    """
    Return structured Google search-result metadata.

    This keeps the search-result title and snippet available for
    diagnostics or later ranking logic.
    """

    data = search_google(
        query,
        num=num,
    )

    organic_results = data.get(
        "organic_results",
        [],
    )

    if not isinstance(organic_results, list):
        return []

    listings: list[RawListing] = []
    seen: set[str] = set()

    for result in organic_results:
        if not isinstance(result, dict):
            continue

        url = result.get("link")

        if not isinstance(url, str):
            continue

        url = clean_search_url(url)

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)

        title = result.get("title")
        snippet = result.get("snippet")

        listings.append(
            RawListing(
                url=url,
                source="google",
                title=title if isinstance(title, str) else None,
                snippet=snippet if isinstance(snippet, str) else None,
            )
        )

    return listings
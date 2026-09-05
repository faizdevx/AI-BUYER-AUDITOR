from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from green_river.scraper import fetch_page


MAX_WORKERS = 5


def fetch_one_candidate(
    url: str,
) -> tuple[str, Any | None]:
    """
    Fetch one candidate using the existing synchronous Scrapling
    StealthyFetcher.
    """

    try:
        page = fetch_page(url)
        return url, page

    except Exception as exc:
        print(
            f"FETCH FAILED: {url}: {exc}"
        )
        return url, None


def fetch_candidate_pages(
    urls: list[str],
    *,
    max_pages: int = 5,
) -> list[tuple[str, Any | None]]:
    """
    Fetch candidate pages concurrently using worker threads.

    Each worker uses the existing synchronous Scrapling fetcher.
    This avoids Windows asyncio subprocess limitations while still
    allowing multiple browser fetches to run concurrently.
    """

    urls = urls[:max_pages]

    if not urls:
        return []

    worker_count = min(
        MAX_WORKERS,
        len(urls),
    )

    print(
        f"Fetching {len(urls)} candidate pages "
        f"with {worker_count} workers..."
    )

    with ThreadPoolExecutor(
        max_workers=worker_count,
    ) as executor:
        results = list(
            executor.map(
                fetch_one_candidate,
                urls,
            )
        )

    return results
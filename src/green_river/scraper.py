from pathlib import Path

from scrapling.fetchers import StealthyFetcher

from green_river.parser import parse_text
from green_river.utils import filename_from_url


RAW_DIR = Path("data/raw")
STRUCTURED_DIR = Path("data/structured")


from scrapling.fetchers import StealthyFetcher


def fetch_page(url: str):
    return StealthyFetcher.fetch(
        url,
        google_search=True,
        headless=True,
        timeout=60_000,
        wait=2_000,
        network_idle=False,
        load_dom=False,
        disable_resources=True,
    )


def scrape_to_raw_txt(
    url: str,
) -> tuple[Path, str]:

    page = fetch_page(url)

    text = page.markdown(
        main_content_only=True,
    ).strip()

    if not text:
        raise RuntimeError(
            "No usable webpage content returned."
        )

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        RAW_DIR
        / f"{filename_from_url(url)}.txt"
    )

    path.write_text(
        text,
        encoding="utf-8",
    )

    return path, text


def scrape_and_process(
    url: str,
):
    raw_path, raw_text = (
        scrape_to_raw_txt(url)
    )

    webpage = parse_text(
        raw_text,
        url,
    )

    structured_text = (
        webpage.to_structured_text(
            max_chars=18_000
        )
    )

    STRUCTURED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    structured_path = (
        STRUCTURED_DIR
        / f"{filename_from_url(url)}.txt"
    )

    structured_path.write_text(
        structured_text,
        encoding="utf-8",
    )

    return (
        raw_path,
        structured_path,
        raw_text,
        structured_text,
    )
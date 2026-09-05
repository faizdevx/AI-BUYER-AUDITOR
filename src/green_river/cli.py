from urllib.parse import urlparse

from green_river.scraper import scrape_and_process


def main() -> None:
    url = input(
        "Paste webpage URL: "
    ).strip()

    parsed = urlparse(url)

    if parsed.scheme not in {
        "http",
        "https",
    }:
        raise ValueError(
            "Please enter a valid HTTP/HTTPS URL."
        )

    if not parsed.netloc:
        raise ValueError(
            "Invalid URL."
        )

    print("\nFetching...")

    (
        raw_path,
        structured_path,
        raw_text,
        structured_text,
    ) = scrape_and_process(url)

    print(
        f"\nRaw characters: "
        f"{len(raw_text):,}"
    )

    print(
        f"Structured characters: "
        f"{len(structured_text):,}"
    )

    print(
        f"\nRaw file: "
        f"{raw_path.resolve()}"
    )

    print(
        f"Structured file: "
        f"{structured_path.resolve()}"
    )

    print(
        "\n========== STRUCTURED ==========\n"
    )

    print(structured_text)


if __name__ == "__main__":
    main()
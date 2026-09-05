import re
from urllib.parse import urlparse


def normalize_line(line: str) -> str:
    """
    Normalize whitespace within one line.
    """
    return " ".join(line.split())


def normalize_text(text: str) -> list[str]:
    """
    Convert raw text into clean non-empty lines.
    """
    lines: list[str] = []

    for raw_line in text.splitlines():
        line = normalize_line(raw_line)

        if line:
            lines.append(line)

    return lines


def deduplicate_lines(
    lines: list[str],
) -> list[str]:
    """
    Remove exact repeated lines while preserving order.
    """
    seen: set[str] = set()
    result: list[str] = []

    for line in lines:
        key = line.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(line)

    return result


def is_noise(line: str) -> bool:
    """
    Detect obvious generic UI noise.

    This is intentionally conservative.
    """

    noise = {
        "close",
        "cancel",
        "ok",
        "login",
        "log in",
        "sign in",
        "sign up",
        "menu",
        "search",
        "share",
        "back",
        "next",
        "previous",
        "cart",
        "wishlist",
        "cookie settings",
        "privacy policy",
        "accessibility",
        "terms & conditions",
    }

    return line.casefold() in noise


def remove_noise(
    lines: list[str],
) -> list[str]:
    return [
        line
        for line in lines
        if not is_noise(line)
    ]


def is_heading(line: str) -> bool:
    """
    Generic heading detection.

    We primarily trust common semantic section names,
    then use a conservative heuristic for short title-like lines.
    """

    common = {
        "description",
        "details",
        "features",
        "specifications",
        "specification",
        "reviews",
        "review",
        "materials",
        "material / care",
        "care",
        "shipping",
        "delivery",
        "returns",
        "return",
        "exchange",
        "production",
        "ingredients",
        "directions",
        "information",
        "overview",
        "about",
        "contact",
        "faq",
        "customer service",
        "product information",
        "product details",
        "size guide",
        "shipping & returns",
    }

    lowered = line.casefold().strip()

    if lowered in common:
        return True

    # Don't classify long sentences as headings.
    if len(line) > 80:
        return False

    words = line.split()

    # Conservative title-like heuristic.
    if 1 <= len(words) <= 5:
        if line[0].isupper() and not line.endswith("."):
            return True

    return False


def filename_from_url(url: str) -> str:
    """
    Generate a usable filename from the URL.
    """

    parsed = urlparse(url)

    parts = [
        part
        for part in parsed.path.rstrip("/").split("/")
        if part
    ]

    if "products" in parts:
        index = parts.index("products")

        if index + 1 < len(parts):
            name = parts[index + 1]
        else:
            name = parts[-1] if parts else "page"

    else:
        name = parts[-1] if parts else "page"

    name = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        name,
    )

    return name.strip(" .") or "page"
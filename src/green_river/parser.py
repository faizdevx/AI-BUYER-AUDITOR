from green_river.models import ContentSection, WebPage
from green_river.utils import (
    deduplicate_lines,
    is_heading,
    normalize_text,
    remove_noise,
)


# Sections that are generally useful for an LLM.
IMPORTANT_SECTIONS = {
    "description",
    "details",
    "features",
    "specifications",
    "specification",
    "product information",
    "product details",
    "material",
    "material / care",
    "care",
    "ingredients",
    "directions",
    "reviews",
    "review",
    "shipping",
    "delivery",
    "returns",
    "return",
    "exchange",
    "usage",
    "instructions",
    "overview",
}


# Common junk sections that should usually disappear.
JUNK_SECTIONS = {
    "shopping guide",
    "membership",
    "customer service",
    "faq",
    "privacy policy",
    "accessibility",
    "cookie settings",
    "footer",
}


def detect_title(
    lines: list[str],
) -> str | None:

    for line in lines[:15]:
        if 10 <= len(line) <= 160:
            return line

    return None


def extract_general_content(
    lines: list[str],
    title: str | None,
) -> list[str]:
    """
    Preserve only a small amount of important content that appears
    before the first recognized section heading.
    """

    result = []

    for line in lines:
        if title and line == title:
            continue

        if is_heading(line):
            break

        # Ignore obvious navigation garbage.
        if len(line) < 2:
            continue

        result.append(line)

        # Don't let the general section swallow the page.
        if len(result) >= 50:
            break

    return result


def build_sections(
    lines: list[str],
) -> list[ContentSection]:

    sections: list[ContentSection] = []

    current_heading: str | None = None
    current_content: list[str] = []

    def flush() -> None:
        nonlocal current_heading
        nonlocal current_content

        if not current_content:
            return

        heading = (
            current_heading.casefold()
            if current_heading
            else None
        )

        # Drop obvious junk sections.
        if heading in JUNK_SECTIONS:
            current_heading = None
            current_content = []
            return

        # Keep general content, but cap it.
        if heading is None:
            content = current_content[:50]

        # Keep recognized sections with a reasonable cap.
        elif heading in IMPORTANT_SECTIONS:
            content = current_content[:80]

        # Unknown sections get a smaller allowance.
        else:
            content = current_content[:25]

        if content:
            sections.append(
                ContentSection(
                    heading=current_heading,
                    content=content,
                )
            )

        current_heading = None
        current_content = []

    for line in lines:

        if is_heading(line):
            flush()
            current_heading = line
            continue

        current_content.append(line)

    flush()

    return sections


def parse_text(
    raw_text: str,
    url: str,
) -> WebPage:

    lines = normalize_text(
        raw_text
    )

    # Remove exact duplicates.
    lines = deduplicate_lines(
        lines
    )

    # Remove obvious UI noise.
    lines = remove_noise(
        lines
    )

    title = detect_title(
        lines
    )

    sections = build_sections(
        lines
    )

    # Make sure title is not repeated in the sections.
    for section in sections:
        if section.content:
            section.content = [
                line
                for line in section.content
                if line != title
            ]

    return WebPage(
        url=url,
        title=title,
        sections=sections,
    )
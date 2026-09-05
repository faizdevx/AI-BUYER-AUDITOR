from __future__ import annotations

import json
import re
from typing import Any


def _as_text(page: Any) -> str:
    try:
        return page.markdown(
            main_content_only=True,
        ).strip()
    except Exception:
        return ""


def _extract_json_ld(page: Any) -> list[dict[str, Any]]:
    """
    Extract JSON-LD Product/Offer objects from the page.
    """
    results: list[dict[str, Any]] = []

    try:
        scripts = page.css(
            'script[type="application/ld+json"]'
        )
    except Exception:
        return results

    for script in scripts:
        try:
            text = script.text
            if not text:
                continue

            data = json.loads(text)

            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue

                if "@graph" in item and isinstance(
                    item["@graph"],
                    list,
                ):
                    for graph_item in item["@graph"]:
                        if isinstance(graph_item, dict):
                            results.append(graph_item)
                else:
                    results.append(item)

        except (
            json.JSONDecodeError,
            TypeError,
            AttributeError,
        ):
            continue

    return results


def _contains_product_schema(
    json_ld: list[dict[str, Any]],
) -> bool:
    for item in json_ld:
        item_type = item.get("@type")

        if isinstance(item_type, str):
            types = {item_type.casefold()}
        elif isinstance(item_type, list):
            types = {
                str(value).casefold()
                for value in item_type
            }
        else:
            types = set()

        if "product" in types:
            return True

    return False


def _contains_offer_schema(
    json_ld: list[dict[str, Any]],
) -> bool:
    for item in json_ld:
        offers = item.get("offers")

        if offers:
            return True

    return False


def assess_product_page(
    page: Any,
) -> dict[str, Any]:
    """
    Deterministically decide whether a webpage is worth sending
    to Groq.

    This does NOT claim the page is definitely buyable.
    It only decides whether the page looks sufficiently like an
    individual product page.
    """

    text = _as_text(page)

    if not text:
        return {
            "is_likely_product": False,
            "score": 0,
            "signals": [],
            "text": "",
            "json_ld": [],
        }

    lower = text.casefold()

    json_ld = _extract_json_ld(page)

    score = 0
    signals: list[str] = []

    # Strong signal: schema.org Product.
    if _contains_product_schema(json_ld):
        score += 4
        signals.append("product_jsonld")

    # Strong signal: schema.org Offer.
    if _contains_offer_schema(json_ld):
        score += 2
        signals.append("offer_jsonld")

    # Product-page language.
    product_terms = (
        "add to cart",
        "add to bag",
        "buy now",
        "size",
        "select size",
        "select color",
        "quantity",
        "availability",
        "in stock",
        "out of stock",
    )

    matched_terms = [
        term
        for term in product_terms
        if term in lower
    ]

    if matched_terms:
        score += min(len(matched_terms), 4)
        signals.append(
            f"product_terms:{','.join(matched_terms[:4])}"
        )

    # Price/currency signal.
    if re.search(
        r"(₹|rs\.?|inr|\$|€|£)\s?\d[\d,]*(?:\.\d{1,2})?",
        text,
        flags=re.IGNORECASE,
    ):
        score += 2
        signals.append("price_found")

    # Product-like buying action.
    if re.search(
        r"\b(add to (cart|bag)|buy now|shop now)\b",
        lower,
    ):
        score += 2
        signals.append("purchase_action")

    # Discount / sale information is common on product pages.
    if re.search(
        r"\b(discount|sale|mrp|off)\b",
        lower,
    ):
        score += 1
        signals.append("commercial_signal")

    is_likely_product = score >= 5

    return {
        "is_likely_product": is_likely_product,
        "score": score,
        "signals": signals,
        "text": text,
        "json_ld": json_ld,
    }


def extract_product_image_url(
    json_ld: list[dict[str, Any]],
) -> str | None:
    """
    Extract a product image URL from Product JSON-LD.
    """

    for item in json_ld:
        item_type = item.get("@type")

        types: set[str]

        if isinstance(item_type, str):
            types = {
                item_type.casefold()
            }
        elif isinstance(item_type, list):
            types = {
                str(value).casefold()
                for value in item_type
            }
        else:
            types = set()

        if "product" not in types:
            continue

        image = item.get("image")

        if isinstance(image, str):
            return image

        if isinstance(image, list):
            for value in image:
                if isinstance(value, str):
                    return value

    return None
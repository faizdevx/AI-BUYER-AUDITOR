from __future__ import annotations


SPEC_FIELDS = (
    "product_name",
    "brand",
    "category",
    "price",
    "currency",
    "color",
    "sizes",
    "availability",
    "description",
    "features",
    "material",
    "care_instructions",
    "rating",
    "review_count",
    "shipping",
    "returns",
    "country_of_origin",
    "manufacturer",
)


def _parse_price(price: str | None) -> float | None:
    if not price:
        return None

    cleaned = (
        price
        .replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        return None


def compute_price_percentile(
    merchant_price: str | None,
    merchant_currency: str | None,
    competitor_prices: list[tuple[str | None, str | None]],
) -> float:
    merchant_value = _parse_price(
        merchant_price
    )

    if merchant_value is None:
        return 0.5

    comparable = []

    for price, currency in competitor_prices:
        value = _parse_price(price)

        if value is None:
            continue

        if (
            merchant_currency
            and currency
            and currency != merchant_currency
        ):
            continue

        comparable.append(value)

    if not comparable:
        return 0.5

    return sum(
        value <= merchant_value
        for value in comparable
    ) / len(comparable)


def _is_filled(value: object) -> bool:
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, list):
        return len(value) > 0

    return True


def _completeness(product) -> float:
    filled = sum(
        _is_filled(
            getattr(product, field, None)
        )
        for field in SPEC_FIELDS
    )

    return filled / len(SPEC_FIELDS)


def compute_spec_completeness(
    merchant_structured,
    competitor_structured_list,
) -> float:
    return _completeness(
        merchant_structured
    )


def compute_feature_gap(
    merchant_features: list[str],
    competitor_features_list: list[list[str]],
) -> float:
    merchant_count = len(
        merchant_features or []
    )

    if not competitor_features_list:
        return 0.0

    competitor_counts = [
        len(features or [])
        for features in competitor_features_list
    ]

    competitor_average = (
        sum(competitor_counts)
        / len(competitor_counts)
    )

    return round(
        merchant_count - competitor_average,
        2,
    )

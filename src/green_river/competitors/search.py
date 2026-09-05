from green_river.competitors.discovery import (
    generate_discovery_queries,
)
from green_river.db import get_product
from green_river.models import StructuredProduct


def load_merchant_product(
    merchant_id: int,
) -> StructuredProduct:
    """Load the merchant product from Supabase."""

    row = get_product(merchant_id)

    product_data = row.get("product_json")

    if not isinstance(product_data, dict):
        raise ValueError(
            "Stored product_json is invalid."
        )

    return StructuredProduct.model_validate(
        product_data
    )


def build_search_queries(
    product: StructuredProduct,
):
    """Generate semantic competitor discovery queries."""

    return generate_discovery_queries(product)
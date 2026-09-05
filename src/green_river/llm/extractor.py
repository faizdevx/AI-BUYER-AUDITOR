from green_river.llm.graph import product_graph
from green_river.models import StructuredProduct


def extract_product(
    structured_text: str,
) -> dict:
    """
    Structured webpage text
    → LangGraph
    → Groq
    → StructuredProduct
    → dict
    """

    if not structured_text.strip():
        raise ValueError(
            "structured_text cannot be empty."
        )

    result = product_graph.invoke(
        {
            "raw_text": structured_text,
            "product": None,
        }
    )

    product = result.get(
        "product"
    )

    if not isinstance(
        product,
        StructuredProduct,
    ):
        product = StructuredProduct.model_validate(
            product
        )

    return product.model_dump()
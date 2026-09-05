"""Main Green River extraction and embedding service."""

from green_river.db import insert_product
from green_river.embeddings.service import (
    embed_product,
    embed_product_image,
)
from green_river.llm.extractor import extract_product
from green_river.models import StructuredProduct
from green_river.scraper import scrape_and_process

def extract_webpage(url: str):
    """Scrape a webpage and create structured text."""

    return scrape_and_process(url)


def extract_product_from_url(url: str):
    """Extract a StructuredProduct from a webpage URL."""

    (
        raw_path,
        structured_path,
        raw_text,
        structured_text,
    ) = extract_webpage(url)

    product_data = extract_product(structured_text)

    product = StructuredProduct.model_validate(product_data)

    return {
        "raw_path": raw_path,
        "structured_path": structured_path,
        "raw_text": raw_text,
        "structured_text": structured_text,
        "product": product,
    }


def extract_and_embed_product(
    url: str,
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
):
    """Extract product, create embeddings, and save to Supabase."""

    result = extract_product_from_url(url)

    product: StructuredProduct = result["product"]

    embedding_text = product.to_embedding_text()

    embedding_record = embed_product(
        content=embedding_text,
        source_url=url,
        product_id=product.product_id,
    )

    image_embedding = None

    if image_bytes is not None:
        if image_mime_type is None:
            raise ValueError(
                "Image MIME type is required."
            )

        image_embedding = embed_product_image(
            image_bytes=image_bytes,
            mime_type=image_mime_type,
        )

    product_json = product.model_dump(mode="json")

    supabase_id = insert_product(
        product_id=product.product_id,
        source_url=url,
        product_json=product_json,
        embedding=embedding_record.embedding,
        image_embedding=image_embedding,
    )

    result["embedding"] = embedding_record
    result["image_embedding"] = image_embedding
    result["supabase_id"] = supabase_id

    return result


if __name__ == "__main__":
    url = "https://www.amazon.in/Cotton-Khadi-Regular-Casual-Formal/dp/B0GVP528JX?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&smid=A8FRHW4WE2VVR&th=1&psc=1"

    print("Starting product pipeline...")
    print("URL:", url)

    result = extract_and_embed_product(url)

    print("\nPipeline completed.")
    print("Supabase ID:", result["supabase_id"])
    print("Product ID:", result["product"].product_id)
    print("Product:", result["product"].model_dump(mode="json"))
    print("Embedding model:", result["embedding"].model)
    print("Embedding dimensions:", result["embedding"].dimensions)
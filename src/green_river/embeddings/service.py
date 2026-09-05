from green_river.embeddings.graph import embedding_graph
from green_river.models import EmbeddingRecord
from green_river.embeddings.jina import (
    embed_image,
    embed_text,
)

def embed_product(
    content: str,
    source_url: str,
    product_id: str | None = None,
) -> EmbeddingRecord:
    """
    Send product content through the embedding LangGraph.
    """

    if not content.strip():
        raise ValueError(
            "Embedding content cannot be empty."
        )

    result = embedding_graph.invoke(
        {
            "source_url": source_url,
            "product_id": product_id,
            "content": content,
            "embedding": None,
            "record": None,
        }
    )

    record = result.get("record")

    if not isinstance(
        record,
        EmbeddingRecord,
    ):
        raise RuntimeError(
            "Embedding graph did not return "
            "a valid EmbeddingRecord."
        )

    return record

def embed_product_text(content: str) -> list[float]:
    """Create a text embedding."""

    return embed_text(content)


def embed_product_image(
    image_bytes: bytes,
    mime_type: str,
) -> list[float]:
    """Create an image embedding."""

    return embed_image(
        image_bytes=image_bytes,
        mime_type=mime_type,
    )
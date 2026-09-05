from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from green_river.embeddings.jina import (
    JINA_DIMENSIONS,
    JINA_MODEL,
    create_embedding,
)
from green_river.embeddings.storage import (
    save_embedding,
)
from green_river.models import EmbeddingRecord


class EmbeddingState(TypedDict):
    source_url: str
    product_id: str | None
    content: str

    embedding: list[float] | None
    record: EmbeddingRecord | None


def generate_embedding_node(
    state: EmbeddingState,
) -> dict:

    embedding = create_embedding(
        state["content"]
    )

    return {
        "embedding": embedding
    }


def save_embedding_node(
    state: EmbeddingState,
) -> dict:

    embedding = state["embedding"]

    if not embedding:
        raise RuntimeError(
            "Embedding was not generated."
        )

    record = EmbeddingRecord(
        source_url=state["source_url"],
        product_id=state["product_id"],
        content=state["content"],
        model=JINA_MODEL,
        dimensions=JINA_DIMENSIONS,
        embedding=embedding,
    )

    save_embedding(record)

    return {
        "record": record
    }


builder = StateGraph(
    EmbeddingState
)

builder.add_node(
    "generate_embedding",
    generate_embedding_node,
)

builder.add_node(
    "save_embedding",
    save_embedding_node,
)

builder.add_edge(
    START,
    "generate_embedding",
)

builder.add_edge(
    "generate_embedding",
    "save_embedding",
)

builder.add_edge(
    "save_embedding",
    END,
)

embedding_graph = builder.compile()
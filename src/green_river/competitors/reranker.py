from __future__ import annotations

import math

from green_river.competitors.models import CompetitorProduct
from green_river.embeddings.jina import embed_text


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.
    """

    if not a or not b:
        return 0.0

    if len(a) != len(b):
        raise ValueError(
            f"Vector dimensions do not match: "
            f"{len(a)} != {len(b)}"
        )

    dot = sum(
        x * y
        for x, y in zip(a, b)
    )

    norm_a = math.sqrt(
        sum(x * x for x in a)
    )

    norm_b = math.sqrt(
        sum(y * y for y in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def rank_competitors(
    merchant_text_embedding: list[float],
    competitors: list[CompetitorProduct],
) -> list[CompetitorProduct]:
    """
    Generate text similarity scores and rank competitors.

    Image similarity is used when both merchant and competitor
    image embeddings are available.
    """

    ranked: list[CompetitorProduct] = []

    for competitor in competitors:
        candidate_text = competitor.product.to_embedding_text()

        if not candidate_text.strip():
            continue

        candidate_embedding = embed_text(
            candidate_text,
        )

        text_similarity = cosine_similarity(
            merchant_text_embedding,
            candidate_embedding,
        )

        competitor.text_similarity = round(
            text_similarity,
            6,
        )

        # ---------------------------------------------------------
        # Image score
        # ---------------------------------------------------------
        image_similarity = competitor.image_similarity

        if image_similarity is not None:
            final_score = (
                0.6 * text_similarity
                + 0.4 * image_similarity
            )
        else:
            # Text-only fallback when image comparison is unavailable.
            final_score = text_similarity

        competitor.final_score = round(
            final_score,
            6,
        )

        ranked.append(
            competitor,
        )

    ranked.sort(
        key=lambda item: (
            item.final_score
            if item.final_score is not None
            else -1.0
        ),
        reverse=True,
    )

    return ranked
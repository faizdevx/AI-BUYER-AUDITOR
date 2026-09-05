import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

load_dotenv(
    PROJECT_ROOT / ".env"
)


JINA_URL = "https://api.jina.ai/v1/embeddings"

JINA_MODEL = "jina-embeddings-v5-text-small"

JINA_DIMENSIONS = 1024


def create_embedding(
    text: str,
) -> list[float]:

    if not text.strip():
        raise ValueError(
            "Cannot embed empty text."
        )

    api_key = os.getenv(
        "JINA_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "JINA_API_KEY is missing."
        )

    payload = {
        "model": JINA_MODEL,
        "task": "retrieval.passage",
        "dimensions": JINA_DIMENSIONS,
        "normalized": True,
        "embedding_type": "float",
        "input": [text],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = httpx.post(
        JINA_URL,
        headers=headers,
        json=payload,
        timeout=60.0,
    )

    response.raise_for_status()

    data = response.json()

    try:
        embedding = data["data"][0]["embedding"]
    except (
        KeyError,
        IndexError,
        TypeError,
    ) as exc:
        raise RuntimeError(
            "Unexpected Jina API response."
        ) from exc

    return embedding
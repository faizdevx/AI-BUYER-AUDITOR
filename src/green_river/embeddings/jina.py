import base64
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


JINA_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v5-omni-small"
JINA_DIMENSIONS = 1024

JINA_API_KEY = os.getenv("JINA_API_KEY")

if not JINA_API_KEY:
    raise RuntimeError("JINA_API_KEY is missing.")


def _request_embedding(payload: dict) -> list[float]:
    """Send an embedding request to Jina."""

    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
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

    if not data.get("data"):
        raise RuntimeError(
            "Jina returned no embedding data."
        )

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

    if len(embedding) != JINA_DIMENSIONS:
        raise RuntimeError(
            f"Expected {JINA_DIMENSIONS} dimensions, "
            f"got {len(embedding)}."
        )

    return embedding


def create_embedding(
    text: str,
) -> list[float]:
    """Backward-compatible text embedding function."""

    return embed_text(text)


def embed_text(
    text: str,
) -> list[float]:
    """Generate a text embedding."""

    if not text.strip():
        raise ValueError(
            "Cannot embed empty text."
        )

    payload = {
        "model": JINA_MODEL,
        "task": "retrieval.passage",
        "dimensions": JINA_DIMENSIONS,
        "normalized": True,
        "embedding_type": "float",
        "input": [
            text,
        ],
    }

    return _request_embedding(payload)


def embed_image(
    image_bytes: bytes,
    mime_type: str,
) -> list[float]:
    """Generate an image embedding from uploaded image bytes."""

    if not image_bytes:
        raise ValueError(
            "Cannot embed empty image."
        )

    if not mime_type.startswith("image/"):
        raise ValueError(
            f"Invalid image MIME type: {mime_type}"
        )

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data = (
        f"data:{mime_type};base64,{encoded}"
    )

    payload = {
        "model": JINA_MODEL,
        "dimensions": JINA_DIMENSIONS,
        "normalized": True,
        "embedding_type": "float",
        "input": [
            {
                "image": image_data,
            }
        ],
    }

    return _request_embedding(payload)
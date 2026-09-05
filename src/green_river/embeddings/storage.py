import json
from pathlib import Path

from green_river.models import EmbeddingRecord


VECTOR_DIR = (
    Path.cwd()
    / "data"
    / "embeddings"
)


def save_embedding(
    record: EmbeddingRecord,
) -> Path:

    VECTOR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        record.product_id
        or "document"
    )

    path = (
        VECTOR_DIR
        / f"{filename}.json"
    )

    path.write_text(
        json.dumps(
            record.model_dump(),
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path
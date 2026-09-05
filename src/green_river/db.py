"""PostgreSQL persistence for Green River."""

import os

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing.")


def get_connection():
    """Create a database connection."""
    return psycopg.connect(
        DATABASE_URL,
        prepare_threshold=None,
    )


def insert_product(
    *,
    product_id: str | None,
    source_url: str,
    product_json: dict,
    embedding: list[float],
    image_embedding: list[float] | None = None,
) -> int:
    """Insert one product and return its database id."""

    embedding_value = "[" + ",".join(
        str(value) for value in embedding
    ) + "]"

    image_embedding_value = None

    if image_embedding is not None:
        image_embedding_value = "[" + ",".join(
            str(value) for value in image_embedding
        ) + "]"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO merchant_products (
                    product_id,
                    source_url,
                    product_json,
                    embedding,
                    image_embedding
                )
                VALUES (%s, %s, %s, %s::vector, %s::vector)
                RETURNING id
                """,
                (
                    product_id,
                    source_url,
                    Jsonb(product_json),
                    embedding_value,
                    image_embedding_value,
                ),
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError("Insert returned no id.")

            return row[0]

def get_product(product_row_id: int) -> dict:
    """Return one product by database id."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    product_id,
                    source_url,
                    product_json,
                    embedding,
                    created_at
                FROM merchant_products
                WHERE id = %s
                """,
                (product_row_id,),
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError(
                    f"Product {product_row_id} not found."
                )

            columns = [desc.name for desc in cur.description]

            return dict(zip(columns, row))


def similarity_search(
    query_embedding: list[float],
    limit: int = 8,
) -> list[dict]:
    """Return the most similar products."""

    embedding_value = "[" + ",".join(
        str(value) for value in query_embedding
    ) + "]"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    product_id,
                    source_url,
                    product_json,
                    1 - (embedding <=> %s::vector) AS similarity
                FROM merchant_products
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    embedding_value,
                    embedding_value,
                    limit,
                ),
            )

            rows = cur.fetchall()
            columns = [desc.name for desc in cur.description]

            return [
                dict(zip(columns, row))
                for row in rows
            ]


if __name__ == "__main__":
    url = "YOUR_REAL_PRODUCT_URL"

    print("Starting product pipeline...")
    print("URL:", url)

    result = extract_and_embed_product(url)

    print("\nPipeline completed.")
    print("Supabase ID:", result["supabase_id"])
    print("Product ID:", result["product"].product_id)
    print("Product:", result["product"].model_dump(mode="json"))
    print("Embedding model:", result["embedding"].model)
    print("Embedding dimensions:", result["embedding"].dimensions)
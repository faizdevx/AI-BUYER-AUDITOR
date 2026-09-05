from fastapi import FastAPI, HTTPException

from green_river.models import (
    EmbedProductResponse,
    ExtractRequest,
    ExtractResponse,
    MerchantIngestResponse,
    ProductExtractResponse,
)
from green_river.service import (
    extract_and_embed_product,
    extract_product_from_url,
    extract_webpage,
)

app = FastAPI(
    title="Green River",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post(
    "/extract",
    response_model=ExtractResponse,
)
def extract(
    request: ExtractRequest,
):
    try:
        (
            raw_path,
            structured_path,
            raw_text,
            structured_text,
        ) = extract_webpage(
            str(request.url)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return ExtractResponse(
        url=str(request.url),
        raw_file=str(raw_path),
        structured_file=str(structured_path),
        raw_characters=len(raw_text),
        structured_characters=len(structured_text),
        content=structured_text,
    )


@app.post(
    "/extract-product",
    response_model=ProductExtractResponse,
)
def extract_product_endpoint(
    request: ExtractRequest,
):
    try:
        result = extract_product_from_url(
            str(request.url)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return ProductExtractResponse(
        url=str(request.url),
        product=result["product"],
    )


@app.post(
    "/embed-product",
    response_model=EmbedProductResponse,
)
def embed_product_endpoint(
    request: ExtractRequest,
):
    try:
        result = extract_and_embed_product(
            str(request.url)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return EmbedProductResponse(
        url=str(request.url),
        product_id=result["product"].product_id,
        supabase_id=result["supabase_id"],
        model=result["embedding"].model,
        dimensions=result["embedding"].dimensions,
    )


@app.post(
    "/merchant/ingest",
    response_model=MerchantIngestResponse,
)
def merchant_ingest(
    request: ExtractRequest,
):
    try:
        result = extract_and_embed_product(
            str(request.url)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return MerchantIngestResponse(
        id=result["supabase_id"],
        url=str(request.url),
        product=result["product"],
        model=result["embedding"].model,
        dimensions=result["embedding"].dimensions,
    )
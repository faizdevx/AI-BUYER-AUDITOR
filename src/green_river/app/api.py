from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

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


from green_river.competitors.graph import discover_competitors
from green_river.competitors.models import CompetitorFetchResponse
from green_river.models import CompetitorFetchRequest



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
async def merchant_ingest(
    url: str = Form(...),
    image: UploadFile = File(...),
):
    if not image.content_type:
        raise HTTPException(
            status_code=400,
            detail="Image content type is missing.",
        )

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be an image.",
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    if len(image_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image must be 5 MB or smaller.",
        )

    try:
        result = await run_in_threadpool(
            extract_and_embed_product,
            url,
            image_bytes,
            image.content_type,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return MerchantIngestResponse(
        id=result["supabase_id"],
        url=url,
        product=result["product"],
        model=result["embedding"].model,
        dimensions=result["embedding"].dimensions,
    )

@app.post(
    "/competitors/fetch",
    response_model=CompetitorFetchResponse,
)
def competitors_fetch(
    request: CompetitorFetchRequest,
):
    try:
        return discover_competitors(
            request.merchant_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
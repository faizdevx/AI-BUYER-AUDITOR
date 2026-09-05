from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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

from fastapi import HTTPException

from green_river.audit.service import compute_audit_trail
from green_river.db import (
    get_latest_audit_trail,
    get_product,
    save_audit_trail,
)

from green_river.models import (
    GeneratePromptsRequest,
    SimulationRunRequest,
    StructuredProduct,
)
from green_river.prompt_service import (
    generate_and_store_buyer_prompts,
)
from green_river.simulation.service import (
    simulate_buyer_decisions,
)
from green_river.scoring.service import (
    compute_score_report,
)

app = FastAPI(
    title="Green River",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        import traceback

        print("MERCHANT INGEST FAILED:")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
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
async def competitors_fetch(
    request: CompetitorFetchRequest,
):
    try:
        return await discover_competitors(
            request.merchant_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@app.post("/simulation/run")
async def run_simulation(
    request: SimulationRunRequest,
):
    try:
        merchant = get_product(
            request.merchant_id,
        )

        if merchant is None:
            raise HTTPException(
                status_code=404,
                detail=f"Merchant {request.merchant_id} not found.",
            )

        merchant_product = StructuredProduct.model_validate(
            merchant["product_json"]
        )

        merchant_product_id = (
            merchant_product.product_id
            or str(request.merchant_id)
        )

        competitor_result = await discover_competitors(
            request.merchant_id,
        )

        candidates = [
            {
                "product_id": str(merchant_product_id),
                "product": merchant_product.model_dump(
                    exclude_none=True,
                ),
            }
        ]

        for competitor in competitor_result["competitors"]:
            product = competitor["product"]

            product_id = (
                product.get("product_id")
                or competitor["source_url"]
            )

            candidates.append(
                {
                    "product_id": str(product_id),
                    "product": product,
                }
            )

        if not candidates:
            raise ValueError(
                "No candidate products available for simulation."
            )

        results = await simulate_buyer_decisions(
            merchant_id=request.merchant_id,
            candidates=candidates,
            provider="groq",
        )

        completed = sum(
            result["status"] == "completed"
            for result in results
        )

        failed = sum(
            result["status"] == "failed"
            for result in results
        )

        return {
            "merchant_id": request.merchant_id,
            "status": (
                "completed"
                if failed == 0
                else "partial"
            ),
            "candidate_count": len(candidates),
            "prompt_count": len(results),
            "completed": completed,
            "failed": failed,
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.post("/prompts/generate")
async def generate_prompts(
    request: GeneratePromptsRequest,
):
    try:
        prompts = await run_in_threadpool(
            generate_and_store_buyer_prompts,
            request.merchant_id,
        )

        return {
            "merchant_id": request.merchant_id,
            "prompts": prompts,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.get("/audit/{merchant_id}")
async def get_audit(
    merchant_id: int,
):
    try:
        merchant = get_product(
            merchant_id,
        )

        if merchant is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Merchant {merchant_id} not found."
                ),
            )

        existing = get_latest_audit_trail(
            merchant_id,
        )

        if existing:
            return existing["audit_json"]

        product_json = merchant["product_json"]

        merchant_product_id = product_json.get(
            "product_id"
        )

        if not merchant_product_id:
            raise HTTPException(
                status_code=400,
                detail="Merchant product_id is missing.",
            )

        audit = compute_audit_trail(
            merchant_id=merchant_id,
            merchant_product_id=merchant_product_id,
        )

        audit_dict = audit.model_dump()

        save_audit_trail(
            merchant_id,
            audit_dict,
        )

        return audit_dict

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.post("/score/{merchant_id}")
async def score_merchant(
    merchant_id: int,
):
    try:
        report = await compute_score_report(
            merchant_id
        )

        return report.model_dump()

    except ValueError as exc:
        print(f"SCORE VALUE ERROR: {exc!r}")
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        import traceback

        print("SCORE FAILED:")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc
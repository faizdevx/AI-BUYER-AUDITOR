from __future__ import annotations

from pydantic import BaseModel, Field

from green_river.models import StructuredProduct


class DiscoveryQueries(BaseModel):
    queries: list[str] = Field(
        min_length=3,
        max_length=5,
    )


class CandidateURL(BaseModel):
    url: str
    source: str


class SearchQuery(BaseModel):
    query: str
    source: str = "semantic"


class RawListing(BaseModel):
    url: str
    source: str
    title: str | None = None
    snippet: str | None = None
    image_url: str | None = None


class CompetitorProduct(BaseModel):
    source: str
    source_url: str
    product: StructuredProduct
    text_similarity: float | None = None
    image_similarity: float | None = None
    final_score: float | None = None


class CompetitorFetchResponse(BaseModel):
    merchant_id: int

    queries: list[SearchQuery] = Field(
        default_factory=list
    )

    candidates: list[CandidateURL] = Field(
        default_factory=list
    )

    competitors: list[CompetitorProduct] = Field(
        default_factory=list
    )
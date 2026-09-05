from __future__ import annotations

from pydantic import BaseModel, Field


class GapAnalysis(BaseModel):
    price_percentile: float
    is_overpriced: bool

    spec_completeness_score: float

    feature_count_vs_competitor_avg: float


class Recommendation(BaseModel):
    title: str
    priority: str
    reasoning: str

    modeled_estimate: float = Field(
        ge=0.0,
        le=0.20,
    )

    disclaimer: str

    evidence: dict[str, object] = Field(
        default_factory=dict
    )

    confidence: str


class ScoreReport(BaseModel):
    merchant_id: int

    current_win_rate: float

    overall_score: float

    gap_analysis: GapAnalysis

    recommendations: list[Recommendation] = Field(
        default_factory=list
    )

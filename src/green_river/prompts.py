from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PromptIntent = Literal[
    "budget",
    "feature",
    "use_case",
    "comparison",
    "value",
    "alternative",
    "quality",
    "beginner",
    "expert",
    "purchase_decision",
]


class BuyerPrompt(BaseModel):
    prompt: str = Field(min_length=10)
    intent_type: PromptIntent


class BuyerPromptSet(BaseModel):
    prompts: list[BuyerPrompt] = Field(
        min_length=10,
        max_length=10,
    )
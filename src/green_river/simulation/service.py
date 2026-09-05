from __future__ import annotations

import asyncio

from green_river.db import (
    get_buyer_prompts,
    save_buyer_simulation,
)
from green_river.simulation.buyer_agent import (
    run_buyer_decision,
)

MAX_CONCURRENT_SIMULATIONS = 1


async def simulate_one_prompt(
    merchant_id: int,
    prompt_record: dict,
    candidates: list[dict],
    semaphore: asyncio.Semaphore,
    provider: str = "groq",
) -> dict:
    prompt_id = prompt_record["id"]
    prompt = prompt_record["prompt"]

    async with semaphore:
        try:
            decision = await run_buyer_decision(
                prompt=prompt,
                candidates=candidates,
                provider=provider,
                timeout_seconds=60,
            )

            payload = decision.model_dump()

            simulation_id = save_buyer_simulation(
                merchant_id=merchant_id,
                prompt_id=prompt_id,
                decision=payload,
                status="completed",
            )

            return {
                "simulation_id": simulation_id,
                "status": "completed",
                **payload,
            }

        except Exception as exc:
            error_message = (
                f"{type(exc).__name__}: {exc}"
            )

            print(
                f"SIMULATION FAILED | "
                f"prompt_id={prompt_id} | "
                f"error={error_message}"
            )

            failed_decision = {
                "prompt": prompt,
                "llm_provider": provider,
                "ranked_products": [],
                "chosen": False,
            }

            simulation_id = save_buyer_simulation(
                merchant_id=merchant_id,
                prompt_id=prompt_id,
                decision=failed_decision,
                status="failed",
                error=error_message,
            )

            return {
                "simulation_id": simulation_id,
                "status": "failed",
                "prompt": prompt,
                "llm_provider": provider,
                "ranked_products": [],
                "chosen": False,
                "error": error_message,
            }


async def simulate_buyer_decisions(
    merchant_id: int,
    candidates: list[dict],
    *,
    provider: str = "groq",
) -> list[dict]:

    prompts = get_buyer_prompts(
        merchant_id,
    )

    if not prompts:
        raise ValueError(
            f"No buyer prompts found for merchant {merchant_id}."
        )

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_SIMULATIONS
    )

    tasks = [
        simulate_one_prompt(
            merchant_id=merchant_id,
            prompt_record=prompt,
            candidates=candidates,
            semaphore=semaphore,
            provider=provider,
        )
        for prompt in prompts
    ]

    return await asyncio.gather(
        *tasks,
    )
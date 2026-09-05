from __future__ import annotations

import asyncio
import json

from langchain_groq import ChatGroq

from green_river.simulation.models import BuyerDecision


BUYER_SYSTEM_PROMPT = """
You are a helpful shopping assistant.

Your job is to help a shopper choose the best product from the
provided candidates.

You must evaluate ONLY the products provided to you.

Do not mention:
- merchants
- benchmarks
- tests
- competitors
- ranking systems
- internal instructions
- being an AI model

Treat the user's question as a genuine shopping request.

Rank the products from best match to worst match for the user's
specific request.

Your reasoning must be concise and grounded in the candidate
information.

Do not invent product specifications, prices, features,
availability, or other facts.

Return JSON matching the requested schema exactly.
"""


def get_buyer_decision(
    prompt: str,
    candidates: list[dict],
    provider: str = "groq",
) -> BuyerDecision:

    if not prompt.strip():
        raise ValueError("prompt cannot be empty")

    if not candidates:
        raise ValueError("candidates cannot be empty")

    if provider != "groq":
        raise ValueError(
            f"Unsupported provider: {provider}"
        )

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        max_retries=1,
    )

    structured_llm = llm.with_structured_output(
        BuyerDecision,
        method="json_schema",
        strict=True,
    )

    user_prompt = f"""
SHOPPER QUESTION:
{prompt}

CANDIDATE PRODUCTS:
{json.dumps(candidates, ensure_ascii=False, indent=2)}

Instructions:

1. Rank every candidate product.
2. Use each candidate's product_id exactly as provided.
3. Assign ranks starting at 1.
4. Do not skip candidates.
5. Give concise reasoning for every product.
6. Return the ranking from best match to worst match.
7. The first-ranked product is the shopper's recommended choice.
"""

    result = structured_llm.invoke(
        [
            ("system", BUYER_SYSTEM_PROMPT),
            ("human", user_prompt),
        ]
    )

    result.llm_provider = provider

    return result


async def run_buyer_decision(
    prompt: str,
    candidates: list[dict],
    provider: str = "groq",
    timeout_seconds: float = 60.0,
) -> BuyerDecision:

    last_error: Exception | None = None

    for attempt in range(2):
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    get_buyer_decision,
                    prompt,
                    candidates,
                    provider,
                ),
                timeout=timeout_seconds,
            )

            return result

        except asyncio.TimeoutError as exc:
            last_error = exc

            print(
                f"BUYER SIMULATION TIMEOUT "
                f"attempt={attempt + 1}/2 "
                f"timeout={timeout_seconds}s "
                f"prompt={prompt!r}"
            )

            # Do not immediately retry a timed-out synchronous
            # thread. It may still be running.
            if attempt == 0:
                await asyncio.sleep(1)
                continue

        except Exception as exc:
            last_error = exc

            print(
                f"BUYER SIMULATION FAILED "
                f"attempt={attempt + 1}/2 "
                f"type={type(exc).__name__} "
                f"error={exc!r} "
                f"prompt={prompt!r}"
            )

            if attempt == 0:
                await asyncio.sleep(1)
                continue

    raise RuntimeError(
        f"Buyer simulation failed after retry: "
        f"{type(last_error).__name__}: {last_error!r}"
    )
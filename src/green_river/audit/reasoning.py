from __future__ import annotations

import json

from langchain_groq import ChatGroq


def extract_loss_reasons(
    losses: list[dict],
) -> list[str]:
    if not losses:
        return []

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        max_retries=1,
    )

    prompt = f"""
You are analyzing shopping assistant decisions.

The merchant product failed to rank #1 in these cases.

LOSS DATA:
{json.dumps(losses, ensure_ascii=False, indent=2)}

Summarize the main reasons the merchant lost.

Rules:

- Return only concise reasons.
- Group similar reasons together.
- Do not invent information.
- Use only the supplied reasoning.
- Focus on actionable product-level causes.
- Do not mention benchmarks, testing, AI providers, or internal systems.
- Return 3 to 7 reasons.
"""

    result = llm.invoke(prompt)

    text = getattr(result, "content", "")

    if not isinstance(text, str):
        return []

    reasons = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        line = line.lstrip("-•*0123456789. ").strip()

        if line:
            reasons.append(line)

    return reasons[:7]

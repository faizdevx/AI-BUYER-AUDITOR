import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

from green_river.llm.prompts import SYSTEM_PROMPT
from green_river.models import StructuredProduct


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

load_dotenv(
    PROJECT_ROOT / ".env"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing."
    )


class ExtractionState(TypedDict):
    raw_text: str
    product: StructuredProduct | None


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=2,
    api_key=GROQ_API_KEY,
)


structured_llm = llm.with_structured_output(
    StructuredProduct,
    method="json_schema",
    strict=True,
)


def extract_product_node(
    state: ExtractionState,
) -> dict:

    prompt = f"""
{SYSTEM_PROMPT}

SOURCE TEXT:
--------------------
{state["raw_text"]}
--------------------
"""

    product = structured_llm.invoke(
        prompt
    )

    return {
        "product": product
    }


builder = StateGraph(
    ExtractionState
)

builder.add_node(
    "extract_product",
    extract_product_node,
)

builder.add_edge(
    START,
    "extract_product",
)

builder.add_edge(
    "extract_product",
    END,
)

product_graph = builder.compile()
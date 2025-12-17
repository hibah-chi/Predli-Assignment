from tools.llm import call_llm
from graph.state import GraphState
from rich import print

from pydantic import BaseModel
from typing import Optional, Literal

class ContextSchema(BaseModel):
    geography: Optional[str]  # country, "Global", or null
    time_range: Optional[str]  # year(s) or relative phrase
    domain: Literal["finance", "awards", "movies", "other"]


def context_node(state: GraphState) -> GraphState:
    topic = state["topic"]

    prompt = f"""
Extract the following information from the topic.

Topic: "{topic}"

Fields:
- geography (country or Global or null)
- time_range (explicit year(s) or relative phrase)
- domain (finance, awards, movies, other)
"""

    context = call_llm(
        prompt=prompt,
        system="You extract structured metadata from user prompts. You return only JSON. Do not include any explanations or comments or backticks. Only give a JSON object.",
        schema=ContextSchema,
        json_output=True,
        cost_tracker=state["cost_tracker"],
    )

    # `context` is already a validated object
    print(context)

    # Convert to dict if your GraphState expects raw JSON
    state["context"] = context.model_dump()
    return state

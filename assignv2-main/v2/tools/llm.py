import time
import os
import json
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

NANO_MODEL = "gpt-4.1-nano"
MINI_MODEL = "gpt-4.1-mini"

# Pricing per 1 token
PRICING = {
    NANO_MODEL: {"input": 0.1 / 1_000_000, "output": 0.4 / 1_000_000},
    MINI_MODEL: {"input": 0.4 / 1_000_000, "output": 1.6 / 1_000_000},
}


def _print_cost(model: str, prompt_tokens: int, completion_tokens: int, cost: float):
    print(
        f"[LLM] model={model} prompt_tokens={prompt_tokens} completion_tokens={completion_tokens} "
        f"step_cost=${cost:.6f}"
    )


def call_llm(
    prompt: str,
    system: str = "You are a helpful research assistant.",
    max_tokens: int = 400,
    temperature: float = 0.3,
    retries: int = 3,
    schema: Optional[type[BaseModel]] = None,
    json_output: bool = False,
    model: str = NANO_MODEL,
    cost_tracker=None,
):
    """
    If `schema` is provided, the response will:
      - be forced to JSON
      - validated against the schema
      - returned as a parsed Pydantic object

    Otherwise, returns plain text.
    Uses OpenAI GPT-4.1-nano by default.
    """
    client = OpenAI()

    for attempt in range(retries):
        try:
            user_prompt = prompt
            if schema:
                schema_json = schema.model_json_schema()
                user_prompt = (
                    f"{prompt}\n\nReturn a JSON object matching this schema: {schema_json}"
                )
            elif json_output:
                user_prompt = (
                    f"{prompt}\n\nReturn ONLY a valid JSON object. Do not include comments, backticks, or extra text."
                )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content.strip()

            usage = getattr(response, "usage", None)
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            pricing = PRICING.get(model, {"input": 0.0, "output": 0.0})
            step_cost = prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]
            _print_cost(model, prompt_tokens, completion_tokens, step_cost)
            if cost_tracker and hasattr(cost_tracker, "add_usage"):
                cost_tracker.add_usage(model, prompt_tokens, completion_tokens, step_cost)

            # Strip markdown code blocks if present (```json ... ``` or ``` ... ```)
            if text.startswith("```"):
                lines = text.split('\n')
                if lines[0].strip() in ['```', '```json', '```JSON']:
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                text = '\n'.join(lines).strip()

            if schema:
                return schema.model_validate_json(text)
            if json_output:
                return json.loads(text)
            return text

        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                wait = 2 ** attempt
                print(f"LLM rate limit encountered: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                if attempt == retries - 1:
                    raise
                time.sleep(1)

    raise RuntimeError("LLM failed after retries")


def call_gemini(
    prompt: str,
    system: str = "You are a helpful research assistant.",
    max_tokens: int = 4000,
    temperature: float = 0.3,
    retries: int = 3,
    cost_tracker=None,
) -> str:
    """
    Use GPT-4.1-mini (OpenAI) for final summarization.
    """
    client = OpenAI()

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MINI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            text = response.choices[0].message.content.strip()

            usage = getattr(response, "usage", None)
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            pricing = PRICING.get(MINI_MODEL, {"input": 0.0, "output": 0.0})
            step_cost = prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]
            _print_cost(MINI_MODEL, prompt_tokens, completion_tokens, step_cost)
            if cost_tracker and hasattr(cost_tracker, "add_usage"):
                cost_tracker.add_usage(MINI_MODEL, prompt_tokens, completion_tokens, step_cost)

            return text

        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                wait = 2 ** attempt
                print(f"LLM rate limit encountered: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                if attempt == retries - 1:
                    raise
                time.sleep(1)

    raise RuntimeError("OpenAI call failed after retries")


def count_tokens(text: str) -> int:
    if not text:
        return 0
    return len(text) // 4 + 1

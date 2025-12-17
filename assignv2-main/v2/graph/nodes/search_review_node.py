import json
from typing import List, Dict

from graph.state import GraphState
from tools.web_search import web_search, fetch_page_text
from tools.llm import call_llm, count_tokens
from pydantic import BaseModel, Field
from rich import print


class Decision(BaseModel):
    should_search_more: bool = Field(...)
    reason: str
    suggested_queries: List[str] = Field(default_factory=list)


def _token_tally(articles: List[Dict]) -> int:
    """Count tokens in title + snippet only (no summaries)."""
    total = 0
    for a in articles:
        combined = " ".join([
            a.get("title", ""),
            a.get("snippet", ""),
        ])
        total += count_tokens(combined)
    return total


def _content_token_tally(articles: List[Dict]) -> int:
    """Count tokens in title + snippet + content (for final summary budget)."""
    total = 0
    for a in articles:
        combined = " ".join([
            a.get("title", ""),
            a.get("snippet", ""),
            a.get("content", ""),
        ])
        total += count_tokens(combined)
    return total


def search_review_node(state: GraphState) -> GraphState:
    search_results = state.get("search_results", {})

    # iterative loop
    while True:
        # compute token counts:
        # - snippet+title for decision prompt (what LLM sees)
        # - content+snippet+title for final summary budget (hard limit)
        snippet_tokens = 0
        total_tokens = 0
        for _, articles in search_results.items():
            snippet_tokens += _token_tally(articles)
            total_tokens += _content_token_tally(articles)

        print(f"[search_review] Token tally - Decision (title+snippet): {snippet_tokens}, Summary budget (title+snippet+content): {total_tokens}")

        # hard stop at 250k based on full content
        if total_tokens >= 250_000:
            print("Token cap reached (250k). Stopping further search.")
            break

        # build snippets+title list for LLM decision
        snippet_lines = []
        for subtopic, articles in search_results.items():
            for a in articles[:4]:  # keep prompt bounded
                snippet_lines.append(
                    f"Subtopic: {subtopic}\nTitle: {a.get('title','')}\nSnippet: {(a.get('snippet') or '')[:400]}"
                )
        snippet_text = "\n\n".join(snippet_lines)

        prompt = f"""
You are advising whether to continue web searches for a research task.
Review the provided titles and snippets. If we already have diverse material and token budget is reasonable, suggest stopping.
Otherwise, suggest focused new queries to fill gaps or deepen coverage.
Current tokens for decision: {snippet_tokens} (title+snippet).
Full content tokens for final summary: {total_tokens}. Hard limit is 250k.

Titles and snippets (sampled):
{snippet_text}

Advise: should we search more? If yes, suggest 1-3 focused queries.
"""

        decision = call_llm(
            prompt=prompt,
            system="You are a concise research operations advisor. Respond with JSON only.",
            schema=Decision,
                cost_tracker=state["cost_tracker"],
        )

        print(f"[search_review] Decision: {decision}")

        if not decision.should_search_more or not decision.suggested_queries:
            break

        # run additional searches per suggested query
        for q in decision.suggested_queries:
            results = web_search(q, max_results=4)
            for r in results:
                content = fetch_page_text(r.get("url"))
                if not content:
                    continue
                article = {
                    "title": r.get("title"),
                    "snippet": r.get("snippet"),
                    "content": content,
                    "url": r.get("url"),
                    "query": q,
                }

                # assign to a generic subtopic bucket for new queries
                search_results.setdefault("additional", []).append(article)

    # persist snapshot
    with open("debug_search_results.json", "w", encoding="utf-8") as f:
        json.dump(search_results, f, ensure_ascii=False, indent=2)

    state["search_results"] = search_results
    state["token_estimate"] = total_tokens
    return state

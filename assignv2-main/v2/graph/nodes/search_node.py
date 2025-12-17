from graph.state import GraphState
from tools.web_search import web_search, fetch_page_text
from rich import print
from tqdm import tqdm

def search_node(state: GraphState) -> GraphState:
    search_queries = state["search_queries"]

    search_results = {}
    print(search_queries)

    for subtopic, queries in tqdm(search_queries.items(), desc="Searching subtopics"):
        articles = []

        for q in queries:
            results = web_search(q, max_results=4)

            for r in results:
                content = fetch_page_text(r.get("url"))
                if not content:
                    continue  # discard items with no content (e.g., bot checks)
                articles.append({
                    "title": r.get("title"),
                    "snippet": r.get("snippet"),
                    "content": content,
                    "url": r.get("url"),
                    "query": q
                })

        search_results[subtopic] = articles
    print("Completed web searches for all subtopics.")
    # print("Example item:", search_results[next(iter(search_results))][0] if search_results else "No results")
    state["search_results"] = search_results
    # save to a json fioe
    with open("debug_search_results.json", "w", encoding="utf-8") as f:
        import json
        json.dump(search_results, f, ensure_ascii=False, indent=4)
    # report how many tokens in title + snippet + content
    total_tokens = 0
    for subtopic, articles in search_results.items():
        for a in articles:
            from tools.llm import count_tokens
            text = (a.get("title") or "") + " " + (a.get("snippet") or "") + " " + (a.get("content") or "")
            total_tokens += count_tokens(text)
    print(f"Total tokens in search results: {total_tokens}")
    return state


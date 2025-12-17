from graph.state import GraphState
from datetime import datetime


def query_node(state: GraphState) -> GraphState:
    context = state["context"]
    subtopics = state["subtopics"]

    year_now = datetime.now().year
    time_phrase = context.get("time_range")

    # Convert relative time
    if time_phrase == "last year":
        time_query = str(year_now - 1)
    elif time_phrase == "last three years":
        time_query = f"{year_now-3} {year_now-2} {year_now-1}"
    else:
        time_query = time_phrase or ""

    queries = {}

    for sub in subtopics:
        base = f"{sub}"

        if context.get("geography"):
            base += f" {context['geography']}"

        if time_query:
            base += f" {time_query}"

        base = base.strip()

        # Create 4 focused variants to ensure multiple searches per subtopic
        variants = [
            base,
            f"{base} overview analysis",
            f"{base} latest developments",
            f"{base} key statistics data",
            f"{base} expert commentary",
        ][:4]

        queries[sub] = variants

    state["search_queries"] = queries
    return state

from graph.graph import build_graph
from graph.nodes.input_node import input_node
from graph.nodes.pdf_node import pdf_node


def run(topic, output_pdf):
    graph = build_graph()
    state = input_node(topic)
    final_state = graph.invoke(state)
    pdf_node(final_state, output_pdf)

    cost_summary = final_state["cost_tracker"].summary()

    state_snapshot = {
        "topic": final_state.get("topic"),
        "geography": final_state.get("context", {}).get("geography"),
        "time_range": final_state.get("context", {}).get("time_range"),
        "domain": final_state.get("context", {}).get("domain"),
        "subtopics": final_state.get("subtopics"),
        "search_queries_count": sum(len(v) for v in final_state.get("search_queries", {}).values()),
        "search_results_count": sum(len(v) for v in final_state.get("search_results", {}).values()),
        "citations_count": len(final_state.get("citations", [])),
    }

    print(f"Report generated: {output_pdf}")
    print("Agent state snapshot:", state_snapshot)
    print(
        f"Cost summary: prompt_tokens={cost_summary['prompt_tokens']}, "
        f"completion_tokens={cost_summary['completion_tokens']}, "
        f"total_cost=${cost_summary['total_cost_usd']:.6f}"
    )


if __name__ == "__main__":
    run("Indian markets over the last year", "reports/indian_markets.pdf")
    run("Nobel awards from the last three years", "reports/nobel_awards.pdf")
    run("Movies to look out for in 2026", "reports/movies_2026.pdf")

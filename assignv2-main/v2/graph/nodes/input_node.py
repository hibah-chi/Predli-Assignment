from graph.state import GraphState
from tools.cost_tracker import CostTracker


def input_node(topic: str) -> GraphState:
    return {
        "topic": topic,
        "context": {},
        "subtopics": [],
        "search_queries": {},
        "search_results": {},
        "expanded_results": {},
        "clusters": {},
        "cluster_summaries": {},
        "final_markdown": "",
        "citations": set(),
        "cost_tracker": CostTracker(),
    }

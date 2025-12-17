from langgraph.graph import StateGraph
from graph.state import GraphState

from graph.nodes.input_node import input_node
from graph.nodes.context_node import context_node
from graph.nodes.planner_node import planner_node
from graph.nodes.query_node import query_node
from graph.nodes.search_node import search_node
from graph.nodes.search_review_node import search_review_node
from graph.nodes.summarize_node import summarize_node


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("context", context_node) # done
    graph.add_node("planner", planner_node) # done
    graph.add_node("query", query_node) # done 
    graph.add_node("search", search_node) # needs fixing
    graph.add_node("search_review", search_review_node)
    graph.add_node("summarize", summarize_node)

    graph.set_entry_point("context")

    graph.add_edge("context", "planner")
    graph.add_edge("planner", "query")
    graph.add_edge("query", "search")
    graph.add_edge("search", "search_review")
    graph.add_edge("search_review", "summarize")

    return graph.compile()

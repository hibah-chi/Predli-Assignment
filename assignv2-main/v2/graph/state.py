from typing import Dict, List, Set, TypedDict, Optional


class GraphState(TypedDict):
    # Raw input
    topic: str

    # Normalized context
    context: Dict[str, Optional[str]]

    # Planning
    subtopics: List[str]

    # Search
    search_queries: Dict[str, List[str]]
    search_results: Dict[str, List[Dict]]

    # Synthesis
    cluster_summaries: Dict[str, List[str]]

    # Output
    final_markdown: str
    citations: Set[str]

    # Meta
    cost_tracker: object

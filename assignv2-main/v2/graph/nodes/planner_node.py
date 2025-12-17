from tools.llm import call_llm
from graph.state import GraphState
from rich import print

def planner_node(state: GraphState) -> GraphState:
    
    domain = state["context"].get("domain", "general")
    topic = state["topic"]
    print("Generating subtopics for topic " + topic + " in domain " + domain)

    prompt = f"""
Generate 3 professional report subtopics for the topic "{topic}". These subtopics will be used for web searches, so include
relevant keywords from the topic in each subtopic. 
Domain: {domain}

Rules:
- no more than 8 words per subtopic
- return each subtopic on a new line
- no numbering, no bullet points, just the subtopic text
- be specific and relevant to the main topic
- include enough detail to guide focused web searches
"""

    output = call_llm(
        prompt,
        system="You are a research planner.",
            cost_tracker=state["cost_tracker"],
        json_output=False,
    )

    subtopics = [
        line.strip("- ").strip()
        for line in output.split("\n")
        if line.strip()
    ]
    print(subtopics)
    state["subtopics"] = subtopics
    # print(subtopics)
    return state

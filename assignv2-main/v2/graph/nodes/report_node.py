from graph.state import GraphState
from tools.llm import call_llm


def report_node(state: GraphState) -> GraphState:
    topic = state["topic"]
    context = state["context"]
    summaries = state["cluster_summaries"]

    sections_text = ""

    for subtopic, summary_list in summaries.items():
        combined = "\n".join(summary_list)

        sections_text += f"""
## {subtopic}

{combined}
"""

    prompt = f"""
Write a professional analytical report in Markdown.

Title: {topic}

Context:
- Geography: {context.get('geography')}
- Time range: {context.get('time_range')}
- Domain: {context.get('domain')}

Rules:
- Include an Executive Summary (150–200 words)
- Total length: 1500–2000 words
- Use clear headings
- Neutral, factual tone

Content:
{sections_text}
"""

    markdown = call_llm(
        prompt,
        system="You are an expert research report writer.",
        cost_tracker=state["cost_tracker"],
    )

    state["cost_tracker"].add(markdown)
    state["final_markdown"] = markdown
    return state

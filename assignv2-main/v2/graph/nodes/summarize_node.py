from graph.state import GraphState
from tools.llm import call_gemini, count_tokens
import json
import os


def summarize_node(state: GraphState) -> GraphState:
    """Generate a single final markdown report from all search results."""
    search_results = state.get("search_results", {})
    topic = state["topic"]
    context = state["context"]

    # Aggregate all content and snippets into one text block
    all_material = []
    for subtopic, articles in search_results.items():
        all_material.append(f"\n### {subtopic}\n")
        for a in articles:
            title = a.get("title", "")
            snippet = a.get("snippet", "")
            content = a.get("content", "")
            url = a.get("url", "")

            item_text = f"**{title}** (source: {url})\n"
            if snippet:
                item_text += f"Summary: {snippet}\n"
            if content:
                item_text += f"Full content: {content}\n"
            all_material.append(item_text)

            if url:
                state["citations"].add(url)

    combined_material = "\n".join(all_material)

    # Enforce 250k token cap for summarizer input (approx 4 chars/token)
    max_tokens = 250_000
    input_tokens = count_tokens(combined_material)
    was_trimmed = False
    if input_tokens > max_tokens:
        char_cap = max_tokens * 4
        combined_material = combined_material[:char_cap]
        was_trimmed = True
        print(f"[summarize] Input tokens {input_tokens} exceed {max_tokens}. Trimmed to ~{max_tokens} tokens (~{char_cap} chars).")

    # Save input to JSON
    input_data = {
        "topic": topic,
        "context": context,
        "search_results": search_results,
        "combined_material": combined_material,
        "input_tokens": input_tokens,
        "trimmed_to_250k": was_trimmed,
    }
    
    os.makedirs("debug_outputs", exist_ok=True)
    with open("debug_outputs/summarize_input.json", "w", encoding="utf-8") as f:
        json.dump(input_data, f, ensure_ascii=False, indent=2)

    prompt_text = f"""You are an expert research report writer. Using the provided search results, titles, snippets, and content, write a professional analytical HTML report.

Topic: {topic}
Geography: {context.get('geography')}
Time range: {context.get('time_range')}
Domain: {context.get('domain')}

REQUIREMENTS:
- Write 1500–2000 words
- Include an Executive Summary (150–200 words)
- Use HTML tags: <h1>, <h2>, <h3>, <p>, <b>, <i>, <ul>, <li>
- Use <h1> for main title, <h2> for major sections, <h3> for subsections
- BOLD ALL HEADINGS: <h1><b>Title</b></h1>, <h2><b>Section</b></h2>, <h3><b>Subsection</b></h3>
- Neutral, factual tone
- Organize by themes/subtopics where applicable
- NO TABLES - use bullet lists or prose instead
- Use numbered citations [1], [2], [3], etc. in the text when referencing specific information

CITATION AND REFERENCE INSTRUCTIONS:
1. When citing a source in the text, use numbered citations like: [1], [2], etc.
2. Select ONLY the 7-8 MOST IMPORTANT and RELEVANT sources you cite in the report
3. Include these sources in a <h2><b>References</b></h2> section at the END
4. Format all references in APA 7 style with numbered citations:
   - [1] Author(s). (Year). Title. Source name. URL
   - [2] Author(s). (Year). Title. Source name. URL
   - Example: [1] Smith, J. (2023). Economic trends in India. Financial Times. https://example.com
5. Each reference must start with its number in brackets [1], [2], etc. to match the text citations

IMPORTANT HTML FORMATTING:
- Wrap all content in proper HTML tags
- Use <b> and </b> tags for bold emphasis (NOT <strong>)
- Use <i> and </i> tags for italics (NOT <em>)
- Output ONLY valid HTML content (no <html>, <head>, or <body> tags)
- Use <b> in bullet points and text for any emphasis: <li><b>Key term:</b> description</li>
- ALWAYS use <b> for technical terms, important phrases, names, emphasized words, AND ALL HEADINGS
- Every heading must be wrapped in <b> tags

Material:
{combined_material}
"""

    system_message = (
        "You are an expert research report writer. Output valid HTML only with numbered citations [1], [2], etc. "
        "in the text and APA 7 formatted references section at the end. Use <b> tags for bold, <i> tags for italics. "
        "IMPORTANT: BOLD ALL HEADINGS by wrapping them in <b></b> tags. Example: <h2><b>Section Title</b></h2>. "
        "Limit to 7-8 most important sources. Do not create tables. Do NOT emit <br> tags. Do NOT leave unclosed tags. Do not put unnecessary artifacts. Keep citations closest to the text, not only at the end of every paragraph."
    )

    markdown = None
    last_error = None
    for attempt in range(3):
        try:
            candidate = call_gemini(
                prompt_text,
                system=system_message,
                max_tokens=10000,
                cost_tracker=state["cost_tracker"],
            )
            # Sanitize common HTML issues that break ReportLab parsing
            candidate = candidate.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
            markdown = candidate
            break
        except Exception as exc:  # Retry on transient failures
            last_error = exc
            if attempt == 2:
                raise
            continue

    if markdown is None:
        raise last_error

    # Save output to JSON
    output_data = {
        "topic": topic,
        "final_markdown": markdown,
        "citations": list(state["citations"])
    }
    
    with open("debug_outputs/summarize_output.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    state["cost_tracker"].add(markdown)
    state["final_markdown"] = markdown
    state["cluster_summaries"] = {"report": [markdown]}  # for pdf_node compatibility
    return state

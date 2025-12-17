# Agentic Research & PDF Report Generation

This project was built as part of the **Predli Internship Assignment**.  
It implements an agentic system that takes a topic as input, performs structured online research, and generates a professional PDF report.

The system is designed as a **LangGraph-based workflow** where each node handles a specific step, instead of using a single large prompt.

---

## What the System Does

Given a topic, the system:
- Extracts structured context (geography, time range, domain)
- Plans relevant research subtopics
- Generates focused web search queries
- Performs online searches and extracts content
- Controls search expansion based on coverage and token budget
- Summarizes all information into a structured report
- Exports the report as a PDF

---

## Architecture Overview

The workflow is implemented as a LangGraph pipeline with the following nodes:
- Input initialization
- Context extraction
- Subtopic planning
- Query generation
- Web search and content extraction
- Search review and control
- Report summarization
- PDF generation

Each node operates on a shared state, making the system easier to debug and extend.

---

## Cost-Aware Design

Cost optimization was treated as a core design constraint.

- Token-level pricing is manually defined in `llm.py`
- A smaller model is used for planning and control logic
- A larger model is used only for final summarization

This approach reflects real-world constraints where LLM usage must be monitored and controlled.

---

## Technologies Used

- Python
- LangGraph
- OpenAI API
- DuckDuckGo Search (ddgs)
- BeautifulSoup
- ReportLab
- Pydantic

---

## Running the Project

```bash
pip install -r requirements.txt
python main.py

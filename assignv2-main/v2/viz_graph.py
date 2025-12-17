#!/usr/bin/env python3
"""
Generate a Mermaid diagram of the research report generation langgraph.
"""

def generate_mermaid_graph():
    """Generate a Mermaid flowchart of the langgraph pipeline."""
    
    mermaid = """graph TD
    A["🟢 Input Node<br/>Parse Topic"] -->|Initialize State| B
    
    B["📍 Context Node<br/>Extract Geography,<br/>Time Range, Domain<br/><br/>Model: gpt-4.1-nano"] -->|Structured Metadata| C
    
    C["🎯 Planner Node<br/>Generate 3 Subtopics<br/>per Research Theme<br/><br/>Model: gpt-4.1-nano"] -->|Subtopic List| D
    
    D["🔍 Query Node<br/>Create 4 Query Variants<br/>per Subtopic<br/>12 Total Queries<br/><br/>Deterministic"] -->|Search Queries| E
    
    E["🌐 Search Node<br/>DuckDuckGo Web Search<br/>Fetch Content + PDFs<br/>Title, Snippet, URL<br/><br/>Max 4 Results/Query"] -->|Raw Search Results| F
    
    F["🔎 Search Review Node<br/>Iterative Token Counting<br/>LLM-Guided Decisions<br/>Max 250k Tokens<br/><br/>Model: gpt-4.1-nano"] -->|Filtered + Ranked Results| G
    
    G["📝 Summarize Node<br/>Full Content Aggregation<br/>Truncate to 250k Tokens<br/>Generate HTML Report<br/>APA 7 Citations [1-8]<br/><br/>Model: gpt-4.1-mini"] -->|HTML Report| H
    
    H["📄 PDF Node<br/>Times-Roman Font<br/>Justified Typography<br/>Semantic HTML Parsing<br/><br/>Output: .pdf"] -->|✅ Final Report|I["🎁 Report Ready"]
    
    J["💰 Cost Tracker<br/>Track Tokens + USD<br/>per Step<br/>Cumulative Summary"] -.->|Parallel Monitoring| F
    J -.->|Parallel Monitoring| G
    
    style A fill:#90EE90,stroke:#228B22,stroke-width:2px,color:#000
    style B fill:#87CEEB,stroke:#00008B,stroke-width:2px,color:#000
    style C fill:#87CEEB,stroke:#00008B,stroke-width:2px,color:#000
    style D fill:#FFD700,stroke:#FF8C00,stroke-width:2px,color:#000
    style E fill:#FFD700,stroke:#FF8C00,stroke-width:2px,color:#000
    style F fill:#DDA0DD,stroke:#8B008B,stroke-width:2px,color:#000
    style G fill:#DDA0DD,stroke:#8B008B,stroke-width:2px,color:#000
    style H fill:#FFA07A,stroke:#FF4500,stroke-width:2px,color:#000
    style I fill:#98FB98,stroke:#228B22,stroke-width:3px,color:#000
    style J fill:#F0E68C,stroke:#DAA520,stroke-width:2px,color:#000
"""
    
    return mermaid


def generate_mermaid_graph_simple():
    """Simpler version of the graph."""
    
    mermaid = """graph TD
    INPUT["Input: Topic"] 
    INPUT -->|topic string| CONTEXT["📍 Context<br/>gpt-4.1-nano"]
    
    CONTEXT -->|geography,<br/>time_range, domain| PLANNER["🎯 Planner<br/>gpt-4.1-nano"]
    
    PLANNER -->|3 subtopics| QUERY["🔍 Query<br/>Generate Variants"]
    
    QUERY -->|12 queries| SEARCH["🌐 Search<br/>DuckDuckGo + Fetch"]
    
    SEARCH -->|raw results| REVIEW["🔎 Review<br/>gpt-4.1-nano<br/>250k token cap"]
    
    REVIEW -->|filtered results| SUMMARIZE["📝 Summarize<br/>gpt-4.1-mini<br/>HTML + Citations"]
    
    SUMMARIZE -->|HTML| PDF["📄 PDF<br/>Times-Roman<br/>Justified"]
    
    PDF -->|.pdf| OUTPUT["✅ Final Report"]
    
    COST["💰 Cost Tracker<br/>USD + Tokens"] -.->|monitors all| REVIEW
    COST -.->|monitors all| SUMMARIZE
    
    style INPUT fill:#e1f5e1
    style CONTEXT fill:#bbdefb
    style PLANNER fill:#bbdefb
    style QUERY fill:#fff9c4
    style SEARCH fill:#fff9c4
    style REVIEW fill:#e1bee7
    style SUMMARIZE fill:#e1bee7
    style PDF fill:#ffccbc
    style OUTPUT fill:#c8e6c9
    style COST fill:#ffe0b2
"""
    
    return mermaid


if __name__ == "__main__":
    # Save detailed version
    with open("graph_detailed.md", "w") as f:
        f.write("# Research Report Generation Pipeline\n\n")
        f.write("## Detailed Mermaid Diagram\n\n")
        f.write("```mermaid\n")
        f.write(generate_mermaid_graph())
        f.write("\n```\n\n")
    
    # Save simple version
    with open("graph_simple.md", "w") as f:
        f.write("# Research Report Generation Pipeline (Simplified)\n\n")
        f.write("```mermaid\n")
        f.write(generate_mermaid_graph_simple())
        f.write("\n```\n\n")
    
    print("✅ Generated graph_detailed.md and graph_simple.md")
    print("\nPaste either diagram into https://mermaid.live for visualization")

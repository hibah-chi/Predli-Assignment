from graph.state import GraphState
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import os


def pdf_node(state: GraphState, output_path: str) -> GraphState:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Register Times font family for proper bold/italic rendering
    registerFontFamily('Times-Roman', normal='Times-Roman', bold='Times-Bold', 
                       italic='Times-Italic', boldItalic='Times-BoldItalic')

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles using Times-Roman (LaTeX-like serif font)
    title_style = ParagraphStyle(
        'CustomTitle',
        fontName='Times-Roman',
        fontSize=18,
        leading=22,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        fontName='Times-Roman',
        fontSize=14,
        leading=17,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        spaceBefore=12,
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        spaceBefore=10,
    )
    
    # Custom body style for justified text
    body_style = ParagraphStyle(
        'JustifiedBody',
        fontName='Times-Roman',
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    
    # Small style for references
    small_style = ParagraphStyle(
        'SmallRef',
        fontName='Times-Roman',
        fontSize=7,
        leading=10,
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    
    story = []

    html_content = state["final_markdown"]  # HTML format now
    html_content = (
        html_content.replace("<br>", " ")
        .replace("<br/>", " ")
        .replace("<br />", " ")
    )
    
    # Parse HTML line by line
    lines = html_content.split('\n')
    
    in_references = False
    
    for line in lines:
        line = line.rstrip()
        
        if not line.strip():
            story.append(Spacer(1, 6))
            continue
        
        # Check if we're entering references section
        if '<h2>References</h2>' in line:
            in_references = True
            story.append(Paragraph("<b>References</b>", heading2_style))
            continue
        
        # Use small style for everything in references
        current_style = small_style if in_references else body_style
        
        # H1 headings
        if line.startswith('<h1>'):
            story.append(Paragraph(line, title_style))
        # H2 headings
        elif line.startswith('<h2>'):
            story.append(Paragraph(line, heading2_style))
        # H3 headings
        elif line.startswith('<h3>'):
            story.append(Paragraph(line, heading3_style))
        # List items
        elif line.startswith('<li>'):
            story.append(Paragraph(line, current_style))
        # Paragraphs and other HTML content
        elif line.startswith('<p>') or '<' in line:
            story.append(Paragraph(line, current_style))
        # Plain text
        else:
            if line.strip():
                story.append(Paragraph(line, current_style))

    doc.build(story)
    return state

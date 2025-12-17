#!/usr/bin/env python3
"""
Standalone script to convert summarize_output.json to a well-formatted PDF.
Usage: python utils/json_to_pdf.py <input_json> <output_pdf>
"""

import json
import sys
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import re


def html_to_pdf(html_text: str, output_path: str, topic: str = "Research Report"):
    """Convert HTML text to a properly formatted PDF."""
    
    # Register Times font family for proper bold/italic rendering
    registerFontFamily('Times-Roman', normal='Times-Roman', bold='Times-Bold', 
                       italic='Times-Italic', boldItalic='Times-BoldItalic')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles using Times-Roman (LaTeX-like serif font)
    title_style = ParagraphStyle(
        'CustomTitle',
        fontName='Times-Roman',
        fontSize=24,
        leading=28,
        spaceAfter=20,
        alignment=TA_LEFT,
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        fontName='Times-Roman',
        fontSize=14,
        leading=17,
        spaceAfter=12,
        spaceBefore=14,
        alignment=TA_LEFT,
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        fontName='Times-Roman',
        fontSize=12,
        leading=15,
        spaceAfter=10,
        spaceBefore=12,
        alignment=TA_LEFT,
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        fontName='Times-Roman',
        fontSize=11,
        leading=14,
        spaceAfter=8,
        spaceBefore=10,
        alignment=TA_LEFT,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        fontName='Times-Roman',
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        fontName='Times-Roman',
        fontSize=11,
        leading=14,
        leftIndent=20,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    
    small_ref_style = ParagraphStyle(
        'SmallRef',
        fontName='Times-Roman',
        fontSize=7,
        leading=10,
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    
    # Build document content
    story = []
    
    html_text = (
        html_text.replace("<br>", " ")
        .replace("<br/>", " ")
        .replace("<br />", " ")
    )

    # Parse HTML line by line
    lines = html_text.split('\n')
    
    in_references = False
    
    for line in lines:
        line = line.rstrip()
        
        # Skip empty lines
        if not line.strip():
            story.append(Spacer(1, 8))
            continue
        
        # Check if we're entering references section
        if '<h2>References</h2>' in line:
            in_references = True
            story.append(Paragraph("<b>References</b>", h1_style))
            continue
        
        # Use small style for everything in references
        current_body_style = small_ref_style if in_references else body_style
        current_bullet_style = small_ref_style if in_references else bullet_style
        
        # H1 headings
        if line.startswith('<h1>'):
            story.append(Paragraph(line, title_style))
            
        # H2 headings
        elif line.startswith('<h2>'):
            story.append(Paragraph(line, h1_style))
            
        # H3 headings
        elif line.startswith('<h3>'):
            story.append(Paragraph(line, h2_style))
            
        # H4 headings
        elif line.startswith('<h4>'):
            story.append(Paragraph(line, h3_style))
            
        # List items
        elif line.startswith('<li>'):
            story.append(Paragraph(line, current_bullet_style))
            
        # Paragraphs and other HTML content
        elif line.startswith('<p>') or '<' in line:
            story.append(Paragraph(line, current_body_style))
            
        # Plain text
        else:
            if line.strip():
                story.append(Paragraph(line, current_body_style))
    
    # Build PDF
    doc.build(story)
    print(f"✓ PDF generated: {output_path}")


def process_inline_markdown(text: str) -> str:
    """Process inline markdown formatting (bold, italic, links)."""
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Italic: *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(.+?)_(?!_)', r'<i>\1</i>', text)
    
    # Links: [text](url) - just show the text
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1', text)
    
    return text


def main():
    if len(sys.argv) < 2:
        print("Usage: python utils/json_to_pdf.py <input_json> [output_pdf]")
        print("Example: python utils/json_to_pdf.py debug_outputs/summarize_output.json reports/output.pdf")
        sys.exit(1)
    
    input_json = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else "output.pdf"
    
    # Read JSON
    if not os.path.exists(input_json):
        print(f"Error: File not found: {input_json}")
        sys.exit(1)
    
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract HTML and topic (support both field names for compatibility)
    content = data.get('final_html', data.get('final_markdown', ''))
    topic = data.get('topic', 'Research Report')
    
    if not content:
        print("Error: No 'final_html' or 'final_markdown' field found in JSON")
        sys.exit(1)
    
    # Generate PDF
    html_to_pdf(content, output_pdf, topic)
    print(f"✓ Citations count: {len(data.get('citations', []))}")


if __name__ == '__main__':
    main()

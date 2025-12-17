import subprocess
import os

# Read mermaid markdown files
diagrams = ['graph_simple.md', 'graph_detailed.md']

for diagram_file in diagrams:
    if os.path.exists(diagram_file):
        with open(diagram_file, 'r') as f:
            content = f.read()
        
        # Extract mermaid content (remove markdown code block markers)
        mermaid_content = content.replace('```mermaid\n', '').replace('```', '').strip()
        
        # Write to temporary mermaid file
        temp_file = 'temp_diagram.mmd'
        with open(temp_file, 'w') as f:
            f.write(mermaid_content)
        
        # Try to render using mmdc with SVG first (no browser needed)
        output_file = diagram_file.replace('.md', '.svg')
        result = subprocess.run([
            'mmdc', '-i', temp_file, '-o', output_file, '-t', 'default'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f'✓ Generated {output_file}')
        else:
            print(f'✗ Failed to generate {output_file}: {result.stderr}')
        
        os.remove(temp_file)

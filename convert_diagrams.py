#!/usr/bin/env python3
import os
from mermaid_py import Mermaid

diagrams = [
    ('sprint_cycle.mmd', 'sprint_cycle.png'),
    ('system_architecture.mmd', 'system_architecture.png'),
    ('use_case.mmd', 'use_case.png'),
    ('erd.mmd', 'erd.png'),
    ('activity_diagram.mmd', 'activity_diagram.png')
]

diagrams_dir = 'docs/diagrams'

for mmd_file, png_file in diagrams:
    mmd_path = os.path.join(diagrams_dir, mmd_file)
    png_path = os.path.join(diagrams_dir, png_file)
    
    with open(mmd_path, 'r') as f:
        mermaid_code = f.read()
    
    print(f"Converting {mmd_file} to {png_file}...")
    try:
        mermaid = Mermaid(mermaid_code)
        mermaid.render_file(png_path)
        print(f"Successfully created {png_file}")
    except Exception as e:
        print(f"Error converting {mmd_file}: {e}")

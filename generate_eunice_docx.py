import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def clean_text_equations(text):
    """
    Cleans up any stray LaTeX string artifacts into clean, readable typography.
    """
    if not text:
        return text
    
    # Replace LaTeX commands
    replacements = [
        (r'\alpha', 'α'),
        (r'\beta', 'β'),
        (r'\times', '×'),
        (r'\cdot', '×'),
        (r'\rightarrow', '→'),
        (r'\in', '∈'),
        (r'\min', 'min'),
        (r'\max', 'max'),
        (r'S_{\text{req}}', 'S_req'),
        (r'C_{\text{norm}}', 'C_norm'),
        (r'U_{\text{norm}}', 'U_norm'),
        (r'C_{\text{max}}', 'C_max'),
        (r'C_{\text{min}}', 'C_min'),
        (r'U_{\text{max}}', 'U_max'),
        (r'U_{\text{min}}', 'U_min'),
        (r'SLA_{\text{req}}', 'SLA_req'),
        (r'Latency_{\text{req}}', 'Latency_req'),
        (r'\text{req}', 'req'),
        (r'\text{norm}', 'norm'),
        (r'\text{max}', 'max'),
        (r'\text{min}', 'min'),
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
        
    # Clean up any \text{...} wrappers
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    # Remove math dollar signs surrounding words/variables if present
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    
    return text

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def format_table(table, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        clean_title = clean_text_equations(title.strip())
        hdr_cells[i].text = clean_title
        set_cell_background(hdr_cells[i], "F2F2F2")  # Light gray background for clean academic style
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=180, right=180)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.15
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.bold = True
            run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(0, 0, 0)  # Pure black text

    for r_idx, row_data in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "FAFAFA" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            if c_idx < len(row_cells):
                clean_val = clean_text_equations(val.strip())
                row_cells[c_idx].text = clean_val
                set_cell_background(row_cells[c_idx], bg_color)
                set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=150, right=150)
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.line_spacing = 1.15
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(10)
                    run.font.color.rgb = RGBColor(0, 0, 0)  # Pure black text

def append_markdown_to_doc(md_filepath, doc):
    with open(md_filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code_block = False
    code_lines = []
    in_table = False
    table_headers = []
    table_rows = []

    for line in lines:
        line_str = line.rstrip('\r\n')

        # Code block handling
        if line_str.startswith('```'):
            if in_code_block:
                in_code_block = False
                table = doc.add_table(rows=1, cols=1)
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = table.cell(0, 0)
                set_cell_background(cell, "F8F9FA")
                set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.05
                run = p.add_run('\n'.join(code_lines))
                run.font.name = 'Consolas'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(0, 0, 0)  # Pure black code text
                
                p_space = doc.add_paragraph()
                p_space.paragraph_format.space_after = Pt(6)
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line_str)
            continue

        # Table handling
        if '|' in line_str and not line_str.startswith('```'):
            parts = [p.strip() for p in line_str.split('|')[1:-1]]
            if not parts:
                continue
            if all(set(p).issubset({'-', ':', ' '}) for p in parts if p):
                continue
            if not in_table:
                in_table = True
                table_headers = parts
                table_rows = []
            else:
                table_rows.append(parts)
            continue
        else:
            if in_table:
                in_table = False
                if table_headers and table_rows:
                    cols = len(table_headers)
                    table = doc.add_table(rows=len(table_rows) + 1, cols=cols)
                    format_table(table, table_headers, table_rows)
                    p_space = doc.add_paragraph()
                    p_space.paragraph_format.space_after = Pt(6)
                table_headers = []
                table_rows = []

        if not line_str.strip():
            continue

        # Image handling ![Caption](file:///path/to/image.png)
        img_match = re.search(r'!\[(.*?)\]\((file:///.*?|.*?)\)', line_str)
        if img_match:
            caption = img_match.group(1)
            img_path = img_match.group(2).replace('file://', '')
            if os.path.exists(img_path):
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(14)
                p_img.paragraph_format.space_after = Pt(4)
                p_img.paragraph_format.keep_with_next = True
                run = p_img.add_run()
                run.add_picture(img_path, width=Inches(6.2))

                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_before = Pt(2)
                p_cap.paragraph_format.space_after = Pt(14)
                
                # Format "Figure X.Y:" as Bold Times New Roman and description text as Italic
                clean_cap = clean_text_equations(caption)
                fig_prefix_match = re.match(r'^(Figure\s+\d+\.\d+:?\s*)(.*)$', clean_cap, re.IGNORECASE)
                if fig_prefix_match:
                    prefix = fig_prefix_match.group(1)
                    rest = fig_prefix_match.group(2)
                    
                    run_pre = p_cap.add_run(prefix)
                    run_pre.font.name = 'Times New Roman'
                    run_pre.font.size = Pt(10)
                    run_pre.font.bold = True
                    run_pre.font.color.rgb = RGBColor(0, 0, 0)
                    
                    run_rest = p_cap.add_run(rest)
                    run_rest.font.name = 'Times New Roman'
                    run_rest.font.size = Pt(10)
                    run_rest.font.italic = True
                    run_rest.font.color.rgb = RGBColor(0, 0, 0)
                else:
                    run_cap = p_cap.add_run(clean_cap)
                    run_cap.font.name = 'Times New Roman'
                    run_cap.font.size = Pt(10)
                    run_cap.font.italic = True
                    run_cap.font.color.rgb = RGBColor(0, 0, 0)
            continue

        # Horizontal Rule
        if line_str.strip() == '---':
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(8)
            continue

        # Clean line text equation strings
        line_clean = clean_text_equations(line_str)

        # Headings
        if line_clean.startswith('# '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(line_clean[2:])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(16)
            run.bold = True
            run.font.color.rgb = RGBColor(0, 0, 0)
        elif line_clean.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(line_clean[3:])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.bold = True
            run.font.color.rgb = RGBColor(0, 0, 0)
        elif line_clean.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(line_clean[4:])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12.5)
            run.bold = True
            run.font.color.rgb = RGBColor(0, 0, 0)
        elif line_clean.startswith('#### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(line_clean[5:])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.bold = True
            run.font.color.rgb = RGBColor(0, 0, 0)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.5

            parts = re.split(r'(\*\*.*?\*\*)', line_clean)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    run = p.add_run(part)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(0, 0, 0)

    if in_table and table_headers and table_rows:
        cols = len(table_headers)
        table = doc.add_table(rows=len(table_rows) + 1, cols=cols)
        format_table(table, table_headers, table_rows)

def parse_markdown_to_docx(md_filepath, docx_filepath):
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    append_markdown_to_doc(md_filepath, doc)
    doc.save(docx_filepath)
    print(f"Successfully generated Word Document at {docx_filepath}")

def generate_combined_chapter_4_and_5():
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    ch4_md = os.path.join(docs_dir, 'Chapter_4_System_Implementation_Testing.md')
    ch5_md = os.path.join(docs_dir, 'Chapter_5_Discussion_Conclusion_Recom.md')
    combined_docx = os.path.join(docs_dir, 'Chapter_4_and_5_Eunice.docx')
    combined_md = os.path.join(docs_dir, 'Chapter_4_and_5_Eunice.md')

    # 1. Create combined Markdown file
    with open(ch4_md, 'r', encoding='utf-8') as f4:
        content4 = f4.read()
    with open(ch5_md, 'r', encoding='utf-8') as f5:
        content5 = f5.read()

    combined_markdown = content4 + "\n\n---\n\n" + content5
    with open(combined_md, 'w', encoding='utf-8') as f_out:
        f_out.write(combined_markdown)
    print(f"Successfully generated Combined Markdown file at {combined_md}")

    # 2. Create combined Word Document
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    append_markdown_to_doc(ch4_md, doc)
    doc.add_page_break()
    append_markdown_to_doc(ch5_md, doc)

    doc.save(combined_docx)
    print(f"Successfully generated Combined Chapter 4 & 5 Word Document at {combined_docx}")

def generate_full_dissertation():
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    ch123_docx = os.path.join(docs_dir, 'Chap_1_2_3_Eunice.docx')
    ch4_md = os.path.join(docs_dir, 'Chapter_4_System_Implementation_Testing.md')
    ch5_md = os.path.join(docs_dir, 'Chapter_5_Discussion_Conclusion_Recom.md')
    full_docx = os.path.join(docs_dir, 'Full_Project_Dissertation_Eunice.docx')

    if os.path.exists(ch123_docx):
        doc = docx.Document(ch123_docx)
    else:
        doc = docx.Document()

    doc.add_page_break()
    append_markdown_to_doc(ch4_md, doc)

    doc.add_page_break()
    append_markdown_to_doc(ch5_md, doc)

    doc.save(full_docx)
    print(f"Successfully generated Full Dissertation Word Document at {full_docx}")

if __name__ == "__main__":
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    ch4_md = os.path.join(docs_dir, 'Chapter_4_System_Implementation_Testing.md')
    ch4_docx = os.path.join(docs_dir, 'Chapter_4_System_Implementation_Testing.docx')
    ch5_md = os.path.join(docs_dir, 'Chapter_5_Discussion_Conclusion_Recom.md')
    ch5_docx = os.path.join(docs_dir, 'Chapter_5_Discussion_Conclusion_Recom.docx')

    parse_markdown_to_docx(ch4_md, ch4_docx)
    parse_markdown_to_docx(ch5_md, ch5_docx)
    generate_combined_chapter_4_and_5()
    generate_full_dissertation()

from __future__ import annotations

import os
import subprocess
import shutil
from pathlib import Path
import markdown


def compile_md_to_pdf(md_path: Path, pdf_path: Path, header_text: str = "") -> None:
    print(f"Reading {md_path.name}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML (using the tables extension)
    html_body = markdown.markdown(md_content, extensions=['tables'])

    # Style sheet matching the Navy SBIR BAA rules
    header_html = ""
    table_wrapper_start = ""
    table_wrapper_end = ""
    
    if header_text:
        header_html = f"""
        <div class="header-content">
            {header_text}
        </div>
        """
        table_wrapper_start = """
        <table class="header-table">
            <thead>
                <tr>
                    <td>
                        <div class="header-spacer"></div>
                    </td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>
        """
        table_wrapper_end = """
                    </td>
                </tr>
            </tbody>
        </table>
        """

    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Volume 2 Technical Proposal</title>
    <style>
        @page {{
            size: letter;
            margin: 0.6in 1in 0.8in 1in;
        }}
        body {{
            font-family: "Times New Roman", Times, serif;
            font-size: 11pt;
            line-height: 1.15;
            color: #000000;
            margin: 0;
            padding: 0;
        }}
        .header-table {{
            width: 100%;
            border-collapse: collapse;
            border: none;
        }}
        .header-table td, .header-table th {{
            border: none;
            padding: 0;
        }}
        .header-spacer {{
            height: 0.5in;
        }}
        .header-content {{
            position: fixed;
            top: 0in;
            left: 0;
            right: 0;
            height: 0.4in;
            text-align: center;
            font-size: 10pt;
            border-bottom: 0.5pt solid #000000;
            line-height: 1.5;
            font-weight: normal;
        }}
        h1 {{
            font-size: 15pt;
            font-weight: bold;
            margin-top: 14pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
        }}
        h2 {{
            font-size: 13pt;
            font-weight: bold;
            margin-top: 12pt;
            margin-bottom: 6pt;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 11.5pt;
            font-weight: bold;
            margin-top: 10pt;
            margin-bottom: 4pt;
            page-break-after: avoid;
        }}
        h4 {{
            font-size: 11pt;
            font-weight: bold;
            margin-top: 8pt;
            margin-bottom: 2pt;
            page-break-after: avoid;
        }}
        p {{
            margin-top: 0;
            margin-bottom: 6pt;
            text-align: justify;
        }}
        ul, ol {{
            margin-top: 0;
            margin-bottom: 6pt;
            padding-left: 20pt;
        }}
        li {{
            margin-bottom: 3pt;
            text-align: justify;
        }}
        /* Table formatting for proposal tables */
        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8pt;
            margin-bottom: 8pt;
            page-break-inside: avoid;
        }}
        .content th, .content td {{
            border: 0.5pt solid #000000;
            padding: 4pt 6pt;
            font-size: 10pt;
            text-align: left;
            vertical-align: top;
        }}
        .content th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    {header_html}
    {table_wrapper_start}
    <div class="content">
        {html_body}
    </div>
    {table_wrapper_end}
</body>
</html>
"""

    temp_html_path = md_path.parent / "temp_print.html"
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print("Invoking Microsoft Edge to print to PDF...")
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    cmd = [
        edge_path,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        str(temp_html_path)
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Successfully generated {pdf_path.name}")
    except Exception as e:
        print(f"Error invoking Edge: {e}")
    finally:
        # Clean up temporary HTML
        if temp_html_path.exists():
            os.remove(temp_html_path)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    submission_dir = project_root / 'docs' / 'submission'
    
    # We will copy compiled PDFs to the finalDraft directory automatically
    final_draft_dir = project_root.parent / 'finalDraft'
    v2_final_pdf = final_draft_dir / 'volume_2' / 'volume_2_technical-proposal.pdf'
    v5_final_dir = final_draft_dir / 'volume_5'
    
    # Common header text required by the BAA
    header_text = "Techman Studios &nbsp;|&nbsp; Topic: DON26BZ01-NV023 &nbsp;|&nbsp; Proposal Number: N26BZ-NV023-0825"
    
    # Compile Cover Sheet Volume 1 (if draft exists)
    v1_md = submission_dir / 'volume_1_cover_sheet_draft.md'
    v1_pdf = submission_dir / 'volume_1_cover_sheet_draft.pdf'
    if v1_md.exists():
        compile_md_to_pdf(v1_md, v1_pdf)
    else:
        print(f"File not found: {v1_md}")
        
    # Compile Technical Proposal Volume 2
    v2_md = submission_dir / 'volume_2_10_page_submission_draft.md'
    v2_pdf = submission_dir / 'volume_2_10_page_submission_draft.pdf'
    if v2_md.exists():
        compile_md_to_pdf(v2_md, v2_pdf, header_text=header_text)
        # Copy to finalDraft
        if v2_final_pdf.parent.exists():
            shutil.copy2(v2_pdf, v2_final_pdf)
            print(f"Copied compiled Technical Proposal to {v2_final_pdf}")
    else:
        print(f"File not found: {v2_md}")
        
    # Compile Cost Proposal Volume 3 (if draft exists)
    v3_md = submission_dir / 'volume_3_cost_draft.md'
    v3_pdf = submission_dir / 'volume_3_cost_draft.pdf'
    if v3_md.exists():
        compile_md_to_pdf(v3_md, v3_pdf)
    else:
        print(f"File not found: {v3_md}")
        
    # Compile Supporting Documents Volume 5
    v5_md = submission_dir / 'volume_5_supporting_docs_draft.md'
    v5_pdf = submission_dir / 'volume_5_supporting_docs_draft.pdf'
    if v5_md.exists():
        compile_md_to_pdf(v5_md, v5_pdf, header_text=header_text)
        # Copy to finalDraft with the correct names
        if v5_final_dir.exists():
            # Search for existing files in finalDraft/volume_5 to get the exact filenames (with generated random numbers)
            copied = False
            for file in os.listdir(v5_final_dir):
                if file.startswith("N26BZ-NV023-0825_") and file.endswith(".pdf"):
                    dest = v5_final_dir / file
                    shutil.copy2(v5_pdf, dest)
                    print(f"Copied compiled Supporting Documents to {dest}")
                    copied = True
            if not copied:
                # Fallback names if none found
                dest1 = v5_final_dir / "N26BZ-NV023-0825_Other_1757091.pdf"
                dest2 = v5_final_dir / "N26BZ-NV023-0825_Tech_Data_Rights_1757090.pdf"
                shutil.copy2(v5_pdf, dest1)
                shutil.copy2(v5_pdf, dest2)
                print(f"Copied compiled Supporting Documents to {dest1} and {dest2}")
    else:
        print(f"File not found: {v5_md}")


if __name__ == '__main__':
    main()

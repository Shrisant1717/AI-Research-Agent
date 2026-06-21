from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
import subprocess


def wrap_latex(text: str):

    # If the model already produced a full LaTeX document
    if "\\documentclass" in text:
        return text

    # Escape problematic characters
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # Otherwise wrap it inside a template
    return f"""
\\documentclass{{article}}

\\usepackage{{amsmath}}
\\usepackage{{hyperref}}

\\title{{AI Generated Research Paper}}
\\author{{Research AI Agent}}
\\date{{}}

\\begin{{document}}

\\maketitle

{text}

\\end{{document}}
"""


@tool
def render_latex_pdf(latex_content: str) -> str:
    """
    Convert LLM-generated text into LaTeX and compile it into a PDF using tectonic.
    """

    project_dir = Path(__file__).resolve().parent
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    tectonic_path = project_dir / "tectonic.exe"

    if not tectonic_path.exists():
        raise RuntimeError("tectonic.exe not found in project directory")

    # Convert text to LaTeX
    latex_content = wrap_latex(latex_content)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    tex_file = output_dir / f"paper_{timestamp}.tex"
    pdf_file = output_dir / f"paper_{timestamp}.pdf"

    tex_file.write_text(latex_content, encoding="utf-8")

    result = subprocess.run(
        [
            str(tectonic_path),
            tex_file.name,
            "--outdir",
            str(output_dir)
        ],
        cwd=output_dir,
        capture_output=True,
        text=True
    )

    print("TECTONIC STDOUT:")
    print(result.stdout)

    print("TECTONIC STDERR:")
    print(result.stderr)

    if not pdf_file.exists():
        raise RuntimeError(
            f"PDF generation failed.\n\n{result.stderr}"
        )

    return str(pdf_file)
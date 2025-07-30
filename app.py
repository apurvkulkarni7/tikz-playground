import gradio as gr
import subprocess
import os
import shutil
from tempfile import mkdtemp
import re

LATEX_TEMPLATE = r"""
\documentclass[tikz,border=2mm]{standalone}
\usepackage{pgfplots}
\usepackage{pgffor,etoolbox}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, shapes.geometric, fit, decorations, shapes, shapes.geometric, shapes.multipart}
\usetikzlibrary{positioning,shapes,shadows,arrows,pgfplots.colormaps,backgrounds,calc}
\begin{document}
%s
\end{document}
"""

TMPDIR = mkdtemp()


def raise_error(output_image):
    if output_image == None:
        return "Error occurred"


def compile_tikz(tikz_code):
    if not tikz_code.strip():
        return None, "Please enter TikZ code."

    tex_path = os.path.abspath(os.path.join(TMPDIR, "drawing.tex"))
    pdf_path = os.path.abspath(os.path.join(TMPDIR, "drawing.pdf"))
    png_path = os.path.abspath(os.path.join(TMPDIR, "drawing.png"))

    # Write the full LaTeX document
    try:
        with open(tex_path, "w+") as f:
            f.write(LATEX_TEMPLATE % tikz_code)
            f.close()
        print(f"Successfully wrote to {tex_path}")
    except Exception as e:
        print(f"Error writing to {tex_path}: {e}")

    try:
        # Compile LaTeX document to PDF
        result = subprocess.run(
            ["pdflatex", "--interaction=nonstopmode", tex_path],
            cwd=TMPDIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        with open(os.path.join(TMPDIR, "stdout.log"), "w") as f:
            f.write(result.stdout.decode("utf-8").strip())
            f.close()
        print("stderr:", result.stderr.decode("utf-8").strip())
        # Convert PDF to PNG using pdftoppm or fallback to convert
        if shutil.which("pdftoppm"):
            cmd = ["pdftoppm", "-png", "-singlefile", pdf_path, png_path[:-4]]
            print(f"Running: {cmd}")
            result = subprocess.run(
                cmd,
                cwd=TMPDIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Print stdout and stderr
            with open(os.path.join(TMPDIR, "xelatex_stdout.log"), "a") as f:
                f.write(result.stdout.decode("utf-8").strip())
                f.close()
            print("stderr:", result.stderr.decode("utf-8"))
            print(f"PNG saved to {png_path}")
        elif shutil.which("convert"):
            cmd = ["convert", "-density", "300", pdf_path, png_path]
            print(f"Running: {cmd}")
            subprocess.run(
                ["convert", "-density", "300", pdf_path, png_path],
                cwd=TMPDIR,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(f"PDF saved to {pdf_path}")
        else:
            return (
                None,
                "Error: install `pdftoppm` (poppler-utils) or `convert` (ImageMagick).",
            )

        return png_path, None

    except Exception as e:
        try:
            with open(f"{TMPDIR}/drawing.log", "r") as file:
                file_contents = file.read()
                return (
                    None,
                    f"LaTeX compilation failed. Check your code. {e}\nLog Contents:\n{file_contents}",
                )
        except FileNotFoundError:
            return None, f"LaTeX compilation failed. Check your code. {e}"


def compile_and_show(tikz):
    img, err = compile_tikz(tikz)
    if err:
        gr.Error("Erro during compilation...")
        return None, err
    return img, "Success!"


def prepare_header():
    with open("./static/js/script.js", "r") as f_js:
        js_content = f_js.read()

    with open("./static/head.html.orig", "r") as f_html:
        html_template = f_html.read()

    # Replace the first <script>...</script> block
    updated_html = re.sub(
        r"<script[^>]*>.*?</script>",
        f"<script>\n{js_content}\n</script>",
        html_template,
        flags=re.DOTALL
    )

    with open("./static/head.html", "w+") as f_out:
        f_out.write(updated_html)

    with open("./static/head.html", "r") as f_head:
        final_header_content = f_head.read()
    
    return final_header_content


###############################################################################

with gr.Blocks(head=prepare_header(), css_paths=["./static/css/style.css"]) as demo:
    gr.Markdown("# TikZ Playground")
    tikz_input = gr.Code(
        label="Enter TikZ code (inside \\begin{tikzpicture} ... \\end{tikzpicture})",
        language="latex",
        lines=5,
        value="\\begin{tikzpicture}\n  \\draw (0,0) -- (2,2);\n\\end{tikzpicture}",
    )
    output_image = gr.Image(label="Rendered Output")
    output_text = gr.Textbox(
        label="Messages",
        info="If there are any errors, it will appear here. Use CTRL+F and type error to navigate to errors.",
        interactive=False,
        value="",
        autoscroll=False,
    )

    btn = gr.Button("Compile & Preview (META/WIN + S)", elem_id="my_btn")
    btn.click(
        fn=compile_and_show, inputs=tikz_input, outputs=[output_image, output_text]
    )

    gr.Markdown("## References")
    gr.Markdown("- [https://tikz.dev/](https://tikz.dev/)")
    gr.Markdown("- [https://www.overleaf.com/learn/latex/TikZ_package](https://www.overleaf.com/learn/latex/TikZ_package)")
    gr.Markdown("- [https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf](https://www.bu.edu/math/files/2013/08/tikzpgfmanual.pdf)")
    gr.Markdown("- [https://en.wikibooks.org/wiki/LaTeX/PGF/TikZ](https://en.wikibooks.org/wiki/LaTeX/PGF/TikZ)")

if __name__ == "__main__":
    demo.launch(allowed_paths=["."])

"""Markdown (with raw HTML/SVG allowed) -> A4 PDF using the Markdown package and headless Chrome.

  python3 code/tools/md_to_pdf.py docs/M2_report.md docs/M2_report.pdf [--title "..."]
Relative image paths resolve against the markdown file's folder."""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
* { box-sizing: border-box; }
body { font: 10.2pt/1.45 -apple-system, "Helvetica Neue", Arial, sans-serif; color: #1b2430; }
h1 { font-size: 20pt; margin: 0 0 6pt; color: #0f3d5e; }
h2 { font-size: 14pt; margin: 18pt 0 6pt; padding-bottom: 3pt; border-bottom: 2px solid #0f3d5e; color: #0f3d5e; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; color: #164e78; page-break-after: avoid; }
h4 { font-size: 10.5pt; margin: 8pt 0 3pt; }
p { margin: 4pt 0 6pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 8.6pt; page-break-inside: auto; }
th { background: #0f3d5e; color: #fff; text-align: left; padding: 4pt 5pt; }
td { border: 1px solid #c9d3de; padding: 3.5pt 5pt; vertical-align: top; }
tr { page-break-inside: avoid; }
tr:nth-child(even) td { background: #f4f7fa; }
code { font: 8.6pt "SF Mono", Menlo, monospace; background: #eef2f6; padding: 0 2pt; border-radius: 2pt; }
pre { font: 7.9pt/1.35 "SF Mono", Menlo, monospace; background: #f4f7fa; border: 1px solid #d5dde6; border-left: 3px solid #0f3d5e; padding: 6pt 8pt; white-space: pre-wrap; word-wrap: break-word; }
pre code { background: none; padding: 0; font-size: inherit; }
img { max-width: 100%; border: 1px solid #c9d3de; border-radius: 3pt; }
figure { margin: 8pt 0; text-align: center; page-break-inside: avoid; }
figcaption, .cap { font-size: 8.6pt; color: #4a5a6a; margin-top: 3pt; }
svg { max-width: 100%; height: auto; }
.cover { text-align: center; padding-top: 14mm; }
.cover h1 { font-size: 25pt; border: 0; }
h2:first-of-type { margin-top: 0; }
.cover .sub { font-size: 12.5pt; color: #164e78; margin-bottom: 22pt; }
.cover table { width: 78%; margin: 14pt auto; font-size: 10pt; }
.pb { page-break-before: always; }
.diag { page-break-inside: avoid; }
.pass { color: #137333; font-weight: 600; } .fail { color: #b3261e; font-weight: 600; }
blockquote { margin: 6pt 0; padding: 4pt 10pt; border-left: 3px solid #d98e04; background: #fff8e8; }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--title", default="")
    a = ap.parse_args()
    src = Path(a.src).resolve()
    body = markdown.markdown(src.read_text(), extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{a.title or src.stem}</title><style>{CSS}</style></head><body>{body}</body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=src.parent, delete=False) as f:
        f.write(html); tmp = Path(f.name)
    try:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={Path(a.out).resolve()}",
                        "--virtual-time-budget=4000", tmp.as_uri()], check=True, capture_output=True, timeout=120)
    finally:
        tmp.unlink(missing_ok=True)
    print("wrote", a.out)


if __name__ == "__main__":
    sys.exit(main())

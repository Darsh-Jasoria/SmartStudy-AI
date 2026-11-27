"""Render the IEEE report to HTML and then to PDF with headless Chrome (two-column IEEE layout)."""
import re, subprocess, html
from pathlib import Path
import report_content as R
from data import ROOT

OUT = ROOT / "submission_ieee"
FIGS = OUT / "figs"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

def resolve(blocks):
    """Number citations by first appearance; returns (blocks with [n], ordered ref keys)."""
    order = []
    def sub(text):
        def rep(mo):
            k = mo.group(1)
            if k not in order: order.append(k)
            return f"[{order.index(k)+1}]"
        return re.sub(r"\[\[(\w+)\]\]", rep, text)
    out = []
    for b in blocks:
        b = list(b)
        for i, x in enumerate(b):
            if isinstance(x, str) and b[0] in ("p", "eq"): b[i] = sub(x) if i == 1 else x
        if b[0] == "list": b[1] = [sub(t) for t in b[1]]
        if b[0] == "table":
            b[5] = sub(b[5]) if b[5] else b[5]
        out.append(tuple(b))
    return out, order

def curly(t):
    return re.sub(r'"([^"<>]*)"', "\u201c\\1\u201d", t)

def build_html():
    blocks, order = resolve(R.B)
    blocks = [tuple(curly(x) if isinstance(x, str) and b[0] in ("p", "eq") and i == 1 else x for i, x in enumerate(b)) if b[0] in ("p", "eq") else (("list", [curly(y) for y in b[1]]) if b[0] == "list" else b) for b in blocks]
    # every reference must be cited at least once (IEEE requires it); append remaining refs
    for k in R.REFS:
        if k not in order: order.append(k)
    parts, n1, n2, tn, fn = [], 0, 0, 0, 0
    for b in blocks:
        t = b[0]
        if t == "h1":
            n1 += 1; n2 = 0
            parts.append(f'<h1>{ROMAN[n1-1]}. {html.escape(b[1]).upper()}</h1>')
        elif t == "h2":
            n2 += 1; parts.append(f'<h2>{chr(64+n2)}. {html.escape(b[1])}</h2>')
        elif t == "p": parts.append(f"<p>{b[1]}</p>")
        elif t == "list":
            parts.append("<ol>" + "".join(f"<li>{x}</li>" for x in b[1]) + "</ol>")
        elif t == "eq":
            parts.append(f'<div class="eq"><span></span><span>{b[1]}</span><span class="n">({b[2]})</span></div>')
        elif t == "fig":
            fn += 1
            src = (FIGS / b[1]).resolve()
            parts.append(f'<figure><img src="file://{src}"><figcaption>Fig. {fn}. {b[2]}</figcaption></figure>')
        elif t == "appendix":
            parts.append(f'<h1>APPENDIX A. {html.escape(b[1]).upper()}</h1>')
        elif t == "code":
            parts.append(f'<h2>{html.escape(b[1])}</h2><pre>{html.escape(b[2], quote=False)}</pre>')
        elif t == "table":
            tn += 1
            _, cap, head, rows, widths, note = b
            cg = ""
            if widths:
                tot = sum(widths); cg = "<colgroup>" + "".join(f'<col style="width:{w/tot*100:.1f}%">' for w in widths) + "</colgroup>"
            th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
            tr = "".join("<tr>" + "".join(f"<td>{curly(html.escape(str(c), quote=False))}</td>" for c in r) + "</tr>" for r in rows)
            parts.append(f'<div class="tbl"><div class="tcap">TABLE {ROMAN[tn-1]}<br>{html.escape(cap).upper()}</div>'
                         f'<table>{cg}<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'
                         + (f'<div class="tnote">{note}</div>' if note else "") + "</div>")
    body = "\n".join(parts)
    auth = "".join(f'<div class="au"><b>{n}</b><br>{e}</div>' for n, e in R.AUTHORS)
    refs = "".join(f"<li>{curly(R.REFS[k])}</li>" for k in order)
    css = """
@page { size: A4; margin: 17mm 15mm 20mm 15mm; @bottom-center { content: counter(page); font: 8pt 'Times New Roman'; } }
* { box-sizing: border-box; }
body { font: 9.6pt/1.2 'Times New Roman', Times, serif; color: #000; margin: 0; }
.head { column-span: all; text-align: center; margin-bottom: 8pt; }
.head h1.title { font: 400 21pt/1.1 'Times New Roman'; margin: 0 0 9pt; text-transform: none; text-align: center; }
.authors { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4pt; font-size: 9.6pt; margin-bottom: 5pt; }
.au b { font-weight: 400; font-size: 10.5pt; } .au { font-size: 8.4pt; font-style: italic; }
.au b { font-style: normal; }
.aff { font-size: 9pt; font-style: italic; } .team { font-size: 8.4pt; margin-top: 3pt; }
.cols { column-count: 2; column-gap: 7mm; text-align: justify; hyphens: auto; }
.abs { margin-bottom: 6pt; font-weight: 700; font-size: 9pt; line-height: 1.17; }
.abs i, .kw i { font-weight: 700; }
.kw { font-weight: 700; font-size: 9pt; margin-bottom: 6pt; }
h1 { font: 400 9.6pt 'Times New Roman'; text-align: center; margin: 9pt 0 4pt; letter-spacing: 0; break-after: avoid; }
h2 { font: italic 400 9.6pt 'Times New Roman'; margin: 6pt 0 3pt; break-after: avoid; text-align: left; }
p { margin: 0 0 4pt; text-indent: 9pt; } p:first-of-type { text-indent: 0; }
h1 + p, h2 + p { text-indent: 0; }
ol { margin: 0 0 4pt; padding-left: 15pt; } li { margin-bottom: 2pt; }
figure { margin: 4pt 0 6pt; break-inside: avoid; text-align: center; } figure img { max-width: 100%; max-height: 62mm; object-fit: contain; }
figure:has(img[src*="workflow"]) img { max-height: 92mm; }
figcaption { font-size: 8pt; margin-top: 2pt; text-align: justify; }
.tbl { margin: 4pt 0 6pt; break-inside: avoid; }
.tcap { font-size: 7.8pt; text-align: center; margin-bottom: 3pt; line-height: 1.15; }
table { border-collapse: collapse; width: 100%; font-size: 7.6pt; line-height: 1.12; }
th, td { border: 0.5pt solid #000; padding: 1.4pt 2.5pt; text-align: left; vertical-align: top; }
th { background: #e9e9e9; font-weight: 700; }
.tnote { font-size: 7.2pt; margin-top: 2pt; }
.eq { display: grid; grid-template-columns: 1fr auto 1fr; margin: 3pt 0 4pt; font-style: italic; } .eq .n { font-style: normal; text-align: right; }
.refs { font-size: 7.8pt; line-height: 1.12; } .refs ol { padding-left: 18pt; } .refs li { margin-bottom: 2pt; text-align: left; }
pre { font: 6.3pt/1.18 "Courier New", Courier, monospace; background: #f4f4f4; border: 0.5pt solid #999; padding: 3pt 4pt; margin: 0 0 5pt; white-space: pre-wrap; word-break: break-word; text-align: left; }
.ack { margin-top: 4pt; font-size: 8.6pt; }
"""
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(R.TITLE)}</title><style>{css}</style></head><body>
<div class="cols"><div class="head"><h1 class="title">{html.escape(R.TITLE)}</h1><div class="authors">{auth}</div>
<div class="aff">{html.escape(R.AFFIL)}</div><div class="team">{html.escape(R.TEAMLINE)}</div></div>
<div class="abs"><i>Abstract</i>—{curly(R.ABSTRACT)}</div>
<div class="kw"><i>Index Terms</i>—{R.KEYWORDS}.</div>
{body}
<h1>ACKNOWLEDGMENT</h1><p style="text-indent:0">{curly(R.ACK)}</p>
<h1>REFERENCES</h1><div class="refs"><ol>{refs}</ol></div>
</div></body></html>"""
    return doc

if __name__ == "__main__":
    h = OUT / "report" / "SmartStudy_IEEE_Report.html"
    h.write_text(build_html())
    pdf = OUT / "report" / "SmartStudy_IEEE_Report.pdf"
    subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--print-to-pdf={pdf}", f"file://{h}"], check=True, capture_output=True)
    print("wrote", pdf)

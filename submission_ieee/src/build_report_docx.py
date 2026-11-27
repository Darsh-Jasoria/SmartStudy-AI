"""Editable IEEE-style two-column Word version of the report (same content as the PDF)."""
import re
from docx import Document
from docx.shared import Pt, Inches, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import report_content as R
from build_report_pdf import resolve, curly, ROMAN, FIGS, OUT

FONT = "Times New Roman"
COLW = 3.35   # inches, text column width

def set_cols(section, n, space_twips=397):
    sp = section._sectPr
    for c in sp.findall(qn("w:cols")): sp.remove(c)
    cols = OxmlElement("w:cols"); cols.set(qn("w:num"), str(n)); cols.set(qn("w:space"), str(space_twips))
    grid = sp.find(qn("w:docGrid"))
    (grid.addprevious(cols) if grid is not None else sp.append(cols))      # schema order: cols before docGrid

def run(p, text, size, bold=False, italic=False):
    r = p.add_run(text); r.font.name = FONT; r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    r.font.size = Pt(size); r.bold = bold; r.italic = italic
    return r

def rich(p, html, size, base_bold=False, base_italic=False):
    """Write text containing <i> and <b> tags as runs."""
    bold, ital = base_bold, base_italic
    for tok in re.split(r"(</?[ib]>)", html):
        if tok == "<i>": ital = True
        elif tok == "</i>": ital = base_italic
        elif tok == "<b>": bold = True
        elif tok == "</b>": bold = base_bold
        elif tok:
            tok = tok.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            run(p, tok, size, bold, ital)

def para(doc, html="", size=9.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, before=0, after=3, bold=False, italic=False, keep_next=False):
    p = doc.add_paragraph(); pf = p.paragraph_format
    pf.alignment = align; pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = 1.0
    if indent: pf.first_line_indent = Pt(9)
    pf.keep_with_next = keep_next
    if html: rich(p, html, size, bold, italic)
    return p

def shade(cell, color):
    tcPr = cell._element.get_or_add_tcPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), color); tcPr.append(shd)

def cell_margins(table, top=15, bottom=15, left=45, right=45):
    tblPr = table._element.tblPr; m = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = OxmlElement(f"w:{k}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); m.append(e)
    tblPr.append(m)

def add_table(doc, cap, head, rows, widths, note, num):
    c = para(doc, f"TABLE {ROMAN[num-1]}", 7.5, WD_ALIGN_PARAGRAPH.CENTER, False, 4, 0, keep_next=True)
    c2 = para(doc, curly(cap).upper(), 7.5, WD_ALIGN_PARAGRAPH.CENTER, False, 0, 3, keep_next=True)
    t = doc.add_table(rows=1, cols=len(head)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False; cell_margins(t)
    tot = sum(widths) if widths else len(head); ws = [(w / tot) * COLW for w in (widths or [1] * len(head))]
    def fill(cells, vals, bold=False, grey=False):
        for cell, v, w in zip(cells, vals, ws):
            cell.width = Inches(w); cell.text = ""
            pp = cell.paragraphs[0]; pp.paragraph_format.space_after = Pt(0); pp.paragraph_format.line_spacing = 1.0
            run(pp, curly(str(v)), 7.2, bold=bold)
            if grey: shade(cell, "E9E9E9")
    fill(t.rows[0].cells, head, True, True)
    # repeat header + keep rows intact
    for r in rows:
        fill(t.add_row().cells, r)
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
    if note: para(doc, curly(note), 7, WD_ALIGN_PARAGRAPH.LEFT, False, 2, 5)
    else: para(doc, "", 3, WD_ALIGN_PARAGRAPH.LEFT, False, 0, 2)

def footer_page_number(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        r = p.add_run(); r.font.size = Pt(8); r.font.name = FONT
        if t:
            f = OxmlElement("w:fldChar"); f.set(qn("w:fldCharType"), t); r._r.append(f)
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = txt; r._r.append(it)

def build():
    blocks, order = resolve(R.B)
    for k in R.REFS:
        if k not in order: order.append(k)
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(9.5)
    s0 = doc.sections[0]
    s0.page_width, s0.page_height = Mm(210), Mm(297)
    s0.left_margin = s0.right_margin = Mm(15); s0.top_margin = Mm(17); s0.bottom_margin = Mm(20)
    footer_page_number(s0)
    # ---- title block (single column)
    para(doc, R.TITLE, 20, WD_ALIGN_PARAGRAPH.CENTER, False, 0, 8)
    t = doc.add_table(rows=1, cols=4); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for cell, (n, e) in zip(t.rows[0].cells, R.AUTHORS):
        cell.width = Inches(1.75); cell.text = ""; pp = cell.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run(pp, n, 10.5); pp.add_run().add_break(); run(pp, e, 8.5, italic=True)
    para(doc, R.AFFIL, 9, WD_ALIGN_PARAGRAPH.CENTER, False, 5, 1, italic=True)
    para(doc, R.TEAMLINE, 8.5, WD_ALIGN_PARAGRAPH.CENTER, False, 0, 6)
    # ---- two-column body
    s1 = doc.add_section(WD_SECTION.CONTINUOUS); set_cols(s1, 2)
    brk = doc.paragraphs[-1] if doc.paragraphs[-1].text == "" else None
    for pp in doc.paragraphs:                       # the empty paragraph that carries the section break: make it tiny
        if pp.text == "" and pp._p.pPr is not None and pp._p.pPr.find(qn("w:sectPr")) is not None:
            pp.paragraph_format.space_after = Pt(0); pp.paragraph_format.space_before = Pt(0); pp.paragraph_format.line_spacing = Pt(1)
            r_ = pp.add_run(); r_.font.size = Pt(1)
    p = para(doc, "", 9, indent=False, after=5); run(p, "Abstract", 9, True, True); run(p, "—", 9, True); rich(p, curly(R.ABSTRACT), 9, True)
    p = para(doc, "", 9, indent=False, after=5); run(p, "Index Terms", 9, True, True); run(p, "—" + R.KEYWORDS + ".", 9, True)
    n1 = n2 = tn = fn = 0
    for b in blocks:
        k = b[0]
        if k == "h1":
            n1 += 1; n2 = 0; para(doc, f"{ROMAN[n1-1]}. {b[1].upper()}", 9.5, WD_ALIGN_PARAGRAPH.CENTER, False, 8, 3, keep_next=True)
        elif k == "h2":
            n2 += 1; para(doc, f"{chr(64+n2)}. {b[1]}", 9.5, WD_ALIGN_PARAGRAPH.LEFT, False, 5, 2, italic=True, keep_next=True)
        elif k == "p": para(doc, curly(b[1]), 9.5)
        elif k == "list":
            for i, it in enumerate(b[1], 1):
                p = para(doc, "", 9.5, indent=False, after=2); p.paragraph_format.left_indent = Pt(14); p.paragraph_format.first_line_indent = Pt(-14)
                run(p, f"{i}.  ", 9.5); rich(p, curly(it), 9.5)
        elif k == "eq":
            p = para(doc, "", 9.5, WD_ALIGN_PARAGRAPH.LEFT, False, 2, 3)
            p.paragraph_format.tab_stops.add_tab_stop(Inches(COLW / 2), WD_TAB_ALIGNMENT.CENTER)
            p.paragraph_format.tab_stops.add_tab_stop(Inches(COLW), WD_TAB_ALIGNMENT.RIGHT)
            run(p, "\t", 9.5); run(p, b[1], 9.5, italic=True); run(p, f"\t({b[2]})", 9.5)
        elif k == "fig":
            fn += 1
            p = para(doc, "", 9, WD_ALIGN_PARAGRAPH.CENTER, False, 3, 1, keep_next=True)
            from PIL import Image
            im = Image.open((FIGS / b[1]).resolve()); w, h = im.size
            width = COLW; hh = width * h / w; maxh = 3.6 if "workflow" in b[1] else 2.45
            if hh > maxh: width = width * maxh / hh
            p.add_run().add_picture(str((FIGS / b[1]).resolve()), width=Inches(width))
            c = para(doc, "", 8, WD_ALIGN_PARAGRAPH.JUSTIFY, False, 1, 5)
            rich(c, curly(f"Fig. {fn}. {b[2]}"), 8)
        elif k == "appendix":
            para(doc, f"APPENDIX A. {b[1].upper()}", 9.5, WD_ALIGN_PARAGRAPH.CENTER, False, 8, 3, keep_next=True)
        elif k == "code":
            para(doc, b[1], 9.5, WD_ALIGN_PARAGRAPH.LEFT, False, 5, 2, italic=True, keep_next=True)
            for ln in b[2].split("\n"):
                pp = para(doc, "", 6.3, WD_ALIGN_PARAGRAPH.LEFT, False, 0, 0)
                run(pp, ln if ln else " ", 6.3).font.name = "Courier New"
            para(doc, "", 3, WD_ALIGN_PARAGRAPH.LEFT, False, 0, 2)
        elif k == "table":
            tn += 1; _, cap, head, rows, widths, note = b
            add_table(doc, cap, head, rows, widths, note, tn)
    para(doc, "ACKNOWLEDGMENT", 9.5, WD_ALIGN_PARAGRAPH.CENTER, False, 8, 3, keep_next=True)
    para(doc, curly(R.ACK), 8.8, indent=False)
    para(doc, "REFERENCES", 9.5, WD_ALIGN_PARAGRAPH.CENTER, False, 8, 3, keep_next=True)
    for i, k in enumerate(order, 1):
        p = para(doc, "", 7.8, WD_ALIGN_PARAGRAPH.LEFT, False, 0, 2); p.paragraph_format.left_indent = Pt(18); p.paragraph_format.first_line_indent = Pt(-18)
        run(p, f"[{i}]  ", 7.8); rich(p, curly(R.REFS[k]), 7.8)
    out = OUT / "report" / "SmartStudy_IEEE_Report.docx"
    doc.save(out); return out

if __name__ == "__main__":
    print("wrote", build())

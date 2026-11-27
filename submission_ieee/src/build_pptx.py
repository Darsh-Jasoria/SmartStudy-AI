"""Builds the SmartStudy slide deck (16:9) with python-pptx. Numbers come from the repo's result files."""
import re
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from lxml import etree
from PIL import ImageFont
import report_content as R
from data import *

OUT = ROOT / "submission_ieee"; FIGS = OUT / "figs"
FONT = "Calibri"
NAVY, TEAL, RED, GREY, LIGHT, INK = "12263F", "1F7A8C", "C8553D", "5B6B7B", "F3F6F9", "1B2430"
BLUE_F, GREEN_F, YELL_F, RED_F = "D6E6F5", "DCEFD9", "FFF1C9", "F7D6D0"
VCOL = ["999999", "E69F00", "56B4E9", "009E73", "0072B2", "D55E00"]

def rgb(h): return RGBColor.from_string(h)
_f = {}
def _font(bold, size):
    k = (bold, size)
    if k not in _f:
        _f[k] = ImageFont.truetype("/Applications/Microsoft 365/Microsoft PowerPoint.app/Contents/Resources/DFonts/" + ("Calibrib.ttf" if bold else "Calibri.ttf"), size * 4)
    return _f[k]
WARN = []
def est_height(text, width_in, size, bold=False):
    f = _font(bold, size); maxw = width_in * 72 * 4; lines = 0
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        n = 1
        for w in words:
            t = (cur + " " + w).strip()
            if f.getlength(t) > maxw and cur: n += 1; cur = w
            else: cur = t
        lines += n
    return lines * size * 1.2 / 72

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
SLIDE_NO = [0]

def rect(s, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, lw=1.0, radius=None):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    else: sh.fill.background()
    if line: sh.line.color.rgb = rgb(line); sh.line.width = Pt(lw)
    else: sh.line.fill.background()
    sh.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE: sh.adjustments[0] = radius
    return sh

def runs(p, text, size, color=INK, bold=False, italic=False):
    for i, part in enumerate(re.split(r"\*\*", text)):
        if not part: continue
        r = p.add_run(); r.text = part; f = r.font; f.name = FONT; f.size = Pt(size); f.color.rgb = rgb(color)
        f.bold = bold or (i % 2 == 1); f.italic = italic

def bullet(p, char="•", indent=0.28, color=TEAL):
    pPr = p._p.get_or_add_pPr(); pPr.set("marL", str(int(Inches(indent)))); pPr.set("indent", str(-int(Inches(indent))))
    for tag in ("a:buNone", "a:buChar", "a:buClr"):
        for e in pPr.findall(qn(tag)): pPr.remove(e)
    clr = etree.SubElement(pPr, qn("a:buClr")); c = etree.SubElement(clr, qn("a:srgbClr")); c.set("val", color)
    bu = etree.SubElement(pPr, qn("a:buChar")); bu.set("char", char)

def text(s, x, y, w, h, paras, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT, bullets=False, anchor=MSO_ANCHOR.TOP,
         space=6, italic=False, check=True, line_spacing=1.0):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.03); tf.vertical_anchor = anchor
    if isinstance(paras, str): paras = [paras]
    tot = 0
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(space); p.line_spacing = line_spacing
        runs(p, para, size, color, bold, italic)
        if bullets: bullet(p)
        tot += est_height(re.sub(r"\*\*", "", para), w - 0.1 - (0.28 if bullets else 0), size, bold) + space / 72
    if check and tot > h + 0.05: WARN.append(f"slide {SLIDE_NO[0]}: text overflow {tot:.2f}in > {h:.2f}in : {paras[0][:40]}")
    return tb

def card(s, x, y, w, h, title, body, fill=LIGHT, tcolor=NAVY, size=15, tsize=17, accent=TEAL, bullets=False):
    rect(s, x, y, w, h, fill, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
    rect(s, x, y + 0.12, 0.07, h - 0.24, accent)
    text(s, x + 0.2, y + 0.08, w - 0.3, 0.45, title, tsize, tcolor, True, check=False)
    text(s, x + 0.2, y + 0.55, w - 0.3, h - 0.6, body, size, INK, bullets=bullets, space=4)

def notes(s, txt): s.notes_slide.notes_text_frame.text = txt

def new_slide(title, sub=None):
    s = prs.slides.add_slide(BLANK); SLIDE_NO[0] += 1
    rect(s, 0, 0, 13.333, 0.16, NAVY)
    rect(s, 0.55, 0.52, 0.09, 0.62, TEAL)
    text(s, 0.75, 0.4, 11.9, 0.9, title, 30, NAVY, True, anchor=MSO_ANCHOR.MIDDLE, check=False)
    if sub: text(s, 0.75, 1.15, 11.9, 0.4, sub, 15, GREY, italic=True, check=False)
    text(s, 0.55, 7.05, 9, 0.3, "SmartStudy  ·  Team IntelliCore (PE-B37-17)  ·  Bennett University", 10.5, GREY, check=False)
    text(s, 12.0, 7.05, 0.8, 0.3, str(SLIDE_NO[0]), 10.5, GREY, align=PP_ALIGN.RIGHT, check=False)
    return s

def table(s, x, y, w, rows, colw, size=13, rowh=0.38, header=True, bold_cells=(), fills=None, align_center=()):
    nr, nc = len(rows), len(rows[0])
    gs = s.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rowh * nr)); t = gs.table
    tblPr = gs._element.graphic.graphicData.tbl.tblPr
    for a in ("firstRow", "bandRow"): tblPr.set(a, "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is not None: sid.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"    # "No Style, Table Grid" -> we colour cells ourselves
    tot = sum(colw)
    for j, cw in enumerate(colw): t.columns[j].width = Inches(w * cw / tot)
    for i, r in enumerate(rows):
        t.rows[i].height = Inches(rowh)
        for j, v in enumerate(r):
            c = t.cell(i, j); c.margin_left = c.margin_right = Inches(0.07); c.margin_top = c.margin_bottom = Inches(0.025)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]
            hdr = header and i == 0
            runs(p, re.sub(r'"([^"]*)"', "\u201c\\1\u201d", str(v)), size, "FFFFFF" if hdr else INK, bold=hdr or (i, j) in bold_cells)
            if j in align_center: p.alignment = PP_ALIGN.CENTER
            c.fill.solid()
            fc = NAVY if hdr else (fills.get((i, j)) if fills and (i, j) in fills else ("FFFFFF" if i % 2 else LIGHT))
            c.fill.fore_color.rgb = rgb(fc)
            if hdr is False and fills and (i, j) in fills and fills[(i, j)] in ("2E7D32", "B3261E"):
                for rr in p.runs: rr.font.color.rgb = rgb("FFFFFF"); rr.font.bold = True
    return t

def pic(s, name, x, y, w=None, h=None):
    kw = {}
    if w: kw["width"] = Inches(w)
    if h: kw["height"] = Inches(h)
    return s.shapes.add_picture(str(FIGS / name) if not name.startswith("/") else name, Inches(x), Inches(y), **kw)

def arrow(s, x1, y1, x2, y2, color=NAVY, w=1.75):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(w)
    ln = c.line._get_or_add_ln(); te = etree.SubElement(ln, qn("a:tailEnd")); te.set("type", "triangle"); te.set("w", "med"); te.set("len", "med")
    return c

def chip(s, x, y, w, h, label, fill, tcolor=INK, size=14, bold=True, line=None):
    sh = rect(s, x, y, w, h, fill, line, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.25)
    tf = sh.text_frame; tf.margin_left = tf.margin_right = Inches(0.05); tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; runs(p, label, size, tcolor, bold)
    if est_height(re.sub(r"\*\*", "", label), w - 0.1, size, bold) > h + 0.03: WARN.append(f"slide {SLIDE_NO[0]}: chip overflow '{label[:30]}'")
    return sh

def stat(s, x, y, w, big, small, color=TEAL):
    rect(s, x, y, w, 1.25, LIGHT, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    text(s, x, y + 0.05, w, 0.65, big, 30, color, True, PP_ALIGN.CENTER, check=False)
    text(s, x + 0.1, y + 0.7, w - 0.2, 0.5, small, 12.5, GREY, align=PP_ALIGN.CENTER, space=0)

def col_chart(s, x, y, w, h, title, key, ymax=None, lower_better=False):
    cd = CategoryChartData(); cd.categories = VERS; cd.add_series(title, [round(RES[v]["metrics"][key], 3) for v in VERS])
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd); ch = gf.chart
    ch.has_legend = False; ch.has_title = True; ch.chart_title.text_frame.text = title
    tp = ch.chart_title.text_frame.paragraphs[0]; tp.runs[0].font.size = Pt(15); tp.runs[0].font.bold = True; tp.runs[0].font.name = FONT; tp.runs[0].font.color.rgb = rgb(NAVY)
    va = ch.value_axis; va.visible = False; va.has_major_gridlines = False; va.minimum_scale = 0
    va.maximum_scale = ymax or round(max(RES[v]["metrics"][key] for v in VERS) * 1.25 + 0.02, 2)
    ca = ch.category_axis; ca.tick_labels.font.size = Pt(13); ca.tick_labels.font.name = FONT; ca.format.line.color.rgb = rgb("999999")
    pl = ch.plots[0]; pl.gap_width = 45; pl.has_data_labels = True; dl = pl.data_labels
    dl.number_format = "0.000"; dl.number_format_is_linked = False; dl.font.size = Pt(11); dl.font.name = FONT; dl.position = XL_LABEL_POSITION.OUTSIDE_END
    for i, pt in enumerate(pl.series[0].points):
        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(VCOL[i])
    return ch

m = lambda v, k: RES[v]["metrics"][k]
# =========================================================== slides
# 1 Title
s = prs.slides.add_slide(BLANK); SLIDE_NO[0] += 1
rect(s, 0, 0, 13.333, 7.5, NAVY); rect(s, 0, 5.05, 13.333, 0.06, TEAL)
text(s, 0.8, 0.7, 11.5, 0.5, "SCSE4041 PROMPT ENGINEERING  ·  MILESTONE 2  ·  PROBLEM POOL C2", 14, "9FB6CC", True, check=False)
text(s, 0.8, 1.35, 11.8, 1.0, "SmartStudy", 60, "FFFFFF", True, check=False)
text(s, 0.8, 2.5, 11.6, 1.5, "A Grounded, Multi-Stage Prompt Workflow for Generating Verifiable Study Packs from Lecture Notes", 30, "E8EEF4", False)
text(s, 0.8, 5.3, 11.8, 0.5, "Team IntelliCore (Team ID PE-B37-17 · Batch B37-48)   ·   Darsh Jasoria · Mahak Soni · Pradanya Sharma · Arnav Singh", 17, "FFFFFF", check=False)
text(s, 0.8, 5.85, 11.8, 0.5, "Faculty: Pawan Kumar   ·   School of Computer Science Engineering and Technology, Bennett University", 15, "C9D6E3", check=False)
text(s, 0.8, 6.4, 11.8, 0.4, "November 2026", 14, "9FB6CC", check=False)
notes(s, "Introduce the team and the course. SmartStudy turns lecture notes into a summary, key terms and practice questions, and every item carries a quote from the notes that code verifies. We will cover the problem, the design, a six-version experiment on a live model, the test table and what the numbers really mean.")

# 2 Agenda
s = new_slide("Outline")
items = ["Problem and goal", "Core idea and design", "Implementation", "Experimental setup", "Results", "Analysis and failures", "Next steps"]
for i, t_ in enumerate(items):
    y = 1.65 + i * 0.7
    chip(s, 0.9, y, 0.55, 0.5, str(i + 1), TEAL, "FFFFFF", 18)
    text(s, 1.65, y + 0.02, 8, 0.5, t_, 22, INK, anchor=MSO_ANCHOR.MIDDLE, check=False)
card(s, 8.0, 1.65, 4.7, 2.9, "In one sentence", ["SmartStudy converts lecture notes into a summary, key terms and practice questions, and **every item carries a quote that program code checks against the notes.**"], size=20)
notes(s, "Seven parts. The two things to remember: grounding by verifiable quote, and the honest analysis of what our metrics do and do not show.")

# 3 Problem
s = new_slide("The problem: revision material you cannot trust", "Students paste notes into a chatbot and hope")
card(s, 0.7, 1.8, 3.85, 3.0, "Long notes, little time", ["Lecture notes run to hundreds of words per topic.", "Students want a short summary, key terms and practice questions."], size=18.5, bullets=True)
card(s, 4.75, 1.8, 3.85, 3.0, "Chatbots add facts", ["Fluent but unsupported content (hallucination).", "True facts the lecture never taught still mislead an exam answer."], size=18.5, bullets=True, accent=RED)
card(s, 8.8, 1.8, 3.85, 3.0, "Limits are ignored", ["Wrong number of questions.", "Summary over the word limit.", "Only one question type."], size=18.5, bullets=True, accent="E69F00")
rect(s, 0.7, 5.2, 11.95, 1.2, NAVY, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
text(s, 1.0, 5.3, 11.4, 1.0, "A wrong answer key is worse than none: the student cannot tell which items to trust.", 22, "FFFFFF", True, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
notes(s, "Frame the problem from the student's side. The cost of a wrong key is high because the student has no way to check it. Our goal is therefore not just a good summary but checkable output.")

# 4 Goal and contributions
s = new_slide("Goal and contributions")
text(s, 0.75, 1.5, 11.8, 0.8, "Study how **prompt design alone** (no training) can make a study-pack generator trustworthy, measured on a real hosted model.", 20, INK)
cs = ["A four-prompt, two-guard workflow (v5): chaining, over-generate-and-filter, quote guard, moderator, length guard",
      "Controlled ablation of six versions: Gemini 3.1 Flash-Lite, 9 gold-labelled notes, 8 metrics",
      "13-case test table: normal, edge (thin, Hinglish, injection, missing info) and invalid inputs",
      "Post-hoc validity audit: which headline metrics mislead, and the recall ceiling",
      "Open implementation: deployed prototype, 22 unit tests, no third-party packages"]
for i, c_ in enumerate(cs):
    y = 2.55 + i * 0.84
    chip(s, 0.8, y + 0.05, 0.55, 0.55, str(i + 1), TEAL, "FFFFFF", 18)
    text(s, 1.55, y, 11.0, 0.75, c_, 18, INK, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "Read the five contributions. The audit contribution matters: some of our own metrics turned out to mislead, and we report that.")

# 5 Core idea
s = new_slide("Core idea: every item carries a quote that code verifies", "Turns “is it invented?” into a string test")
chip(s, 0.7, 2.3, 2.5, 1.2, "Lecture notes", YELL_F, size=18)
chip(s, 3.9, 2.0, 3.0, 1.8, "LLM emits item **+ one exact quote** from the notes", BLUE_F, size=17)
chip(s, 7.6, 2.0, 2.6, 1.8, "**Code** checks: is the quote in the notes?", GREEN_F, size=17)
chip(s, 10.9, 1.75, 1.85, 0.8, "Yes: kept", "2E7D32", "FFFFFF", 17)
chip(s, 10.9, 3.25, 1.85, 0.8, "No: dropped, logged", "B3261E", "FFFFFF", 15)
arrow(s, 3.2, 2.9, 3.9, 2.9); arrow(s, 6.9, 2.9, 7.6, 2.9); arrow(s, 10.2, 2.65, 10.9, 2.15); arrow(s, 10.2, 3.15, 10.9, 3.65)
card(s, 0.7, 4.4, 5.9, 2.35, "Where an exact check is possible, code does it", ["String matching, word counting, keeping the first N.", "Cheaper and more reliable than another model call."], size=19, bullets=True)
card(s, 6.85, 4.4, 5.9, 2.35, "Where meaning is involved, the model does it", ["Topic outline, generation, answering from the notes, shortening.", "A separate moderator call re-answers each question."], size=19, bullets=True, accent="E69F00")
notes(s, "This is the central design rule: split the task between model and code according to whether an exact check exists. The quote requirement is what makes the code check possible.")

# 6 IO contract
s = new_slide("Input / output contract")
card(s, 0.7, 1.55, 4.3, 3.1, "Input", ["**Notes:** 40 to 20,000 characters (6,000 on the public deployment)", "**N questions:** default 5, range 1 to 15", "**Word limit:** default 100, range 30 to 300"], size=18, bullets=True)
card(s, 5.25, 1.55, 7.4, 3.1, "Output (JSON)", ["**summary** within the limit", "**key_terms:** term, definition, evidence quote", "**questions:** type (mcq, short, true_false), options, answer, evidence quote", "**warnings** (escape hatch) and a **workflow trace**"], size=18, bullets=True, accent="E69F00")
text(s, 0.7, 4.85, 12, 0.4, "A pack meets the constraints when:", 17, NAVY, True, check=False)
for i, c_ in enumerate(["Exactly N questions", "Summary ≤ limit", "≥ 3 types incl. MCQ", "Only the notes' knowledge", "One exact quote per item"]):
    chip(s, 0.7 + i * 2.43, 5.45, 2.3, 1.0, c_, BLUE_F, size=16.5)
notes(s, "These five conditions are exactly what the constraints metric checks. The limits in brackets are the public-deployment settings that protect the free API quota.")

# 7 Workflow
s = new_slide("Final workflow v5: four prompts, three code steps", "Blue = LLM prompt   ·   Green = code   ·   Yellow = data")
bw, bh = 2.75, 1.6; xs = [0.7, 3.95, 7.2, 10.45]
r1 = [("Input", "notes, N, word limit", YELL_F), ("P1 Outline  (LLM)", "list the topics the notes teach", BLUE_F),
      ("P2 Generate  (LLM)", "summary, terms, N+2 questions, each with a quote", BLUE_F), ("Quote guard  (code)", "keep only items whose quote is in the notes", GREEN_F)]
r2 = [("Study pack", "summary, terms, Q&A, warnings, trace", YELL_F), ("Length guard  (code)", "summary words ≤ limit? else P4 shortens once", GREEN_F),
      ("Keep first N  (code)", "never pad; warn if fewer survive", GREEN_F), ("P3 Moderator  (LLM)", "answers each question from the notes only", BLUE_F)]
def wf_box(x, y, t_, d_, f_):
    rect(s, x, y, bw, bh, f_, NAVY, MSO_SHAPE.ROUNDED_RECTANGLE, lw=1.25, radius=0.08)
    text(s, x + 0.1, y + 0.1, bw - 0.2, 0.4, t_, 16, NAVY, True, PP_ALIGN.CENTER, check=False)
    text(s, x + 0.12, y + 0.55, bw - 0.24, 1.0, d_, 15.5, INK, align=PP_ALIGN.CENTER, space=0)
for x, (t_, d_, f_) in zip(xs, r1): wf_box(x, 1.85, t_, d_, f_)
for x, (t_, d_, f_) in zip(xs, r2): wf_box(x, 4.2, t_, d_, f_)
for i in range(3): arrow(s, xs[i] + bw, 2.65, xs[i + 1], 2.65)
arrow(s, xs[3] + bw / 2, 1.85 + bh, xs[3] + bw / 2, 4.2)       # quote guard -> (moderator is directly below)
for i in range(3, 0, -1): arrow(s, xs[i], 5.0, xs[i - 1] + bw, 5.0)
text(s, 0.7, 6.05, 12.0, 0.9, ["Dropped items are logged in the workflow trace. P4 Shorten runs only when the summary is over the limit, then the length is re-checked once; a warning is added if it is still too long."], 15, GREY, italic=True)
notes(s, "Walk the top row left to right, then the bottom row right to left. The moderator is an independent call: it sees only the notes and the candidate questions. We ask for N+2 candidates so filtering still leaves N. The length guard exists because models cannot count words reliably.")

# 8 Techniques
s = new_slide("Prompt-engineering techniques used")
rows = [["Technique", "Where", "Purpose"],
        ["Role and constraints", "P2", "Teaching-assistant role; use only the notes"],
        ["Strict JSON schema", "P1 to P4", "Machine-checkable output"],
        ["Few-shot + negative example", "P2", "Shows the format; distractors must not become terms"],
        ["Source grounding by quote", "P2 + guard", "Turns “invented?” into a string test"],
        ["Prompt chaining", "P1 to P4", "Specialised, inspectable steps"],
        ["Over-generate and filter", "P2, P3", "Ask for N+2 so filtering still keeps N"],
        ["Escape hatch (warnings)", "P2, code", "Allow fewer items instead of inventing"],
        ["Temperature 0, minimal thinking", "All calls", "Reproducibility and speed"]]
table(s, 0.7, 1.55, 11.95, rows, [3.2, 1.6, 5.2], 16, 0.58)
notes(s, "Each technique maps to a failure we saw in the zero-shot version. The negative example in P2 shows distractor options such as Heap and Array that must not be turned into key terms.")

# 8b Final prompt sheet
s = new_slide("Final prompt sheet: P1 to P4", "Full verbatim text is in Appendix A of the report and in prompts/final/")
card(s, 0.7, 1.7, 5.9, 2.4, "P1 Outline", ["List 4 to 10 topics with main points, **only from the notes**. JSON: topics[{title, main_points}]."], size=16.5, accent=TEAL)
card(s, 6.85, 1.7, 5.8, 2.4, "P2 Generate", ["Teaching-assistant role; summary, key terms, N+2 questions; **one exact contiguous quote per item**; mcq + short + true/false; one few-shot example; warn if notes are thin."], size=15.5, accent="E69F00")
card(s, 0.7, 4.3, 5.9, 2.4, "P3 Moderator", ["Strict examiner: answers each question **from the notes only**; valid true/false, reason, corrected answer; mcq must have one correct option."], size=16, accent="2E7D32")
card(s, 6.85, 4.3, 5.8, 2.4, "P4 Shorten", ["Rewrite the summary to at most the word limit (aim about 10% under); keep topics and terms, **add nothing new**. Runs only if over the limit."], size=16, accent=RED)
notes(s, "These four files are the final prompts. P2 is the longest because it carries the role, schema, rules and the worked example. The contradiction discussed later (exactly N versus return fewer) sits in P2.")

# 9 Quote guard
s = new_slide("The quote guard: a substring test on normalised text")
card(s, 0.7, 1.55, 6.3, 2.2, "Normalise, then test", ["norm(): lowercase, curly quotes to ASCII, every run of non-alphanumeric characters becomes one space.", "**grounded(e, S) = [ e ≠ ∅  ∧  norm(e) ⊆ norm(S) ]**"], size=17)
card(s, 0.7, 3.95, 6.3, 2.8, "Example from the TCP notes", ["Quote kept: “Sequence numbers label bytes so the receiver can reorder segments and detect loss”", "Quote dropped: two fragments joined with “...” (seen in v3): not one contiguous quote."], size=17, accent=RED)
card(s, 7.25, 1.55, 5.4, 2.4, "What it proves", ["The quote really occurs in the notes.", "Tolerant of line breaks and punctuation, strict about wording."], size=18, bullets=True, accent="2E7D32")
card(s, 7.25, 4.15, 5.4, 2.6, "What it does not prove", ["That the quote supports the claim.", "That the text is lecture content (see failures).", "A one-word quote such as “FIFO” passes."], size=18, bullets=True, accent=RED)
notes(s, "Be upfront that the guard is a necessary check, not a sufficient one. That limitation reappears in the failure analysis: the padded questions in tests 8 and 12 were all grounded.")

# 10 Implementation
s = new_slide("Implementation and deployment")
stat(s, 0.7, 1.55, 2.0, "~1,100", "lines of backend Python")
stat(s, 2.85, 1.55, 2.0, "22", "unit tests, all pass")
stat(s, 0.7, 3.0, 2.0, "0", "third-party packages")
stat(s, 2.85, 3.0, 2.0, "3", "model providers + replay")
text(s, 0.7, 4.45, 4.3, 2.4, ["Python 3.9+, standard library only", "Gemini client: 3 retries (2 s, 4 s), 40 s timeout, fallback models", "Same code runs locally and on Vercel", "Key only in environment or a git-ignored file"], 15.5, INK, bullets=True, space=4)
pic(s, "../../docs/figures/m2_run_test3_tcp.png", 5.3, 1.55, w=7.3)
text(s, 5.3, 6.3, 7.3, 0.6, "Live app: v5 pack for the TCP notes (81-word summary, 4 terms, 5 questions, 100% verified quotes). Prototype: smartstudy-ai-swart.vercel.app", 12, GREY, italic=True)
notes(s, "The standard-library choice means no install step: the grader can run it with python3 only. The frontend has Overview, Summary, Key terms, Questions, Quiz, Plan, Compare, Notes and Trace views plus an evaluation dashboard that reads the result files.")

# 11 Setup
s = new_slide("Experimental setup")
card(s, 0.7, 1.55, 3.9, 4.9, "Data set", ["**9 original CS notes**", "6 short (165 to 199 words)", "3 long (528 to 1,037 words)", "3,463 words in total", "**Gold labels:** 173 key terms, 74 must-cover groups, out-of-scope terms"], size=19, bullets=True)
card(s, 4.8, 1.55, 3.9, 4.9, "Model and protocol", ["**Gemini 3.1 Flash-Lite** via the Gemini API", "Temperature 0.0, minimal thinking", "N = 5 questions, 100-word limit", "One run per version, 22 Nov 2026", "Free-tier quotas limited repetition"], size=19, bullets=True, accent="E69F00")
card(s, 8.9, 1.55, 3.75, 4.9, "Six versions", ["**v0** rules, no LLM", "**v1** zero-shot", "**v2** role + schema + quotes", "**v3** + one example", "**v4** chain + moderator", "**v5** + length guard"], size=19, bullets=True, accent=RED)
notes(s, "The October experiments used simulated answers because no key existed; they are kept separately and are not used for any claim. Everything shown here is from live runs on 22 November.")

# 12 Metrics
s = new_slide("How we measured: eight automatic metrics")
rows = [["Metric", "Definition"], ["Term recall", "gold terms matched / gold terms"], ["Coverage", "gold must-cover groups present in summary + definitions"],
        ["Flagged terms", "output terms not found as a phrase in the notes"], ["Ungrounded questions", "questions whose quote is not in the notes (n/a for v1)"],
        ["Answer support", "answers with ≥ 60% of their words (> 3 chars) in the notes"], ["Outside facts", "out-of-scope gold terms leaking into the pack"],
        ["Constraints met", "N questions, ≤ 100 words, ≥ 3 types incl. MCQ"], ["JSON failures", "runs whose output could not be parsed"]]
table(s, 0.7, 1.55, 11.95, rows, [2.6, 7.4], 16, 0.58)
notes(s, "All eight are computed automatically against the gold files. Remember the later audit: three of them are proxies with known weaknesses.")

# 13 Results table
s = new_slide("Results: structure fixes the format, the chain adds coverage")
hdr = ["Version", "Term recall", "Coverage", "Flagged terms", "Ungrounded Q", "Answer support", "Outside facts", "Constraints"]
rows = [hdr] + [[v, R.f3(m(v, "term_recall")), R.f3(m(v, "coverage")), R.f3(m(v, "term_halluc")), R.f3(m(v, "ungrounded_q")), R.f3(m(v, "answer_support")),
                 str(m(v, "outside_know")), f"{m(v,'constraints'):.1f}"] for v in VERS]
best = {(2, 1): 1, }
bc = {(2, 1), (5, 2), (6, 2), (4, 5), (1, 5)}   # v1 recall (2,1)... computed below instead
bold = set()
for j, (k, hi) in enumerate([("term_recall", 1), ("coverage", 1), ("term_halluc", 0), ("ungrounded_q", 0), ("answer_support", 1), ("outside_know", 0), ("constraints", 1)], 1):
    vals = [None] + [(m(v, k) if not isinstance(m(v, k), str) else None) for v in VERS[1:]]
    ok = [x for x in vals if x is not None]
    if k == "constraints": tgt = max(ok)
    elif hi: tgt = max(ok)
    else: tgt = min(ok)
    for i, x in enumerate(vals, 1):
        if x == tgt and k not in ("term_halluc", "ungrounded_q", "outside_know"): bold.add((i, j))
table(s, 0.7, 1.55, 11.95, rows, [1.2, 1.4, 1.4, 1.5, 1.5, 1.6, 1.4, 1.4], 16, 0.52, bold_cells=bold, align_center=range(1, 8))
text(s, 0.7, 5.25, 12, 0.35, "Bold = best among the LLM versions v1 to v5. v0 is extractive, so its answer support is 1.0 by construction. v1 Ung is n/a.", 12, GREY, italic=True)
stat(s, 0.7, 5.7, 3.8, "0/9 → 9/9", "notes meeting constraints, v1 → v2")
stat(s, 4.75, 5.7, 3.8, "0.725 → 0.956", "answer support, v1 → v2")
stat(s, 8.8, 5.7, 3.85, "0.568 → 0.676", "coverage, v3 → v4 (+19%)", color=RED)
notes(s, "v1 could not meet the type rule by construction: all 40 of its questions were short answer. v4 and v5 have identical numbers because the length guard never fired: every summary was already at most 99 words.")

# 14 Charts
s = new_slide("The same data as charts (editable)")
col_chart(s, 0.6, 1.5, 6.1, 2.65, "Term recall", "term_recall"); col_chart(s, 6.75, 1.5, 6.1, 2.65, "Coverage", "coverage")
col_chart(s, 0.6, 4.2, 6.1, 2.65, "Answer support", "answer_support", 1.15); col_chart(s, 6.75, 4.2, 6.1, 2.65, "Flagged-term rate (lower is better)", "term_halluc")
notes(s, "Version colours are consistent across the report and deck. v1 has the highest recall but also the only flagged terms, and no quotes.")

# 15 Short vs long
s = new_slide("Long notes are much harder than short ones")
rows = [["Ver.", "Recall short", "Cov. short", "Recall long", "Cov. long"]] + [[v, R.f3(RES[v]["groups"]["short"]["metrics"]["term_recall"]), R.f3(RES[v]["groups"]["short"]["metrics"]["coverage"]),
        R.f3(RES[v]["groups"]["long"]["metrics"]["term_recall"]), R.f3(RES[v]["groups"]["long"]["metrics"]["coverage"])] for v in VERS]
table(s, 0.7, 1.6, 5.6, rows, [0.7, 1.2, 1.1, 1.2, 1.1], 14, 0.5, align_center=range(1, 5))
text(s, 0.7, 5.3, 5.6, 1.5, ["For v5, recall falls **0.421 → 0.124** and coverage **0.842 → 0.500**.", "A fixed-size pack (about 4 terms, 5 questions) cannot cover notes with 30 to 36 gold terms."], 16.5, INK, bullets=True, space=5)
pic(s, "fig_heat_cov.png", 6.9, 1.45, w=5.8)
notes(s, "Heat map: coverage per note and version. The weakest cells are long notes: memory management at 0.33 for v5 and software-engineering slides at 0.50. This points to scaling the pack size with the notes.")

# 16 Recall ceiling
s = new_slide("Key-term recall is capped by how many terms the model emits")
pic(s, "fig_ceiling.png", 0.6, 1.5, w=7.1)
stat(s, 8.0, 1.6, 2.2, "38", "terms emitted by v5 (9 notes)")
stat(s, 10.45, 1.6, 2.2, "173", "gold key terms", color=RED)
text(s, 8.0, 3.1, 4.7, 3.6, ["One-to-one matching would cap recall at 38 / 173 = **0.22**.", "Reported recall is **0.254** (44 gold terms matched): lenient containment lets one output term match several gold entries.", "So recall mainly measures how many terms the prompt asks for. The prompts never set a minimum."], 16.5, INK, bullets=True, space=7)
notes(s, "This is why v1 wins on recall: it lists about six terms per note against three in v2. The fix is a prompt that asks for every defined term, and a one-to-one scorer.")

# 17 Cost
s = new_slide("Cost versus quality")
pic(s, "fig_tradeoff.png", 0.6, 1.5, w=6.7)
stat(s, 7.5, 1.55, 1.65, "3", "calls per v5 pack")
stat(s, 9.3, 1.55, 1.65, "34", "calls in the test run")
stat(s, 11.1, 1.55, 1.6, "+11", "coverage points for 3x calls", color=RED)
text(s, 7.5, 3.05, 5.2, 3.7, ["Test run: **30,153** input and **19,054** output tokens.", "The moderator rejected **0 of 63** candidate questions and edited the answer of 7 of 45 kept ones.", "The two extra N+2 candidates were never needed: no question was dropped. Only one term (“Scrum”) was removed by the quote guard.", "“About 4 calls” per pack is the worst case (with P4)."], 16, INK, bullets=True, space=6)
notes(s, "On this data the measurable effect of the moderator is small. Its value may show up on harder notes or weaker models; that is a Milestone 3 question. The 34 calls are 11 v5 packs at three calls each plus one P4 call.")

# 18 Test table
s = new_slide("Test table: 11 of 13 pass", "Normal 7/7  ·  Edge 3/4  ·  Invalid 1/2   (code-checked, live model)")
rows = [["#", "Input", "Type", "Result", "P/F"]] + [[r[0], r[1], r[2], r[3], r[4]] for r in R.TESTROWS]
fills = {}
for i, r in enumerate(rows[1:], 1): fills[(i, 4)] = "2E7D32" if r[4] == "Pass" else "B3261E"
table(s, 0.7, 1.6, 11.95, rows, [0.35, 4.3, 0.9, 3.9, 0.8], 13.5, 0.375, fills=fills, align_center=(0, 4))
notes(s, "Test 7 is a component test: a real 102-word summary is sent to the length guard and comes back at 45 words against a limit of 60. The injection test and the missing-slide test both pass; Hinglish input yields five terms and five grounded questions.")

# 19 Failures
s = new_slide("The two failures: padding thin and non-lecture input")
card(s, 0.7, 1.55, 5.9, 1.85, "Test 8: 3-sentence photosynthesis note", ["22 words in, **5 questions and no warning**."], size=19, accent=RED)
card(s, 6.85, 1.55, 5.8, 1.85, "Test 12: casual Hinglish chat", ["46 words about the canteen and a cricket match: **5 questions, 3 “terms”, no warning**."], size=19, accent=RED)
card(s, 0.7, 3.6, 5.9, 3.15, "Why it slips through", ["Every padded question was **grounded**, so the quote guard cannot object.", "The moderator checks answerability, not whether the text is lecture content.", "P2 says “exactly the number asked” and also “return fewer and warn”: a contradiction."], size=17, bullets=True)
card(s, 6.85, 3.6, 5.8, 3.15, "Planned fixes", ["Cap N by note length **in code**.", "Add a lecture-content gate before P1.", "Remove the contradiction in P2; make the warning mandatory for thin input."], size=17, bullets=True, accent="2E7D32")
notes(s, "Grounding is not the same as usefulness. The guard proves a quote exists; it cannot tell that the quote is about a samosa. The contradiction in P2 is our own prompt bug and is a likely cause.")

# 20 Audit
s = new_slide("What the headline metrics hide: a post-hoc audit")
card(s, 0.7, 1.55, 5.95, 5.2, "Flagged terms are not hallucinations", ["7 terms flagged (5 in v1, 2 in v4/v5).", "5 are naming variants of terms the notes do teach: “Big-O Notation” (×2), “Learning Rate (alpha)”, “AUC-ROC”, “CI/CD”.", "2 are acronym expansions (“Boyce-Codd Normal Form”): true but absent from the notes.", "**Invented concepts: 0 in every version.** The metric is a strict phrase check."], size=17.5, bullets=True, accent=RED)
card(s, 6.85, 1.55, 5.8, 5.2, "The answer-support dip is mostly an artifact", ["Scorer keeps words > 3 characters, so “UDP”, “O(n^2)”, “FIN and ACK” leave **no words** and count as unsupported.", "**4 of the 6** unsupported v4 answers; the other 2 are paraphrases (overlap 0.33, 0.57).", "v4 had more MCQs (13 vs 9), so its score fell 0.956 → 0.867 with no outside knowledge used."], size=17.5, bullets=True, accent="E69F00")
notes(s, "This audit is based on re-reading the saved outputs. The team should confirm each of the seven flagged terms against the notes before citing it. The lesson: report what a metric measures, not just what it is called.")

# 21 Hypotheses + engineering
s = new_slide("Hypotheses and engineering review")
rows = [["H", "Claim", "Outcome"], ["H1", "v2 beats v1", "Supported on format, not recall"], ["H2", "v3 beats v2", "Not supported"],
        ["H3", "v4 beats v3", "Mixed: coverage up, flags up, 3x calls"], ["H5", "Length guard fixes limits", "Not testable on packs; passes test 7"]]
table(s, 0.7, 1.6, 6.2, rows, [0.5, 2.2, 3.5], 16, 0.85)
text(s, 7.2, 1.55, 5.5, 0.4, "Observations from code review", 18, NAVY, True, check=False)
text(s, 7.2, 2.05, 5.5, 4.7, ["Moderator failure keeps candidates unverified (fail-open); the quote guard still applies.", "Guard checks quote existence only; no minimum length.", "Local server is single-threaded; Vercel is unaffected.", "Default provider is “anthropic” in code while the docs say Gemini; design diagram outdated.", "Public endpoints have no rate limit; /api/diag calls the model."], 16.5, INK, bullets=True, space=8)
notes(s, "Hypotheses were written in October before any live run and re-tested here. H4 on human scoring is deferred to Milestone 3.")

# 22 Limitations
s = new_slide("Limitations and future work")
card(s, 0.7, 1.55, 5.9, 5.2, "Limitations", ["One run, one model, nine CS notes written by the team that also wrote the gold labels.", "Lenient recall matching; word-overlap answer support.", "No human scoring yet.", "Fixed pack size: poor on long notes.", "Free-tier quota limits repeated runs."], size=19, bullets=True, accent=RED)
card(s, 6.85, 1.55, 5.8, 5.2, "Next steps", ["Fix padding: cap N, content gate, mandatory warning.", "Raise recall: ask for every defined term; scale the pack with note length; one-to-one fuzzy scoring.", "Human rubric: two raters, five criteria, 1 to 5.", "≥ 3 runs per version; compare other models.", "Semantic support check (entailment) beyond substring."], size=19, bullets=True, accent="2E7D32")
notes(s, "These map one-to-one to the failures and audit findings. Human evaluation uses the rubric already written in docs/human_eval_rubric.md.")

# 23 Conclusion
s = new_slide("Conclusion")
cs = ["**Prompt structure plus code-side checks**, not a larger model, make generated study material verifiable.",
      "Role + schema + quotes fixed format (**0/9 → 9/9**) and answer support (**0.725 → 0.956**).",
      "The chain added coverage (**+19%**) and removed ungrounded questions, at **3x the calls**.",
      "Audit: flagged terms were naming variants, the answer-support dip was a scoring artifact, recall is capped by list length.",
      "Open items: padding thin or non-lecture input; recall on long notes."]
for i, c_ in enumerate(cs):
    y = 1.55 + i * 0.88
    chip(s, 0.8, y + 0.08, 0.5, 0.5, str(i + 1), TEAL, "FFFFFF", 17)
    text(s, 1.5, y, 11.1, 0.8, c_, 17.5, INK, anchor=MSO_ANCHOR.MIDDLE)
rect(s, 0.7, 6.05, 11.95, 0.75, NAVY, None, MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.15)
text(s, 0.9, 6.1, 11.6, 0.65, "Prototype: smartstudy-ai-swart.vercel.app   ·   Code: github.com/Darsh-Jasoria/SmartStudy-AI", 17, "FFFFFF", True, PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "Close on the takeaway: design the workflow so that the checkable parts are checked by code, and audit your own metrics.")

# 24 References
s = new_slide("Selected references")
refs = ["T. B. Brown et al., “Language models are few-shot learners,” NeurIPS, 2020.", "J. Wei et al., “Chain-of-thought prompting elicits reasoning in large language models,” NeurIPS, 2022.",
        "T. Wu, M. Terry, C. J. Cai, “AI Chains: chaining large language model prompts,” CHI, 2022.", "P. Lewis et al., “Retrieval-augmented generation for knowledge-intensive NLP tasks,” NeurIPS, 2020.",
        "J. Maynez et al., “On faithfulness and factuality in abstractive summarization,” ACL, 2020.", "Z. Ji et al., “Survey of hallucination in natural language generation,” ACM Comput. Surv., 2023.",
        "S. Dhuliawala et al., “Chain-of-verification reduces hallucination in LLMs,” arXiv:2309.11495, 2023.", "L. Zheng et al., “Judging LLM-as-a-judge with MT-Bench and Chatbot Arena,” NeurIPS D&B, 2023.",
        "F. Perez and I. Ribeiro, “Ignore previous prompt: attack techniques for language models,” arXiv:2211.09527, 2022.", "E. Kasneci et al., “ChatGPT for good? LLMs for education,” Learn. Individual Differences, 2023."]
text(s, 0.7, 1.5, 11.95, 5.4, [f"[{i}] {r}" for i, r in enumerate(refs, 1)], 15.5, INK, space=9)
notes(s, "The full reference list is in the IEEE report.")

# 25 Q&A
s = prs.slides.add_slide(BLANK); SLIDE_NO[0] += 1
rect(s, 0, 0, 13.333, 7.5, NAVY); rect(s, 0, 4.2, 13.333, 0.06, TEAL)
text(s, 0.8, 2.0, 11.7, 1.2, "Thank you", 54, "FFFFFF", True, PP_ALIGN.CENTER, check=False)
text(s, 0.8, 3.2, 11.7, 0.8, "Questions?", 28, "C9D6E3", False, PP_ALIGN.CENTER, check=False)
text(s, 0.8, 4.6, 11.7, 0.5, "Team IntelliCore (PE-B37-17)  ·  Bennett University", 18, "FFFFFF", False, PP_ALIGN.CENTER, check=False)
text(s, 0.8, 5.15, 11.7, 0.5, "smartstudy-ai-swart.vercel.app   ·   github.com/Darsh-Jasoria/SmartStudy-AI", 15, "9FB6CC", False, PP_ALIGN.CENTER, check=False)
notes(s, "Open for questions. Likely ones: why Gemini Flash-Lite; why the moderator rejected nothing; how the audit was done; what changes for Milestone 3.")

out = OUT / "presentation" / "SmartStudy_Presentation.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides))
for w in WARN: print("WARN", w)

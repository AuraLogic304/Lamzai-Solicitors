"""
Generates a professional A4 letterhead DOCX for Lamzai Solicitors.
Run:  python generate_letterhead.py
Output: LetterHead.docx  (overwrites existing file)
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ── Brand colours ──────────────────────────────────────────────────────────────
NAVY  = RGBColor(0x0D, 0x1F, 0x3C)
GOLD  = RGBColor(0xC9, 0xA8, 0x4C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY  = RGBColor(0x6B, 0x72, 0x80)
DARK  = RGBColor(0x37, 0x41, 0x51)

# ── Company details ────────────────────────────────────────────────────────────
COMPANY   = "Lamzai Solicitors"
TAGLINE   = "Expert Legal Advice & Representation"
PHONE     = "0208 080 3737"
EMAIL     = "enquiries@lamzaisolicitors.co.uk"
ADDRESS1  = "Jhumat House, 160 London Road"
ADDRESS2  = "Barking  IG11 8BB"
WEBSITE   = "www.lamzaisolicitors.co.uk"
SRA_NOTE  = "Authorised and regulated by the Solicitors Regulation Authority"

LOGO_PATH = os.path.join(os.path.dirname(__file__), "Logo.png")

# ── Helpers ────────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color: str):
    """Fill a table cell with a solid background colour (hex like '0D1F3C')."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def set_cell_margins(cell, top=0, start=80, bottom=0, end=80):
    """Set cell internal margins (twips)."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for side, val in (('top', top), ('start', start), ('bottom', bottom), ('end', end)):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:w'), str(val))
        el.set(qn('w:type'), 'dxa')
        tcMar.append(el)
    tcPr.append(tcMar)


def remove_cell_borders(tbl):
    """Remove all internal/external borders from a table."""
    tblPr = tbl._tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl._tbl.insert(0, tblPr)
    tblBorders = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'none')
        el.set(qn('w:sz'), '0')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), 'auto')
        tblBorders.append(el)
    tblPr.append(tblBorders)


def add_paragraph_border(paragraph, position='bottom', color='C9A84C', sz='6', space='1'):
    """Add a border to a paragraph (bottom rule)."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    el = OxmlElement(f'w:{position}')
    el.set(qn('w:val'), 'single')
    el.set(qn('w:sz'), sz)
    el.set(qn('w:space'), space)
    el.set(qn('w:color'), color)
    pBdr.append(el)
    pPr.append(pBdr)


def set_para_spacing(para, before=0, after=0, line=None):
    pPr = para._p.get_or_add_pPr()
    pSpc = OxmlElement('w:spacing')
    pSpc.set(qn('w:before'), str(before))
    pSpc.set(qn('w:after'), str(after))
    if line:
        pSpc.set(qn('w:line'), str(line))
        pSpc.set(qn('w:lineRule'), 'exact')
    pPr.append(pSpc)


def add_run(para, text, bold=False, italic=False, font_size=10,
            font_name='DM Sans', color=None, all_caps=False):
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(font_size)
    run.font.name = font_name
    if color:
        run.font.color.rgb = color
    if all_caps:
        run.font.all_caps = True
    # Fallback font for rPr
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rPr.insert(0, rFonts)
    return run


def add_field(para, field_type='DATE'):
    """Insert a DOCX field (e.g. date field)."""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = f' {field_type} \\@ "d MMMM yyyy" '
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    r = para.add_run()
    r._r.append(fldChar1)
    r._r.append(instrText)
    r._r.append(fldChar2)
    r._r.append(fldChar3)


# ── Document setup ─────────────────────────────────────────────────────────────

doc = Document()
section = doc.sections[0]

# A4 page size
section.page_width  = Cm(21.0)
section.page_height = Cm(29.7)

# Generous but professional margins
section.top_margin    = Cm(0.7)
section.bottom_margin = Cm(1.5)
section.left_margin   = Cm(2.2)
section.right_margin  = Cm(1.8)

# Remove default paragraph spacing from Normal style
doc.styles['Normal'].paragraph_format.space_before = Pt(0)
doc.styles['Normal'].paragraph_format.space_after  = Pt(0)

# ══ HEADER ════════════════════════════════════════════════════════════════════
header = section.header
header.is_linked_to_previous = False

# Clear default empty paragraph
for p in header.paragraphs:
    p._element.getparent().remove(p._element)

# Left accent bar via a full-width table with a thin navy left cell
# (Word doesn't support CSS-style borders per-page; we simulate with a table row)

# ── Header table: [logo+name] | [spacer] | [contact] ────────────────────────
hdr_tbl = header.add_table(rows=1, cols=3, width=Inches(6.5))
hdr_tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
remove_cell_borders(hdr_tbl)

hdr_tbl.columns[0].width = Cm(9.5)   # logo + company name
hdr_tbl.columns[1].width = Cm(0.5)   # spacer
hdr_tbl.columns[2].width = Cm(7.0)   # contact details

logo_cell    = hdr_tbl.cell(0, 0)
spacer_cell  = hdr_tbl.cell(0, 1)
contact_cell = hdr_tbl.cell(0, 2)

logo_cell.vertical_alignment    = WD_ALIGN_VERTICAL.TOP
contact_cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP

set_cell_margins(logo_cell,    top=100, start=0,   bottom=80, end=80)
set_cell_margins(contact_cell, top=100, start=80,  bottom=80, end=0)

# ── Logo image ──
logo_para = logo_cell.paragraphs[0]
logo_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
set_para_spacing(logo_para, before=0, after=60)

if os.path.exists(LOGO_PATH):
    run_logo = logo_para.add_run()
    run_logo.add_picture(LOGO_PATH, height=Cm(1.6))
else:
    # Fallback: styled text monogram
    add_run(logo_para, "LS", bold=True, font_size=28,
            font_name='Cormorant Garamond', color=NAVY)

# ── Company name & tagline ──
name_para = logo_cell.add_paragraph()
set_para_spacing(name_para, before=0, after=0)
add_run(name_para, COMPANY, bold=False, font_size=20,
        font_name='Cormorant Garamond', color=NAVY)

tag_para = logo_cell.add_paragraph()
set_para_spacing(tag_para, before=30, after=0)
add_run(tag_para, TAGLINE.upper(), bold=False, font_size=6.5,
        font_name='DM Sans', color=GOLD, all_caps=False)

# ── Contact details (right cell) ──
contact_items = [
    ("☎  ", PHONE),
    ("✉  ", EMAIL),
    ("⌂  ", f"{ADDRESS1}, {ADDRESS2}"),
    ("⌐  ", WEBSITE),
]

for i, (icon, text) in enumerate(contact_items):
    p = contact_cell.paragraphs[0] if i == 0 else contact_cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_para_spacing(p, before=0, after=55)
    add_run(p, icon, font_size=8, font_name='DM Sans', color=GOLD)
    add_run(p, text, font_size=8, font_name='DM Sans', color=DARK)

# ── Gold rule under header ──
rule_para = header.add_paragraph()
set_para_spacing(rule_para, before=80, after=0)
add_paragraph_border(rule_para, 'bottom', color='C9A84C', sz='8', space='1')

# thin secondary rule
rule2 = header.add_paragraph()
set_para_spacing(rule2, before=20, after=80)
add_paragraph_border(rule2, 'bottom', color='C9A84C', sz='2', space='1')

# ══ FOOTER ════════════════════════════════════════════════════════════════════
footer = section.footer
footer.is_linked_to_previous = False

for p in footer.paragraphs:
    p._element.getparent().remove(p._element)

# Top rule (navy)
top_rule = footer.add_paragraph()
set_para_spacing(top_rule, before=0, after=0)
add_paragraph_border(top_rule, 'top', color='0D1F3C', sz='12', space='1')

# Footer table — navy background: [brand] | [div] | [address+phone] | [div] | [email+web] | [div] | [disclaimer]
ftbl = footer.add_table(rows=1, cols=7, width=Inches(6.5))
ftbl.alignment = WD_TABLE_ALIGNMENT.LEFT
remove_cell_borders(ftbl)

col_widths = [Cm(2.2), Cm(0.3), Cm(4.5), Cm(0.3), Cm(4.5), Cm(0.3), Cm(5.1)]
for i, w in enumerate(col_widths):
    ftbl.columns[i].width = w

# Fill all cells navy
for ci in range(7):
    cell = ftbl.cell(0, ci)
    set_cell_bg(cell, '0D1F3C')
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_margins(cell, top=120, start=100, bottom=120, end=100)

# Divider cells (thinner margins)
for di in [1, 3, 5]:
    set_cell_margins(ftbl.cell(0, di), top=80, start=0, bottom=80, end=0)

# ── Brand cell ──
brand_cell = ftbl.cell(0, 0)
bp = brand_cell.paragraphs[0]
bp.alignment = WD_ALIGN_PARAGRAPH.LEFT
set_para_spacing(bp, before=0, after=30)
add_run(bp, COMPANY, bold=True, font_size=9,
        font_name='Cormorant Garamond', color=GOLD)

bp2 = brand_cell.add_paragraph()
set_para_spacing(bp2, before=0, after=0)
add_run(bp2, "Regulated by the SRA", font_size=6.5,
        font_name='DM Sans', color=WHITE)

# ── Dividers ──
for di in [1, 3, 5]:
    dp = ftbl.cell(0, di).paragraphs[0]
    add_run(dp, "│", font_size=12, font_name='DM Sans', color=GOLD)
    dp.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ── Address + phone ──
addr_cell = ftbl.cell(0, 2)
ap = addr_cell.paragraphs[0]
set_para_spacing(ap, before=0, after=30)
add_run(ap, "📍 " if False else "▸ ", font_size=7.5, font_name='DM Sans', color=GOLD)
add_run(ap, f"{ADDRESS1}, {ADDRESS2}", font_size=7.5, font_name='DM Sans', color=WHITE)

ap2 = addr_cell.add_paragraph()
set_para_spacing(ap2, before=0, after=0)
add_run(ap2, "▸ ", font_size=7.5, font_name='DM Sans', color=GOLD)
add_run(ap2, PHONE, font_size=7.5, font_name='DM Sans', color=WHITE)

# ── Email + website ──
ew_cell = ftbl.cell(0, 4)
ep = ew_cell.paragraphs[0]
set_para_spacing(ep, before=0, after=30)
add_run(ep, "▸ ", font_size=7.5, font_name='DM Sans', color=GOLD)
add_run(ep, EMAIL, font_size=7.5, font_name='DM Sans', color=WHITE)

ep2 = ew_cell.add_paragraph()
set_para_spacing(ep2, before=0, after=0)
add_run(ep2, "▸ ", font_size=7.5, font_name='DM Sans', color=GOLD)
add_run(ep2, WEBSITE, font_size=7.5, font_name='DM Sans', color=WHITE)

# ── Disclaimer ──
disc_cell = ftbl.cell(0, 6)
disc_p = disc_cell.paragraphs[0]
disc_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
set_para_spacing(disc_p, before=0, after=0)
add_run(disc_p,
        "This communication is confidential and intended solely for the named recipient(s). "
        "Lamzai Solicitors is authorised and regulated by the Solicitors Regulation Authority.",
        font_size=5.5, font_name='DM Sans', color=RGBColor(0xB0, 0xB8, 0xC8))

# ══ BODY — Reference / date fields ═══════════════════════════════════════════

# Ref table
ref_tbl = doc.add_table(rows=1, cols=3)
ref_tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
remove_cell_borders(ref_tbl)
ref_tbl.columns[0].width = Cm(5.5)
ref_tbl.columns[1].width = Cm(5.5)
ref_tbl.columns[2].width = Cm(5.7)

for ci, (label, field) in enumerate([
    ("Date", "DATE"),
    ("Our Ref", None),
    ("Your Ref", None),
]):
    cell = ref_tbl.cell(0, ci)
    set_cell_margins(cell, top=0, start=0, bottom=0, end=200)

    lp = cell.paragraphs[0]
    lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_para_spacing(lp, before=0, after=40)
    add_run(lp, label.upper(), font_size=7, font_name='DM Sans',
            color=GOLD, all_caps=False)

    vp = cell.add_paragraph()
    vp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_para_spacing(vp, before=0, after=120)
    add_paragraph_border(vp, 'bottom', color='C9A84C', sz='4', space='1')
    if field == "DATE":
        add_field(vp, 'DATE')
    else:
        add_run(vp, " ", font_size=10, font_name='DM Sans', color=DARK)

# Spacer
sp = doc.add_paragraph()
set_para_spacing(sp, before=0, after=200)

# ── Addressee block ──
for line in ["[Recipient Name]", "[Company / Organisation]",
             "[Address Line 1]", "[Address Line 2]", "[City, Postcode]"]:
    ap = doc.add_paragraph()
    set_para_spacing(ap, before=0, after=40)
    add_run(ap, line, font_size=10.5, font_name='DM Sans',
            color=RGBColor(0xC0, 0xC0, 0xC0), italic=True)

sp2 = doc.add_paragraph()
set_para_spacing(sp2, before=0, after=160)

# ── Subject line ──
subj_label = doc.add_paragraph()
set_para_spacing(subj_label, before=0, after=40)
add_run(subj_label, "RE: ", font_size=7, font_name='DM Sans', color=GOLD)

subj_val = doc.add_paragraph()
set_para_spacing(subj_val, before=0, after=240)
add_paragraph_border(subj_val, 'bottom', color='C9A84C', sz='4', space='1')
add_run(subj_val, " ", font_size=10.5, font_name='DM Sans', color=DARK)

# ── Salutation ──
salute = doc.add_paragraph()
set_para_spacing(salute, before=0, after=240)
add_run(salute, "Dear Sir / Madam,", font_size=10.5,
        font_name='DM Sans', color=DARK)

# ── Body text placeholder ──
body_p = doc.add_paragraph()
set_para_spacing(body_p, before=0, after=80)
add_run(body_p,
        "[Begin your letter here. This template uses Cormorant Garamond for headings "
        "and DM Sans for body text, matching the Lamzai Solicitors brand.]",
        italic=True, font_size=10.5, font_name='DM Sans',
        color=RGBColor(0xC0, 0xC0, 0xC0))

# Extra body lines
for _ in range(6):
    ep = doc.add_paragraph()
    set_para_spacing(ep, before=0, after=240)
    add_run(ep, " ", font_size=10.5, font_name='DM Sans', color=DARK)

# ── Closing ──
close = doc.add_paragraph()
set_para_spacing(close, before=0, after=500)
add_run(close, "Yours faithfully,", font_size=10.5,
        font_name='DM Sans', color=DARK)

# Signature line
sig_line = doc.add_paragraph()
set_para_spacing(sig_line, before=0, after=60)
add_paragraph_border(sig_line, 'bottom', color='C9A84C', sz='4', space='1')
add_run(sig_line, "                                        ",
        font_size=10.5, font_name='DM Sans', color=DARK)

sig_name = doc.add_paragraph()
set_para_spacing(sig_name, before=60, after=40)
add_run(sig_name, "[Solicitor Name & Position]",
        italic=True, font_size=10, font_name='DM Sans',
        color=RGBColor(0xC0, 0xC0, 0xC0))

sig_co = doc.add_paragraph()
set_para_spacing(sig_co, before=0, after=0)
add_run(sig_co, COMPANY, bold=False, font_size=10,
        font_name='Cormorant Garamond', color=NAVY)

# ── Save ──────────────────────────────────────────────────────────────────────
output = os.path.join(os.path.dirname(__file__), "LetterHead.docx")
doc.save(output)
print(f"Done. Saved: {output}")

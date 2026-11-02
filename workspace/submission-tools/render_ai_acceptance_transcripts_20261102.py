#!/usr/bin/env python3
"""Render the two retained Markdown guides as Unicode A4 PDFs with navigation.

Dependencies: reportlab, mistune 3, PyMuPDF and Pillow.
Use the existing presentation environment, or install these in a virtualenv.
"""
import hashlib
import html
import json
import re
from io import BytesIO
from ai_release_context import review_path, part_prefix
import os
from pathlib import Path
from urllib.parse import unquote

import fitz
import mistune
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, PageBreak, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

WORKSPACE = Path(__file__).resolve().parents[1]
REPORT = WORKSPACE / 'reports/ai-final-report-20261030'
FONT_DIR = Path('/usr/share/fonts/dejavu-sans-fonts')
INK = colors.HexColor('#23373B')
ORANGE = colors.HexColor('#EB811B')
GRAY = colors.HexColor('#626E72')
WIDTH = A4[0] - 34 * mm
PARSER = mistune.create_markdown(renderer='ast', plugins=['table', 'strikethrough'])

for name, file in [('Guide', 'DejaVuSans.ttf'), ('Guide-Bold', 'DejaVuSans-Bold.ttf'),
                   ('Guide-Italic', 'DejaVuSans-Oblique.ttf'),
                   ('Guide-BoldItalic', 'DejaVuSans-BoldOblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
pdfmetrics.registerFontFamily('Guide', normal='Guide', bold='Guide-Bold',
                              italic='Guide-Italic', boldItalic='Guide-BoldItalic')

STYLES = {
    'body': ParagraphStyle('body', fontName='Guide', fontSize=9.8, leading=14,
                           textColor=INK, spaceAfter=7, splitLongWords=True),
    'title': ParagraphStyle('title', fontName='Guide-Bold', fontSize=21, leading=28,
                            textColor=INK, spaceAfter=17, keepWithNext=True),
    'h2': ParagraphStyle('h2', fontName='Guide-Bold', fontSize=16, leading=22,
                         textColor=INK, spaceBefore=12, spaceAfter=10, keepWithNext=True),
    'h3': ParagraphStyle('h3', fontName='Guide-Bold', fontSize=11, leading=16,
                         textColor=INK, spaceBefore=9, spaceAfter=5, keepWithNext=True),
    'hardware': ParagraphStyle('hardware', fontName='Guide', fontSize=9.2, leading=13,
                               textColor=INK, spaceAfter=10, keepWithNext=True),
    'brief': ParagraphStyle('brief', fontName='Guide', fontSize=10.2, leading=15,
                            textColor=INK, backColor=colors.HexColor('#FFF4E9'),
                            borderColor=ORANGE, borderWidth=0.6, borderPadding=8,
                            spaceBefore=5, spaceAfter=13),
    'cell': ParagraphStyle('cell', fontName='Guide', fontSize=8.7, leading=12.5,
                           textColor=INK, spaceAfter=0),
    'headcell': ParagraphStyle('headcell', fontName='Guide-Bold', fontSize=8.8,
                               leading=13, textColor=colors.white),
}
STYLES['bullet'] = ParagraphStyle('bullet', parent=STYLES['body'], leftIndent=11,
                                 bulletIndent=0, spaceAfter=5)


def inline(nodes):
    result = []
    for node in nodes:
        kind = node['type']
        if kind in ['text', 'codespan']:
            value = html.escape(node.get('raw', ''))
            result.append(f'<font color="#375C6A">{value}</font>' if kind == 'codespan' else value)
        elif kind in ['softbreak', 'linebreak']:
            result.append(' ' if kind == 'softbreak' else '<br/>')
        elif kind in ['strong', 'emphasis', 'strikethrough']:
            tag = {'strong': 'b', 'emphasis': 'i', 'strikethrough': 'strike'}[kind]
            result.append(f'<{tag}>{inline(node["children"])}</{tag}>')
        elif kind == 'link':
            url = node['attrs']['url']
            # A sibling language link should open the portable PDF counterpart.
            if url in ['TRANSCRIPT_VI.md', 'TRANSCRIPT_EN.md']:
                url = url[:-3] + '.pdf'
            result.append(f'<link href="{html.escape(url, quote=True)}" color="#375C6A">'
                          f'{inline(node["children"])}</link>')
        elif kind == 'inline_html':
            # The Markdown's slide anchor is created on the heading instead.
            if not re.fullmatch(r'</?a\b[^>]*>', node.get('raw', '')):
                raise ValueError(f'Unhandled inline HTML: {node}')
        else:
            raise ValueError(f'Unhandled inline node: {kind}')
    return ''.join(result)


class GuideDocument(BaseDocTemplate):
    def __init__(self, target, lang):
        super().__init__(str(target), pagesize=A4, leftMargin=17*mm, rightMargin=17*mm,
                         topMargin=18*mm, bottomMargin=17*mm,
                         title=f'TripleU — slide transcript ({lang})',
                         author='VNUHCM - TripleU')
        self.lang = lang
        self.section = 'TripleU / APAC HPC-AI 2026'
        self.slide_pages = {}
        self.addPageTemplates(PageTemplate('guide', frames=[Frame(
            self.leftMargin, self.bottomMargin, self.width, self.height,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
            onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(ORANGE)
        canvas.setLineWidth(1)
        canvas.line(17*mm, A4[1]-12*mm, A4[0]-17*mm, A4[1]-12*mm)
        canvas.setFont('Guide', 7.4)
        canvas.setFillColor(GRAY)
        title = f'TripleU / APAC HPC-AI 2026 · {self.lang} transcript'
        while pdfmetrics.stringWidth(title, 'Guide', 7.4) > WIDTH - 30:
            title = title[:-2]
        canvas.drawString(17*mm, A4[1]-10*mm, title)
        canvas.drawString(17*mm, 10*mm, f'TripleU · {self.lang} · Transcript')
        canvas.drawRightString(A4[0]-17*mm, 10*mm, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, item):
        if not getattr(item, '_outline_key', None):
            return
        self.canv.bookmarkPage(item._outline_key)
        self.canv.addOutlineEntry(item.getPlainText(), item._outline_key,
                                 level=item._outline_level, closed=False)
        self.section = item.getPlainText()
        if item._outline_key.startswith('slide-'):
            self.slide_pages[int(item._outline_key[6:])] = self.page


def render(source, target, lang):
    nodes = PARSER(source.read_text())
    story = []
    state = {'brief': False, 'section': 0, 'images': 0, 'slides': []}

    def blocks(items, bullet=False):
        for node in items:
            kind = node['type']
            if kind in ['blank_line', 'thematic_break']:
                continue
            if kind == 'heading':
                text = inline(node['children'])
                plain = re.sub('<[^>]+>', '', html.unescape(text))
                level = node['attrs']['level']
                slide = re.match(r'Slide (\d{2}) —', plain)
                if slide:
                    story.append(PageBreak())
                    state['slides'].append(int(slide.group(1)))
                style = STYLES['title' if level == 1 else 'h2' if level == 2 else 'h3']
                paragraph = Paragraph(text, style)
                if level <= 2:
                    state['section'] += 1
                    paragraph._outline_key = f'slide-{slide.group(1)}' if slide else f'section-{state["section"]}'
                    paragraph._outline_level = 0 if level == 1 else 1
                state['brief'] = plain.startswith(('Nói nhanh', 'Quick brief'))
                story.append(paragraph)
            elif kind in ['paragraph', 'block_text']:
                images = [c for c in node['children'] if c['type'] == 'image']
                if images:
                    assert len(images) == len(node['children']) == 1
                    path = (source.parent / unquote(images[0]['attrs']['url'])).resolve()
                    with PILImage.open(path) as picture:
                        width, height = picture.size
                        # Re-encode only the embedded copy; retain original slide assets.
                        rgba = picture.convert('RGBA')
                        rgb = PILImage.new('RGB', picture.size, 'white')
                        rgb.paste(rgba, mask=rgba.getchannel('A'))
                        buffer = BytesIO()
                        rgb.save(buffer, format='JPEG', quality=90, subsampling=0)
                        buffer.seek(0)
                    picture = Image(buffer, width=WIDTH, height=WIDTH * height / width)
                    picture.hAlign = 'LEFT'
                    story.extend([picture, Spacer(1, 10)])
                    state['images'] += 1
                    continue
                text = inline(node['children'])
                if not text.strip():
                    continue
                hardware = text.startswith(('<b>Phần cứng:', '<b>Hardware:'))
                style = STYLES['brief' if state['brief'] else 'hardware' if hardware else 'bullet' if bullet else 'body']
                story.append(Paragraph(text, style, bulletText='•' if bullet else None))
                state['brief'] = False
            elif kind == 'list':
                for item in node['children']:
                    blocks(item['children'], bullet=True)
            elif kind == 'table':
                rows = []
                for part in node['children']:
                    children = [part] if part['type'] == 'table_head' else part['children']
                    for row in children:
                        style = STYLES['headcell' if part['type'] == 'table_head' else 'cell']
                        rows.append([Paragraph(inline(c['children']), style) for c in row['children']])
                assert all(len(row) == 2 for row in rows)
                table = Table(rows, colWidths=[WIDTH*.29, WIDTH*.71], repeatRows=1, hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), INK),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F0F3F3')]),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 7),
                    ('RIGHTPADDING', (0,0), (-1,-1), 7),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.extend([table, Spacer(1, 10)])
            else:
                raise ValueError(f'Unhandled block node: {kind}')

    blocks(nodes)
    assert state['slides'] == list(range(1, 43)) and state['images'] == 42
    doc = GuideDocument(target, lang)
    doc.build(story)
    return doc.slide_pages


def check_pdf(path, source, pages):
    document = fitz.open(path)
    all_text = '\n'.join(p.get_text() for p in document)
    normalized = ' '.join(all_text.split())
    assert '\ufffd' not in all_text
    assert len(pages) == 42
    assert all(len(p.get_text().strip()) > 30 for p in document), 'Blank page'
    for n, page in pages.items():
        assert f'Slide {n:02d}' in document[page-1].get_text()
    records = json.loads((REPORT / 'investigation-transcript.json').read_text())
    lang = 'vi' if '_VI' in path.name else 'en'
    for record in records:
        brief = ' '.join(record[lang]['brief'].split())
        assert brief in normalized, f'Missing brief in {path.name}, slide {record["slide"]}'
    assert sum(len(page.get_images()) for page in document) >= 42
    destinations = set()
    for page in document:
        for link in page.get_links():
            if link['kind'] == fitz.LINK_GOTO:
                destinations.add(link['page'])
            elif link['kind'] == fitz.LINK_NAMED and str(link.get('page', '')).isdigit():
                # PyMuPDF represents ReportLab's /Fit targets as one-based named pages.
                destinations.add(int(link['page'])-1)
    assert all(page-1 in destinations for page in pages.values()), 'Missing TOC destination'
    fonts = {row[0] for page in document for row in page.get_fonts() if 'DejaVu' in row[3]}
    assert fonts and all(document.extract_font(xref)[3] for xref in fonts), 'Font not embedded'
    # Check body text stays within the physical page, allowing fractional rounding.
    for page in document:
        for block in page.get_text('dict')['blocks']:
            if block['type'] == 0:
                x0, y0, x1, y1 = block['bbox']
                assert x0 >= -1 and y0 >= -1 and x1 <= page.rect.width+1 and y1 <= page.rect.height+1
    return dict(file=path.name, pages=len(document), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                markdown_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                slide_start_pages={str(n): p for n,p in sorted(pages.items())},
                checks=['42 slide sections and images', '42 complete briefs present in extracted text',
                        'Vietnamese font embedded and extractable', 'No blank pages or text outside page',
                        '42 clickable table-of-contents destinations', 'PDF outline bookmarks'])


def main():
    # Fail before replacing any PDF when the two teaching sources are out of sync.
    records = json.loads((REPORT / 'investigation-transcript.json').read_text())
    for lang in ['VI', 'EN']:
        body = ' '.join((REPORT / f'TRANSCRIPT_{lang}.md').read_text().split())
        for record in records:
            assert ' '.join(record[lang.lower()]['brief'].split()) in body, \
                f'Stale Markdown before PDF render: {lang}, slide {record["slide"]}'
    results = []
    for lang in ['VI', 'EN']:
        source = REPORT / f'TRANSCRIPT_{lang}.md'
        target = source.with_suffix('.pdf')
        pages = render(source, target, lang)
        results.append(check_pdf(target, source, pages))
    report = dict(passed=True, format='A4 portrait; embedded DejaVu Sans; linked navigation',
                  source='Current Markdown files, without changing their scientific content',
                  dependencies={'mistune': mistune.__version__, 'PyMuPDF': fitz.VersionBind},
                  outputs=results)
    (REPORT / 'transcript-pdf-validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

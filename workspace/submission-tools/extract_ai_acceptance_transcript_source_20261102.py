#!/usr/bin/env python3
"""Bind the teaching guides to logical slide order and refresh preserved HPC previews."""
from pathlib import Path
import hashlib
import json

import fitz
from PIL import Image, ImageDraw
from pptx import Presentation

WORKSPACE = Path(__file__).resolve().parents[1]
STAGE = WORKSPACE / 'submission-review/ai-acceptance-update-20261102'
REPORT = WORKSPACE / 'reports/ai-final-report-20261030'
DECK = STAGE / 'TripleU_APAC2026_Presentation.pptx'
slides = [
    {
        'slide': index,
        'texts': [shape.text for shape in slide.shapes if shape.has_text_frame],
        'notes': slide.notes_slide.notes_text_frame.text,
    }
    for index, slide in enumerate(Presentation(DECK).slides, 1)
]
assert len(slides) == 42
(REPORT / 'transcript-slide-source.json').write_text(json.dumps({
    'presentation_sha256': hashlib.sha256(DECK.read_bytes()).hexdigest(),
    'review_directory': str(STAGE),
    'slides': slides,
}, ensure_ascii=False, indent=2) + '\n')
with fitz.open(STAGE / 'TripleU_APAC2026_Presentation.pdf') as document:
    for index in range(34, 42):
        document[index].get_pixmap(matrix=fitz.Matrix(1.25, 1.25)).save(
            REPORT / f'transcript-assets/slide-{index + 1:02d}.png')
    sheet = Image.new('RGB', (1920, 600), '#e0e6e7')
    draw = ImageDraw.Draw(sheet)
    for position, index in enumerate([2, 3, 5, 7, 8, 13, 15, 33]):
        pixmap = document[index].get_pixmap(matrix=fitz.Matrix(.6, .6))
        preview = Image.frombytes('RGB', [pixmap.width, pixmap.height], pixmap.samples)
        preview.thumbnail((470, 265))
        x, y = (position % 4) * 480, (position // 4) * 300
        sheet.paste(preview, (x, y))
        draw.text((x + 10, y + 275), f'Slide {index + 1:02d}', fill='#23373b')
    sheet.save(STAGE / 'reasoning-review-contact.png')
print('42 logical source records, eight HPC guide previews and review contact sheet generated.')

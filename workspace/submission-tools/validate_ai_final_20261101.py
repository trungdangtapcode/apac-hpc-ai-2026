#!/usr/bin/env python3
"""Check the final AI edition, its source-bound guides and the explicit package selection."""
from pathlib import Path
from urllib.parse import unquote
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import re
import zipfile

import fitz
from pptx import Presentation

parser = argparse.ArgumentParser()
parser.add_argument('--published', action='store_true')
args = parser.parse_args()
W = Path(__file__).resolve().parents[1]
O = W / 'submission-review/ai-final-update-20261101'
R = W / 'reports/ai-final-report-20261030'
T = W / 'VNUHCM - TripleU'
sha = lambda value: hashlib.sha256(value).hexdigest()
plan = json.loads((O / 'reasoning-plan.json').read_text())
records = json.loads((R / 'investigation-transcript.json').read_text())
source = json.loads((R / 'transcript-slide-source.json').read_text())
deck = O / 'TripleU_APAC2026_Presentation.pptx'
identity = sha(deck.read_bytes())
assert identity == source['presentation_sha256']
presentation = Presentation(deck)
assert len(presentation.slides) == len(records) == 42
visible = []
for index, slide in enumerate(presentation.slides, 1):
    if slide._element.get('show') != '0':
        visible.append(index)
    if index <= 34:
        texts = [' '.join(shape.text.split()) for shape in slide.shapes if shape.has_text_frame]
        assert plan['slides'][index - 1]['title'] in texts
        assert records[index - 1]['title'] in texts
        assert records[index - 1]['en']['brief'] in slide.notes_slide.notes_text_frame.text
        assert not re.search('[ăâđêôơưĂÂĐÊÔƠƯ]', '\n'.join(texts))
assert visible == list(range(1, 17)) + list(range(35, 43))
with fitz.open(O / 'TripleU_APAC2026_Presentation.pdf') as full, fitz.open(O / 'TripleU_APAC2026_Main_Talk.pdf') as main:
    assert len(full) == 42 and len(main) == 24
    for page, number in zip(main, visible):
        original = full[number - 1]
        assert page.get_text() == original.get_text()
        assert page.get_pixmap(matrix=fitz.Matrix(.5, .5)).samples == original.get_pixmap(matrix=fitz.Matrix(.5, .5)).samples
snapshot = json.loads((O / 'HPC_BEFORE.json').read_text())
with zipfile.ZipFile(deck) as archive:
    for name, digest in snapshot['presentation']['hpc_dependency_closure_parts'].items():
        assert sha(archive.read(name)) == digest
pdf_validation = json.loads((R / 'transcript-pdf-validation.json').read_text())
for output in pdf_validation['outputs']:
    assert sha((R / output['file']).read_bytes()) == output['sha256']
    assert sha((R / Path(output['file']).with_suffix('.md')).read_bytes()) == output['markdown_sha256']
assert json.loads((R / 'transcript-validation.json').read_text())['deck_sha256'] == identity
files = json.loads((O / 'package-file-map.json').read_text())
assert all(name.startswith('AI_Task/logs/') and 'AI_Task/logs/AI_Task' not in name for name in files)
for name, path in files.items():
    assert Path(path).is_file() and (O / 'package-files') in Path(path).parents
manifest = json.loads(Path(files['AI_Task/logs/research-20261101/source-manifest.json']).read_text())
compressed = 0
for entry in manifest['entries']:
    data = Path(files[entry['path']]).read_bytes()
    assert len(data) == entry['bytes'] and sha(data) == entry['sha256']
    if entry['path'].endswith('profile_export.jsonl.gz'):
        assert sha(gzip.decompress(data)) == entry['source_sha256']
        compressed += 1
assert compressed == 9
ledger = list(csv.DictReader(Path(files['AI_Task/logs/research-20261101/final-nine-run-ledger.csv']).open()))
expected = {27777:3038.022906882578,27779:2999.245473486658,27781:2738.9400990655995,27783:2721.8157997151875,27804:2821.8848620339454,27806:2900.606831097833,27826:3039.1670930293776,27828:3039.356215188634,27830:3043.1412580549845}
assert {int(row['job']) for row in ledger} == set(expected)
for row in ledger:
    job = int(row['job'])
    exported = json.loads(Path(files[f'AI_Task/logs/research-20261101/jobs/{job}/profile_export_aiperf.json']).read_text())
    assert math.isclose(exported['goodput']['avg'] * 200, expected[job], abs_tol=1e-8)
    assert math.isclose(float(row['good_output_tokens_s']), expected[job], abs_tol=1e-8)
    assert int(row['concurrency']) == (54 if job == 27781 else 64)
link_count = 0
for name in ['TRANSCRIPT_EN.md', 'TRANSCRIPT_VI.md', 'REPORT.md', 'PRESENTATION_PLAN.md', 'MOCK_QA_EVIDENCE.md', 'TALK_SCRIPT_EN.md', 'TALK_SCRIPT_VI.md', 'FEEDBACK_RESPONSE.md', 'JOURNEY_COVERAGE.md']:
    path = R / name
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if target.startswith(('http://', 'https://', '#')):
            continue
        actual = (path.parent / unquote(target.strip('<>').split('#')[0])).resolve()
        if actual == O / 'publication-validation.json' and not args.published:
            continue
        assert actual.exists(), (path.name, target)
        link_count += 1
publication = None
if args.published:
    publication = json.loads((O / 'publication-validation.json').read_text())
    assert publication['passed'] and publication['pptx_sha256'] == identity
    assert sha((T / 'Presentation/TripleU_APAC2026_Presentation.pptx').read_bytes()) == identity
    with zipfile.ZipFile(W / 'VNUHCM - TripleU.zip') as archive:
        assert archive.testzip() is None
        assert sha(archive.read(T.name + '/Presentation/TripleU_APAC2026_Presentation.pptx')) == identity
        for target, path in files.items():
            assert (T / target).read_bytes() == Path(path).read_bytes()
            assert archive.read(T.name + '/' + target) == Path(path).read_bytes()
        zipped = {name[len(T.name)+1:]: archive.read(name) for name in archive.namelist() if not name.endswith('/')}
        folder = {str(path.relative_to(T)): path.read_bytes() for path in T.rglob('*') if path.is_file()}
        for surface in [folder, zipped]:
            stored = json.loads(surface['AI_Task/logs/FILE_MANIFEST.json'])
            for entry in stored['files']:
                assert sha(surface[entry['path']]) == entry['sha256']
            for line in surface['AI_Task/logs/SHA256SUMS'].decode().splitlines():
                digest, relative = line.split('  ', 1)
                import posixpath
                assert sha(surface[posixpath.normpath(posixpath.join('AI_Task/logs', relative))]) == digest
    assert sha((W / 'VNUHCM - TripleU.zip').read_bytes()) == publication['zip_sha256']
result = {
    'passed': True, 'published_checked': args.published, 'pptx_sha256': identity,
    'main_ai_slides': 16, 'hidden_ai_backups': 18, 'preserved_hpc_slides': 8,
    'visible_sequence': visible, 'main_pdf_pages': 24, 'full_pdf_pages': 42,
    'protected_hpc_parts': len(snapshot['presentation']['hpc_dependency_closure_parts']),
    'explicit_packaged_ai_files': len(files), 'lossless_request_exports_verified': compressed,
    'final_job_score_exports_verified': len(ledger), 'working_source_links': link_count,
    'not_performed': ['Actual Office slideshow/device test', 'Human timed combined mock', 'Official full-set model quality evaluation', 'New complete portable GPU replay after reader repair'],
}
(O / ('FINAL_VALIDATION.json' if args.published else 'STAGED_VALIDATION.json')).write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))

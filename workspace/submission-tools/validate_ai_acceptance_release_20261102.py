#!/usr/bin/env python3
"""Check deck, guides and optionally the published delivery against reviewed sources."""
from ai_release_context import review_path, part_prefix
import os
from pathlib import Path
import argparse
import hashlib
import json
import os
import stat
import zipfile

import fitz
from pptx import Presentation

W = Path(__file__).resolve().parents[1]
O = review_path(W)
R = W / 'reports/ai-final-report-20261030'
T = W / 'VNUHCM - TripleU'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--published', action='store_true')
    args = parser.parse_args()
    checks = []

    def check(name, condition):
        assert condition, name
        checks.append(name)

    deck = O / 'TripleU_APAC2026_Presentation.pptx'
    merge = json.loads((O / 'merge-validation.json').read_text())
    guide = json.loads((R / 'transcript-validation.json').read_text())
    source = json.loads((R / 'transcript-slide-source.json').read_text())
    pdfs = json.loads((R / 'transcript-pdf-validation.json').read_text())
    before = json.loads((O / 'HPC_BEFORE.json').read_text())
    expected = digest(deck.read_bytes())
    check('source_guide_merge_exact_deck_identity',
          expected == merge['pptx_sha256'] == guide['deck_sha256'] == source['presentation_sha256'])
    presentation = Presentation(deck)
    check('42_slides_16_main_18_hidden_8_HPC', len(presentation.slides) == 42 and all(
        (slide._element.get('show') == '0') == (17 <= index <= 34)
        for index, slide in enumerate(presentation.slides, 1)))
    for index in (13, 16, 26, 31):
        notes = presentation.slides[index - 1].notes_slide.notes_text_frame.text
        check(f'acceptance_bound_to_notes_{index}', '28197' in notes and '611' in notes)
    for name, meta in guide['files'].items():
        check('markdown_identity_' + name, digest((R / name).read_bytes()) == meta['sha256'])
    for meta in pdfs['outputs']:
        name = meta['file']
        check('pdf_identity_' + name, digest((R / name).read_bytes()) == meta['sha256'])
        check('pdf_markdown_identity_' + name,
              meta['markdown_sha256'] == digest((R / name.replace('.pdf', '.md')).read_bytes()))
        with fitz.open(R / name) as pdf:
            check('pdf_pages_' + name, len(pdf) == meta['pages'])
    with fitz.open(O / 'TripleU_APAC2026_Presentation.pdf') as full, \
         fitz.open(O / 'TripleU_APAC2026_Main_Talk.pdf') as main_pdf:
        check('full_42_main_24_pages', len(full) == 42 and len(main_pdf) == 24)
        for n, slide in enumerate([*range(16), *range(34, 42)]):
            check(f'main_page_matches_full_{slide + 1}',
                  full[slide].get_pixmap().samples == main_pdf[n].get_pixmap().samples)
    check('HPC_PDF_preserved', merge['hpc_pdf_render_pixels_identical'])
    with zipfile.ZipFile(deck) as archive:
        check('68_HPC_PPTX_parts_preserved', len(before['presentation']['hpc_dependency_closure_parts']) == 68 and all(
            digest(archive.read(path)) == sha
            for path, sha in before['presentation']['hpc_dependency_closure_parts'].items()))
    if args.published:
        folder = {str(p.relative_to(T)): p.read_bytes() for p in T.rglob('*') if p.is_file()}
        zip_path = W / (T.name + '.zip')
        with zipfile.ZipFile(zip_path) as archive:
            check('zip_CRC', archive.testzip() is None)
            names = archive.namelist()
            check('zip_unique_safe_names', len(names) == len(set(names)) and all(
                name.startswith(T.name + '/') and '..' not in Path(name).parts and not name.startswith('/')
                for name in names))
            packed = {name[len(T.name) + 1:]: archive.read(name) for name in names if not name.endswith('/')}
        pmap = json.loads((O / 'package-file-map.json').read_text())
        for path, staged in pmap.items():
            check('published_folder_' + path, folder[path] == Path(staged).read_bytes())
            check('published_zip_' + path, packed[path] == Path(staged).read_bytes())
        check('published_PPTX_exact', folder['Presentation/' + deck.name] == packed['Presentation/' + deck.name] == deck.read_bytes())
        check('HPC_folder_hashes_preserved', {p: digest(b) for p, b in folder.items() if p.startswith('HPC_Task/')} == before['hpc_task_files'])
        check('HPC_folder_modes_preserved', all(
            stat.S_IMODE((T / p).stat().st_mode) == mode for p, mode in before['hpc_modes'].items()))
        check('HPC_zip_hashes_preserved', {T.name + '/' + p: digest(b) for p, b in packed.items() if p.startswith('HPC_Task/')} == before['zip_hpc_files'])
        for label, files in [('folder', folder), ('zip', packed)]:
            manifest = json.loads(files['AI_Task/logs/FILE_MANIFEST.json'])
            recorded = {x['path']: x['sha256'] for x in manifest['files']}
            actual = {p: digest(b) for p, b in files.items() if p not in {'AI_Task/logs/FILE_MANIFEST.json', 'AI_Task/logs/SHA256SUMS'}}
            check(label + '_global_manifest', recorded == actual)
            lines = files['AI_Task/logs/SHA256SUMS'].decode().splitlines()
            sums = {os.path.normpath(os.path.join('AI_Task/logs', line.split('  ', 1)[1])): line.split('  ', 1)[0] for line in lines}
            check(label + '_global_checksums', sums == {p: digest(b) for p, b in files.items() if p != 'AI_Task/logs/SHA256SUMS'})
        check('zip_checksum_sidecar', (W / (T.name + '.zip.sha256')).read_text() == f'{digest(zip_path.read_bytes())}  {T.name}.zip\n')
    output = {'passed': True, 'published_surface_checked': args.published,
              'pptx_sha256': expected, 'checks': len(checks), 'checks_run': checks,
              'limits': ['Office/projector rendering and human timed rehearsal not tested',
                         'Official quality and organiser upload not performed']}
    (O / ('CROSS_ARTIFACT_VALIDATION.json' if args.published else 'CROSS_ARTIFACT_STAGE_VALIDATION.json')).write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if k != 'checks_run'}, indent=2))


if __name__ == '__main__':
    main()

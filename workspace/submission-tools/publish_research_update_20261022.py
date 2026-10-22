"""Publish the reviewed talk while preserving AI scripts and HPC payloads."""
from datetime import datetime, timezone
from pathlib import Path
import fcntl
import hashlib
import json
import os
import re
import shutil
import zipfile

from lxml import etree
from pptx import Presentation

W = Path('/home/apacsc42/workspace')
O = W / 'submission-review/research-update-2026-10-22'
T = W / 'VNUHCM - TripleU'
C = O / 'TripleU_APAC2026_Presentation.pptx'
EXTERNAL = W / 'submission-tools/design-assets'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def inventory():
    return {p.relative_to(T).as_posix(): p.read_bytes()
            for p in sorted(T.rglob('*')) if p.is_file()}


def atomic(path, data):
    temporary = path.with_name('.' + path.name + '.presentation-update')
    assert not temporary.exists(), 'Inspect an interrupted publication first'
    temporary.write_bytes(data)
    temporary.replace(path)


def validate():
    deck = Presentation(C)
    assert len(deck.slides) == 32
    visible = [s.text for slide in deck.slides for s in slide.shapes
               if s.has_text_frame]
    notes = [s.notes_slide.notes_text_frame.text for s in deck.slides]
    vi = re.compile('[đĐăĂưƯơƠấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựỵỷỹ]')
    assert all(n.strip() for n in notes)
    assert not any(vi.search(t) for t in visible + notes)
    for label in ['3,044.49', '3,044.28', '3,044.07', '2,433.02',
                  '98.632%', '22 October 2026', '+2.273%']:
        assert any(label in text for text in visible), label
    for label in ['README', 'AI_Task/', 'HPC_Task/', 'folder structure',
                  'No HPC task scripts', 'FILE_MANIFEST']:
        assert not any(label.lower() in text.lower() for text in visible), label
    for stale in ['N62 is a single accepted observation',
                  'new N62 single observation still requires',
                  'N62 still needs independent repetition']:
        assert not any(stale.lower() in text.lower() for text in notes), stale
    data = json.loads((O / 'presentation-data.json').read_text())
    for name, expected in data['sources'].items():
        assert sha(Path(name).read_bytes()) == expected, name
    layout = json.loads((O / 'layout-validation.json').read_text())
    assert layout['text_within_boxes'] and layout['boxes_within_slides']
    assert layout['raw_sla_checked'] == dict(job='25373', requests=1901, passed=1875)
    backgrounds = json.loads((O / 'background-manifest.json').read_text())['slides']
    assert len(backgrounds) == len({b['sha256'] for b in backgrounds}) == 32
    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    with zipfile.ZipFile(C) as archive:
        assert archive.testzip() is None
        for number, bg in enumerate(backgrounds, 1):
            assert sha((EXTERNAL / bg['file']).read_bytes()) == bg['sha256']
            rels = etree.fromstring(archive.read(f'ppt/slides/_rels/slide{number}.xml.rels'))
            mapping = {r.get('Id'): r.get('Target') for r in rels}
            slide = etree.fromstring(archive.read(f'ppt/slides/slide{number}.xml'))
            digests = []
            for blip in slide.findall('.//a:blip', ns):
                target = mapping.get(blip.get('{' + ns['r'] + '}embed'), '')
                if target.startswith('../media/'):
                    digests.append(sha(archive.read('ppt/' + target[3:])))
            assert bg['sha256'] in digests, number
            alpha = {int(x.get('val')) for x in slide.findall(
                './/a:gradFill/a:gsLst/a:gs/a:srgbClr/a:alpha', ns)}
            assert ({92000, 84000} if number == 24 else {91000, 82000}).issubset(alpha)
        assert 'customXml/assetCredits.xml' in archive.namelist()
    return deck, notes, data, backgrounds


def main():
    with (W / '.submission-publication.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        deck, notes, data, backgrounds = validate()
        assert {p.name for p in T.iterdir()} == {'Presentation', 'AI_Task', 'HPC_Task'}
        before = inventory()
        protected = {name: sha(value) for name, value in before.items()
                     if name.startswith(('HPC_Task/', 'AI_Task/job_scripts/'))}
        now = datetime.now(timezone.utc)
        report = dict(
            checked_utc=now.isoformat(), passed=True, slides=32,
            main_slides=24, appendix_slides=8, distinct_backgrounds=32,
            source_hashes_checked=len(data['sources']), english_slides_and_notes=True,
            native_gradients=True, raw_sla_job='25373',
            raw_requests=1901, raw_joint_good=1875,
            publication_scope='Presentation and its validation/checksums only',
            primary_script_unchanged=True, primary_concurrency=62,
            hpc_payload_unchanged=True, official_accuracy_verified=False,
            organiser_upload_performed=False,
            render_method='PDF/previews share drawing coordinates; not an Office render')
        config = json.loads(before['AI_Task/job_scripts/config.json'])
        assert config['declared_concurrency'] == 62
        changes = {
            'Presentation/' + C.name: C.read_bytes(),
            'AI_Task/logs/presentation-validation.json': encoded(report),
            'AI_Task/logs/presentation-backgrounds.json': encoded(dict(slides=backgrounds))}
        after = {**before, **changes}
        manifest_name, sums_name = 'AI_Task/logs/FILE_MANIFEST.json', 'AI_Task/logs/SHA256SUMS'
        manifest = dict(created_utc=now.isoformat(), paths_relative_to_team_directory=True,
                        files=[dict(path=name, bytes=len(value), sha256=sha(value))
                               for name, value in sorted(after.items())
                               if name not in (manifest_name, sums_name)])
        changes[manifest_name] = encoded(manifest)
        after.update(changes)
        changes[sums_name] = ''.join(
            sha(value) + '  ' + os.path.relpath(T / name, T / 'AI_Task/logs') + '\n'
            for name, value in sorted(after.items()) if name != sums_name).encode()
        after.update(changes)
        assert all(sha(after[name]) == digest for name, digest in protected.items())
        ztmp = O / 'updated-package.zip'
        with zipfile.ZipFile(ztmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            archive.writestr(T.name + '/', b'')
            for directory in sorted(p for p in T.rglob('*') if p.is_dir()):
                archive.writestr(T.name + '/' + directory.relative_to(T).as_posix() + '/', b'')
            for name, value in sorted(after.items()):
                archive.writestr(T.name + '/' + name, value)
        with zipfile.ZipFile(ztmp) as archive:
            assert archive.testzip() is None
            assert {name: sha(archive.read(T.name + '/' + name))
                    for name in after} == {name: sha(value) for name, value in after.items()}
        # Refuse overwriting concurrent work. Never replace the team directory.
        assert {n: sha(v) for n, v in inventory().items()} == {
            n: sha(v) for n, v in before.items()}, 'Concurrent package edit; review and retry'
        backup = W / 'submission-archive' / ('before-research-deck-' + now.strftime('%Y%m%dT%H%M%SZ'))
        backup.mkdir()
        for name in changes:
            if name in before:
                path = backup / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(before[name])
        for name in ['VNUHCM - TripleU.zip', 'VNUHCM - TripleU.zip.sha256']:
            if (W / name).exists():
                shutil.copy2(W / name, backup / name)
        for name, value in changes.items():
            atomic(T / name, value)
        atomic(W / 'VNUHCM - TripleU.zip', ztmp.read_bytes())
        atomic(W / 'VNUHCM - TripleU.zip.sha256',
               (sha(ztmp.read_bytes()) + '  VNUHCM - TripleU.zip\n').encode())
        actual = inventory()
        assert {n: sha(v) for n, v in actual.items()} == {n: sha(v) for n, v in after.items()}
        assert all(sha(actual[n]) == digest for n, digest in protected.items())
        report.update(pptx_sha256=sha(C.read_bytes()), zip_sha256=sha(ztmp.read_bytes()),
                      zip_bytes=ztmp.stat().st_size, zip_crc_verified=True,
                      protected_files_verified=len(protected), backup=str(backup))
        (O / 'publication-validation.json').write_bytes(encoded(report))
        titles = json.loads((O / 'slide-content.json').read_text())
        (O / 'PRESENTER_NOTES.md').write_text('# Presenter notes — 22 October 2026\n\n' +
            '\n\n'.join(f"## Slide {i+1}: {titles[i]['title']}\n\n{note}"
                        for i, note in enumerate(notes)) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

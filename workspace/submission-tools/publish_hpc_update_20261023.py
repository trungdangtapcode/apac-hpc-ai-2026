#!/usr/bin/env python3
"""Publish the reviewed 80/20 talk and CPU scripts with an atomic ZIP backup."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
from pptx import Presentation

W = Path('/home/apacsc42/workspace')
O = W / 'submission-review/hpc-update-20261023'
T = W / 'VNUHCM - TripleU'
DECK = 'Presentation/TripleU_APAC2026_Presentation.pptx'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def inventory():
    return {p.relative_to(T).as_posix(): p.read_bytes()
            for p in sorted(T.rglob('*')) if p.is_file()}


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.hpc-update')
    assert not temporary.exists(), 'Review an interrupted publication before retrying'
    temporary.write_bytes(value)
    temporary.replace(path)


def main():
    with (W / '.submission-publication.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        before = inventory()
        merge = json.loads((O / 'merge-validation.json').read_text())
        assert sha(before[DECK]) in {merge['base_sha256'], merge['combined_sha256']}, 'AI deck changed: rebase this section'
        assert merge['passed'] and (merge['ai_slides'], merge['hpc_slides']) == (32, 8)
        deck = Presentation(O / 'TripleU_APAC2026_Presentation.pptx')
        assert len(deck.slides) == 40
        visible = [s.text for slide in deck.slides for s in slide.shapes if s.has_text_frame]
        notes = [slide.notes_slide.notes_text_frame.text for slide in deck.slides]
        vi = re.compile('[đĐăĂưƯơƠấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựỵỷỹ]')
        assert all(n.strip() for n in notes) and not any(vi.search(t) for t in visible + notes)
        for unwanted in ['README', 'FILE_MANIFEST', 'No HPC task scripts', 'folder structure']:
            assert not any(unwanted.lower() in text.lower() for text in visible)
        layout = json.loads((O / 'slide-section/layout-validation.json').read_text())
        assert layout['slide_count'] == 8
        assert all(0 <= b['x'] and 0 <= b['y'] and b['x'] + b['w'] <= 13.334
                   and b['y'] + b['h'] <= 7.501 for b in layout['text_boxes'])
        bg = json.loads(before['AI_Task/logs/presentation-backgrounds.json'])['slides']
        assert len(bg) in (32, 40)
        if len(bg) == 32:
            for i, item in enumerate(layout['backgrounds'], 33):
                bg.append({**item, 'slide': i, 'section': 'HPC'})
        else:
            assert [x['sha256'] for x in bg[32:]] == [x['sha256'] for x in layout['backgrounds']]
        assert len({x['sha256'] for x in bg}) == 40
        scripts = O / 'package/HPC_Task/job_scripts'
        subprocess.run(['python3', str(scripts / 'verify-inputs.py'), '--root', str(scripts),
                        '--mode', 'bundle'], check=True, stdout=subprocess.DEVNULL)
        script_review = json.loads((O / 'script-validation.json').read_text())
        assert all(x['validation_passed'] for x in script_review['native_output_replays'])
        assert {x['job_id'] for x in script_review['native_output_replays']} == {'25921487', '25921492', '25921488'}
        native = json.loads((O / 'package/HPC_Task/logs/provenance.json').read_text())
        for row in native['files']:
            assert sha((O / 'package/HPC_Task/logs' / row['path']).read_bytes()) == row['sha256']
        now = datetime.now(timezone.utc)
        prior_validation = json.loads(before['AI_Task/logs/presentation-validation.json'])
        if prior_validation.get('slides') == 40:
            prior_validation = prior_validation['previous_ai_validation']
        report = dict(checked_utc=now.isoformat(), passed=True,
                      slides=40, ai_slides=32, hpc_slides=8, hpc_slide_fraction=0.2,
                      english_slides_and_notes=True, distinct_backgrounds=40,
                      ai_slide_parts_and_notes_preserved=True,
                      ai_scripts_and_raw_logs_unchanged=True,
                      previous_ai_validation=prior_validation,
                      hpc_primary='HPC_Task/job_scripts/submit-best.pbs',
                      hpc_candidate_job='25921488', hpc_candidate_seconds_per_step=3.677906731,
                      hpc_confirmation_job='25940700.pbs101',
                      hpc_new_portable_bundle_compute_replay=False,
                      hpc_official_score_or_acceptance_claimed=False,
                      organiser_upload_performed=False,
                      render_method=merge['render_method'],
                      publication_scope='Combined presentation, reviewed CPU scripts/logs, presentation metadata and package checksums')
        changes = {DECK: (O / 'TripleU_APAC2026_Presentation.pptx').read_bytes(),
                   'AI_Task/logs/presentation-validation.json': encoded(report),
                   'AI_Task/logs/presentation-backgrounds.json': encoded(dict(slides=bg)),
                   'HPC_Task/logs/presentation-validation.json': encoded(merge)}
        for source in sorted((O / 'package/HPC_Task').rglob('*')):
            assert not source.is_symlink()
            if source.is_file():
                changes['HPC_Task/' + source.relative_to(O / 'package/HPC_Task').as_posix()] = source.read_bytes()
        mutable_ai = {'AI_Task/logs/presentation-validation.json',
                      'AI_Task/logs/presentation-backgrounds.json',
                      'AI_Task/logs/FILE_MANIFEST.json', 'AI_Task/logs/SHA256SUMS'}
        protected = {n: sha(v) for n, v in before.items()
                     if n.startswith('AI_Task/') and n not in mutable_ai}
        after = {**before, **changes}
        manifest_name = 'AI_Task/logs/FILE_MANIFEST.json'
        sums_name = 'AI_Task/logs/SHA256SUMS'
        changes[manifest_name] = encoded(dict(created_utc=now.isoformat(),
            paths_relative_to_team_directory=True,
            files=[dict(path=n, bytes=len(v), sha256=sha(v)) for n, v in sorted(after.items())
                   if n not in (manifest_name, sums_name)]))
        after.update(changes)
        changes[sums_name] = ''.join(sha(v) + '  ' + os.path.relpath(T / n, T / 'AI_Task/logs') + '\n'
                                    for n, v in sorted(after.items()) if n != sums_name).encode()
        after.update(changes)
        assert all(sha(after[n]) == h for n, h in protected.items())
        assert {p.name for p in T.iterdir()} == {'Presentation', 'AI_Task', 'HPC_Task'}
        zpath = O / 'updated-package.zip'
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            directories = {T.name}
            for n in after:
                directories.update(str(p) for p in Path(T.name, n).parents if str(p) != '.')
            for directory in sorted(directories):
                z.writestr(directory + '/', b'')
            for n, v in sorted(after.items()):
                z.writestr(T.name + '/' + n, v)
        with zipfile.ZipFile(zpath) as z:
            assert z.testzip() is None
            assert {n: sha(z.read(T.name + '/' + n)) for n in after} == {n: sha(v) for n, v in after.items()}
        assert {n: sha(v) for n, v in inventory().items()} == {n: sha(v) for n, v in before.items()}, 'Concurrent package edit'
        backup = W / 'submission-archive' / ('before-hpc-update-' + now.strftime('%Y%m%dT%H%M%SZ'))
        backup.mkdir()
        for n in changes:
            if n in before:
                p = backup / n
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(before[n])
        for name in ['VNUHCM - TripleU.zip', 'VNUHCM - TripleU.zip.sha256']:
            if (W / name).exists():
                shutil.copy2(W / name, backup / name)
        for n, v in changes.items():
            atomic(T / n, v)
        atomic(W / 'VNUHCM - TripleU.zip', zpath.read_bytes())
        atomic(W / 'VNUHCM - TripleU.zip.sha256', (sha(zpath.read_bytes()) + '  VNUHCM - TripleU.zip\n').encode())
        actual = inventory()
        assert {n: sha(v) for n, v in actual.items()} == {n: sha(v) for n, v in after.items()}
        assert all(sha(actual[n]) == h for n, h in protected.items())
        report.update(pptx_sha256=sha(actual[DECK]), zip_sha256=sha(zpath.read_bytes()),
                      zip_crc_and_content_hashes_verified=True,
                      protected_ai_files_verified=len(protected), backup=str(backup),
                      published_files=len(changes), package_files=len(after))
        (O / 'publication-validation.json').write_bytes(encoded(report))
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

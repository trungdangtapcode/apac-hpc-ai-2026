#!/usr/bin/env python3
"""Seal terminal H200 tokenizer/backend review inputs without editing frozen payloads."""
from pathlib import Path
import datetime, hashlib, json, subprocess

HERE = Path(__file__).resolve().parent
Q = HERE.parent
JOBS = (26949, 26951, 26953, 27077)

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

for job in JOBS:
    run = Q / 'runs' / str(job)
    accounting = subprocess.check_output([
        'sacct', '-X', '-j', str(job), '-P',
        '--format=JobID,State,ExitCode,Elapsed,NodeList'
    ], text=True)
    rows = [line.split('|') for line in accounting.splitlines()]
    matches = [row for row in rows[1:] if row[0] == str(job)]
    assert len(matches) == 1 and matches[0][1:3] == ['COMPLETED', '0:0'], (job, accounting)
    assert str(job) not in subprocess.check_output(
        ['squeue', '-h', '-u', 'apacsc42', '-o', '%i'], text=True).split()
    accounting_path = run / 'scheduler-accounting.psv'
    if accounting_path.exists():
        assert accounting_path.read_text() == accounting, f'Existing accounting differs for {job}'
    else:
        accounting_path.write_text(accounting)

    manifest_path = run / 'artifact-manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        # Existing manifest is retained with its original schema; verify every listed artifact.
        for item in manifest['files']:
            path = Q / item['path']
            assert path.is_file() and path.stat().st_size == item['bytes'] and sha256(path) == item['sha256'], (job, item['path'])
        continue

    files = []
    candidates = sorted(run.rglob('*')) + [Q / 'runs' / f'{job}.out', Q / 'runs' / f'{job}.err']
    for path in candidates:
        if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts or path == manifest_path:
            continue
        before = path.stat()
        digest = sha256(path)
        after = path.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), path
        files.append({'path': str(path.relative_to(Q)), 'bytes': after.st_size, 'sha256': digest})
    manifest_path.write_text(json.dumps({
        'job': job,
        'sealed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'terminal_accounting': accounting,
        'files': files,
    }, indent=2) + '\n')
    # Re-read and verify the newly written manifest before considering the seal complete.
    for item in json.loads(manifest_path.read_text())['files']:
        path = Q / item['path']
        assert path.stat().st_size == item['bytes'] and sha256(path) == item['sha256']
print('Verified terminal accounting and preserved raw evidence for jobs 26949, 26951, 26953, 27077.')

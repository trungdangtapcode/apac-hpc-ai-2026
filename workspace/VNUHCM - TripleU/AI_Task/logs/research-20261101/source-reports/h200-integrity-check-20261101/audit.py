"""Read-only source/archive/object integrity audit of the completed H200 transfers."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

D = Path(__file__).resolve().parent
Q = D.parent
H = Q.parent.parent
A = H / 'apac-hpc-ai-research'
STORE = H / 'apac-hpc-ai-research-artifacts'
JOBS = (27777, 27779, 27781, 27783, 27804, 27806, 27826, 27828, 27830)

def digest(path):
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'Unstable file'
    return h.hexdigest(), after.st_size

def object_digest(path):
    process = subprocess.Popen(['zstd', '-q', '-d', '-c', str(path)], stdout=subprocess.PIPE)
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: process.stdout.read(4 * 1024 * 1024), b''):
        h.update(block)
        size += len(block)
    assert process.wait() == 0, 'Decompression failed'
    return h.hexdigest(), size

target = D / 'audit.json'
assert not target.exists(), 'Preserve prior audit evidence'
manifest = {row['path']: row for row in map(json.loads, (A / 'backup/manifest.jsonl').read_text().splitlines())}
tracked = set(subprocess.check_output(['git', '-C', str(A), 'ls-files', '-z'], text=True).split('\0'))
head = subprocess.check_output(['git', '-C', str(A), 'rev-parse', 'HEAD'], text=True).strip()
remote = subprocess.check_output(['git', '-C', str(A), 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
queue = subprocess.check_output(['squeue', '-h', '-u', 'apacsc42', '-o', '%i|%j|%T|%M|%D|%R'], text=True)
account = subprocess.check_output(['sacct', '-X', '-j', ','.join(map(str, JOBS)),
    '--starttime', '2026-10-31T00:00:00', '-P',
    '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList,AllocTRES'], text=True)
lines = [line.split('|') for line in account.splitlines()]
terminal = {int(row[0]): dict(zip(lines[0], row)) for row in lines[1:] if row[0] in set(map(str, JOBS))}
assert set(terminal) == set(JOBS), 'Accounting coverage incomplete'
assert all(row['State'] == 'COMPLETED' and row['ExitCode'] == '0:0' and 'gres/gpu=16' in row['AllocTRES']
           for row in terminal.values()), 'Unexpected terminal state or GPU resource count'
assert not any(line.split('|')[0] in set(map(str, JOBS)) for line in queue.splitlines())
checks, verified_objects, job_summaries = [], {}, []
for job in JOBS:
    seal = Q / f'runs/{job}/artifact-manifest.json'
    rows = json.loads(seal.read_text())['files']
    rows = rows + [dict(path=str(seal.relative_to(Q)), sha256=digest(seal)[0], bytes=seal.stat().st_size)]
    for item in rows:
        path = Q / item['path']
        result = dict(job=job, path=item['path'], passed=False)
        try:
            assert not path.is_symlink() and path.resolve().is_relative_to(Q.resolve()), 'Source path escape'
            wanted = item['sha256'], item['bytes']
            assert digest(path) == wanted, 'Source differs from sealed bytes'
            relative = str(path.relative_to(H))
            archived = manifest[relative]
            assert (archived['sha256'], archived['bytes']) == wanted, 'Archive capture metadata mismatch'
            if archived['storage'] == 'git':
                assert relative in tracked, 'Inline capture not tracked by Git'
                assert digest(A / relative) == wanted, 'Inline capture bytes mismatch'
            else:
                assert archived['storage'] == 'object'
                compressed = STORE / archived['object']
                assert compressed.resolve().is_relative_to(STORE.resolve()) and not compressed.is_symlink(), 'Object path escape'
                key = archived['sha256']
                if key not in verified_objects:
                    verified_objects[key] = object_digest(compressed)
                assert verified_objects[key] == wanted, 'External object decompressed bytes mismatch'
            result.update(passed=True, storage=archived['storage'], bytes=item['bytes'])
        except Exception as error:
            result['error'] = type(error).__name__ + ': ' + str(error)
        checks.append(result)
    own = [check for check in checks if check['job'] == job]
    job_summaries.append(dict(job=job, checked_files=len(own), passed=all(c['passed'] for c in own),
                              sealed_source_bytes=sum(c.get('bytes', 0) for c in own)))
    print(json.dumps(job_summaries[-1]), flush=True)
result = dict(checked_vietnam_time=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
    passed=head == remote and all(c['passed'] for c in checks),
    archive_reference_HEAD=head, origin_main_at_check=remote, own_slurm_queue=queue,
    terminal_accounting=terminal, job_summaries=job_summaries, file_checks=checks,
    total_checked_files=len(checks), source_bytes_verified=sum(c.get('bytes', 0) for c in checks),
    unique_external_objects_decompressed_and_verified=len(verified_objects),
    actual_nine_job_GPU_hours=sum(16 * int(row['ElapsedRaw']) / 3600 for row in terminal.values()),
    PBS_SU=0, new_GPU_submissions=0,
    limits='Integrity of these nine retained runs only. Git origin contains tracked bytes and recovery metadata; this does not prove external object bytes are copied off-host. No official model accuracy, new performance result, H100 scheduler state, or unretained historical chat coverage is certified.')
target.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('passed', 'total_checked_files', 'source_bytes_verified',
    'unique_external_objects_decompressed_and_verified', 'actual_nine_job_GPU_hours')}), flush=True)
raise SystemExit(0 if result['passed'] else 1)

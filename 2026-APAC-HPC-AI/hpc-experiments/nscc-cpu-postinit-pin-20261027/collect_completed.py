"""Collect one completed NSCC diagnostic using native tar and per-member hashes."""
from pathlib import Path
import datetime
import hashlib
import io
import json
import shlex
import shutil
import subprocess
import tarfile

E = Path(__file__).resolve().parent
R = Path('/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments')
SSH = R / 'tools/nscc-cpu-ssh.sh'


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    deployment = json.loads((E / 'deployment.json').read_text())
    root = deployment['root']
    job = (E / 'submission.json').read_text()
    job_id = json.loads(job)['stdout'].strip()
    assert job_id and '.' in job_id
    short = job_id.split('.', 1)[0]
    attempt = E / ('collection-attempt-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    attempt.mkdir(exist_ok=False)
    fresh = subprocess.run(['bash', str(SSH), f'qstat -fx -F json {shlex.quote(job_id)}'],
                           capture_output=True, text=True, timeout=35)
    (attempt / 'fresh-qstat.stdout.json').write_text(fresh.stdout)
    (attempt / 'fresh-qstat.stderr.txt').write_text(fresh.stderr)
    (attempt / 'fresh-qstat.exit-code.txt').write_text(str(fresh.returncode) + '\n')
    terminal = None
    source = None
    if fresh.returncode == 0:
        try:
            terminal = json.loads(fresh.stdout)['Jobs'][job_id]
            assert terminal['job_state'] == 'F'
            source = 'fresh qstat query collected at ' + utc()
        except Exception:
            terminal = None
    if terminal is None:
        fallback = E / 'terminal-status-snapshot.json'
        if fallback.exists():
            snap = json.loads(fallback.read_text())
            terminal = snap['job']
            source = f"dated terminal-status-snapshot.json at {snap['observed_at_utc']}; fresh qstat exit={fresh.returncode}; preserve query files"
            shutil.copyfile(fallback, out / fallback.name)
        else:
            raise RuntimeError(f'PBS history unavailable and no dated terminal snapshot supplied; preserved failed query in {attempt}; do not infer status')
    assert terminal['job_state'] == 'F'
    out = E / ('completed-' + short)
    out.mkdir(exist_ok=False)
    for name in ('fresh-qstat.stdout.json', 'fresh-qstat.stderr.txt', 'fresh-qstat.exit-code.txt'):
        shutil.copyfile(attempt / name, out / name)
    batch = f'postinit-pin-qual.o{short}'
    remote_cmd = (f'cd {shlex.quote(root)} && tar --exclude={shlex.quote("runs/"+short+"/mpi-init-probe")} '
                  f'--exclude={shlex.quote("runs/"+short+"/postinit-pin-probe")} -czf - '
                  f'{shlex.quote("runs/"+short)} {shlex.quote(batch)}')
    captured = subprocess.run(['bash', str(SSH), remote_cmd], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=180)
    (out / 'native-tar.stderr.txt').write_bytes(captured.stderr)
    assert captured.returncode == 0, f'native tar failed rc={captured.returncode}: {captured.stderr[-2000:]!r}'
    archive_path = out / 'raw-records.tar.gz'
    archive_path.write_bytes(captured.stdout)
    manifest = {}
    with tarfile.open(fileobj=io.BytesIO(captured.stdout), mode='r:gz') as archive:
        for member in archive.getmembers():
            parts = Path(member.name).parts
            assert not member.name.startswith('/') and '..' not in parts
            if member.isdir():
                continue
            assert member.isfile() and member.size < 2_000_000
            assert not member.name.endswith('/mpi-init-probe')
            assert not member.name.endswith('/postinit-pin-probe')
            data = archive.extractfile(member).read()
            manifest[member.name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    assert f'runs/{short}/arms/baseline/native/pre/rank-0000.json' in manifest
    assert f'runs/{short}/arms/postinit_pin/rank-0000.json' in manifest
    terminal_keys = ('job_state', 'Exit_status', 'Resource_List', 'resources_used', 'project',
                     'queue', 'stime', 'obittime', 'comment', 'exec_host', 'Output_Path')
    terminal = {key: terminal[key] for key in terminal_keys if key in terminal}
    document = {'collected_at_utc': utc(), 'job_id': job_id, 'remote_root': root,
                'terminal_evidence_source': source,
                'fresh_qstat': {'exit_code': fresh.returncode, 'stdout_file': 'fresh-qstat.stdout.json',
                                'stderr_file': 'fresh-qstat.stderr.txt'},
                'terminal': terminal, 'archive': 'raw-records.tar.gz',
                'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                'files': manifest,
                'scope': 'Native tar of only this job run directory and explicitly selected PBS stdout; compiled probes excluded before transfer. Full archive and per-member byte/SHA-256 inventory retained; replay reads from the archive without extracting thousands of files.'}
    (out / 'collection.json').write_text(json.dumps(document, indent=2) + '\n')
    print(json.dumps({'job_id': job_id, 'files': len(manifest), 'archive_bytes': archive_path.stat().st_size,
                      'archive_sha256': document['archive_sha256'], 'terminal_evidence_source': source}, indent=2))


if __name__ == '__main__':
    main()

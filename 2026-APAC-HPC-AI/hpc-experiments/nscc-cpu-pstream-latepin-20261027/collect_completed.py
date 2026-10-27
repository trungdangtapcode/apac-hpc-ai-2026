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
    (attempt / 'fresh-qstat.stderr.txt').write_text(fresh.stderr)
    (attempt / 'fresh-qstat.exit-code.txt').write_text(str(fresh.returncode) + '\n')
    terminal = None
    source = None
    sanitized_fresh_stdout = None
    if fresh.returncode == 0:
        try:
            fresh_document = json.loads(fresh.stdout)
            fresh_document = json.loads(json.dumps(fresh_document))
            for job_record in fresh_document.get('Jobs', {}).values():
                job_record.pop('Variable_List', None)
                job_record.pop('environment', None)
                job_record.pop('Environment', None)
            sanitized_fresh_stdout = json.dumps(fresh_document, indent=2) + '\n'
            terminal = fresh_document['Jobs'][job_id]
            assert terminal['job_state'] == 'F'
            source = 'fresh qstat query collected at ' + utc()
        except Exception:
            terminal = None
            sanitized_fresh_stdout = json.dumps({
                'sanitization_status': 'response not saved because successful qstat output could not be safely parsed',
                'stdout_bytes': len(fresh.stdout.encode()),
                'stdout_sha256': hashlib.sha256(fresh.stdout.encode()).hexdigest()
            }, indent=2) + '\n'
    if terminal is None:
        fallback = E / 'terminal-status-snapshot.json'
        if fallback.exists():
            snap = json.loads(fallback.read_text())
            terminal = snap['job']
            observed = snap.get('observed_at_utc') or snap.get('utc')
            assert observed, 'Fallback snapshot must carry its observation time'
            source = f"dated terminal-status-snapshot.json at {observed}; fresh qstat exit={fresh.returncode}; preserve query evidence"
            sanitized_fresh_stdout = json.dumps({
                'fresh_query_exit_code': fresh.returncode,
                'stdout_bytes': len(fresh.stdout.encode()),
                'stdout_sha256': hashlib.sha256(fresh.stdout.encode()).hexdigest(),
                'note': 'Raw stdout omitted to prevent runtime environment capture.'
            }, indent=2) + '\n'
        else:
            # Preserve a failed query's digest and error text without retaining unparsed output.
            (attempt / 'fresh-qstat.stdout-evidence.json').write_text(json.dumps({
                'exit_code': fresh.returncode,
                'stdout_bytes': len(fresh.stdout.encode()),
                'stdout_sha256': hashlib.sha256(fresh.stdout.encode()).hexdigest(),
                'note': 'Raw stdout omitted; no runtime environment is retained.'
            }, indent=2) + '\n')
            raise RuntimeError(f'PBS history unavailable and no dated terminal snapshot supplied; preserved failed query in {attempt}; do not infer status')
    assert terminal['job_state'] == 'F'
    out = E / ('completed-' + short)
    out.mkdir(exist_ok=False)
    (attempt / 'fresh-qstat.stdout.json').write_text(sanitized_fresh_stdout or '{}\n')
    for name in ('fresh-qstat.stdout.json', 'fresh-qstat.stderr.txt', 'fresh-qstat.exit-code.txt'):
        (out / name).write_bytes((attempt / name).read_bytes())
    batch = f'pstream-latepin.o{short}'
    remote_cmd = (f'cd {shlex.quote(root)} && tar --exclude={shlex.quote("runs/"+short+"/mpi-init-probe")} '
                  f'--exclude={shlex.quote("runs/"+short+"/latepin-pmpi-adapter.so")} -czf - '
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
            assert not member.name.endswith('/latepin-pmpi-adapter.so')
            data = archive.extractfile(member).read()
            manifest[member.name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    record_presence={name:name in manifest for name in [f'runs/{short}/arms/no-adapter/native/pre/rank-0000.json',f'runs/{short}/arms/with-adapter/adapter-ranks/rank-0000/init.json']}
    terminal_keys = ('job_state', 'Exit_status', 'Resource_List', 'resources_used', 'project',
                     'queue', 'stime', 'obittime', 'comment', 'exec_host', 'Output_Path')
    terminal = {key: terminal[key] for key in terminal_keys if key in terminal}
    document = {'collected_at_utc': utc(), 'job_id': job_id, 'remote_root': root,
                'terminal_evidence_source': source,
                'deployed_payload_sha256': deployment['files'],
                'fresh_qstat': {'exit_code': fresh.returncode, 'stdout_file': 'fresh-qstat.stdout.json',
                                'stderr_file': 'fresh-qstat.stderr.txt'},
                'terminal': terminal, 'archive': 'raw-records.tar.gz',
                'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                'files': manifest, 'record_presence_not_a_validity_claim':record_presence,
                'scope': 'Native tar of only this job run directory and explicitly selected PBS stdout; compiled probes excluded before transfer. Full archive and per-member byte/SHA-256 inventory retained; replay reads from the archive without extracting thousands of files.'}
    (out / 'collection.json').write_text(json.dumps(document, indent=2) + '\n')
    shutil.rmtree(attempt)
    print(json.dumps({'job_id': job_id, 'files': len(manifest), 'archive_bytes': archive_path.stat().st_size,
                      'archive_sha256': document['archive_sha256'], 'terminal_evidence_source': source}, indent=2))


if __name__ == '__main__':
    main()

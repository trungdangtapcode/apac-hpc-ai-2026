#!/usr/bin/env python3
"""Seal, deploy, preflight, or submit the reviewed Iris full-150 order pair.

Submission records a full 168 allocated-CPU-hour reservation before the sole
sbatch attempt. Any uncertain remote result keeps that reservation and blocks
replay until the Iris queue and remote intent are reconciled.
"""
from pathlib import Path
import argparse
import base64
import datetime as dt
import fcntl
import hashlib
import io
import json
import math
import os
import re
import sys
import tarfile
from typing import Any


E = Path(__file__).resolve().parent
B = E.parent
C = B / 'iris-scotch56-20261025'
sys.path.insert(0, str(B / 'tools'))
from iris_bridge import run_json

RUNTIME = ('run.py', 'job.sbatch', 'source-pins.json', 'native_checks.py',
           'case_checks.py', 'native_output.py', 'affinity-probe.py', 'tree-manifest.py')
PARENT_REVIEW = B / 'iris-order56-full150-20261027/REVIEW.json'
ROOT_REVIEW = E / 'ROOT_REVIEW.json'
MANIFEST = E / 'payload-sha256.json'
HASH_TEXT = E / 'payload-sha256.txt'
DEPLOYMENT = E / 'deployment.json'
PRECHECK = E / 'pre-submit-checks.json'
INTENT = E / 'submission-intent.json'
RECEIPT = E / 'submission-receipt.json'
UNCERTAIN = E / 'submission-uncertain.json'
LEDGER = C / 'budget.json'
LOCK = C / 'budget.lock'
MAXIMUM_CPU_HOURS = 168.0
NEW_CEILING_CPU_HOURS = 505.0
REMOTE_PREFIX = '/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-reverse150-'


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(path: Path, data: Any, *, exclusive: bool = False) -> None:
    """Durably write JSON. Replacement is atomic; exclusive files never clobber."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + f'.{os.getpid()}.tmp')
    target = path if exclusive else temp
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        if not exclusive:
            os.replace(temp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BaseException:
        if not exclusive:
            try:
                temp.unlink()
            except FileNotFoundError:
                pass
        raise


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def compute_files(experiment: Path = E) -> dict[str, str]:
    paths = [experiment / name for name in RUNTIME]
    case_root = experiment / 'payload-case'
    if not case_root.is_dir() or case_root.is_symlink():
        raise ValueError('payload-case missing or symlinked')
    nested = list(case_root.rglob('*'))
    if any(path.is_symlink() for path in nested):
        raise ValueError('symlinks are forbidden in payload-case')
    paths += sorted(p for p in nested if p.is_file())
    if len(paths) != 49 or len(set(paths)) != 49:
        raise ValueError(f'expected eight runtime files plus 41 case files; got {len(paths)} files')
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'missing or symlinked frozen source: {path.relative_to(experiment)}')
    return {path.relative_to(experiment).as_posix(): _sha256(path) for path in sorted(paths)}


def current_files(experiment: Path = E) -> dict[str, str]:
    actual = compute_files(experiment)
    saved = json.loads((experiment / 'payload-sha256.json').read_text())
    expected = saved.get('files')
    if expected != actual:
        raise ValueError('working files differ from frozen hash manifest')
    return expected


def require_root_review(files: dict[str, str], experiment: Path = E) -> None:
    review = json.loads((experiment / 'ROOT_REVIEW.json').read_text())
    if review.get('passed') is not True or review.get('payload_sha256') != files:
        raise ValueError('root review is missing, failed, or bound to different hashes')


def validate_sbatch(files: dict[str, str], experiment: Path = E) -> str:
    scripts = [name for name in files if name == 'job.sbatch']
    if len(scripts) != 1:
        raise ValueError('frozen runtime must contain exactly job.sbatch')
    text = (experiment / scripts[0]).read_text()
    directives = [line.strip() for line in text.splitlines() if line.lstrip().startswith('#SBATCH')]
    required = (
        r'^#SBATCH\s+-p\s+iris$',
        r'^#SBATCH\s+-A\s+rdmaworkshop$',
        r'^#SBATCH\s+--qos=low$',
        r'^#SBATCH\s+--exclusive$',
        r'^#SBATCH\s+-N\s+1$',
        r'^#SBATCH\s+-n\s+56$',
        r'^#SBATCH\s+-t\s+03:00:00$',
    )
    for pattern in required:
        if sum(bool(re.fullmatch(pattern, line)) for line in directives) != 1:
            raise ValueError('sbatch must request Iris/rdmaworkshop/QoS low, exclusive 1 node, 56 tasks, max 3 hours')
    gpu_zero = sum(bool(re.fullmatch(r'#SBATCH\s+(?:--gres=gpu:0|--gpus=0)', line)) for line in directives)
    if gpu_zero != 1:
        raise ValueError('sbatch must explicitly request zero GPUs')
    return scripts[0]


def seal(experiment: Path = E) -> dict[str, str]:
    files = compute_files(experiment)
    manifest = experiment / 'payload-sha256.json'
    if manifest.exists():
        if json.loads(manifest.read_text()).get('files') != files:
            raise ValueError('existing manifest differs; do not reseal implicitly')
    else:
        save(manifest, {'created_utc': utc(), 'files': files}, exclusive=True)
    lines = ''.join(f'{digest}  {name}\n' for name, digest in sorted(files.items()))
    hash_text = experiment / 'payload-sha256.txt'
    if hash_text.exists():
        if hash_text.read_text() != lines:
            raise ValueError('existing hash text differs from frozen manifest')
    else:
        hash_text.write_text(lines)
    return files


def require_parent_review(path: Path = PARENT_REVIEW) -> dict[str, Any]:
    review = json.loads(path.read_text())
    if review.get('passed') is not True or str(review.get('job_id')) != '2294234':
        raise ValueError('the exact completed-2294234 full150 matched-pair review must pass')
    return review


def max_cpu_hours(request: float = MAXIMUM_CPU_HOURS) -> float:
    value = float(request)
    if not math.isfinite(value) or value != 56 * 3:
        raise ValueError('request must remain one 56-CPU, three-hour allocation (168 CPU-hours)')
    return value


def financial_check(budget: dict[str, Any], request: float = MAXIMUM_CPU_HOURS) -> dict[str, float]:
    request = max_cpu_hours(request)
    if budget.get('cluster') != 'Iris' or budget.get('account') != 'rdmaworkshop':
        raise ValueError('wrong Iris budget account')
    ceiling = float(budget.get('branch_planning_ceiling_allocated_CPU_hours'))
    consumed = float(budget.get('consumed_planning_allowance_allocated_CPU_hours'))
    reserved = float(budget.get('reserved_maximum_allocated_CPU_hours'))
    if not all(math.isfinite(x) and x >= 0 for x in (ceiling, consumed, reserved)):
        raise ValueError('invalid Iris budget values')
    if ceiling != NEW_CEILING_CPU_HOURS:
        raise ValueError('Iris ceiling differs from the recorded one-job authorization')
    committed_after = consumed + reserved + request
    if committed_after > ceiling + 1e-9:
        raise ValueError('Iris planning ceiling would be exceeded')
    return {'consumed_planning_allowance_allocated_CPU_hours': consumed,
            'prior_reserved_maximum_allocated_CPU_hours': reserved,
            'new_maximum_allocated_CPU_hours': request,
            'committed_after_allocated_CPU_hours': committed_after,
            'authorized_ceiling_allocated_CPU_hours': ceiling}


def require_no_active_local_jobs(budget: dict[str, Any]) -> None:
    terminal_prefixes = ('COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT')
    jobs = budget.get('jobs')
    if not isinstance(jobs, list):
        raise ValueError('Iris budget jobs list missing')
    active = [job for job in jobs if not str(job.get('state', '')).startswith(terminal_prefixes)]
    if active:
        raise ValueError('Iris ledger contains an unresolved job or submission intent')


def require_no_own_jobs(queue: str) -> None:
    if any('|tu-' in row for row in queue.splitlines()):
        raise ValueError('Iris own-job cap reached; preserve existing queue position')


def require_no_local_attempt(experiment: Path = E) -> None:
    for path in (experiment / 'submission-intent.json', experiment / 'submission-receipt.json',
                 experiment / 'submission-uncertain.json'):
        if path.exists():
            raise FileExistsError('existing submission artifact; inspect local and remote state, never retry blindly')


def _expected_tar(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
        for name in sorted(files):
            archive.add(E / name, arcname=name, recursive=False)
        archive.add(MANIFEST, arcname='payload-sha256.json', recursive=False)
        archive.add(HASH_TEXT, arcname='payload-sha256.txt', recursive=False)
    return buffer.getvalue()


def deploy(files: dict[str, str]) -> dict[str, Any]:
    require_parent_review()
    require_root_review(files)
    script = validate_sbatch(files)
    if DEPLOYMENT.exists():
        raise FileExistsError('deployment exists; inspect and do not overwrite')
    root = REMOTE_PREFIX + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    data = base64.b64encode(_expected_tar(files)).decode('ascii')
    body = '''import base64,hashlib,io,json,tarfile
from pathlib import Path
ROOT=ROOT_VALUE;FILES=FILES_VALUE;DATA=DATA_VALUE
r=Path(ROOT);r.mkdir(parents=True,exist_ok=False);k=r/'kit';k.mkdir();(k/'runs').mkdir();(r/'runs').mkdir()
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(DATA)),mode='r:gz') as tar:
 for m in tar.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  p=k/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(m).read())
actual=sorted(p.relative_to(k).as_posix() for p in k.rglob('*') if p.is_file() and p.name not in ('payload-sha256.json','payload-sha256.txt'))
assert actual==sorted(FILES)
assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==h for n,h in FILES.items())
result={'root':str(r),'kit':str(k),'files':FILES,'job_script':'job.sbatch','state':'DEPLOYED_NOT_SUBMITTED'}
'''.replace('ROOT_VALUE', repr(root)).replace('FILES_VALUE', repr(files)).replace('DATA_VALUE', repr(data))
    result = run_json(body, timeout=120)
    expected = {'root': root, 'kit': root + '/kit', 'files': files,
                'job_script': script, 'state': 'DEPLOYED_NOT_SUBMITTED'}
    if result != expected:
        raise ValueError('Iris deployment response differs from expected root and frozen hashes')
    result['created_utc'] = utc()
    save(DEPLOYMENT, result, exclusive=True)
    return result


def precheck(files: dict[str, str]) -> dict[str, Any]:
    require_parent_review()
    require_root_review(files)
    validate_sbatch(files)
    require_no_local_attempt()
    with LOCK.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        require_no_local_attempt()
        budget = json.loads(LEDGER.read_text())
        require_no_active_local_jobs(budget)
        financial = financial_check(budget)
        remote = run_json("import subprocess,socket\nq=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True)\nresult={'host':socket.gethostname(),'queue':q}", timeout=55)
        require_no_own_jobs(remote['queue'])
        result = {'utc': utc(), 'state': 'ADMISSIBLE_AT_PREFLIGHT_ONLY',
                  'queue': [{'id': row.split('|')[0], 'job_name': row.split('|')[1], 'state': row.split('|')[2]}
                            for row in remote['queue'].splitlines() if row.count('|') == 2],
                  'financial': financial, 'request': {'nodes': 1, 'cpus': 56,
                  'walltime_seconds': 10800, 'maximum_allocated_CPU_hours': MAXIMUM_CPU_HOURS},
                  'host': remote['host']}
        save(PRECHECK, result)
        return result


def _remote_integrity_body(root: str, files: dict[str, str], *, perform_submit: bool) -> str:
    values = {'root': root, 'files': files, 'submit': perform_submit}
    prefix = 'ROOT=' + repr(values['root']) + '\nFILES=' + repr(values['files']) + '\nDO_SUBMIT=' + repr(values['submit']) + '\n'
    body = '''from pathlib import Path
import hashlib,json,subprocess,datetime,os
r=Path(ROOT);k=r/'kit';files=FILES;do_submit=DO_SUBMIT
assert not any(p.is_symlink() for p in k.rglob('*'))
assert not (r/'submission-intent.json').exists(),'remote submission intent already exists'
assert not (r/'sbatch-response.json').exists(),'remote sbatch response already exists'
actual=sorted(p.relative_to(k).as_posix() for p in k.rglob('*') if p.is_file() and p.name not in ('payload-sha256.json','payload-sha256.txt'))
assert actual==sorted(files),(actual,sorted(files))
assert all(hashlib.sha256((k/n).read_bytes()).hexdigest()==h for n,h in files.items())
manifest=json.loads((k/'payload-sha256.json').read_text())['files'];assert manifest==files
queue=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True)
assert not any('|tu-' in row for row in queue.splitlines()),'Iris own-job cap reached'
if not do_submit:
 result={'root':str(r),'files':files,'queue':queue,'state':'REMOTE_INTEGRITY_PASS'}
else:
 intent=r/'submission-intent.json'
 with intent.open('x') as f:
  json.dump({'state':'CALLING_SBATCH','queue_before':queue,'utc':datetime.datetime.utcnow().isoformat()+'Z'},f);f.flush();os.fsync(f.fileno())
 dfd=os.open(r,os.O_RDONLY);os.fsync(dfd);os.close(dfd)
 stage='CALLING_SBATCH'
 try:
  p=subprocess.run(['sbatch','--parsable','job.sbatch'],cwd=str(k),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
  response={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'queue_before':queue,'root':str(r),'stage':stage}
  (r/'sbatch-response.json').write_text(json.dumps(response,indent=2)+'\\n')
  if p.returncode==0 and p.stdout.strip().split(';')[0].isdigit():response['job_id']=p.stdout.strip().split(';')[0]
  else:response['ambiguous']=True
  result=response
 except Exception as exc:
  result={'root':str(r),'stage':stage,'error_type':type(exc).__name__,'ambiguous':True}
'''
    return prefix + body


def _remote_verify(root: str, files: dict[str, str]) -> dict[str, Any]:
    return run_json(_remote_integrity_body(root, files, perform_submit=False), timeout=90)


def submit(files: dict[str, str]) -> str:
    require_local_attempt_free()
    require_parent_review()
    require_root_review(files)
    job_script = validate_sbatch(files)
    deployment = json.loads(DEPLOYMENT.read_text())
    if deployment.get('files') != files or deployment.get('state') != 'DEPLOYED_NOT_SUBMITTED':
        raise ValueError('deployment does not match current reviewed hashes')
    root = deployment.get('root', '')
    if not re.fullmatch(re.escape(REMOTE_PREFIX) + r'\d{8}T\d{6}Z', root):
        raise ValueError('deployment root has unexpected path')
    if deployment.get('job_script') != job_script:
        raise ValueError('deployed job script differs from frozen job.sbatch')
    with LOCK.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        require_local_attempt_free()
        require_parent_review()
        require_root_review(files)
        budget = json.loads(LEDGER.read_text())
        require_no_active_local_jobs(budget)
        financial = financial_check(budget)
        remote = run_json("import subprocess,socket\nq=subprocess.check_output(['squeue','-u','rdmaworkshop30','-h','-o','%i|%j|%T'],text=True)\nresult={'host':socket.gethostname(),'queue':q}", timeout=55)
        require_no_own_jobs(remote['queue'])
        preflight = {'utc': utc(), 'host': remote['host'], 'queue': remote['queue'],
                     'financial': financial, 'root': root, 'job_script': job_script,
                     'payload_sha256': files}
        save(PRECHECK, preflight)

        entry = {'utc': utc(), 'state': 'RESERVED_SUBMISSION_UNCERTAIN', 'root': root,
                 'maximum_allocated_CPU_hours': MAXIMUM_CPU_HOURS,
                 'stage': 'reverse_full150_xyz_zyx_matched_order_pair', 'preflight': preflight}
        budget_after = json.loads(json.dumps(budget))
        budget_after['reserved_maximum_allocated_CPU_hours'] += MAXIMUM_CPU_HOURS
        budget_after.setdefault('jobs', []).append(entry)
        budget_after['updated_utc'] = utc()
        # Intent and reservation are durable before any remote sbatch-capable code.
        save(INTENT, entry, exclusive=True)
        save(LEDGER, budget_after)

        try:
            verified = _remote_verify(root, files)
            if verified.get('state') != 'REMOTE_INTEGRITY_PASS' or verified.get('files') != files:
                raise RuntimeError('fresh remote integrity check failed; reservation retained')
            response = run_json(_remote_integrity_body(root, files, perform_submit=True), timeout=90)
            save(RECEIPT, response, exclusive=True)
            job_id = response.get('job_id')
            if not isinstance(job_id, str) or not job_id.isdigit() or response.get('returncode') != 0:
                raise RuntimeError('sbatch response is ambiguous; reservation retained and reconcile Iris')
        except Exception as exc:
            save(UNCERTAIN, {'utc': utc(), 'root': root,
                 'reason': type(exc).__name__ + ': ' + str(exc)[:300],
                 'instruction': 'Keep full reservation. Reconcile local and remote intent plus squeue; never blindly retry.'}, exclusive=True)
            raise

        entry.update(state='SUBMITTED', job_id=job_id, submitted_utc=utc())
        budget_after['jobs'][-1].update(entry)
        budget_after['updated_utc'] = utc()
        save(LEDGER, budget_after)
        save(INTENT, entry)
        return job_id


def require_local_attempt_free() -> None:
    require_no_local_attempt(E)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('seal', 'deploy', 'precheck', 'submit'))
    args = parser.parse_args(argv)
    files = seal()
    if args.action == 'seal':
        print(json.dumps({'sealed': True, 'files': len(files)}))
    elif args.action == 'deploy':
        print(json.dumps(deploy(files), sort_keys=True))
    elif args.action == 'precheck':
        print(json.dumps(precheck(files), sort_keys=True))
    else:
        print(json.dumps({'job_id': submit(files)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

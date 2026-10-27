#!/usr/bin/env python3
"""Seal, deploy, precheck, and submit one reviewed native NSCC triple.

Submission is deliberately one-shot. A durable intent and full SU reservation
are written before qsub; any uncertain response requires independent PBS
reconciliation and must never trigger a blind retry.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import sys
import tarfile
from typing import Any, Callable


CAMPAIGN = Path(__file__).resolve().parent.parent
EXPERIMENT = CAMPAIGN / 'native-wave'
RESEARCH = CAMPAIGN.parent
ACCOUNT = Path('/home/apacsc42')
SSH = RESEARCH / 'tools/nscc-cpu-ssh.sh'
VPN = ACCOUNT / 'workspace/vpn-rootless/vpn.sh'
CPU_LEDGER_DIR = RESEARCH / 'nscc-cpu-timing-probe-20261021'
CPU_LEDGER = CPU_LEDGER_DIR / 'cpu-budget.json'
CPU_LOCK = CPU_LEDGER_DIR / 'cpu-budget.lock'
AI_LOCK = ACCOUNT / '2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/budget.lock'
ROOT_REVIEW = EXPERIMENT / 'ROOT_REVIEW.json'
MANIFEST = EXPERIMENT / 'payload-sha256.json'
DEPLOYMENT = EXPERIMENT / 'deployment.json'
PRECHECK = EXPERIMENT / 'pre-submit-checks.json'
INTENT = EXPERIMENT / 'submission-intent.json'
RECEIPT = EXPERIMENT / 'submission.json'
UNCERTAIN = EXPERIMENT / 'submission-uncertain.json'
PROJECT = '59000042'
GRANT_SU = 30000.0
RATE_SU_PER_CPU_HOUR = 1.0
NEW_MAXIMUM_SU = 512 * 90 / 60 * RATE_SU_PER_CPU_HOUR
REMOTE_PREFIX = '/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-nscc-native-'
JOB_ID = re.compile(r'^\d+(?:\[\d+\])?\.pbs\d+(?:\[\d+\])?$')


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path: Path, value: Any, *, exclusive: bool = False) -> None:
    """Fsync a new JSON file and its parent; never replace when exclusive."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + f'.{os.getpid()}.tmp')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path if exclusive else tmp, flags, 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        if not exclusive:
            os.replace(tmp, path)
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if not exclusive:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass
        raise


def _safe_relative(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts and str(p) == name


def payload_hashes(experiment: Path = EXPERIMENT) -> dict[str, str]:
    root = experiment / 'payload'
    if not root.is_dir() or root.is_symlink():
        raise ValueError('payload directory missing or symlinked')
    result: dict[str, str] = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'symlink forbidden in payload: {path.relative_to(experiment)}')
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            name = path.relative_to(experiment).as_posix()
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if not result:
        raise ValueError('empty payload')
    return result


def reviewed_hashes(experiment: Path = EXPERIMENT) -> dict[str, str]:
    actual = payload_hashes(experiment)
    saved = json.loads((experiment / 'payload-sha256.json').read_text())
    review = json.loads((experiment / 'ROOT_REVIEW.json').read_text())
    expected = saved.get('files')
    if expected != actual:
        raise ValueError('payload differs from frozen manifest; inspect and reseal explicitly')
    if review.get('passed') is not True or review.get('payload_sha256') != expected:
        raise ValueError('root review missing, failed, or bound to different payload hashes')
    for name, digest in expected.items():
        if not _safe_relative(name) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError('invalid manifest path or digest')
    return expected


def seal(experiment: Path = EXPERIMENT) -> dict[str, str]:
    """Write a hash manifest only if absent; never mutate an existing seal."""
    hashes = payload_hashes(experiment)
    manifest = experiment / 'payload-sha256.json'
    if manifest.exists():
        if json.loads(manifest.read_text()).get('files') != hashes:
            raise ValueError('existing manifest differs; do not reseal implicitly')
    else:
        atomic_json(manifest, {'created_utc': utc(), 'files': hashes}, exclusive=True)
    return hashes


def parse_project_report(text: str) -> dict[str, float]:
    """Parse the documented myprojects pipe rows; reject ambiguous values."""
    project_headers = re.findall(r'(?m)^Project\s+(\d+)\s+balance\b', text)
    if project_headers and any(project != PROJECT for project in project_headers):
        raise ValueError('project report header does not match selected project')
    rows = [line.strip() for line in text.splitlines() if line.strip().startswith('|')]
    su = [row for row in rows if re.match(r'^\|\s*SU\s*\|', row)]
    cpu = [row for row in rows if re.match(r'^\|\s*CPU\s+Hour\s*\|', row)]
    if len(su) != 1 or len(cpu) != 1:
        raise ValueError('project report does not contain exactly one SU and CPU Hour row')
    values = [x.strip() for x in su[0].strip('|').split('|')]
    if len(values) != 5 or values[0] != 'SU':
        raise ValueError('unrecognized SU report row')
    grant, used, balance, in_doubt = [_finite_number(x) for x in values[1:]]
    rate_values = [x.strip() for x in cpu[0].strip('|').split('|')]
    if len(rate_values) < 4:
        raise ValueError('unrecognized CPU Hour report row')
    rate = _finite_number(rate_values[2])
    if grant != GRANT_SU or rate != RATE_SU_PER_CPU_HOUR:
        raise ValueError('unexpected grant or CPU SU rate')
    if min(used, balance, in_doubt) < 0:
        raise ValueError('negative project value')
    return {'grant_SU': grant, 'used_SU': used, 'balance_SU': balance,
            'in_doubt_SU': in_doubt, 'rate_SU_per_CPU_hour': rate}


def _finite_number(value: str | float | int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'not a numeric value: {value!r}') from exc
    if not math.isfinite(number):
        raise ValueError('non-finite financial or queue value')
    return number


def parse_qstat_json(text: str, *, user: str = 'apacsc42') -> list[dict[str, str]]:
    """Return sanitized own-job identity/state only; never retain Variable_List."""
    data = json.loads(text)
    jobs = data.get('Jobs')
    if not isinstance(jobs, dict):
        raise ValueError('qstat JSON missing Jobs object')
    result = []
    for job_id, info in jobs.items():
        if not isinstance(info, dict):
            raise ValueError('malformed qstat job record')
        if not isinstance(info.get('Job_Owner'), str) or not info['Job_Owner']:
            raise ValueError('qstat job record missing Job_Owner; queue provenance is ambiguous')
        owner = info['Job_Owner'].split('@', 1)[0]
        if owner != user:
            continue
        state = str(info.get('job_state', '')).upper()
        if not state or not JOB_ID.fullmatch(str(job_id)):
            raise ValueError('qstat returned malformed own job identity/state')
        result.append({'id': str(job_id), 'state': state})
    return sorted(result, key=lambda item: item['id'])


def pbs_script(hashes: dict[str, str], experiment: Path = EXPERIMENT) -> str:
    """Select and validate the single frozen native-wave PBS script."""
    scripts = [name for name in hashes if name.startswith('payload/') and name.endswith('.pbs')]
    if len(scripts) != 1:
        raise ValueError('frozen manifest must contain exactly one PBS script')
    name = scripts[0]
    body = (experiment / name).read_text()
    directives = [line.strip() for line in body.splitlines() if line.lstrip().startswith('#PBS')]
    required = (
        re.compile(r'^#PBS\s+-P\s+59000042$'),
        re.compile(r'^#PBS\s+-l\s+select=4:ncpus=128:mpiprocs=128:[^\s]*ngpus=0$'),
        re.compile(r'^#PBS\s+-l\s+place=scatter:excl$'),
        re.compile(r'^#PBS\s+-l\s+walltime=01:30:00$'),
    )
    for pattern in required:
        if sum(bool(pattern.fullmatch(line)) for line in directives) != 1:
            raise ValueError('PBS script does not request project 59000042, 4x128 CPUs, 90 min, ngpus=0, place=scatter:excl')
    return name


def financial_admission(ledger: dict[str, Any], report: dict[str, float], maximum: float = NEW_MAXIMUM_SU) -> dict[str, float]:
    """Compute conservative campaign and live-credit gates without retiring reservations."""
    if ledger.get('schema') != 2 or ledger.get('project') != PROJECT:
        raise ValueError('CPU ledger schema/project mismatch')
    ceiling = _finite_number(ledger.get('baseline_wave_planning_ceiling_SU'))
    baseline_used = _finite_number(ledger.get('published_snapshot', {}).get('used_SU'))
    consumed = _finite_number(ledger.get('consumed_ceiling_SU'))
    outstanding = _finite_number(ledger.get('outstanding_reserved_max_SU'))
    maximum = _finite_number(maximum)
    if min(ceiling, baseline_used, consumed, outstanding, maximum) < 0:
        raise ValueError('negative ledger or request value')
    expected_reserved = _finite_number(ledger.get('reserved_max_SU'))
    # Preserve the maximum of the ledger's extant reservation and its explicit
    # entries. Unknown/missing job maxima are not inferred as zero.
    jobs = ledger.get('jobs')
    if not isinstance(jobs, list):
        raise ValueError('ledger jobs list missing')
    intent_sum = 0.0
    for job in jobs:
        if not isinstance(job, dict) or 'maximum_SU' not in job:
            raise ValueError('ledger contains a job with unknown maximum')
        amount = _finite_number(job['maximum_SU'])
        if amount < 0:
            raise ValueError('negative job maximum')
        if job.get('state') in {'SUBMITTED', 'SUBMISSION_INTENT', 'RESERVED', 'UNKNOWN'}:
            intent_sum += amount
    if intent_sum > outstanding + 1e-6:
        raise ValueError('ledger outstanding maximum is below explicit unresolved job maxima')
    if expected_reserved + 1e-6 < consumed + outstanding:
        raise ValueError('ledger reserved_max_SU is inconsistent with consumed plus outstanding')
    delta = max(0.0, report['used_SU'] - baseline_used)
    fresh_consumed = max(consumed, math.ceil(delta + 1.0))
    campaign_total = fresh_consumed + outstanding + maximum
    live_available = report['balance_SU'] - report['in_doubt_SU']
    required_live = outstanding + maximum
    if campaign_total > ceiling + 1e-9:
        raise ValueError('cumulative research ceiling would be exceeded')
    if live_available + 1e-9 < required_live:
        raise ValueError('fresh project balance less in-doubt amount cannot cover outstanding plus request')
    return {'consumed_ceiling_SU': fresh_consumed, 'outstanding_reserved_max_SU': outstanding,
            'request_maximum_SU': maximum, 'campaign_total_after_SU': campaign_total,
            'campaign_ceiling_SU': ceiling, 'live_available_after_indoubt_SU': live_available,
            'live_required_for_existing_plus_request_SU': required_live}


def enforce_queue_caps(cpu_jobs: list[dict[str, str]], ai_jobs: list[dict[str, str]]) -> None:
    # All jobs owned by this shared account count until provenance/state has
    # been explicitly reconciled. Held and queued jobs remain in these lists.
    if cpu_jobs:
        raise ValueError('CPU PBS queue contains shared-account jobs; reconcile provenance and reservations')
    if len(cpu_jobs) + len(ai_jobs) + 1 > 3:
        raise ValueError('combined own CPU/AI PBS cap of three would be exceeded')


def project_reference() -> str:
    return "myprojects -p " + shlex.quote(PROJECT)


def _run_local(args: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, input=input_bytes, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True, timeout=120)


def _cpu(command: str) -> subprocess.CompletedProcess:
    return _run_local(['bash', str(SSH), 'bash -lc ' + shlex.quote(command)])


def _ai(command: str) -> subprocess.CompletedProcess:
    return _run_local(['bash', str(VPN), 'ssh-batch', "bash -lc " + shlex.quote(command)])


def _qstat() -> str:
    return 'qstat -f -F json -u apacsc42'


def _queue_snapshots(cpu_query: Callable[[str], subprocess.CompletedProcess] = _cpu,
                     ai_query: Callable[[str], subprocess.CompletedProcess] = _ai) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    cpu_jobs = parse_qstat_json(cpu_query(_qstat()).stdout.decode())
    ai_jobs = parse_qstat_json(ai_query(_qstat()).stdout.decode())
    return cpu_jobs, ai_jobs


def _safe_precheck(ledger: dict[str, Any], cpu_jobs: list[dict[str, str]], ai_jobs: list[dict[str, str]],
                   report: dict[str, float]) -> dict[str, Any]:
    fin = financial_admission(ledger, report)
    enforce_queue_caps(cpu_jobs, ai_jobs)
    return {'utc': utc(), 'project': PROJECT, 'request': {'ncpus': 512, 'walltime_seconds': 5400,
            'maximum_SU': NEW_MAXIMUM_SU}, 'cpu_jobs': cpu_jobs, 'ai_jobs': ai_jobs,
            'combined_jobs_before': len(cpu_jobs) + len(ai_jobs), 'financial': fin}


def capture_precheck(*, cpu_query: Callable[[str], subprocess.CompletedProcess] = _cpu,
                     ai_query: Callable[[str], subprocess.CompletedProcess] = _ai,
                     report_query: Callable[[str], subprocess.CompletedProcess] = _cpu,
                     ledger_path: Path = CPU_LEDGER, output: Path = PRECHECK) -> dict[str, Any]:
    """Capture sanitized success or failure; this never writes intent or ledger."""
    try:
        cpu_jobs, ai_jobs = _queue_snapshots(cpu_query, ai_query)
        report_text = report_query(project_reference()).stdout.decode()
        report = parse_project_report(report_text)
        ledger = json.loads(ledger_path.read_text())
        result = _safe_precheck(ledger, cpu_jobs, ai_jobs, report)
        result['state'] = 'ADMISSIBLE_AT_PRECHECK_ONLY'
    except Exception as exc:
        # No raw command output, environment, or credential details are saved.
        result = {'utc': utc(), 'state': 'BLOCKED', 'reason': type(exc).__name__ + ': ' + str(exc)[:300]}
    atomic_json(output, result)
    return result


def _tar_payload(hashes: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
        for name in sorted(hashes):
            archive.add(EXPERIMENT / name, arcname=name, recursive=False)
        archive.add(MANIFEST, arcname='payload-sha256.json', recursive=False)
    return buffer.getvalue()


def deploy(*, transport: Callable[[str, bytes], subprocess.CompletedProcess] | None = None) -> dict[str, Any]:
    hashes = reviewed_hashes(EXPERIMENT)
    pbs_name = pbs_script(hashes, EXPERIMENT)
    if DEPLOYMENT.exists():
        raise FileExistsError('deployment record exists; inspect and never overwrite')
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    remote_root = REMOTE_PREFIX + stamp
    code = '''import hashlib,io,json,sys,tarfile
from pathlib import Path
r=Path(ROOT);r.mkdir(parents=True,exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as t:
 for m in t.getmembers():
  p=Path(m.name)
  assert m.isfile() and not p.is_absolute() and '..' not in p.parts
  out=r/m.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(t.extractfile(m).read())
x=json.loads((r/'payload-sha256.json').read_text())['files']
actual=sorted(p.relative_to(r).as_posix() for p in r.rglob('*') if p.is_file() and p.name!='payload-sha256.json')
assert actual==sorted(x)
assert all(hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in x.items())
print(json.dumps({'root':str(r),'files':x},sort_keys=True))
'''.replace('ROOT', repr(remote_root))
    command = 'python3 -c ' + shlex.quote(code)
    if transport is None:
        result = _run_local(['bash', str(SSH), command], input_bytes=_tar_payload(hashes))
    else:
        result = transport(command, _tar_payload(hashes))
    record = json.loads(result.stdout.decode())
    if record != {'files': hashes, 'root': remote_root}:
        raise ValueError('remote deployment response did not match reviewed manifest')
    saved = dict(record, created_utc=utc(), state='DEPLOYED_NOT_SUBMITTED', pbs_script=pbs_name)
    atomic_json(DEPLOYMENT, saved, exclusive=True)
    return saved


def _remote_hash_verify(root: str, cpu_query: Callable[[str], subprocess.CompletedProcess] = _cpu) -> str:
    code = """import hashlib,json
from pathlib import Path
r=Path(ROOT);x=json.loads((r/'payload-sha256.json').read_text())['files']
assert not any(p.is_symlink() for p in r.rglob('*'))
actual=sorted(p.relative_to(r).as_posix() for p in r.rglob('*') if p.is_file() and p.name!='payload-sha256.json')
assert actual==sorted(x), (actual,sorted(x))
assert all(hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in x.items())
print(json.dumps({'root':str(r),'files':x},sort_keys=True))
""".replace('ROOT', repr(root))
    return cpu_query('python3 -c ' + shlex.quote(code)).stdout.decode().strip()


def submit(*, cpu_query: Callable[[str], subprocess.CompletedProcess] = _cpu,
           ai_query: Callable[[str], subprocess.CompletedProcess] = _ai,
           ledger_path: Path = CPU_LEDGER, cpu_lock_path: Path = CPU_LOCK,
           ai_lock_path: Path = AI_LOCK,
           qsub: Callable[[str], subprocess.CompletedProcess] | None = None) -> str:
    hashes = reviewed_hashes(EXPERIMENT)
    if INTENT.exists() or RECEIPT.exists() or UNCERTAIN.exists():
        raise FileExistsError('submission artifact exists; reconcile PBS and never retry blindly')
    deployment = json.loads(DEPLOYMENT.read_text())
    root = deployment.get('root', '')
    if deployment.get('state') != 'DEPLOYED_NOT_SUBMITTED' or deployment.get('files') != hashes:
        raise ValueError('deployment is missing or does not match reviewed manifest')
    if not re.fullmatch(re.escape(REMOTE_PREFIX) + r'\d{8}T\d{6}Z', root):
        raise ValueError('deployment root has unexpected path')
    pbs_name = pbs_script(hashes, EXPERIMENT)
    if deployment.get('pbs_script') != pbs_name:
        raise ValueError('deployment PBS script does not match the unique frozen script')
    if not ledger_path.exists():
        raise FileNotFoundError('CPU budget ledger missing')
    with cpu_lock_path.open('a') as cpu_lock:
        fcntl.flock(cpu_lock, fcntl.LOCK_EX)
        with ai_lock_path.open('a') as ai_lock:
            fcntl.flock(ai_lock, fcntl.LOCK_EX)
            if INTENT.exists() or RECEIPT.exists() or UNCERTAIN.exists():
                raise FileExistsError('submission artifact appeared under lock; inspect and do not retry')
            cpu_jobs, ai_jobs = _queue_snapshots(cpu_query, ai_query)
            report_text = cpu_query(project_reference()).stdout.decode()
            report = parse_project_report(report_text)
            ledger = json.loads(ledger_path.read_text())
            check = _safe_precheck(ledger, cpu_jobs, ai_jobs, report)
            check['deployment_root'] = root
            check['payload_sha256'] = hashes
            check['pbs_script'] = pbs_name
            if _remote_hash_verify(root, cpu_query) != json.dumps({'files': hashes, 'root': root}, sort_keys=True):
                raise ValueError('deployed file set or hashes do not match the frozen manifest')
            atomic_json(PRECHECK, check)

            fin = check['financial']
            new_ledger = json.loads(json.dumps(ledger))
            new_ledger['consumed_ceiling_SU'] = fin['consumed_ceiling_SU']
            new_ledger['outstanding_reserved_max_SU'] = fin['outstanding_reserved_max_SU'] + NEW_MAXIMUM_SU
            new_ledger['reserved_max_SU'] = new_ledger['planning_committed_SU'] = (
                fin['consumed_ceiling_SU'] + new_ledger['outstanding_reserved_max_SU'])
            new_ledger['updated_utc'] = utc()
            entry = {'id': None, 'root': root, 'maximum_SU': NEW_MAXIMUM_SU,
                     'branch': 'native_scotch_hxyz_hzyx_triple_90min',
                     'state': 'SUBMISSION_INTENT', 'observed_utc': utc(),
                     'payload_sha256': hashes}
            new_ledger.setdefault('jobs', []).append(entry)
            intent_value = {'utc': utc(), 'root': root, 'project': PROJECT,
                            'maximum_SU': NEW_MAXIMUM_SU, 'payload_sha256': hashes,
                            'state': 'RESERVED_DO_NOT_RETRY_BLINDLY'}
            # Intent is the idempotency gate. Reserve durably before qsub.
            atomic_json(INTENT, intent_value, exclusive=True)
            atomic_json(ledger_path, new_ledger)

            submit_call = qsub or (lambda cmd: cpu_query(cmd))
            command = 'cd ' + shlex.quote(root) + ' && qsub ' + shlex.quote(pbs_name)
            try:
                result = submit_call(command)
                stdout = result.stdout.decode() if isinstance(result.stdout, bytes) else str(result.stdout)
                stderr = result.stderr.decode() if isinstance(result.stderr, bytes) else str(result.stderr)
                job_id = stdout.strip()
                if getattr(result, 'returncode', 0) != 0 or not JOB_ID.fullmatch(job_id):
                    raise RuntimeError('qsub response is ambiguous; preserve reservation and reconcile PBS')
                receipt = {'utc': utc(), 'root': root, 'stdout': stdout, 'stderr': stderr,
                           'returncode': 0, 'project': PROJECT, 'maximum_SU': NEW_MAXIMUM_SU,
                           'ncpus': 512, 'maximum_seconds': 5400, 'job_id': job_id}
                atomic_json(RECEIPT, receipt, exclusive=True)
            except Exception as exc:
                atomic_json(UNCERTAIN, {'utc': utc(), 'root': root,
                    'reason': type(exc).__name__ + ': ' + str(exc)[:300],
                    'instruction': 'Reservation retained. Query PBS and reconcile; never blindly resubmit.'}, exclusive=True)
                raise

            new_ledger['jobs'][-1].update(id=job_id, state='SUBMITTED', observed_utc=utc())
            new_ledger['updated_utc'] = utc()
            atomic_json(ledger_path, new_ledger)
            intent_value.update(state='SUBMITTED', job_id=job_id, updated_utc=utc())
            # Replace the intent atomically only after a definite receipt.
            atomic_json(INTENT, intent_value)
            return job_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('seal', 'deploy', 'precheck', 'submit'))
    args = parser.parse_args(argv)
    if args.action == 'seal':
        print(json.dumps({'files': seal()}, sort_keys=True))
    elif args.action == 'deploy':
        print(json.dumps(deploy(), sort_keys=True))
    elif args.action == 'precheck':
        result = capture_precheck()
        print(json.dumps(result, sort_keys=True))
        return 0 if result['state'] == 'ADMISSIBLE_AT_PRECHECK_ONLY' else 2
    else:
        print(submit())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

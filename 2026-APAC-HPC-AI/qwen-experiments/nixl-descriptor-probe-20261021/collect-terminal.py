#!/usr/bin/env python3
"""Seal probe evidence, exclude raw exchange and replay independent byte checks."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import shlex
import subprocess
import tarfile

O = Path(__file__).resolve().parent
receipt = json.loads((O / 'pbs-receipt.json').read_text())
job = receipt['job']
number = job.split('.')[0]
root = '/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/' + O.name
helper = '/home/apacsc42/workspace/vpn-rootless/vpn.sh'

def remote(command, stream=None):
    return subprocess.run(['bash', helper, 'ssh-batch', 'bash -lc ' + shlex.quote(command)],
        stdout=stream if stream else subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)

q = remote('qstat -xf ' + job)
assert q.returncode == 0
account = q.stdout.decode()
assert re.search(r'Job_Owner\s*=\s*apacsc42@', account)
state = re.search(r'job_state\s*=\s*(\S+)', account)[1]
if state != 'F':
    print('NOT_TERMINAL', job, state)
    raise SystemExit(0)
D = O / 'collected' / job
assert not D.exists(), 'Never overwrite evidence; a failed collection requires an explicit recovery path'
D.mkdir(parents=True)
(D / 'pbs-accounting.txt').write_text(account)
with (D / 'raw-artifacts.tar.gz').open('wb') as stream:
    result = remote('cd ' + root + ' && files=(runs/' + job + '); for f in ./*.o' + number
        + ' ./*.e' + number + '; do if [[ -f "$f" ]]; then files+=("$f"); fi; done; tar -czf - "${files[@]}"', stream)
assert result.returncode == 0
with tarfile.open(D / 'raw-artifacts.tar.gz') as tar:
    members = tar.getmembers()
    assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
        and (m.isfile() or m.isdir()) and 'runtime-peer-state' not in Path(m.name).parts
        and '.descriptor-private' not in Path(m.name).parts for m in members)
    tar.extractall(D, members=members, filter='data')
run = D / 'runs' / job
checksums = subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=run / 'submitted',
    capture_output=True, text=True)
(D / 'payload-checksums.txt').write_text(checksums.stdout + checksums.stderr)
assert checksums.returncode == 0
assert (run / 'submitted/SHA256SUMS').read_bytes() == (O / 'SHA256SUMS').read_bytes()
spec = importlib.util.spec_from_file_location('frozen_descriptor', run / 'submitted/descriptor.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
semantic = module.check(run)
(D / 'semantic-replay.json').write_text(json.dumps(semantic, indent=2) + '\n')
head = json.loads((run / 'head-result-check.json').read_text()) if (run / 'head-result-check.json').exists() else None
exit_status = int(re.search(r'Exit_status\s*=\s*(-?\d+)', account)[1])
passed = exit_status == 0 and semantic['status'] == 'pass' and head == semantic
h, m, sec = map(int, re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)', account).groups())
walltime = h*3600 + m*60 + sec
ranks = [json.loads(p.read_text()) if p.exists() else None
         for p in [run / 'rank0-result.json', run / 'rank1-result.json']]
# Preserve and inspect actual task and joined PBS logs; empty task logs are not
# evidence of absence because pbsdsh may forward output to PBS stdout instead.
logs = [*run.glob('*task.log'), *D.glob('*.o' + number), *D.glob('*.e' + number)]
pattern = re.compile(r'NIXL_ERR|REMOTE_DISCONNECT|metadata.*not.*found|Traceback|UCX.*ERROR|out of memory', re.I)
log_review = {'inspected': [str(p.relative_to(D)) for p in logs],
    'bytes': {str(p.relative_to(D)): p.stat().st_size for p in logs},
    'matching_lines': [{'path': str(p.relative_to(D)), 'line': n, 'text': line[:800]}
        for p in logs for n, line in enumerate(p.read_text(errors='replace').splitlines(), 1)
        if pattern.search(line)]}
(D / 'log-review.json').write_text(json.dumps(log_review, indent=2) + '\n')
seal = {str(p.relative_to(D)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(D.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
(D / 'evidence-sha256.json').write_text(json.dumps(seal, indent=2) + '\n')
result = dict(job=job, collected_utc=datetime.now(timezone.utc).isoformat(),
    state='SGLANG_NIXL_DESCRIPTOR_PASS' if passed else 'SGLANG_NIXL_DESCRIPTOR_FAILED_REVIEW_REQUIRED',
    exit_status=exit_status, payload_and_raw_hashes_verified=True,
    semantic_replayed_without_raw_mutation=True, semantic=semantic, head_result=head,
    rank_results=ranks, walltime_s=walltime, estimated_allocated_charge_su=walltime*2*128/3600,
    model_loaded=False, private_peer_exchange_collected=False,
    ranked_performance_measured=False, official_accuracy_verified=False,
    log_review=log_review,
    hardware_telemetry='No utilization, power, VRAM or CPU-demand sampling; recorded GPU/host identity and transfer evidence only',
    scope='24 actual descriptor writes on two physical GPUs with virtual TP4/TP8 ranks, uniform small synthetic buffers; not native full SGLang/EAGLE3 integration')
(O / 'collection.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ('rank_results', 'log_review')}, indent=2))

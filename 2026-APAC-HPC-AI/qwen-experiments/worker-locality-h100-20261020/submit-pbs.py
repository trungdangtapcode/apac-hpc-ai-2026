"""Submit one serial H100 locality baseline after fresh locked budget checks."""
import datetime
import fcntl
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess

O = Path(__file__).resolve().parent
R = O.parent
P = R / 'nscc-pbs'
REMOTE = '/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
receipt_path = O / 'pbs-receipts.json'
spec = importlib.util.spec_from_file_location('costs', R / 'startup-prefetch-confirm-20261020/reconcile_costs.py')
costs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(costs)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def remote(command, stdin=None):
    return subprocess.run(['bash', '/home/apacsc42/workspace/vpn-rootless/vpn.sh', 'ssh-batch',
                           'bash -lc ' + shlex.quote(command)], stdin=stdin,
                          capture_output=True, timeout=50)


assert not receipt_path.exists(), 'Existing submission: do not retry'
assert json.loads((O / 'validation.json').read_text())['passed']
pilot, = json.loads((O / 'pilots.json').read_text())
assert pilot['max_su'] == 1024 and pilot['minutes'] == 30
name = pilot['id']
subprocess.run(['sha256sum', '--check', 'SHA256SUMS'], cwd=pilot['bundle'], capture_output=True, check=True)
with (O / 'pbs-bundle.tar.gz').open('rb') as archive:
    upload = remote('cd ' + shlex.quote(REMOTE) + ' && test ! -e ' + shlex.quote(name)
                    + ' && tar -xzf - && cd ' + shlex.quote(name) + ' && sha256sum --check SHA256SUMS', archive)
(O / 'pbs-upload.txt').write_bytes(upload.stdout)
(O / 'pbs-upload.stderr').write_bytes(upload.stderr)
assert upload.returncode == 0, 'Upload failed; no reservation or qsub'
with (P / 'budget.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    budget = json.loads((P / 'nscc-budget.json').read_text())
    assert not budget['uncertain_pbs_jobs']
    save(O / 'budget-before.json', budget)
    code = "import subprocess\nfor argv in [['qstat','-u','apacsc42'],['qstat','-xf','222407.pbs111','222408.pbs111','222412.pbs111','222419.pbs111','222420.pbs111'],['myprojects']]:\n p=subprocess.run(argv,capture_output=True,text=True);print(p.stdout,end='');print(p.stderr,end='');assert p.returncode==0\n"
    result = remote('python3 -c ' + shlex.quote(code))
    (O / 'pbs-pre-submit.txt').write_bytes(result.stdout)
    (O / 'pbs-pre-submit.stderr').write_bytes(result.stderr)
    assert result.returncode == 0
    text = re.sub(r'(?<![\d.])-0\.000(?=\s*\|)', '0.000', result.stdout.decode())
    active = re.findall(r'^\s*(\d+\.pbs\d+)\s+', text, re.M)
    assert set(active) <= {'222420.pbs111'} and len(active) + 1 <= 3, 'Unexpected active own jobs'
    proof = costs.reconcile(budget, text, now(), str(O / 'pbs-pre-submit.txt'))
    save(O / 'reconciliation.json', proof)
    assert proof['states']['222419.pbs111'] == 'F'
    assert proof['states']['222420.pbs111'] in {'Q', 'R', 'F', 'E'}, 'Preserve control dependency'
    outstanding = sum(x['max_charge_su'] for x in budget['pending_reservations']
                      if x['state'] not in {'RECONCILED_IN_LEDGER', 'CANCELLED', 'RELEASED'})
    used = budget['ledger']['used_su']
    headroom = budget['commissioning_cap_su'] - used - outstanding - 1024
    assert headroom >= 0
    assert budget['ledger']['grant_su'] - used - outstanding - 1024 >= budget['retain_project_su']
    budget['ledger'].update(queried_utc=now(), source=str(O / 'pbs-pre-submit.txt'),
                           as_of=re.search(r'balance as of (\S+)', text).group(1),
                           freshness_note='Fresh unique cost reconciliation before one bounded locality capture.')
    reservation = dict(purpose=name, state='RESERVED_NOT_SUBMITTED', max_charge_su=1024,
                       requested_gpus=16, requested_walltime='00:30:00', reserved_utc=now())
    budget['pending_reservations'].append(reservation)
    budget.update(updated_utc=now(), active_pbs_jobs=active,
                  unallocated_commissioning_su=headroom, campaign_headroom_after_reserved_su=headroom,
                  reconciliation_note='Reserve one actual H100 worker placement capture after the off-control; budget caps unchanged.')
    save(P / 'nscc-budget.json', budget)
    record = dict(id=name, state='SUBMISSION_IN_PROGRESS', attempted_utc=now(), dependency_afterany='222420.pbs111')
    save(receipt_path, [record])
    reservation['state'] = 'SUBMISSION_IN_PROGRESS'
    save(P / 'nscc-budget.json', budget)
    try:
        result = remote('cd ' + shlex.quote(REMOTE + '/' + name)
                        + ' && sha256sum --check SHA256SUMS >/dev/null && qsub -W depend=afterany:222420.pbs111 benchmark.pbs')
    except Exception:
        record['state'] = reservation['state'] = 'SUBMISSION_UNCERTAIN'
        budget['uncertain_pbs_jobs'].append(name)
        save(receipt_path, [record])
        save(P / 'nscc-budget.json', budget)
        raise
    (O / 'submit.stdout').write_bytes(result.stdout)
    (O / 'submit.stderr').write_bytes(result.stderr)
    ids = re.findall(r'^\s*(\d+\.pbs\d+)\s*$', result.stdout.decode(), re.M)
    if result.returncode or len(ids) != 1:
        record['state'] = reservation['state'] = 'SUBMISSION_UNCERTAIN'
        budget['uncertain_pbs_jobs'].append(name)
        save(receipt_path, [record])
        save(P / 'nscc-budget.json', budget)
        raise RuntimeError('Uncertain qsub: do not retry')
    job, = ids
    record.update(job=job, state='SUBMITTED', submitted_utc=now())
    save(receipt_path, [record])
    reservation.update(job_id=job, state='SUBMITTED_PENDING_ACCOUNTING', submitted_utc=record['submitted_utc'])
    budget['jobs'].append(dict(job_id=job, bundle=name, state='SUBMITTED', requested_gpus=16,
                              requested_walltime='00:30:00', max_charge_su=1024,
                              included_in_ledger_used=False, accounting_pending=True,
                              dependency_afterany='222420.pbs111', planned_ns=[54], submitted_utc=record['submitted_utc']))
    budget['active_pbs_jobs'].append(job)
    save(P / 'nscc-budget.json', budget)
    plan = json.loads((P / 'continuous-plan.json').read_text())
    assert not any(p['id'] == name for p in plan['pilots'])
    plan['pilots'].append(dict(id=name, bundle=pilot['bundle'], job_id=job, state='H',
                               max_su=1024, minutes=30, ns=[54], uploaded=True,
                               payload_sha256=pilot['payload_sha256'], diagnostic_profile=True,
                               resource_monitor=True, worker_locality_capture=True,
                               cpu_binding_changed=False, dependency_afterany='222420.pbs111',
                               result_state='AWAITING_BENCHMARK', accuracy_verified=False))
    plan.update(updated_utc=now(), next_bounded_step='Review pending off-control before any startup conclusion; inspect actual H100/H200 locality before changing binding. EAGLE3 remains a separate preflight.')
    save(P / 'continuous-plan.json', plan)
    result = remote('qstat -f ' + shlex.quote(job))
    (O / 'pbs-post-submit.txt').write_bytes(result.stdout)
    (O / 'pbs-post-submit.stderr').write_bytes(result.stderr)
    assert result.returncode == 0 and b'afterany:222420.pbs111' in result.stdout
    print(job, 'maximum reservation 1024 SU, internal headroom', headroom, flush=True)

"""Submit one bounded component gate after a fresh locked queue/credit check."""
from pathlib import Path
from datetime import datetime, timezone
import fcntl
import importlib.util
import json
import re
import shlex
import subprocess

O = Path(__file__).resolve().parent
P = O.parent / 'nscc-pbs'
REMOTE = '/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
HELPER = '/home/apacsc42/workspace/vpn-rootless/vpn.sh'
spec = importlib.util.spec_from_file_location('costs', O.parent / 'cpu-envelope-balance-20261020/reconcile_costs.py')
costs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(costs)

def now(): return datetime.now(timezone.utc).isoformat()
def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)
def remote(command, source=None):
    return subprocess.run(['bash', HELPER, 'ssh-batch', 'bash -lc ' + shlex.quote(command)],
                          stdin=source, capture_output=True, timeout=60)

preflight = remote('python3 -c ' + shlex.quote(json.loads((O / 'asset-preflight-code.json').read_text())['code']))
(O / 'asset-preflight.stdout').write_bytes(preflight.stdout)
(O / 'asset-preflight.stderr').write_bytes(preflight.stderr)
assert preflight.returncode == 0 and json.loads(preflight.stdout)['passed'], 'Do not allocate on missing/changed assets'

receipt = O / 'pbs-receipt.json'
assert not receipt.exists(), 'Existing attempt: never repeat uncertain qsub'
assert json.loads((O / 'validation.json').read_text())['passed']
assert json.loads((O / 'corpus-prerequisite.json').read_text())['state']=='TOKENIZER_CORPUS_PASS'
assert json.loads((O / 'native-load-prerequisite.json').read_text())['state'] == 'DRAFT_LOAD_PASS_FULL_INTEGRATION_UNVERIFIED'
if (O / 'upload-resume-verified.json').exists():
    import hashlib
    proof = json.loads((O / 'upload-resume-verified.json').read_text())
    assert proof['no_qsub_attempted_before_failure'] and proof['no_reservation_created']
    assert hashlib.sha256((O / 'SHA256SUMS').read_bytes()).hexdigest() == proof['manifest_sha256']
    upload = remote('python3 -c ' + shlex.quote(proof['check_code']))
else:
    with (O / 'payload.tar.gz').open('rb') as source:
        upload = remote('cd ' + REMOTE + ' && test ! -e ' + O.name +
                        ' && tar -xzf - && cd ' + O.name + ' && sha256sum --check SHA256SUMS', source)
(O / 'upload.stdout').write_bytes(upload.stdout)
(O / 'upload.stderr').write_bytes(upload.stderr)
assert upload.returncode == 0, 'No qsub after failed upload'
with (P / 'budget.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    budget = json.loads((P / 'nscc-budget.json').read_text())
    assert not budget['uncertain_pbs_jobs']
    excluded = {'RECONCILED_IN_LEDGER', 'CANCELLED', 'RELEASED'}
    assert not any(row.get('purpose') == O.name and row['state'] not in excluded for row in budget['pending_reservations'])
    code = "import subprocess,json\nrows=[]\nfor args in [['qstat','-u','apacsc42'],['qstat','-xf','222407.pbs111','222408.pbs111','222551.pbs111','222552.pbs111','222721.pbs111','222722.pbs111','222729.pbs111','222749.pbs111','222750.pbs111','222752.pbs111','222759.pbs111'],['myprojects']]:\n r=subprocess.run(args,capture_output=True,text=True);rows.append(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))\nprint(json.dumps(rows))\n"
    result = remote('python3 -c ' + shlex.quote(code))
    (O / 'pre-submit-commands.json').write_bytes(result.stdout)
    (O / 'pre-submit.stderr').write_bytes(result.stderr)
    assert result.returncode == 0
    commands = json.loads(result.stdout)
    assert all(row['returncode'] == 0 for row in commands)
    queue_text = commands[0]['stdout']
    text = '\n'.join(row['stdout'] for row in commands)
    (O / 'pre-submit.txt').write_text(text)
    text = re.sub(r'(?<![\d.])-0\.000(?=\s*\|)', '0.000', text)
    active = re.findall(r'^\s*(\d+\.pbs\d+)\s+', queue_text, re.M)
    assert set(active) <= {'222759.pbs111'} and len(active) + 1 <= 3, 'Only the known predecessor may remain active'
    dependency = '222759.pbs111' if active else ''
    proof = costs.reconcile(budget, text, now(), str(O / 'pre-submit.txt'))
    save(O / 'reconciliation.json', proof)
    outstanding = sum(row['max_charge_su'] for row in budget['pending_reservations'] if row['state'] not in excluded)
    reserve = 16 * 128 * 20 / 60
    used = budget['ledger']['used_su']
    assert used + outstanding + reserve <= budget['commissioning_cap_su']
    assert budget['ledger']['grant_su'] - used - outstanding - reserve >= budget['retain_project_su']
    row = dict(purpose=O.name, state='RESERVED_NOT_SUBMITTED', max_charge_su=reserve,
               requested_gpus=16, requested_walltime='00:20:00', reserved_utc=now())
    budget['pending_reservations'].append(row)
    budget['ledger'].update(queried_utc=now(), source=str(O / 'pre-submit.txt'),
                            as_of=re.search(r'balance as of (\S+)', text).group(1))
    budget.update(updated_utc=now(), active_pbs_jobs=[],
                  campaign_headroom_after_reserved_su=budget['commissioning_cap_su']-used-outstanding-reserve,
                  unallocated_commissioning_su=budget['commissioning_cap_su']-used-outstanding-reserve,
                  reconciliation_note='Reserve one 16-H100/20-minute real target-only token reference gate; unranked, no budget increase.')
    save(P / 'nscc-budget.json', budget)
    record = dict(state='SUBMISSION_IN_PROGRESS', attempted_utc=now(), bundle=O.name,
                  kind='target_token_reference_gate', requested_gpus=16, minutes=20,
                  max_su=reserve, target_inference=True, draft_model_instantiated=False, dependency_afterany=dependency)
    save(receipt, record)
    row['state'] = 'SUBMISSION_IN_PROGRESS'
    save(P / 'nscc-budget.json', budget)
    try:
        result = remote('cd ' + REMOTE + '/' + O.name + ' && sha256sum --check SHA256SUMS >/dev/null && qsub ' + ('-W depend=afterany:' + dependency + ' ' if dependency else '') + 'benchmark.pbs')
    except Exception:
        record['state'] = row['state'] = 'SUBMISSION_UNCERTAIN'
        budget['uncertain_pbs_jobs'].append(O.name)
        save(receipt, record); save(P / 'nscc-budget.json', budget)
        raise
    (O / 'submit.stdout').write_bytes(result.stdout)
    (O / 'submit.stderr').write_bytes(result.stderr)
    ids = re.findall(r'^\s*(\d+\.pbs\d+)\s*$', result.stdout.decode(), re.M)
    if result.returncode or len(ids) != 1:
        record['state'] = row['state'] = 'SUBMISSION_UNCERTAIN'
        budget['uncertain_pbs_jobs'].append(O.name)
        save(receipt, record); save(P / 'nscc-budget.json', budget)
        raise RuntimeError('Uncertain qsub; never retry blindly')
    job = ids[0]
    record.update(job=job, state='SUBMITTED', submitted_utc=now())
    row.update(job_id=job, state='SUBMITTED_PENDING_ACCOUNTING', submitted_utc=record['submitted_utc'])
    budget['jobs'].append(dict(job_id=job, bundle=O.name, kind='target_token_reference_gate',
                              state='SUBMITTED', requested_gpus=16, requested_walltime='00:20:00',
                              max_charge_su=reserve, included_in_ledger_used=False, accounting_pending=True,
                              submitted_utc=record['submitted_utc']))
    budget['jobs'][-1]['dependency_afterany'] = dependency
    budget['active_pbs_jobs'] = active + [job]
    save(receipt, record); save(P / 'nscc-budget.json', budget)
    plan = json.loads((P / 'continuous-plan.json').read_text())
    assert not any(pilot['id'] == O.name for pilot in plan['pilots'])
    plan['pilots'].append(dict(id=O.name, job_id=job, state='Q', kind='target_token_reference_gate',
                               requested_gpus=16, minutes=20, max_su=reserve, target_inference=True, dependency_afterany=dependency,
                               result_state='AWAITING_COMPONENT_CHECK'))
    plan.update(updated_utc=now(), next_bounded_step='Review actual target-only full output IDs and repeat stability before preparing separately frozen speculative comparison; no ranked benchmark.')
    save(P / 'continuous-plan.json', plan)
    state = remote('qstat -f ' + job)
    (O / 'post-submit.txt').write_bytes(state.stdout)
    (O / 'post-submit.stderr').write_bytes(state.stderr)
    assert state.returncode == 0
    if dependency:
        assert 'afterany:' + dependency in re.sub(r'\n\t', '', state.stdout.decode())
    print(job, 'maximum', reserve, 'SU; internal headroom', budget['campaign_headroom_after_reserved_su'])

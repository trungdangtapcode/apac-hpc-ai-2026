"""Refresh posted charges after both reversed startup runs; no submission."""
import datetime
import fcntl
import json
from pathlib import Path
import re
import shlex
import subprocess
from reconcile_costs import reconcile

O = Path(__file__).resolve().parent
P = O.parent / 'nscc-pbs'


def save(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


with (P / 'budget.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    budget = json.loads((P / 'nscc-budget.json').read_text())
    assert not budget['uncertain_pbs_jobs']
    assert not (O / 'budget-before-final-review.json').exists(), 'Retain original checkpoint; do not overwrite'
    save(O / 'budget-before-final-review.json', budget)
    code = "import subprocess\nfor argv in [['qstat','-u','apacsc42'],['qstat','-xf','222407.pbs111','222408.pbs111','222412.pbs111','222419.pbs111','222420.pbs111','222435.pbs111'],['myprojects']]:\n p=subprocess.run(argv,capture_output=True,text=True);print(p.stdout,end='');print(p.stderr,end='');assert p.returncode==0\n"
    result = subprocess.run(['bash', '/home/apacsc42/workspace/vpn-rootless/vpn.sh',
                             'ssh-batch', 'bash -lc ' + shlex.quote('python3 -c ' + shlex.quote(code))],
                            capture_output=True, text=True, timeout=50)
    (O / 'accounting-final.txt').write_text(result.stdout)
    (O / 'accounting-final.stderr').write_text(result.stderr)
    assert result.returncode == 0
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    text = re.sub(r'(?<![\d.])-0\.000(?=\s*\|)', '0.000', result.stdout)
    proof = reconcile(budget, text, stamp, str(O / 'accounting-final.txt'))
    outstanding = sum(x['max_charge_su'] for x in budget['pending_reservations']
                      if x['state'] not in {'RECONCILED_IN_LEDGER', 'CANCELLED', 'RELEASED'})
    budget['ledger'].update(queried_utc=stamp, source=str(O / 'accounting-final.txt'),
                            as_of=re.search(r'balance as of (\S+)', text).group(1),
                            freshness_note='Terminal reversed candidate reviewed; uniquely reconcile posted charges, retain all unposted maxima.')
    active = [job for job, state in proof['states'].items() if state not in {'F', 'X'}]
    headroom = budget['commissioning_cap_su'] - budget['ledger']['used_su'] - outstanding
    assert headroom >= 0 and budget['ledger']['grant_su'] - budget['ledger']['used_su'] - outstanding >= budget['retain_project_su']
    budget.update(updated_utc=stamp, active_pbs_jobs=active,
                  campaign_headroom_after_reserved_su=headroom, unallocated_commissioning_su=headroom,
                  reconciliation_note='Read-only balance review after the reversed pair; no new reservation or job.')
    proof.update(queried_utc=stamp, ledger=budget['ledger'], outstanding_max_su=outstanding,
                 internal_headroom_su=headroom, new_reservations=0)
    save(O / 'reconciliation-final.json', proof)
    save(P / 'nscc-budget.json', budget)
    plan = json.loads((P / 'continuous-plan.json').read_text())
    for pilot in plan['pilots']:
        job = pilot.get('job_id')
        if job in proof['states']:
            pilot['state'] = proof['states'][job]
            if job in {'222419.pbs111', '222420.pbs111'}:
                pilot.update(result_state='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS',
                             review=str(O / (job + '-review.json')), accuracy_verified=False)
    plan.update(updated_utc=stamp, next_bounded_step='Reversed prefetch confirmation misses the prospective 10% SU gate: no automatic third repeat or promotion. Inspect actual H200/H100 worker locality next; EAGLE3 remains a separate correctness-first integration branch.')
    save(P / 'continuous-plan.json', plan)
    print(json.dumps(proof))

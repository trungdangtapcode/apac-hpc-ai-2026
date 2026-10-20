"""Reconcile only uniquely explained allocated-cost deltas before reserving more."""
import itertools,re


def reconcile(budget,text,stamp,source):
    match=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',text)
    assert match
    grant,used,balance,doubt=map(float,match.groups())
    assert abs(grant-used-balance-doubt)<.01
    known={j['job_id']:j for j in budget['jobs']}
    terminal={};states={}
    for block in text.split('Job Id: ')[1:]:
        job=block.splitlines()[0].strip();state=re.search(r'^\s*job_state\s*=\s*(\S+)',block,re.M);assert state and job in known
        states[job]=state[1]
        if state[1]=='F':
            h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',block).groups())
            terminal[job]=(h*3600+m*60+s)*known[job]['requested_gpus']*budget['billing_su_per_gpu_hour']/3600
    assert states.get('222407.pbs111')==states.get('222408.pbs111')=='F'
    unposted=[j for j in terminal if not known[j].get('included_in_ledger_used')]
    zero=[j for j in unposted if terminal[j]==0];positive=[j for j in unposted if terminal[j]>0]
    delta=used-budget['ledger']['used_su']
    matches=[subset for n in range(len(positive)+1) for subset in itertools.combinations(positive,n) if abs(sum(terminal[j] for j in subset)-delta)<.002]
    assert len(matches)==1,('Unexplained or ambiguous delta',delta,terminal)
    reconciled=set(matches[0])|set(zero)
    for job in states:known[job].update(state=states[job],last_checked_utc=stamp)
    for job,cost in terminal.items():known[job]['estimated_charge_su']=cost
    for job in reconciled:known[job].update(included_in_ledger_used=True,accounting_pending=False)
    for row in budget['pending_reservations']:
        if row.get('job_id') in reconciled:row.update(state='RECONCILED_IN_LEDGER',reconciliation_source=source,last_checked_utc=stamp)
    budget['ledger'].update(used_su=used,balance_su=balance,in_doubt_su=doubt)
    return dict(published_delta_su=delta,terminal_estimated_cost_su=terminal,reconciled_jobs=sorted(reconciled),states=states,scope='Allocated cost accounting only; no scored-result acceptance is inferred')

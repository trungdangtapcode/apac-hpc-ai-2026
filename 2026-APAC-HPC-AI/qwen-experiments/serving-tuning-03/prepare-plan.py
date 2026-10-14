"""Bound a concurrency-only continuation after completed standalone repeats."""
import json
from pathlib import Path
from datetime import datetime,timezone

DIR=Path(__file__).resolve().parent;ROOT=DIR.parent;path=DIR/'load-plan.json'
assert not path.exists(), 'Refusing to overwrite an existing load-refinement plan'
state=json.loads((ROOT/'serving-tuning/registry.json').read_text())
assert not state['active'], 'Wait for the previous wave to finish'
entries={e['id']:e for e in state['entries']}
original=entries['s2-chunk4096-dense-n52'];source=entries['s2-repeat-best']
rows=[e['measurements'][0] for e in (original,source)]
assert all(r['concurrency']==52 and r['sla_pass'] and r['errors']==0 and r['cancelled_requests']==0
           and r['output_baseline_comparison']['research_eligible'] for r in rows)
rates=[r['good_output_tokens_s'] for r in rows]
assert abs(rates[0]-rates[1])/min(rates)<.01, 'Confirm the candidate before increasing load'
steps=[]
for name,n,parent in [('s3-control-n52',52,'s2-repeat-best'),('s3-best-n54',54,'s2-repeat-best'),
                      ('s3-best-n56',56,'s3-best-n54'),('s3-best-n60',60,'s3-best-n56')]:
    steps.append(dict(id=name,n=n,parent=parent,state='PLANNED',
                      purpose=f'Independent standalone N{n}; same twice-measured BF16 chunk4096/dense-graph configuration. Only concurrency changes.'))
plan=dict(created_utc=datetime.now(timezone.utc).isoformat(),state='PLANNED',
          source_experiment='s2-repeat-best',source_jobs=[r['job'] for r in rows],
          source_good_tokens_s=rates,reference_good_tokens_s=sum(rates)/2,
          max_active_jobs=4,repeat_min_gain_fraction=.02,steps=steps,
          refinement=dict(id='s3-midpoint',state='UNDECIDED'),
          repeat=dict(id='s3-best-load-repeat',state='UNDECIDED'),
          scope='At most six full independent jobs: N52/54/56/60, optional midpoint, optional winner repeat. No output/model precision changes or automatic submission promotion.',
          gates='N56 requires passing N54; N60 requires passing N56. Failed deployment is not a load boundary. Output research eligibility and full measurements required. Organiser accuracy remains unverified.')
path.write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps(plan,indent=2))

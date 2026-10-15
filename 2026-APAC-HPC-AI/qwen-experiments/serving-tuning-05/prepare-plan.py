"""Confirm round-robin routing and bracket its tighter decode latency margin."""
import json
from datetime import datetime,timezone
from pathlib import Path

DIR=Path(__file__).resolve().parent;ROOT=DIR.parent;path=DIR/'load-plan.json'
assert not path.exists(), 'Refusing to overwrite an existing research plan'
state=json.loads((ROOT/'serving-tuning/registry.json').read_text());assert not state['active']
source=next(e for e in state['entries'] if e['id']=='s4-prefill-roundrobin-n52')
row=source['measurements'][0]
assert row['concurrency']==52 and row['sla_pass'] and row['errors']==0 and row['cancelled_requests']==0
assert row['output_baseline_comparison']['research_eligible']
config=json.loads((Path(source['bundle'])/'config.json').read_text())
assert config['router_extra_flags']==['--prefill-policy','round_robin']
steps=[]
for name,n,parent,purpose in [
    ('s5-rr-repeat-n52',52,source['id'],'Independent repeat of job23325 round-robin prefill at N52; validate the 2402.64 single-point result.'),
    ('s5-rr-n50',50,source['id'],'Round-robin N50 versus N52: test more ITL headroom with identical serving and official client.'),
    ('s5-rr-n54',54,'s5-rr-repeat-n52','Round-robin N54 only after the N52 repeat passes SLA/output research checks; stop advancing after a failure.')]:
    steps.append(dict(id=name,n=n,parent=parent,purpose=purpose,state='PLANNED'))
plan=dict(created_utc=datetime.now(timezone.utc).isoformat(),state='PLANNED',
          source_experiment=source['id'],source_jobs=[row['job']],source_good_tokens_s=[row['good_output_tokens_s']],
          reference_good_tokens_s=row['good_output_tokens_s'],configuration_label='round-robin prefill, BF16 chunk4096/dense-graph',
          max_active_jobs=4,repeat_min_gain_fraction=0.0,repeat_always=True,steps=steps,
          refinement=dict(id='s5-rr-midpoint',state='UNDECIDED'),
          repeat=dict(id='s5-rr-best-repeat',state='UNDECIDED'),
          scope='At most five independent deployments: N52 repeat, N50, gated N54, optional midpoint and best-new-point confirmation. All exact serving flags preserved, only N varies.',
          reason='Round-robin measured2402.64 at N52 with98.93% SLA; mean ITL19.57ms and maximum19.90ms are close to20ms. Confirm before selection and compare a lower load.',
          accuracy_verified=False)
path.write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan,indent=2))

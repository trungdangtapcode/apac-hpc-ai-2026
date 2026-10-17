from pathlib import Path
import importlib.util,json,re
P=Path('nscc-pbs');O=P/'inspection/manual-20261017-0650'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=mod('candidate',P/'review-candidate-sweep.py');core=mod('core',Path('serving-tuning/review-n54.py'))
reports={}
for job,pilot in [('221020.pbs111','h100-mnnvl-frontier-repeat-11'),('221021.pbs111','h100-combo-frontier-repeat-12')]:
 snap=next(p.parent for p in (P/'collected'/job).glob('*/evidence-sha256.json'))
 d=m.compare(snap,P/'collected/220575.pbs111/20261016T054555388584Z',P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json',pilot)
 assert d['terminal_seal_short_payload_pass'] and d['long_diagnostic']['state']=='PASSED'
 run=snap/'runs'/job;proof={}
 for role,world,ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
  f=next(run.glob('task-'+role+'-node*.log'));log=f.read_text();args=core.server_args(f)
  assert args['tp_size']==str(world) and args['ep_size']==str(ep)
  assert args['disaggregation_transfer_backend']=="'nixl'" and 'KV Cache is allocated. dtype: torch.bfloat16' in log
  proof[role]={'tp':world,'ep':ep,'bf16_KV':True}
  if role=='decode-0':
   ranks=sorted(set(map(int,re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',log))));assert ranks==list(range(8));proof[role]['mnnvl_ranks']=ranks
   if job.startswith('221021'):
    ranks=sorted(set(map(int,re.findall(r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3',log))));assert ranks==list(range(8));proof[role]['flashinfer_ranks']=ranks
 d['runtime']=proof;(O/('review-'+job+'.json')).write_text(json.dumps(d,indent=2)+'\n');reports[job]=d
 # Failed controlN48 must be kept, not asserted away as a deployment error.
 assert all(x['protocol_pass'] and x['phase_complete'] for x in d['candidate_review']['points'])
 if job.startswith('221021'):assert all(x['latency_error_gate_pass'] for x in d['candidate_review']['points'])
(O/'pair-review.json').write_text(json.dumps({'continuation_gate_pass':True,'reports':list(reports),'accuracy_verified':False})+'\n');print('Terminal sealed protocol/short/long and runtime passed for both; failed controlN48 retained')

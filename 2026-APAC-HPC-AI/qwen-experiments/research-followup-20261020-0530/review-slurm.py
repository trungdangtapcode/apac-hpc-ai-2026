"""Seal completed runs and review unchanged raw protocol and output gates offline."""
from pathlib import Path
import csv,datetime,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
statuses={row['JobID']:row for row in csv.DictReader((O/'slurm-accounting.psv').read_text().splitlines(),delimiter='|')}
results={}
for job,n in [('24926',60),('24927',60)]:
 run=R/'runs'/job;status=statuses[job]
 assert status['State']=='COMPLETED' and status['ExitCode']=='0:0'
 seal=run/'artifact-manifest.json'
 if not seal.exists():
  paths=[p for p in run.rglob('*') if p.is_file() and p.name not in {'summary.json','artifact-manifest.json'}]
  paths.extend(p for p in [R/'runs'/(job+'.out'),R/'runs'/(job+'.err')] if p.exists())
  files=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=w.core.sha(p)) for p in sorted(paths)]
  seal.write_text(json.dumps(dict(job=job,sealed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status_at_seal=status,scope='Existing terminal files inventoried after completion; not a submission-time checksum. Derived summary.json excluded.',files=files),indent=2)+'\n')
 try:
  point=w.core.point(R,job,n);long=w.long_check(run)
  log=(run/'decode-0.log').read_text()
  for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:
   assert sorted(set(map(int,re.findall(pattern,log))))==list(range(8)),pattern
  for role,args in point['server_args'].items():
   assert args['speculative_algorithm']=='None'
   assert 'KV Cache is allocated. dtype: torch.bfloat16' in (run/(role+'.log')).read_text()
   if args['moe_runner_backend']=="'hpc_ops'":assert 'HPC_OPS_PREFLIGHT_PASSED' in (run/(role+'.log')).read_text()
  refjob='24721' if job in {'24912','24914'} else '24724'
  refpath=R/('research-followup-20261019-0527' if refjob=='24721' else 'research-followup-20261019-0600')/(refjob+'-review.json')
  reference=json.loads(refpath.read_text())['point'];assert w.core.sha(R/'runs'/refjob/'artifact-manifest.json')==reference['seal_sha256']
  assert point['normalized_protocol']==reference['normalized_protocol']
  differences={}
  for role,args in point['server_args'].items():
   ref=reference['server_args'][role];delta={k:[ref.get(k),args.get(k)] for k in args.keys()|ref.keys() if args.get(k)!=ref.get(k)}
   allowed={'random_seed'} | ({'enable_metrics'} if job=='24927' else set())
   assert not set(delta)-allowed,(role,delta)
   assert args['enable_metrics']==('True' if job=='24927' else 'False')
   differences[role]=delta
  passed=point['metrics']['sla_pass'] and long['state']=='PASSED'
  result=dict(job=job,state='LOCAL_PROTOCOL_SLA_OUTPUT_PASS' if passed else 'LOCAL_GATE_FAILED',point=point,long=long,reference_job=refjob,runtime_delta=differences,accuracy_verified=False)
 except Exception as exc:result=dict(job=job,state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(exc),accuracy_verified=False)
 results[job]=result;(O/(job+'-review.json')).write_text(json.dumps(result,indent=2)+'\n');print(job,result['state'],result.get('point',{}).get('metrics',{}),result.get('reason',''),flush=True)
(O/'slurm-reviews.json').write_text(json.dumps(results,indent=2)+'\n')

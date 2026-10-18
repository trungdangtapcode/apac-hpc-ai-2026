"""Check two new trials against same-load frozen controls."""
from pathlib import Path
import importlib.util,json,re,datetime
R=Path.cwd();O=R/'research-followup-20261018-1323';s=importlib.util.spec_from_file_location('w',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
for job,refjob,n,kind in [('24538','24526',56,'decode'),('24544','24352',58,'chunk')]:
 run=R/'runs'/job
 if not (run/'artifact-manifest.json').exists():print(job,'WAITING_FOR_TERMINAL_SEAL');continue
 p=w.core.point(R,job,n);b=w.core.point(R,refjob,n);assert p['normalized_protocol']==b['normalized_protocol'];pilot=next(x for x in json.loads((R/'serving-tuning-10/prepared-pilots.json').read_text())['pilots'] if x.get('job')==job)
 for file,h in pilot['payload_sha256'].items():assert w.core.sha(run/'submitted'/file)==h,file
 changes={}
 for role,a in p['server_args'].items():
  ref=b['server_args'][role];delta={k:[ref.get(k),a.get(k)] for k in a.keys()|ref.keys() if a.get(k)!=ref.get(k)};allowed={'random_seed'}
  if kind=='decode' and role=='decode-0':
   allowed|={'moe_runner_backend','speculative_moe_runner_backend'}
   for key in ['moe_runner_backend','speculative_moe_runner_backend']:assert delta.get(key)==["'auto'","'hpc_ops'"],delta
   assert a['speculative_algorithm']=='None';assert 'HPC_OPS_PREFLIGHT_PASSED' in (run/'decode-0.log').read_text()
  if kind=='chunk' and role.startswith('prefill'):
   allowed|={'chunked_prefill_size','cuda_graph_config'};assert delta.get('chunked_prefill_size')==['4096','8192'];cg=a['cuda_graph_config'];rg=ref['cuda_graph_config'];assert cg.split(', prefill=PhaseConfig(')[0]==rg.split(', prefill=PhaseConfig(')[0];assert "prefill=PhaseConfig(backend='breakable'" in cg
  assert not set(delta)-allowed,(role,delta);changes[role]=delta
 log=(run/'decode-0.log').read_text()
 for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:assert sorted(set(map(int,re.findall(pattern,log))))==list(range(8))
 long=w.long_check(run);passed=p['metrics']['sla_pass'] and long['state']=='PASSED';d=dict(job=job,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if passed else 'REVIEWED_SLA_OR_QUALITY_FAIL',point=p,long=long,runtime_differences=changes,control_job=refjob,comparison_temporally_fresh=kind=='decode',vs_control=w.core.metric_delta(p['metrics'],b['metrics']),accuracy_verified=False);(O/(job+'-review.json')).write_text(json.dumps(d,indent=2)+'\n');print(job,d['state'],p['metrics'],d['vs_control'])

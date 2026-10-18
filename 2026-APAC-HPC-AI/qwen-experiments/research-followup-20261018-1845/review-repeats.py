"""Review predeclared chunk6144 and HPC-Ops prefill against fresh24526."""
from pathlib import Path
import json,importlib.util,datetime,re
R=Path.cwd();O=R/'research-followup-20261018-1845'
s=importlib.util.spec_from_file_location('w',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
for job,name,kind in [('24573','s12-dg-chunk6144-repeat-n56','chunk'),('24574','s12-hpc-prefill-repeat-n56','hpc')]:
 run=R/'runs'/job
 if not (run/'artifact-manifest.json').exists():print(job,'Waiting for terminal seal');continue
 p=w.core.point(R,job,56);b=w.core.point(R,'24575',56);assert p['normalized_protocol']==b['normalized_protocol'];pilot=next(x for x in json.loads((R/'serving-tuning-10/prepared-pilots.json').read_text())['pilots'] if x['job']==job);assert pilot['id']==name
 for filename,digest in pilot['payload_sha256'].items():assert w.core.sha(run/'submitted'/filename)==digest,filename
 diffs={}
 for role,a in p['server_args'].items():
  ref=b['server_args'][role];delta={k:[ref.get(k),a.get(k)] for k in a.keys()|ref.keys() if a.get(k)!=ref.get(k)};allowed={'random_seed'}
  if role.startswith('prefill'):
   assert a['speculative_algorithm']=='None'
   if kind=='chunk':
    allowed|={'chunked_prefill_size','cuda_graph_config'};assert a['chunked_prefill_size']=='6144';assert a['moe_runner_backend']=="'deep_gemm'";cg=a['cuda_graph_config'];rg=ref['cuda_graph_config'];assert cg.split(', prefill=PhaseConfig(')[0]==rg.split(', prefill=PhaseConfig(')[0];assert "prefill=PhaseConfig(backend='breakable'" in cg
   else:
    allowed|={'moe_runner_backend','speculative_moe_runner_backend'}
    for key in ['moe_runner_backend','speculative_moe_runner_backend']:assert delta.get(key)==["'deep_gemm'","'hpc_ops'"],(role,key,delta)
    assert 'HPC_OPS_PREFLIGHT_PASSED' in (run/(role+'.log')).read_text()
  assert not set(delta)-allowed,(role,delta);diffs[role]=delta
 log=(run/'decode-0.log').read_text()
 for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:assert sorted(set(map(int,re.findall(pattern,log))))==list(range(8))
 long=w.long_check(run);passed=p['metrics']['sla_pass'] and long['state']=='PASSED';d=dict(job=job,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if passed else 'REVIEWED_SLA_OR_QUALITY_FAIL',point=p,long=long,control_job='24575',runtime_differences=diffs,vs_control=w.core.metric_delta(p['metrics'],b['metrics']),accuracy_verified=False);(O/(job+'-review.json')).write_text(json.dumps(d,indent=2)+'\n');print(job,d['state'],p['metrics'],d['vs_control'])

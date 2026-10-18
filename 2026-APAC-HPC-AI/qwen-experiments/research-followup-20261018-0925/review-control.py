"""Review frozen one-role trials without relaxing runtime, quality or protocol gates."""
from pathlib import Path
import json,re,importlib.util,datetime
R=Path.cwd();O=R/'research-followup-20261018-0925'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=mod('prefill',R/'nscc-pbs/review-current-prefill.py');core=m.core
snapshots={j:Path(json.loads(Path('/tmp/ap42-collect-'+j+'.json').read_text())['destination']) for j in ['221262.pbs111','221275.pbs111']}
for job,kind in [('221275.pbs111','control')]:
 snapshot=snapshots[job];run=snapshot/'runs'/job;reference=snapshots['221262.pbs111'] if kind=='hpc' else m.CONTROL;refjob='221262.pbs111' if kind=='hpc' else '221151.pbs111';proof={}
 seal=json.loads((snapshot/'evidence-sha256.json').read_text());refseal=json.loads((reference/'evidence-sha256.json').read_text())
 for role,tp,ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
  files=list(run.glob('task-'+role+'-node*.log'));refs=list((reference/'runs'/refjob).glob('task-'+role+'-node*.log'));core.require(len(files)==len(refs)==1,'Ambiguous task logs');f=files[0];rf=refs[0];core.require(seal[str(f.relative_to(snapshot))]==core.sha(f),'Unsealed task log');core.require(refseal[str(rf.relative_to(reference))]==core.sha(rf),'Unsealed control log')
  a=core.server_args(f);b=core.server_args(rf);log=f.read_text();core.require(a['tp_size']==str(tp) and a['ep_size']==str(ep),'Wrong partition');core.require('KV Cache is allocated. dtype: torch.bfloat16' in log,'Missing BF16 KV')
  delta={k:[b.get(k),a.get(k)] for k in a.keys()|b.keys() if a.get(k)!=b.get(k)};allowed={'random_seed'}
  if kind=='control' and role.startswith('prefill'):
   allowed.add('weight_loader_prefetch_checkpoints');core.require(delta.get('weight_loader_prefetch_checkpoints')==['False','True'],'Missing prefetch')
  if kind=='hpc' and role=='decode-0':
   allowed|={'moe_runner_backend','speculative_moe_runner_backend'}
   for key in ['moe_runner_backend','speculative_moe_runner_backend']:core.require(delta.get(key)==["'auto'","'hpc_ops'"],'Wrong HPC-Ops runner: '+key)
   core.require('HPC_OPS_PREFLIGHT_PASSED' in log,'Missing preflight');core.require(a['speculative_algorithm']=='None','Speculation enabled')
  core.require(not set(delta)-allowed,'Unexpected runtime difference: '+role+' '+str(set(delta)-allowed))
  if role=='decode-0':
   for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:core.require(sorted(set(map(int,re.findall(pattern,log))))==list(range(8)),'Missing decode backend ranks')
  proof[role]={'runtime_differences':delta,'startup_timing_lines':[x for x in log.splitlines() if 'Engine startup timings (s):' in x]}
 gates=json.loads((O/(job+'-gates.json')).read_text());core.require(gates['terminal_seal_short_payload_pass'] and gates['long_diagnostic']['state']=='PASSED','Payload or quality gates failed');point=gates['candidate_review']['points'][0];core.require(point['latency_error_gate_pass'],'SLA/error gate failed')
 result=dict(job=job,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS',point=point,runtime=proof,control_job=refjob,accuracy_verified=False,snapshot=str(snapshot))
 if kind=='hpc':
  b=json.loads((O/'221262.pbs111-gates.json').read_text())['candidate_review']['points'][0];result['goodput_gain_percent']=100*(point['good_output_tokens_s']/b['good_output_tokens_s']-1)
 (O/(job+'-review.json')).write_text(json.dumps(result,indent=2)+'\n');print(job,result['state'],result.get('goodput_gain_percent'))

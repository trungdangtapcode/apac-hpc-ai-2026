"""Review fresh matched H100 trials and explicitly inspect each changed role."""
from pathlib import Path
import json,importlib.util,re,datetime
R=Path.cwd();O=R/'research-followup-20261018-1323';s=importlib.util.spec_from_file_location('m',R/'nscc-pbs/review-current-prefill.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.core
snapshots={j:Path(json.loads(Path('/tmp/ap42-collect-'+j+'.json').read_text())['destination']) for j in ['221284.pbs111','221314.pbs111','221315.pbs111','221316.pbs111']}
for job,name in [('221314.pbs111','h100-hpc-fresh-control-30'),('221315.pbs111','h100-hpc-both-31'),('221316.pbs111','h100-hpc-n52-repeat-32')]:
 snap=snapshots[job];g=m.m.compare(snap,m.BASE,m.SMOKE,name);(O/(job+'-gates.json')).write_text(json.dumps(g,indent=2)+'\n');print(job,g['terminal_seal_short_payload_pass'],g['candidate_review']['points'],g['long_diagnostic'],flush=True)
 c.require(g['terminal_seal_short_payload_pass'] and g['long_diagnostic']['state']=='PASSED','Payload/quality gate failed');p=g['candidate_review']['points'][0];refjob='221284.pbs111' if job=='221314.pbs111' else '221314.pbs111';reference=snapshots[refjob];deltas={}
 seal=json.loads((snap/'evidence-sha256.json').read_text());refseal=json.loads((reference/'evidence-sha256.json').read_text())
 for role,tp,ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
  files=list((snap/'runs'/job).glob('task-'+role+'-node*.log'));refs=list((reference/'runs'/refjob).glob('task-'+role+'-node*.log'));c.require(len(files)==len(refs)==1,'Ambiguous task logs');f=files[0];rf=refs[0];c.require(seal[str(f.relative_to(snap))]==c.sha(f),'Unsealed task log');c.require(refseal[str(rf.relative_to(reference))]==c.sha(rf),'Unsealed control log');a=c.server_args(f);b=c.server_args(rf);log=f.read_text();c.require(a['tp_size']==str(tp) and a['ep_size']==str(ep),'Wrong layout');c.require('KV Cache is allocated. dtype: torch.bfloat16' in log,'Missing BF16 KV')
  delta={k:[b.get(k),a.get(k)] for k in a.keys()|b.keys() if a.get(k)!=b.get(k)};allowed={'random_seed'}
  if job=='221315.pbs111' and role.startswith('prefill'):
   allowed|={'moe_runner_backend','speculative_moe_runner_backend'}
   for key in ['moe_runner_backend','speculative_moe_runner_backend']:c.require(delta.get(key)==["'auto'","'hpc_ops'"],'Wrong prefill runner')
   c.require('HPC_OPS_PREFLIGHT_PASSED' in log,'Missing prefill GPU preflight')
  c.require(a['speculative_algorithm']=='None','Unexpected speculation');c.require(not set(delta)-allowed,'Unexpected runtime: '+role+' '+str(delta));deltas[role]=delta
  if role=='decode-0':
   c.require(a['moe_runner_backend']=="'hpc_ops'",'Decode runner not retained')
   for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:c.require(sorted(set(map(int,re.findall(pattern,log))))==list(range(8)),'Missing decode backend ranks')
 state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if p['latency_error_gate_pass'] else 'REVIEWED_SLA_OR_QUALITY_FAIL';d=dict(job=job,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state=state,point=p,runtime_differences=deltas,control_job=refjob,accuracy_verified=False,snapshot=str(snap));
 if job!='221314.pbs111':
  ref=json.loads((O/'221314.pbs111-review.json').read_text())['point'];d['goodput_gain_percent']=100*(p['good_output_tokens_s']/ref['good_output_tokens_s']-1);d['comparison']='SAME_LOAD_RUNNER_CHANGE' if job=='221315.pbs111' else 'CROSS_LOAD_OPERATING_POINT'
 (O/(job+'-review.json')).write_text(json.dumps(d,indent=2)+'\n');print(job,state,d.get('goodput_gain_percent'),flush=True)

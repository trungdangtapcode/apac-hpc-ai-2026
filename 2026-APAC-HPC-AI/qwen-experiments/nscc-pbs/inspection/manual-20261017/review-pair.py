from pathlib import Path
import importlib.util,json,re,hashlib
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments'); P=ROOT/'nscc-pbs'; OUT=P/'inspection/manual-20261017'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sweep=module('sweep',P/'review-load-sweep.py'); longmod=module('cand',P/'review-candidate-sweep.py'); core=module('core',ROOT/'serving-tuning/review-n54.py')
snapshot=P/'collected/220909.pbs111/20261017T005441565035Z'; ref=P/'collected/220908.pbs111/20261017T005441200160Z'
smoke=P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json'
observed=sweep.review(snapshot,smoke); control=json.loads((OUT/'review-control.json').read_text()); long=longmod.long_review(snapshot,'220909.pbs111');longcontrol=longmod.long_review(ref,'220908.pbs111')
assert observed['seal_pass'] and observed['n32_research_evidence_pass'] and observed['exit_status']==0
assert control['seal_pass'] and control['n32_research_evidence_pass'] and control['exit_status']==0
assert all(p['protocol_pass'] and p['phase_complete'] and p['latency_error_gate_pass'] for p in observed['points'])
assert long['state']==longcontrol['state']=='PASSED'
plan=json.loads((P/'continuous-plan.json').read_text()); frozen=next(x for x in plan['pilots'] if x['job_id']=='220909.pbs111')
run=snapshot/'runs/220909.pbs111'; before=ref/'runs/220908.pbs111'
for name,digest in frozen['payload_sha256'].items():assert hashlib.sha256((run/'submitted'/name).read_bytes()).hexdigest()==digest
argsdelta={};rankproof={}
for role,world in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:
 logs=list(run.glob('task-'+role+'-node*.log'));assert len(logs)==1
 log=logs[0].read_text();args=core.server_args(logs[0]);refs=list(before.glob('task-'+role+'-node*.log'));assert len(refs)==1
 prior=core.server_args(refs[0]);delta={k:[prior.get(k),args.get(k)] for k in args.keys()|prior.keys() if prior.get(k)!=args.get(k)}
 allowed={'random_seed','host','port','dist_init_addr','nccl_port','disaggregation_bootstrap_port','flashinfer_allreduce_fusion_backend'}
 assert not set(delta)-allowed,str(delta)
 assert args['tp_size']==str(world) and args['ep_size']==('8' if role=='decode-0' else '1')
 assert args['disaggregation_transfer_backend']=="'nixl'"
 assert 'KV Cache is allocated. dtype: torch.bfloat16' in log
 rankproof[role]={'bf16_allocation_observed':True,'server_args_tp':world,'server_args_ep':args['ep_size']};argsdelta[role]=delta
 if role=='decode-0':
  ranks=sorted(set(map(int,re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',log))));assert ranks==list(range(8));rankproof[role]['mnnvl_ranks']=ranks
# Preserve cross-node/time drift and all higher-load comparisons, never assign sole causality.
comparisons=[]
for p in observed['points']:
 b=next((b for b in control['points'] if b['concurrency']==p['concurrency']),None)
 comparisons.append({'candidate':p,'control':b,'goodput_change_pct':100*(p['good_output_tokens_s']/b['good_output_tokens_s']-1) if b else None})
out={'continuation_gate_pass':True,'candidate_review':observed,'control_review':control,'long':long,'control_long':longcontrol,'runtime':rankproof,'runtime_differences':argsdelta,'comparisons':comparisons,'accuracy_verified':False,'promotion_authorized':False}
(OUT/'pair-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'continuation_gate_pass':True,'long':long,'runtime':rankproof,'gains_N32_N34':[p['goodput_change_pct'] for p in comparisons[:2]]}))

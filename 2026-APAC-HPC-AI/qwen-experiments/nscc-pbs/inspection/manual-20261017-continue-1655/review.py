from pathlib import Path
import importlib.util,json,re,datetime
R=Path.cwd();P=R/'nscc-pbs';O=P/'inspection/manual-20261017-continue-1655'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=mod('candidate',P/'review-candidate-sweep.py');core=mod('core',R/'serving-tuning/review-n54.py');wave=mod('wave',R/'serving-tuning-10/review-wave10.py')
snap=Path(json.loads(Path('/tmp/ap42-collect-221151.pbs111.json').read_text())['destination'])
d=m.compare(snap,P/'collected/220575.pbs111/20261016T054555388584Z',P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json','h100-combo-control-16')
assert d['terminal_seal_short_payload_pass'] and d['long_diagnostic']['state']=='PASSED'
assert all(x['protocol_pass'] and x['phase_complete'] and x['latency_error_gate_pass'] for x in d['candidate_review']['points'])
proof={};run=snap/'runs/221151.pbs111'
for role,tp,ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
 f=next(run.glob('task-'+role+'-node*.log'));log=f.read_text();args=core.server_args(f);assert args['tp_size']==str(tp) and args['ep_size']==str(ep) and args['disaggregation_transfer_backend']=="'nixl'";assert 'KV Cache is allocated. dtype: torch.bfloat16' in log;proof[role]={'tp':tp,'ep':ep,'KV':'BF16'}
 if role=='decode-0':
  for key,pattern in [('mnnvl',r'backend=mnnvl, rank=(\d+), world_size=8'),('flashinfer',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3')]:
   ranks=sorted(set(map(int,re.findall(pattern,log))));assert ranks==list(range(8));proof[role][key+'_ranks']=ranks
d['runtime_proof']=proof;(O/'review-221151.json').write_text(json.dumps(d,indent=2)+'\n');print('H100 control reviewed',d['candidate_review']['points'],flush=True)
p=core.point(R,'24320',56);b=core.point(R,'24263',56);assert p['normalized_protocol']==b['normalized_protocol'];long=wave.long_check(R/'runs/24320');assert long['state']=='PASSED';assert p['metrics']['sla_pass']
for name in p['payload_files']:
 if name not in ['config.json','job.sbatch']:assert core.sha(R/'runs/24320/submitted'/name)==core.sha(R/'serving-tuning-10/s10-combo-repeat-n56'/name),name
for role,args in p['server_args'].items():
 ref=b['server_args'][role];changes={k for k in args.keys()|ref.keys() if args.get(k)!=ref.get(k)};assert changes<= {'random_seed'},(role,changes)
result=dict(job='24320',state='REVIEWED_PROTOCOL_RUNTIME_SLA_SHORT_LONG_PASS',point=p,long=long,accuracy_verified=False,vs_24263=core.metric_delta(p['metrics'],b['metrics']))
(O/'review-24320.json').write_text(json.dumps(result,indent=2)+'\n');print('H200 control reviewed',p['metrics'],flush=True)

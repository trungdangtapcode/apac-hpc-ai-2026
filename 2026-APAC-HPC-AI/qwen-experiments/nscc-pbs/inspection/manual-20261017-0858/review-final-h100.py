from pathlib import Path
import importlib.util,json,re,time
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');P=R/'nscc-pbs';O=P/'inspection/manual-20261017-0858'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=mod('review',P/'review-candidate-sweep.py');core=mod('core',R/'serving-tuning/review-n54.py')
reports={}
for job,pilot in [('221052.pbs111','h100-combo-load-14'),('221058.pbs111','h100-combo-load-repeat-15')]:
 until=time.monotonic()+180
 while True:
  candidates=list((P/'collected'/job).glob('20261017T0900*/evidence-sha256.json'))
  if candidates:break
  if time.monotonic()>until:raise RuntimeError('Collection incomplete: '+job+';no result promotion')
  time.sleep(5)
 snap=candidates[0].parent;d=m.compare(snap,P/'collected/220575.pbs111/20261016T054555388584Z',P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json',pilot)
 assert d['terminal_seal_short_payload_pass'] and d['long_diagnostic']['state']=='PASSED'
 assert all(x['protocol_pass'] and x['phase_complete'] and x['latency_error_gate_pass'] for x in d['candidate_review']['points'])
 run=snap/'runs'/job;proof={}
 for role,tp,ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
  f=next(run.glob('task-'+role+'-node*.log'));log=f.read_text();args=core.server_args(f);assert args['tp_size']==str(tp) and args['ep_size']==str(ep) and args['disaggregation_transfer_backend']=="'nixl'"
  assert 'KV Cache is allocated. dtype: torch.bfloat16' in log;proof[role]={'tp':tp,'ep':ep,'KV':'BF16'}
  if role=='decode-0':
   for key,regex in [('mnnvl',r'backend=mnnvl, rank=(\d+), world_size=8'),('flashinfer',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3')]:
    ranks=sorted(set(map(int,re.findall(regex,log))));assert ranks==list(range(8));proof[role][key+'_ranks']=ranks
 d['runtime_proof']=proof;(O/('review-'+job+'.json')).write_text(json.dumps(d,indent=2)+'\n');reports[job]=d;print('Reviewed',job,'fullprotocol/runtime/short/longpass',flush=True)
means={n:sum(next(x['good_output_tokens_s'] for x in d['candidate_review']['points'] if x['concurrency']==n) for d in reports.values())/len(reports) for n in [48,50,52]}
result={'means_good_tokens_s':means,'same_load_runs':{j:d['candidate_review']['points'] for j,d in reports.items()},'quality_all_pass':True,'accuracy_verified':False,'conclusion':'N50 highest in both runs;N52higherTTFTwithoutgoodputgain;do not increase load blindly','campaign_remaining_su':847.075,'no_new_pbs_allocation':'remaining budget cannot cover observed startup plus fullbenchmark'}
(O/'h100-frontier-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'means':means,'decision':'N50 preferred; noN54'}),flush=True)

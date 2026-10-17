"""Review pending H100 prefill trials against the fresh N50 control; never submit."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,re
P=Path(__file__).resolve().parent;R=P.parent
PILOTS={'221194.pbs111':('h100-prefetch-repeat-21','prefetch'),'221195.pbs111':('h100-io-control-22','control'),'221153.pbs111':('h100-prefill-prefetch-18','prefetch'),'221177.pbs111':('h100-prefill-deepgemm-retry-19','deepgemm'),'221181.pbs111':('h100-prefill-no-graph-20','graphs')}
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('candidate',P/'review-candidate-sweep.py');core=module('core',R/'serving-tuning/review-n54.py')
CONTROL=P/'collected/221151.pbs111/20261017T165422435543Z';CONTROL_RUN=CONTROL/'runs/221151.pbs111'
BASE=P/'collected/220575.pbs111/20261016T054555388584Z';SMOKE=P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json'
def phase_backend(config,phase):
 match=re.search(r'\b'+phase+r"=PhaseConfig\(backend='([^']+)'",config);core.require(match is not None,'Missing graph phase: '+phase);return match[1]
def runtime(snapshot,job,kind):
 run=snapshot/'runs'/job;result={};seal=json.loads((snapshot/'evidence-sha256.json').read_text());refseal=json.loads((CONTROL/'evidence-sha256.json').read_text())
 for role,tp,ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
  candidates=list(run.glob('task-'+role+'-node*.log'));core.require(len(candidates)==1,'Missing or ambiguous task log: '+role);logfile=candidates[0];ref_candidates=list(CONTROL_RUN.glob('task-'+role+'-node*.log'));core.require(len(ref_candidates)==1,'Ambiguous control task log');reffile=ref_candidates[0]
  core.require(seal.get(str(logfile.relative_to(snapshot)))==core.sha(logfile),'Unsealed task log');core.require(refseal.get(str(reffile.relative_to(CONTROL)))==core.sha(reffile),'Control task log changed')
  args=core.server_args(logfile);ref=core.server_args(reffile);text=logfile.read_text();core.require(args['tp_size']==str(tp) and args['ep_size']==str(ep),'Unexpected layout');core.require('KV Cache is allocated. dtype: torch.bfloat16' in text,'Missing BF16 KV allocation')
  changes={k:[ref.get(k),args.get(k)] for k in args.keys()|ref.keys() if args.get(k)!=ref.get(k)};allowed={'random_seed'}
  if role.startswith('prefill'):
   if kind=='prefetch':
    allowed.add('weight_loader_prefetch_checkpoints');core.require(args['weight_loader_prefetch_checkpoints']=='True' and ref['weight_loader_prefetch_checkpoints']=='False','Missing prefetch change')
   elif kind=='deepgemm':
    allowed|={'moe_runner_backend','speculative_moe_runner_backend'}
    for key in ['moe_runner_backend','speculative_moe_runner_backend']:core.require(args[key]=="'deep_gemm'" and ref[key]=="'auto'",'Wrong runner: '+key)
    core.require(args['speculative_algorithm']=='None','Speculative decoding changed')
   elif kind=='graphs':
    allowed|={'cuda_graph_config','disable_prefill_cuda_graph'};core.require(args['disable_prefill_cuda_graph']=='True','Prefill graph switch missing');cg=args['cuda_graph_config'];rg=ref['cuda_graph_config'];core.require(phase_backend(cg,'prefill')=='disabled','Prefill phase still enabled');core.require(cg.split(', prefill=PhaseConfig(')[0]==rg.split(', prefill=PhaseConfig(')[0],'Prefill worker decode graph config changed')
  core.require(not set(changes)-allowed,'Unexpected runtime changes: '+role+' '+str(set(changes)-allowed))
  if role=='decode-0':
   for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:core.require(sorted(set(map(int,re.findall(pattern,text))))==list(range(8)),'Missing decode backend ranks')
  timings=[line for line in text.splitlines() if 'Engine startup timings (s):' in line];result[role]=dict(runtime_differences=changes,startup_timing_lines=timings)
 return result

def review(job,snapshot=None):
 name,kind=PILOTS[job];result=dict(job=job,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='WAITING_FOR_COLLECTED_TERMINAL_EVIDENCE',accuracy_verified=False,submitted_new_jobs=False)
 if snapshot is None:
  snapshots=sorted(p.parent for p in (P/'collected'/job).glob('*/evidence-sha256.json'))
  if not snapshots:return result
  snapshot=snapshots[-1]
 try:
  collection=json.loads((snapshot/'review.json').read_text());core.require(collection['job']==job,'Wrong collected job')
  if collection['pbs_state']!='F':return result
  if collection['exit_status']!=0:
   result.update(state='FAILED_ALLOCATION_NOT_A_COMPLETED_MEASUREMENT',exit_status=collection['exit_status'],snapshot=str(snapshot));return result
  d=m.compare(snapshot,BASE,SMOKE,name);core.require(d['terminal_seal_short_payload_pass'],'Protocol, payload, short output or seal gate failed');points=d['candidate_review']['points'];core.require(len(points)==1 and points[0]['concurrency']==50,'Expected exactly N50');candidate=points[0]
  proof=runtime(snapshot,job,kind);control_review=json.loads((P/'inspection/manual-20261017-continue-1655/review-221151.json').read_text());control=control_review['candidate_review']['points'][0]
  passed=candidate['latency_error_gate_pass'] and d['long_diagnostic']['state']=='PASSED';result.update(state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if passed else 'REVIEWED_SLA_OR_QUALITY_FAIL',snapshot=str(snapshot),point=candidate,frozen_payload=d['frozen_candidate_payload'],long=d['long_diagnostic'],runtime=proof,fresh_control_job='221151.pbs111',goodput_gain_percent=100*(candidate['good_output_tokens_s']/control['good_output_tokens_s']-1),ttft_delta_ms=candidate['ttft_avg_ms']-control['ttft_avg_ms'],itl_delta_ms=candidate['itl_avg_ms']-control['itl_avg_ms'],interpretation='Startup diagnostics and allocation cost are separate from scored throughput. Ordering, loading and cache can confound startup. One useful observed gain requires independent confirmation; official accuracy is not established.')
 except (OSError,ValueError,AssertionError,KeyError,TypeError,StopIteration) as e:result.update(state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(e))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('job',choices=PILOTS);p.add_argument('--snapshot',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=review(a.job,a.snapshot)
 with a.out.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in d.items() if k not in ['runtime','frozen_payload']}))

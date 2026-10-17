"""Review the frozen single-TP8-prefill pilot. Read-only; no scheduler mutations."""
from pathlib import Path
import json,importlib.util,datetime,re
R=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
def review():
 job='24282';run=R/'runs'/job
 result={'job':job,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'WAITING_FOR_TERMINAL_SEAL','accuracy_verified':False,'new_jobs_submitted':False}
 if not (run/'artifact-manifest.json').exists():return result
 try:
  p=w.core.point(R,job,56,prefill_roles=('prefill-0',));base=w.core.point(R,'24263',56)
  w.core.require(p['normalized_protocol']==base['normalized_protocol'],'Client protocol drift')
  placement=(run/'submitted/placement.tsv').read_text().splitlines()
  w.core.require([x.split() for x in placement]==[['prefill-0','0','8','30100','9000'],['decode-0','1','8','30200','0']],'Unexpected placement')
  cfg=w.core.read(run/'submitted/config.json')
  w.core.require(cfg['prefill_tp']==8 and cfg['prefill_workers']==1 and cfg['prefill_ep']==1,'Config layout mismatch')
  source=R/'serving-tuning-10/s10-combo-repeat-n56'
  for name in p['payload_files']:
   if name in ['config.json','placement.tsv','job.sbatch']:continue
   w.core.require(w.core.sha(run/'submitted'/name)==w.core.sha(source/name),'Unexpected execution change: '+name)
  changes={}
  for role in ['prefill-0','decode-0']:
   args=p['server_args'][role];ref=base['server_args'][role]
   delta={k:[ref.get(k),args.get(k)] for k in args.keys()|ref.keys() if args.get(k)!=ref.get(k)}
   allowed={'random_seed'}|({'tp_size'} if role=='prefill-0' else set())
   w.core.require(not set(delta)-allowed,'Unexpected resolved runtime change: '+role)
   w.core.require(args['tp_size']=='8' and args['ep_size']==('1' if role=='prefill-0' else '8'),'TP/EP mismatch')
   log=(run/(role+'.log')).read_text()
   w.core.require('KV Cache is allocated. dtype: torch.bfloat16' in log,'Missing BF16 KV allocation')
   ranks=sorted(set(map(int,re.findall(r'TP(\d+)(?: EP\d+)?\] NIXL KVManager initialized with backend: UCX',log))))
   w.core.require(ranks==list(range(8)),'Missing NIXL ranks: '+role);changes[role]=delta
  log=(run/'decode-0.log').read_text()
  for regex in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:
   w.core.require(sorted(set(map(int,re.findall(regex,log))))==list(range(8)),'Missing decode backend rank proof')
  long=w.long_check(run);passed=p['metrics']['sla_pass'] and long['state']=='PASSED'
  result.update(state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if passed else 'REVIEWED_SLA_OR_QUALITY_FAIL',point=p,long=long,runtime_changes=changes,vs_fresh_control=w.core.metric_delta(p['metrics'],base['metrics']),interpretation='Same16GPU budget; changed prefill parallelism and replica count. One observation is not a replicated gain or organiser accuracy proof.')
 except (KeyError,ValueError,OSError,TypeError,StopIteration,AssertionError) as e:result.update(state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(e))
 return result
if __name__=='__main__':
 d=review();p=Path(__file__).with_name('24282-review.json');p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items() if k not in ['point','runtime_changes']}))

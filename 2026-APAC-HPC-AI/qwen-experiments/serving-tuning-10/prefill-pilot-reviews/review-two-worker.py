"""Review a predeclared prefill-only change; never submit jobs or promote results."""
from pathlib import Path
import importlib.util,json,argparse,datetime,re
R=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
PILOTS={'24428':('moe_runner_backend',"'auto'","'deep_gemm'"),'24429':('moe_runner_backend',"'auto'","'deep_gemm'"),'24322':('weight_loader_prefetch_checkpoints','False','True'),'24281':('prefill_max_requests','None','1'),'24291':('moe_runner_backend',"'auto'","'deep_gemm'"),'24327':('moe_runner_backend',"'auto'","'deep_gemm'"),'24352':('moe_runner_backend',"'auto'","'deep_gemm'")}
def review(job):
 result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':job,'state':'WAITING_FOR_TERMINAL_SEAL','accuracy_verified':False,'new_jobs_submitted':False}
 if not (R/'runs'/job/'artifact-manifest.json').exists():return result
 try:
  n=54 if job=='24428' else 58 if job=='24352' else 56
  control_job='24189' if job=='24428' else '24320' if job=='24429' else '24236' if job=='24352' else '24320' if job in ['24327','24322'] else '24263'
  p=w.core.point(R,job,n);control=w.core.point(R,control_job,n);key,before,after=PILOTS[job]
  w.core.require(p['normalized_protocol']==control['normalized_protocol'],'Client protocol changed')
  source=R/'serving-tuning-10/s10-combo-repeat-n56'
  for name in p['payload_files']:
   if name in ['config.json','job.sbatch']:continue
   f=R/'runs'/job/'submitted'/name
   if name=='worker.sh':
    expected=(source/name).read_text();flag='--prefill-max-requests 1' if job=='24281' else '--weight-loader-prefetch-checkpoints' if job=='24322' else '--moe-runner-backend deep_gemm'
    expected=expected.replace('extra=(--chunked-prefill-size 4096)','extra=(--chunked-prefill-size 4096 '+flag+')')
    w.core.require(f.read_text()==expected,'Unexpected worker change')
   else:w.core.require(w.core.sha(f)==w.core.sha(source/name),'Unexpected payload change: '+name)
  deltas={}
  for role,args in p['server_args'].items():
   ref=control['server_args'][role];changes={k:[ref.get(k),args.get(k)] for k in args.keys()|ref.keys() if args.get(k)!=ref.get(k)}
   allowed={'random_seed'}|({key} if role.startswith('prefill-') else set())
   if key=='moe_runner_backend' and role.startswith('prefill-'):
    # SGLang resolves the speculative runner default from the main runner.
    w.core.require(args['speculative_algorithm']=='None' and ref['speculative_algorithm']=='None','Unexpected speculative decoding')
    w.core.require(changes.get('speculative_moe_runner_backend')==[before,after],'Unexpected inherited runner setting')
    allowed.add('speculative_moe_runner_backend')
   w.core.require(not set(changes)-allowed,'Unexpected runtime changes: '+role)
   if role.startswith('prefill-'):
    w.core.require(ref[key]==before and args[key]==after,'Expected prefill setting missing')
   deltas[role]=changes
  log=(R/'runs'/job/'decode-0.log').read_text()
  for regex in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:
   w.core.require(sorted(set(map(int,re.findall(regex,log))))==list(range(8)),'Missing decode backend ranks')
  long=w.long_check(R/'runs'/job);delta=w.core.metric_delta(p['metrics'],control['metrics'])
  eligible=p['metrics']['sla_pass'] and long['state']=='PASSED'
  result.update(state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if eligible else 'REVIEWED_SLA_OR_QUALITY_FAIL',point=p,long=long,control_job=control_job,control_temporally_fresh=(job not in ['24352','24428','24429']),vs_fresh_control=delta,runtime_differences=deltas,decision='Do not repeat a lower-goodput trial just to fill queue slots; a promising gain needs independent confirmation.')
 except (KeyError,ValueError,OSError,TypeError,StopIteration,AssertionError) as e:result.update(state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(e))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('job',choices=PILOTS);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=review(a.job)
 with a.out.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in d.items() if k not in ['point','runtime_differences']}))

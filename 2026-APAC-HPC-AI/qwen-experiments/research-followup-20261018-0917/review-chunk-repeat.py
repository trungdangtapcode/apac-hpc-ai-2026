"""Review new one-factor DeepGEMM trials against confirmed N56, read-only."""
from pathlib import Path
import importlib.util,json,datetime,argparse,re
R=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
PILOTS={'24527':('s11-dg-chunk8192-repeat-n56','chunk')}
def review(job):
 name,kind=PILOTS[job];run=R/'runs'/job;r=dict(job=job,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='WAITING_FOR_TERMINAL_SEAL',accuracy_verified=False)
 if not (run/'artifact-manifest.json').exists():return r
 try:
  p=w.core.point(R,job,56);b=w.core.point(R,'24526',56);w.core.require(p['normalized_protocol']==b['normalized_protocol'],'Protocol changed');plan=w.core.read(R/'serving-tuning-10/prepared-pilots.json');entry=next(x for x in plan['pilots'] if x['id']==name);w.core.require(entry['job']==job,'Job registry mismatch')
  for filename,digest in entry['payload_sha256'].items():w.core.require(w.core.sha(run/'submitted'/filename)==digest,'Payload mismatch: '+filename)
  changes={}
  for role,args in p['server_args'].items():
   ref=b['server_args'][role];delta={k:[ref.get(k),args.get(k)] for k in args.keys()|ref.keys() if args.get(k)!=ref.get(k)};allowed={'random_seed'}
   if role.startswith('prefill'):
    w.core.require(args['moe_runner_backend']=="'deep_gemm'",'Prefill runner changed');w.core.require(args['speculative_algorithm']=='None','Unexpected speculation');cg=args['cuda_graph_config'];rg=ref['cuda_graph_config'];w.core.require(cg.split(', prefill=PhaseConfig(')[0]==rg.split(', prefill=PhaseConfig(')[0],'Prefill worker decode graph config changed')
    if kind=='chunk':
     allowed|={'chunked_prefill_size','cuda_graph_config'};w.core.require(args['chunked_prefill_size']=='8192','Chunk change missing');w.core.require("prefill=PhaseConfig(backend='breakable'" in cg,'Unexpected graph backend')
    else:
     allowed|={'cuda_graph_config','disable_prefill_cuda_graph'};w.core.require(args['disable_prefill_cuda_graph']=='True' and "prefill=PhaseConfig(backend='disabled'" in cg,'Graph switch missing')
   w.core.require(not set(delta)-allowed,'Unexpected runtime changes: '+role);changes[role]=delta
  log=(run/'decode-0.log').read_text()
  for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:w.core.require(sorted(set(map(int,re.findall(pattern,log))))==list(range(8)),'Missing decode ranks')
  long=w.long_check(run);r.update(state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if p['metrics']['sla_pass'] and long['state']=='PASSED' else 'REVIEWED_SLA_OR_QUALITY_FAIL',point=p,long=long,runtime_differences=changes,control_job='24526',vs_confirmed_control=w.core.metric_delta(p['metrics'],b['metrics']),interpretation='Single observed change versus confirmed DeepGEMM. Separate startup and scored throughput; official accuracy remains unverified.')
 except (OSError,KeyError,ValueError,AssertionError,TypeError,StopIteration) as e:r.update(state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(e))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('job',choices=PILOTS);p.add_argument('--out',type=Path,required=True);a=p.parse_args();d=review(a.job)
 with a.out.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in d.items() if k not in ['point','runtime_differences']}))

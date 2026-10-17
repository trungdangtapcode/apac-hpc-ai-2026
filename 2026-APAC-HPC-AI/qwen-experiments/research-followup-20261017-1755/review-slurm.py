"""Strict, read-only review for the transport repair and prefill graph ablation."""
from pathlib import Path
import importlib.util,json,datetime,re,argparse
R=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
PILOTS={'24375':('s10-prefill-tp8ep2-equal-n56','equal'),'24376':('s10-prefill-no-graph-n56','graphs')}
def review(job):
 name,kind=PILOTS[job];run=R/'runs'/job;r=dict(job=job,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),state='WAITING_FOR_TERMINAL_SEAL',accuracy_verified=False)
 if not (run/'artifact-manifest.json').exists():return r
 try:
  roles=('prefill-0',) if kind=='equal' else ('prefill-0','prefill-1');p=w.core.point(R,job,56,prefill_roles=roles);b=w.core.point(R,'24320',56)
  frozen=w.core.read(R/'research-followup-20261017-1755/validation.json')['bundles'][name]
  for filename,digest in frozen.items():w.core.require(w.core.sha(run/'submitted'/filename)==digest,'Frozen payload mismatch: '+filename)
  w.core.require(p['normalized_protocol']==b['normalized_protocol'],'Client protocol changed')
  differences={}
  for role,args in p['server_args'].items():
   ref=b['server_args'][role];changes={k:[ref.get(k),args.get(k)] for k in args.keys()|ref.keys() if args.get(k)!=ref.get(k)}
   allowed={'random_seed'}
   if role.startswith('prefill'):
    if kind=='equal':
     allowed|={'tp_size','ep_size'};w.core.require(args['tp_size']=='8' and args['ep_size']=='2','Wrong repaired layout')
    else:
     allowed|={'cuda_graph_config','disable_prefill_cuda_graph'};w.core.require(args['disable_prefill_cuda_graph']=='True','Prefill graph switch missing')
     cg=args['cuda_graph_config'];rg=ref['cuda_graph_config'];w.core.require(cg.split(', prefill=PhaseConfig(')[0]==rg.split(', prefill=PhaseConfig(')[0],'Prefill worker decode phase changed');w.core.require("prefill=PhaseConfig(backend='disabled'" in cg,'Prefill graph still enabled')
   w.core.require(not set(changes)-allowed,'Unexpected runtime changes: '+role);differences[role]=changes
  for role in roles+('decode-0',):
   log=(run/(role+'.log')).read_text();w.core.require('KV Cache is allocated. dtype: torch.bfloat16' in log,'Missing BF16 KV proof')
  decode=(run/'decode-0.log').read_text()
  for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:
   w.core.require(sorted(set(map(int,re.findall(pattern,decode))))==list(range(8)),'Missing decode backend rank proof')
  if kind=='equal':
   log=(run/'prefill-0.log').read_text();ranks=sorted(set(map(int,re.findall(r'TP(\d+) EP\d+\] NIXL_EQUAL_ON_DEMAND',log))));w.core.require(ranks==list(range(8)),'Missing equal-TP on-demand activation on all ranks')
  long=w.long_check(run);ok=p['metrics']['sla_pass'] and long['state']=='PASSED';r.update(state='REVIEWED_SLA_AND_RESEARCH_QUALITY_PASS' if ok else 'REVIEWED_SLA_OR_QUALITY_FAIL',point=p,long=long,runtime_differences=differences,control_job='24320',vs_control=w.core.metric_delta(p['metrics'],b['metrics']),interpretation='A transport repair changes layout and patch versus the two-worker control; the graph ablation changes only prefill graph handling. Startup savings must be measured separately from scored goodput. No organiser accuracy claim.')
 except (AssertionError,ValueError,KeyError,OSError,StopIteration,TypeError) as e:r.update(state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(e))
 return r
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('job',choices=PILOTS);a.add_argument('--out',type=Path,required=True);args=a.parse_args();d=review(args.job)
 with args.out.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in d.items() if k not in ['point','runtime_differences']}))

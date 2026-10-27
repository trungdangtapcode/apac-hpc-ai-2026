#!/usr/bin/env python3
"""Preserve the failed native run boundaries without manufacturing a score."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,subprocess
Q=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent
proof=json.loads((Q/'runs/26574/split-proof.json').read_text())
sets=[]
for role in [0,1]:
 found=[]
 for line in (Q/f'runs/26574/split-{role}.log').read_text().splitlines():
  try:r=json.loads(line)
  except ValueError:continue
  if r.get('state')=='SPLIT_FOUR_GPU_TENSOR_PASS':found.append(r)
 assert len(found)==1;uuids=set(found[0]['uuids']);assert len(uuids)==4
 assert uuids==set(proof[f'role{role}_uuids']);sets.append(uuids)
assert not sets[0]&sets[1] and len(sets[0]|sets[1])==8
out={'utc':datetime.now(timezone.utc).isoformat(),'split_eight_independent_log_replay':'PASS','runs':[]}
for job in [26579,26581,26583]:
 A=Q/f'runs/{job}';assert not list(A.rglob('profile_export_aiperf.json'))
 r={'job':job,'eligible_score':None,'raw_profile_export':'NOT_PRODUCED','ttft_ms':None,'itl_ms':None,'good_fraction':None,'profiling_errors':'NOT_MEASURED','smoke_and_retrieval':'NOT_REACHED','role_telemetry':[],'logs':{}}
 for f in [Q/f'runs/{job}.out',Q/f'runs/{job}.err',*[A/n for n in ['benchmark-task.log','head-performance-check.json','pair-warmup.log','router.log','prefill-0.log','prefill-1.log','decode-0.log'] if (A/n).exists()]]:
  r['logs'][str(f.relative_to(Q))]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 for f in sorted((A/'resource-telemetry').glob('*-g*.jsonl')):
  rows=[json.loads(x) for x in f.read_text().splitlines() if x];samples=[x for x in rows if x.get('kind')=='sample'];last=samples[-1] if samples else {}
  final_gpus=last.get('gpus',[])
  metrics={}
  for line in last.get('server_metrics',[]):
   name=line.split('{')[0]
   if name in ['sglang:num_running_reqs','sglang:num_queue_reqs','sglang:token_usage','sglang:num_used_tokens']:
    metrics.setdefault(name,[]).append(float(line.rsplit(' ',1)[1]))
  r['role_telemetry'].append({'file':f.name,'samples':len(samples),'http_status_counts':dict(collections.Counter(str(x.get('server_http_status')) for x in samples)),'last_gpu_activity_percent':[float(x['utilization.gpu']) for x in final_gpus],'last_vram_used_GiB':[float(x['memory.used'])/1024 for x in final_gpus],'last_server_metrics':metrics,'interval':'startup/readiness/semantic warmup only; no scoring interval'})
 if (A/'runtime-readiness.json').exists():r['runtime_readiness']=json.loads((A/'runtime-readiness.json').read_text())['state']
 else:r['runtime_readiness']='NOT_REACHED'
 r['resource_limit']='No sampled disk history at failure; later free-space snapshot cannot establish culprit. GPU activity is not FLOPS and VRAM is not KV occupancy. No heavy profile.'
 out['runs'].append(r)
out['terminal_scheduler']=subprocess.check_output(['sacct','-n','-P','-X','-j','26574,26579,26581,26583','--format=JobID,State,ExitCode,Elapsed,Start,End,NodeList'],text=True)
(D/'review-r2.json').write_text(json.dumps(out,indent=2)+'\n');print('Independent split-eight replay PASS; 3 failed runs preserved without scores')

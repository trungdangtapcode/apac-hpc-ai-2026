#!/usr/bin/env python3
"""Seal terminal evidence and compare observed resources without causal claims."""
from pathlib import Path
import collections,datetime,hashlib,json,statistics,subprocess
Q=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;A=Q/'runs/26313'
state=subprocess.check_output(['sacct','-X','-j','26313','-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True);assert 'COMPLETED|0:0' in state
assert '26313' not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
(A/'scheduler-accounting.psv').write_text(state)
seal=A/'artifact-manifest.json'
if not seal.exists():
 files=[]
 for p in sorted(A.rglob('*')):
  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p.name=='artifact-manifest.json':continue
  before=p.stat();h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),p
  files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':h.hexdigest()})
 for p in (Q/'runs/26313.out',Q/'runs/26313.err'):
  files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 seal.write_text(json.dumps({'job':26313,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':state,'files':files},indent=2)+'\n')
resources=[]
for job in (25487,26313):
 a=Q/f'runs/{job}';raw=[json.loads(l) for l in (a/'confirm/n64/artifacts/profile_export.jsonl').open()];raw=[r for r in raw if r['metadata']['benchmark_phase']=='profiling'];lo=min(r['metadata']['request_start_ns'] for r in raw);hi=max(r['metadata']['request_start_ns'] for r in raw);roles={}
 for p in sorted((a/'resource-telemetry').glob('*.jsonl')):
  allrows=[json.loads(l) for l in p.open()];samples=[r for r in allrows if r.get('kind')=='sample' and lo<=r.get('utc_ns',0)<=hi];gpus=[g for r in samples for g in r.get('gpus',[])];stats={}
  for key in ('utilization.gpu','clocks.sm','clocks.mem','power.draw','temperature.gpu','memory.used'):
   values=[]
   for g in gpus:
    try:values.append(float(g[key]))
    except (KeyError,ValueError,TypeError):pass
   stats[key]={'mean':statistics.mean(values),'min':min(values),'max':max(values)} if values else None
  roles[p.stem]={'samples':len(samples),'gpu_uuid_count':len({g['uuid'] for g in gpus}),'fields':stats}
 resources.append({'job':job,'first_profiling_request_start_ns':lo,'last_profiling_request_start_ns':hi,'roles':roles})
result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'data':resources,'units':{'utilization.gpu':'percent of sample period with kernel activity','clocks.sm':'MHz','clocks.mem':'MHz','power.draw':'W','temperature.gpu':'degrees_C','memory.used':'MiB'},'window':'First-to-last profiling-request START envelope; not exact phase boundary. Warmup/drain excluded; host skew not calibrated.','assessment':'Decode sampled mean SM/memory clocks equal1980/3201MHz and activity100% in both. Prefill clock/power/temperature differ by role; this is not enough to explain or attribute a7% goodput change. No power-limit/throttle reason or per-dispatch trace collected.','limits':'Sparse24 samples/role, not a causal intervention. GPU activity is not FLOPS, allocated VRAM is not KV token occupancy. No claim of healthy/misconfigured hardware from these values.'}
(O/'resource-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print('Terminal raw evidence sealed; resource comparison retained')

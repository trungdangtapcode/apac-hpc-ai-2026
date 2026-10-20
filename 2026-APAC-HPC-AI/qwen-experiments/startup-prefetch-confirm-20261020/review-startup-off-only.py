# Derived reader scope: only new terminal 222420, preserving earlier immutable review outputs.
"""Verify terminal node-prefetch receipts and retain startup/cost timing limits."""
from pathlib import Path
import hashlib,json,math,re
O=Path(__file__).resolve().parent
pilots={p['id']:p for p in json.loads((O/'pilots.json').read_text())}
for receipt in json.loads((O/'pbs-receipts.json').read_text()):
 if receipt['job']!='222420.pbs111':continue
 job=receipt['job'];number=job.split('.')[0];pointer=O/f'collect-{number}.json'
 if not pointer.exists():continue
 snapshot=Path(json.loads(pointer.read_text())['destination']);run=snapshot/'runs'/job
 review=json.loads((O/(job+'-review.json')).read_text())
 assert review['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
 seal=json.loads((snapshot/'evidence-sha256.json').read_text())
 def checked(path):
  assert hashlib.sha256(path.read_bytes()).hexdigest()==seal[str(path.relative_to(snapshot))]
  return path
 expected=pilots[receipt['id']]['startup_prefetch_mode'];node_reports=[]
 source=checked(run/'submitted/prefetch-weights.py');source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
 for i,role in enumerate(['prefill-0','decode-0']):
  p=checked(run/f'startup-prefetch/node-{i}.json');d=json.loads(p.read_text())
  assert d['completed'] and d['mode']==expected and d['helper_sha256']==source_hash
  assert d['total_bytes']==236426193880 and len(d['shards'])==24
  assert math.isfinite(d['elapsed_s']) and 0<=d['elapsed_s']<150
  assert d['workers']==8 and d['internal_read_budget_s']==120 and d['max_block_bytes']==16*1024**2
  logs=list(run.glob('task-'+role+'-node*.log'));assert len(logs)==1
  text=checked(logs[0]).read_text();hosts=re.findall(r'\bhost=([^\s]+)',text);assert hosts and d['host'].split('.')[0]==hosts[0].split('.')[0]
  if expected=='off':assert d['reads']==[]
  else:assert sorted((x['name'],x['bytes_read']) for x in d['reads'])==sorted((x['name'],x['bytes']) for x in d['shards'])
  node_reports.append(d)
 assert len({d['host'] for d in node_reports})==2
 outputs=[p for p in snapshot.rglob('*') if p.is_file() and p.name.endswith('.o'+number)]
 assert len(outputs)==1
 stdout=checked(outputs[0]).read_text(errors='replace')
 ready=re.findall(r'ALL_WORKERS_READY after (\d+)s',stdout);assert len(ready)==1
 accounting=checked(snapshot/'pbs-accounting.txt').read_text()
 h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',accounting).groups());seconds=h*3600+m*60+s
 result=dict(job=job,state='TERMINAL_PREFETCH_AND_SERVING_GATES_PASS',mode=expected,node_reports=node_reports,
             topology_elapsed_to_workers_ready_s=int(ready[0]),allocated_walltime_s=seconds,estimated_charge_su=seconds*16*128/3600,
             limits='The readiness counter starts in topology-job.sh and excludes earlier PBS prologue. Allocation walltime includes startup, scoring, diagnostics and teardown. No initial cache-residency or physical-read proof; node assignment and control-first order can confound a single pair.')
 (O/(job+'-startup-review.json')).write_text(json.dumps(result,indent=2)+'\n');print(job,result['state'])

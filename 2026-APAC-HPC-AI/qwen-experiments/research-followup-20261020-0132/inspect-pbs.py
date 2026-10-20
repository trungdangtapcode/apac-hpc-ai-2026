"""Inspect tails, raw failure components, role logs and sealed diagnostic timelines for the two PBS trials."""
from pathlib import Path
import collections,gzip,hashlib,importlib.util,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('extended',R/'observability-review-20261020/inspect-run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def union(intervals):
 total=0;end=None
 for t,d in sorted(intervals):
  if end is None or t>end:total+=d;end=t+d
  elif t+d>end:total+=t+d-end;end=t+d
 return total
for j in ['222027','222028']:
 snapshot=Path(json.loads((O/('collect-'+j+'.json')).read_text())['destination']);job=j+'.pbs111';run=snapshot/'runs'/job;seal=json.loads((snapshot/'evidence-sha256.json').read_text())
 def checked(p):
  assert m.sha(p)==seal[str(p.relative_to(snapshot))],p
  return p
 artifacts=run/'confirm/n54/artifacts';d=json.loads(checked(artifacts/'profile_export_aiperf.json').read_text());counts=collections.Counter()
 with checked(artifacts/'profile_export.jsonl').open() as f:
  for line in f:
   row=json.loads(line)
   if row['metadata']['phase_kind']!='profiling':continue
   counts['requests']+=1;error=bool(row.get('error') or row.get('errors') or row['metadata']['was_cancelled']);counts['error_or_cancel']+=error
   ttft=row['metrics']['time_to_first_token']['value'];itl=row['metrics']['inter_token_latency']['value'];counts['ttft_over_3000_ms']+=ttft>3000;counts['itl_over_20_ms']+=itl>20;counts['both_latency_breaches']+=(ttft>3000 and itl>20);counts['joint_good']+=not error and ttft<=3000 and itl<=20
 assert counts['requests']==d['request_count']['avg'] and counts['joint_good']==d['good_request_count']['avg']
 result=dict(job=job,client={k:d[k] for k in ['time_to_first_token','inter_token_latency','request_latency','effective_concurrency']},raw_scored_request_components=dict(counts),telemetry_endpoints=d['telemetry_data']['summary']['endpoints_configured'],roles={},traces=[],accuracy_verified=False,limitations=['Server log samples cover the complete deployment and mix phases.','CPU ops can nest; synchronisation duration is waiting, not independent CPU work.','Kernel interval coverage is recorded profile activity, not nvidia-smi utilization or a causal critical-path share.','Separate N48 diagnostic with profile overhead is not the scored N54 run; no prediction of a serving speedup.','Hardware power/VRAM/utilization time series not collected by these old jobs.'])
 for role in ['prefill-0','prefill-1','decode-0']:
  files=list(run.glob('task-'+role+'-node*.log'));assert len(files)==1;lines=checked(files[0]).read_text().splitlines();batches=[line for line in lines if 'Decode batch,' in line or 'Prefill batch,' in line];stats={}
  for key in ['#running-req','#queue-req','token usage']:
   pattern=r'(?:^|, )'+re.escape(key)+r': ([0-9.]+)';stats[key]=m.distribution([float(x.group(1)) for line in batches if (x:=re.search(pattern,line))])
  result['roles'][role]=dict(path=str(files[0]),batch_log_samples=len(batches),distributions=stats,oom_mentions=sum('out of memory' in x.lower() for x in lines if 'server_args=' not in x))
 profile=run/'diagnostic-profile';result['diagnostic_protocol']=json.loads(checked(profile/'protocol.json').read_text());requests=json.loads(checked(profile/'requests.json').read_text());result['diagnostic_requests']=len(requests);result['diagnostic_successes']=sum(x.get('ok') is True and 'error' not in x for x in requests);result['profile_control']=json.loads(checked(profile/'profile-control.json').read_text())
 for p in sorted(profile.rglob('*.trace.json.gz')):
  checked(p)
  with gzip.open(p,'rt') as f:t=json.load(f)
  es=[e for e in t['traceEvents'] if e.get('ph')=='X' and e.get('dur',0)>0];kernels=[e for e in es if e.get('cat')=='kernel'];assert kernels
  counter=collections.Counter();cpu=collections.Counter();rt=collections.Counter();annotations=collections.Counter()
  for e in es:
   target={'kernel':counter,'cpu_op':cpu,'cuda_runtime':rt,'user_annotation':annotations}.get(e.get('cat'))
   if target is not None:target[e.get('name','')]+=e['dur']
  begin=min(e['ts'] for e in kernels);end=max(e['ts']+e['dur'] for e in kernels);busy=union([(e['ts'],e['dur']) for e in kernels]);result['traces'].append(dict(role=p.parent.name,rank=int(re.search(r'-TP-(\d+)',p.name).group(1)),path=str(p),sha256=seal[str(p.relative_to(snapshot))],kernel_span_us=end-begin,kernel_union_us=busy,recorded_kernel_interval_coverage=busy/(end-begin),summed_kernel_us=sum(counter.values()),top_kernel_sums=counter.most_common(6),top_cpu_sums=cpu.most_common(5),top_cuda_runtime_sums=rt.most_common(5),top_annotations=annotations.most_common(5)))
 for role,n in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:assert sorted(x['rank'] for x in result['traces'] if x['role']==role)==list(range(n))
 (O/(job+'-inspection.json')).write_text(json.dumps(result,indent=2)+'\n');print(job,'raw components',dict(counts),'diagnostic',result['diagnostic_successes'],'/',result['diagnostic_requests'],'sealed traces',len(result['traces']),flush=True)

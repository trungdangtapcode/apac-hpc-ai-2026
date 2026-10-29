#!/usr/bin/env python3
"""Review terminal polling arms and retain extended latency/hardware observations."""
from pathlib import Path
import datetime,hashlib,json,math,statistics,subprocess
D=Path(__file__).resolve().parent;Q=D.parent

def dist(values):
 values=sorted(values);assert values
 def quantile(p):
  x=(len(values)-1)*p;i=math.floor(x);j=math.ceil(x)
  return values[i]+(values[j]-values[i])*(x-i)
 return {'count':len(values),'min':min(values),'mean':statistics.mean(values),'p50':quantile(.5),'p95':quantile(.95),'p99':quantile(.99),'max':max(values)}

def analyze(job):
 a=Q/f'runs/{job}';review=json.loads((Q/f'h200-full-load-review-20261026/review-{job}.json').read_text());assert review['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
 raw=[json.loads(l) for l in (a/'confirm/n64/artifacts/profile_export.jsonl').open()];raw=[r for r in raw if r['metadata']['benchmark_phase']=='profiling']
 lo=min(r['metadata']['request_start_ns'] for r in raw);hi=max(r['metadata']['request_start_ns'] for r in raw)
 latency={k:dist([r['metrics'][k]['value'] for r in raw]) for k in ('time_to_first_token','inter_token_latency','request_latency')}
 lengths={k:dist([r['metrics'][k]['value'] for r in raw]) for k in ('input_sequence_length','output_sequence_length')}
 output_histogram={}
 for r in raw:
  key=str(r['metrics']['output_sequence_length']['value']);output_histogram[key]=output_histogram.get(key,0)+1
 hardware={}
 fields={'utilization.gpu':'percent_activity','utilization.memory':'percent_memory_activity','memory.used':'MiB','power.draw':'W','temperature.gpu':'degrees_C','clocks.sm':'MHz','clocks.mem':'MHz'}
 for p in sorted((a/'resource-telemetry').glob('*.jsonl')):
  rows=[json.loads(l) for l in p.open()];samples=[r for r in rows if r['kind']=='sample' and lo<=r['utc_ns']<=hi];role=rows[0]['role'];out={'sample_count':len(samples),'fields':{},'pstates':{}}
  for field,unit in fields.items():
   values=[];missing=0
   for row in samples:
    for g in row.get('gpus',[]):
     try:v=float(g[field]);assert math.isfinite(v)
     except (KeyError,ValueError,TypeError,AssertionError):missing+=1;continue
     values.append(v)
   out['fields'][field]={'unit':unit,'numeric_samples':len(values),'missing_or_nonnumeric':missing,'distribution':dist(values) if values else None}
  for row in samples:
   for g in row.get('gpus',[]):out['pstates'][g.get('pstate','missing')]=out['pstates'].get(g.get('pstate','missing'),0)+1
  hardware[role]=out
 for role in ('prefill-0','prefill-1','decode-0'):assert (a/f'{role}.log').read_text().count('TRANSFER_POLL_SOURCE_VERIFIED')==1
 account=subprocess.check_output(['sacct','-X','-j',str(job),'-P','--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'],text=True);lines=[r.split('|') for r in account.splitlines()];row=dict(zip(lines[0],next(r for r in lines[1:] if r[0]==str(job))));assert row['State']=='COMPLETED' and row['ExitCode']=='0:0'
 result={'job':job,'local_gate':review['state'],'scheduler':row,'actual_allocation_GPU_hours':16*int(row['ElapsedRaw'])/3600,'maximum_reservation_GPU_hours':16*17/60,'PBS_SU':0,'summary':review['summary'],'raw_denominator':len(raw),'ttft_breaches':review['ttft_breaches'],'itl_breaches':review['itl_breaches'],'latency_distributions_ms':latency,'observed_sequence_lengths_tokens':lengths,'observed_output_length_histogram':output_histogram,'diagnostic_exact200_raw_observation':'FAIL_SOME_REPORTED_199; this newly added diagnostic is not a predeclared original gate and does not rewrite it. Physical generated count is unverified without actual IDs or authoritative response usage.','hardware':hardware,'runtime_transport_inspection':review['runtime'],'server_telemetry':review['telemetry_in_admission_envelope'],'source_guard_roles':['prefill-0','prefill-1','decode-0'],'official_accuracy':'UNKNOWN','limits':['Five-second hardware samples inside first-to-last request-start envelope; excludes final drain and has uncalibrated cross-host clock skew.','GPU and memory activity are sample-period time measures, not FLOPS or HBM bandwidth efficiency. Clock/power samples do not diagnose throttling.','Xid/throttling reasons, per-process hot-thread CPU and heavy kernel profile were not collected.','Input command requests fixed synthetic mean 4000/stddev0, but raw tokenizer-measured input length varies; report both without claiming every observed request has exactly 4000 tokens. Raw output accounting also reports a small number of 199 values despite min/max200 command; cause requires independent pinned client-source review.']}
 # Seal original terminal outputs before capture, excluding only cache files and manifest itself.
 manifest=a/'artifact-manifest.json'
 if not manifest.exists():
  (a/'scheduler-accounting.psv').write_text(account)
  files=[]
  for p in sorted(a.rglob('*'))+[Q/f'runs/{job}.out',Q/f'runs/{job}.err']:
   if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p==manifest:continue
   before=p.stat();digest=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
   files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':digest})
  manifest.write_text(json.dumps({'job':job,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':account,'files':files},indent=2)+'\n')
 for f in json.loads(manifest.read_text())['files']:
  p=Q/f['path'];assert p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
 return result

results={str(j):analyze(j) for j in (27270,27272)}
control=results['27270']['summary']['good_output_tokens_s'];value=results['27272']['summary']['good_output_tokens_s']
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'PARTIAL_BRACKET_TWO_REVIEWED_ONE_PENDING','control_job':27270,'candidate_job':27272,'candidate_vs_control_pct':100*(value/control-1),'decision_interval2':'Close unchanged: valid loss, below predeclared >1% useful-gain gate.','interval4_job':27274,'interval4_status':'PENDING at dated scheduler observation; preserve accepted position and do not infer outcome from interval2.','results':results}
(D/'pair-review-27270-27272.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'control_tokens_s':control,'interval2_tokens_s':value,'change_pct':out['candidate_vs_control_pct'],'sequence_lengths':{j:r['observed_sequence_lengths_tokens'] for j,r in results.items()},'decode_hardware':{j:r['hardware']['decode-0'] for j,r in results.items()}},indent=2))

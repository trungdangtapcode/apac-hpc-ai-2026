#!/usr/bin/env python3
"""Inspect actual profiling-request time envelopes; never call them exact phase markers."""
from pathlib import Path
import collections,datetime,importlib.util,json,re
Q=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prior',Q/'research-review-26064-26068-20261025/audit-results.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
results=[]
for job,phase in [(25487,'confirm'),(26083,'screen')]:
 a=Q/f'runs/{job}';p=a/f'{phase}/n64/artifacts/profile_export.jsonl'
 rows=[json.loads(line) for line in p.open()];rows=[r for r in rows if r['metadata']['benchmark_phase']=='profiling'];assert rows
 lo=min(r['metadata']['request_start_ns'] for r in rows);hi=max(r['metadata']['request_start_ns'] for r in rows)
 # This is an observable admission envelope, not a manufactured exact AIPerf phase start.
 role_rows={}
 for role in ('prefill-0','prefill-1'):
  meta=json.loads(next((a/f'resource-telemetry/{role}-g1.jsonl').open()));offsets=set()
  for line in (a/f'resource-telemetry/{role}-g1.jsonl').open():
   r=json.loads(line)
   if r.get('kind')=='sample':offsets.add(r.get('local_utc_offset_s'))
  assert len(offsets)==1 and None not in offsets,offsets
  offset=next(iter(offsets));zone=datetime.timezone(datetime.timedelta(seconds=offset));counts=collections.Counter();batches=[]
  for line in (a/f'{role}.log').read_text().splitlines():
   m=re.match(r'\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) TP0\] Prefill batch, #new-seq: (\d+), #new-token: (\d+).*cuda graph: (True|False)',line)
   if not m:continue
   # Logs have whole-second resolution; exclude boundary seconds to avoid false precision.
   stamp=int(datetime.datetime.strptime(m[1],'%Y-%m-%d %H:%M:%S').replace(tzinfo=zone).timestamp()*1e9)
   if stamp<=lo or stamp+1_000_000_000>=hi:continue
   counts[m[4]]+=1;batches.append({'sequences':int(m[2]),'new_tokens':int(m[3])})
  role_rows[role]={'logged_graph_use_counts':dict(counts),'logged_batch_rows':len(batches),'new_sequence_counts':dict(collections.Counter(r['sequences'] for r in batches)),'log_offset_seconds':offset,'limits':'TP0 batch logging is sparse/implementation-dependent, whole-second timestamps; boundary seconds excluded. Counts are logs, not every kernel invocation or every request.'}
 telemetry=mod.telemetry(a,lo,hi)
 telemetry['limits']='Samples are inside first-to-last profiling REQUEST START envelope. This excludes warmup and final drain but is not an exact AIPerf phase clock; host skew not calibrated. Gauge series remain rank-local. Samples do not prove causal bottlenecks.'
 results.append({'job':job,'profiling_requests':len(rows),'first_request_start_ns':lo,'last_request_start_ns':hi,'observed_admission_span_seconds':(hi-lo)/1e9,'role_graph_logs':role_rows,'telemetry_in_observed_admission_envelope':telemetry})
report={'scope':'Retrospective comparison of actual legacy full25487 versus modern short26083. Workload duration and runtime differ; observations are not a matched causal experiment.','results':results,'next':'Use submitted26313/26315/26317/26319 full controlled study before attributing the score gap.'};(O/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')
for r in results:print(r['job'],round(r['observed_admission_span_seconds'],3),{k:v['logged_graph_use_counts'] for k,v in r['role_graph_logs'].items()})

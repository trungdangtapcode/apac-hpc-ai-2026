"""Review sealed real-ID evidence and bounded runtime/hardware coverage."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,re,importlib.util
O=Path(__file__).resolve().parent
r=json.loads((O/'collection.json').read_text());assert r['state']=='TOKEN_REFERENCE_PASS_AWAITING_RUNTIME_REVIEW'
D=Path(r['destination']);run=D/'runs'/r['job'];seal=json.loads((D/'evidence-sha256.json').read_text())
def read(p):
 assert hashlib.sha256(p.read_bytes()).hexdigest()==seal[str(p.relative_to(D))],str(p)
 return p.read_text(errors='replace')
# Replay semantic gates on the local Python 3.9 reader; frozen compute script uses 3.12 zip(strict=True).
spec=importlib.util.spec_from_file_location('tokens',run/'submitted/token-control.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
token=json.loads(read(run/'token-control.json'));corpus=json.loads(read(run/'submitted/prepared-corpus.json'))
assert token['passed'] and token['cases']==corpus['cases'] and len(corpus['cases'])==4
assert set(token['stages'])=={'target-a','target-b'}
for stage in ['target-a','target-b']:
 rows=token['stages'][stage];assert len(rows)==4
 for case,row in zip(corpus['cases'],rows):
  assert row['name']==case['name'] and row['request']['input_ids']==case['input_ids']
  assert helper.observed(row['response'],len(case['input_ids']))==row['observed']
for before,after in zip(token['stages']['target-a'],token['stages']['target-b']):
 assert before['request']==after['request'] and before['observed']==after['observed']
assert hashlib.sha256((run/'target-identity.json').read_bytes()).hexdigest()==token['target_identity_sha256']
read(run/'target-identity.json')
phases=[json.loads(x) for x in read(run/'phase-markers.jsonl').splitlines()]
a=next(x['utc_ns'] for x in phases if x['event']=='token_diagnostic_start');z=next(x['utc_ns'] for x in phases if x['event']=='token_diagnostic_end');assert a<z
roles={};uuids=set()
for p in (run/'resource-telemetry').glob('*.jsonl'):
 rows=[json.loads(x) for x in read(p).splitlines()];meta=rows[0];samples=[x for x in rows if x['kind']=='sample'];inside=[x for x in samples if a<=x['utc_ns']<=z]
 ids={g['uuid'] for row in samples for g in row.get('gpus',[])};assert not ids & uuids;uuids|=ids
 gauges=collections.defaultdict(list);gpu=collections.defaultdict(lambda:collections.defaultdict(list))
 for row in inside:
  for line in row.get('server_metrics',[]):
   key,value=line.rsplit(' ',1)
   if any(t in key for t in ['num_running_reqs','num_queue_reqs','token_usage']):gauges[key].append(float(value))
  for g in row.get('gpus',[]):
   for key in ['utilization.gpu','memory.used','power.draw']:
    try:gpu[g['uuid']][key].append(float(g[key]))
    except (KeyError,ValueError):pass
 summary=lambda values:dict(samples=len(values),minimum=min(values),maximum=max(values),mean=sum(values)/len(values))
 roles[meta['role']]=dict(host=meta['host'],all_samples=len(samples),diagnostic_samples=len(inside),gpu_uuids=sorted(ids),
  diagnostic_gauges={k:summary(v) for k,v in gauges.items()},diagnostic_gpu={u:{k:summary(v) for k,v in fields.items()} for u,fields in gpu.items()},
  diagnostic_server_statuses=dict(collections.Counter(str(x.get('server_http_status',x.get('server_metrics_status','MISSING'))) for x in inside)))
locality=json.loads(read(run/'worker-locality-request.log'));assert locality['all_roles_mapping_complete'] and len(uuids)==16
runtime={};errors={};warm=[]
for p in run.glob('task-*.log'):
 text=read(p)
 hits=[line for line in text.splitlines() if re.search(r'Traceback|OutOfMemory|out of memory|RuntimeError|AssertionError|NIXL.*(?:fail|error)',line,re.I)]
 if hits:errors[p.name]=hits
 warm.extend(line for line in text.splitlines() if 'ALL 2 P/D paths initialized' in line or re.search(r'prefill-\d/decode-\d OK',line))
 if p.name.startswith(('task-prefill','task-decode')):
  keys=['speculative_algorithm','tp_size','ep_size','kv_cache_dtype','mem_fraction_static','moe_runner_backend','decode_attention_backend','chunked_prefill_size','max_running_requests']
  values={key:list(dict.fromkeys(re.findall(r'\b'+key+r'=([^,)]*)',text))) for key in keys}
  assert values['speculative_algorithm']==['None'] and "'hpc_ops'" in values['moe_runner_backend']
  assert 'NIXL_PATCH_VERIFIED' in text and 'HPC_OPS_PREFLIGHT_PASSED' in text
  runtime[p.name]=values
assert len(runtime)==3 and not errors,errors
responses=[]
for stage,rows in token['stages'].items():
 for row in rows:
  meta=row['response']['meta_info'];assert meta['num_retractions']==0
  responses.append(dict(stage=stage,name=row['name'],elapsed_s=row['elapsed_s'],input_tokens=meta['prompt_tokens'],output_tokens=meta['completion_tokens'],actual_ids=len(meta['output_token_logprobs']),cached_tokens=meta['cached_tokens']))
account=read(D/'pbs-accounting.txt');h,m,s=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());seconds=h*3600+m*60+s
result=dict(job=r['job'],reference_usable=True,reviewed_utc=datetime.now(timezone.utc).isoformat(),collection_sha256=hashlib.sha256((O/'collection.json').read_bytes()).hexdigest(),
 scope='Four exact generic prompt references repeated twice on real target-only PD; not ranked performance or organiser accuracy',
 actual_output_ids=1600,paired_cases=4,all_exact_pairs=True,request_observations=responses,
 phase=dict(start_ns=a,end_ns=z,duration_s=(z-a)/1e9),runtime=runtime,exception_pattern_hits=errors,warmup_paths=warm,roles=roles,
 unique_gpu_uuids=16,locality=locality,walltime_seconds=seconds,estimated_charge_su=16*128*seconds/3600,
 limitations=['Only eight sequential requests; no meaningful contest latency tails/concurrency/error fraction or speedup.',
 'Repeated target-b prompts reuse prefix cache (including 3999 long-prompt tokens). Exact IDs are stable across this cache change; timings are not a cold-cache score.',
 'Hardware/server samples are sparse within the short diagnostic and cannot identify a bottleneck.',
 'Scored per-thread CPU demand and memory placement are uncollected; node-wide CPU/network counters not used to infer role saturation.',
 'No heavy profiles or speculative inference in this target-only job; target/draft embedding/TP/transport/graphs remain future integration gates.',
 'Large target hashes reuse complete verified staging record plus fresh sizes/small-file digests; no new full-weight hash pass.'])
(O/'REFERENCE_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(job=r['job'],reference_usable=True,walltime_seconds=seconds,estimated_su=result['estimated_charge_su'],roles={k:(v['all_samples'],v['diagnostic_samples']) for k,v in roles.items()},elapsed_range_s=[min(x['elapsed_s'] for x in responses),max(x['elapsed_s'] for x in responses)])))

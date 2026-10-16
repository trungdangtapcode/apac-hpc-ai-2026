"""Read existing local artifacts only; never turns a live copy into terminal evidence."""
import collections, datetime, hashlib, json, math, pathlib, re, runpy
ROOT=pathlib.Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT=pathlib.Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
reader=runpy.run_path(str(ROOT/'serving-tuning/review-n54.py'))
rows=[]
for n in (32,34,36):
 artifacts=OUT/f'recovered-live-0626/runs/220720.pbs111/confirm/n{n}/artifacts'
 data=read(artifacts/'profile_export_aiperf.json');manifest=read(artifacts/'phase_manifest.json')
 metrics=reader['validate_metrics'](data,manifest,n)
 raw=[json.loads(line) for line in (artifacts/'profile_export.jsonl').read_text().splitlines()]
 counts=collections.Counter(r['metadata']['phase_kind'] for r in raw)
 assert dict(counts)=={p['kind']:p['requests'] for p in metrics['phases']}
 assert all(not r['metadata']['was_cancelled'] and not r.get('error') and not r.get('errors') for r in raw)
 measured=[r for r in raw if r['metadata']['phase_kind']=='profiling']
 assert sum(r['metrics']['good_request_count']['value'] for r in measured)==data['good_request_count']['avg']
 lengths=[r['metrics']['output_sequence_length']['value'] for r in measured]
 assert (sum(lengths),min(lengths),max(lengths))==tuple(data['output_sequence_length'][k] for k in ('sum','min','max'))
 for key in ('time_to_first_token','inter_token_latency'):
  assert math.isclose(sum(r['metrics'][key]['value'] for r in measured)/len(measured),data[key]['avg'])
 rows.append({'concurrency':n,'metrics':metrics,'raw_counts':dict(counts),'raw_metrics_match':True,'output_length_min_max':[min(lengths),max(lengths)]})
(OUT/'h100-historical-live-point-review.json').write_text(json.dumps({'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'HISTORICAL_LIVE_COPY_POINT_CHECKS_PASS_NOT_TERMINAL','source_capture_utc':'2026-10-16T06:26:32Z','points':rows,'runtime_rank_proof':False,'final_quality_review':False,'accuracy_verified':False},indent=2)+'\n')

def score(row):
 text=row['response']['choices'][0]['message']['content']
 assert text==row['text']
 stripped=re.sub(r'^```(?:json)?\s*|\s*```$', '',text.strip(),flags=re.I).strip();expected=row['expected']
 if isinstance(expected,(dict,list)):
  try:return json.loads(stripped)==expected
  except ValueError:return False
 return stripped.strip('\"\'` .\n').lower()==expected
baseline=[json.loads(line) for line in (ROOT/'runs/23146/output-diagnostic.jsonl').read_text().splitlines()]
smoke=read(ROOT/'runs/23934/output-smoke.json')
assert len(baseline)==132 and all(score(r)==r['passed'] for r in baseline)
assert all(score(r)==r['passed'] for r in smoke['cases'])
assert sum(score(r) for r in smoke['cases'])==smoke['passed']==7
candidate=read(OUT/'n54-23934-review.json')['candidate']
mnnvl=read(ROOT/'nscc-pbs/inspection/wake-20261016-0520UTC/n54-23924-review.json')['candidate']
seal=ROOT/'runs/23924/artifact-manifest.json'
assert hashlib.sha256(seal.read_bytes()).hexdigest()==mnnvl['seal_sha256']
log=(ROOT/'runs/23934/decode-0.log').read_text()
rank_load=sorted({int(r) for r in re.findall(r'TP(\d+) DP\d+ EP\d+\] Load weight end',log)})
args=candidate['server_args']['decode-0']
report={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'dp_job':'23934','mnnvl_job':'23924','dp_n54_vs_mnnvl_n54':reader['metric_delta'](candidate['metrics'],mnnvl['metrics']),'dp_metrics':candidate['metrics'],'mnnvl_metrics':mnnvl['metrics'],'dp_runtime_fields':{k:v for k,v in args.items() if k in ('tp_size','dp_size','ep_size','enable_dp_attention','moe_runner_backend','moe_a2a_backend','deepep_mode','deepep_dispatcher_output_dtype','disable_custom_all_reduce','kv_cache_dtype')},'raw_smoke_rescored':{'baseline_cases':132,'baseline_passed':sum(score(r) for r in baseline),'candidate_cases':8,'candidate_passed':7,'candidate_failed':[r['name'] for r in smoke['cases'] if not score(r)]},'caveat':'One N54 point per backend, seed/node/time drift; descriptive package comparison, no isolated kernel effect, repeatability or organiser accuracy claim. No extra DP repeat or N56 planned.'}
(OUT/'n54-same-load-and-output-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'h100_historical_points':rows,'same_load_dp_vs_mnnvl':report['dp_n54_vs_mnnvl_n54'],'raw_smoke_rescored':report['raw_smoke_rescored']},indent=2))

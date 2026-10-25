#!/usr/bin/env python3
"""Review a failed warmup without manufacturing scored metrics."""
from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,subprocess
OUT=Path(__file__).resolve().parent;Q=OUT.parent;A=Q/'runs/26081';B=A/'submitted-payload'
state=subprocess.check_output(['sacct','-j','26081','--format=JobID,State,ExitCode,Elapsed,NodeList','-n'],text=True)
assert 'FAILED' in state
(A/'scheduler-accounting.txt').write_text(state)
spec=importlib.util.spec_from_file_location('sem',B/'warmup_semantic.py');sem=importlib.util.module_from_spec(spec);spec.loader.exec_module(sem)
inv,pairs,_=sem.inventory(A/'endpoints.tsv');expected={p['pair_id']:p for p in pairs}
context=json.loads((A/'pair-warmup-context.json').read_text());token=hashlib.sha256(context['experiment_id'].encode()).hexdigest()[:32]
receipts=[]
for p in sorted((A/'pair-warmup-receipts').glob('receipt*.json')):
 d=json.loads(p.read_text());assert d['inventory_sha256']==inv and d['run_token']==token
 assert all(d[k]==v for k,v in expected[d['pair_id']].items())
 response=json.loads(p.with_name('response-'+d['pair_id']+'.json').read_text())
 assert d['response_sha256']==hashlib.sha256(json.dumps(response,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 metrics=sem.validate_response(response['http_status'],response['body']);assert all(d[k]==v for k,v in metrics.items())
 receipts.append({'prefill':d['prefill'],'decode':d['decode'],'completion_tokens':d['completion_tokens'],'http_status':d['http_status'],'raw_response_hash_and_semantics':'PASS'})
try:sem.check(A/'pair-warmup-receipts',A/'endpoints.tsv',token)
except ValueError as e:full_gate_error=str(e)
else:raise AssertionError('Incomplete four-route gate incorrectly passed')
telemetry=[];uuids=set()
for p in sorted((A/'resource-telemetry').glob('*.jsonl')):
 samples=successful_server=0;role_ids=set()
 for line in p.open():
  d=json.loads(line)
  if d.get('kind')!='sample':continue
  samples+=1
  role_ids.update(x['uuid'] for x in d.get('gpus',[]) if x.get('uuid'))
  successful_server+=int(d.get('server_http_status')==200)
 uuids.update(role_ids);telemetry.append({'file':p.name,'samples':samples,'gpu_uuid_count':len(role_ids),'server_http_200_samples':successful_server})
geometry=json.loads((A/'kv-geometry-validation.json').read_text());runtime=json.loads((A/'runtime-readiness.json').read_text())
assert geometry['passed'] is True and geometry['receipt_count']==32
report={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':26081,'scheduler':state,'runtime_state':runtime['state'],'geometry_receipts':geometry['receipt_count'],'individually_valid_routes':receipts,'full_semantic_gate':'FAIL','full_semantic_gate_error':full_gate_error,'aiperf_exports':len(list(A.glob('screen/**/profile_export_aiperf.json'))),'unique_sampled_gpus':len(uuids),'telemetry_coverage':telemetry,'telemetry_limit':'Startup-only coverage inspected; no scored phase, so no scored utilization/CPU/KV/tail/error measurement. No causal bottleneck inferred.','scored_goodput':'NOT_MEASURED','official_accuracy':'UNKNOWN','next_decision':'Close full-topology retries after the bounded S62r4 attempt; retain other queued hypotheses. Diagnose failed prefill-0 routes from existing evidence before any new transport experiment.'}
(OUT/'inspection.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

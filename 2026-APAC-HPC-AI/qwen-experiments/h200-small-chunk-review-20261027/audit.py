#!/usr/bin/env python3
"""Audit raw SLA failures without converting them into accepted benchmark scores."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,math,subprocess
S=Path(__file__).resolve().parent;Q=S.parent
A=Q/'runs/26475';B=A/'submitted-payload'
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
spec=importlib.util.spec_from_file_location('gates',B/'performance_gates.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
e=json.loads((A/'confirm/n64/artifacts/profile_export_aiperf.json').read_text());assert g.normalize_input_config(e['input_config'])==json.loads((B/'expected-input-config.json').read_text())
rows=[json.loads(x) for x in (A/'confirm/n64/artifacts/profile_export.jsonl').open()];rows=[r for r in rows if r['metadata']['benchmark_phase']=='profiling'];assert len(rows)==1580
badttft=sum(r['metrics']['time_to_first_token']['value']>3000 for r in rows);baditl=sum(r['metrics']['inter_token_latency']['value']>20 for r in rows);good=sum(r['metrics']['time_to_first_token']['value']<=3000 and r['metrics']['inter_token_latency']['value']<=20 for r in rows)
assert math.isclose(good/len(rows),e['good_request_fraction']['avg'],abs_tol=1e-12) and good/len(rows)<.9
smoke=g.check_smoke(A,B/'reference-output-smoke.json');retrieval=g.check_retrieval(A)
summary=json.loads((A/'summary.json').read_text())[0];assert summary['errors']==summary['cancelled_requests']==0
runtime=json.loads((A/'runtime-readiness.json').read_text());geometry=json.loads((A/'kv-geometry-validation.json').read_text());assert runtime['state']=='PASS_FAST_RUNTIME' and geometry['passed']
logs={}
for role in ['prefill-0','prefill-1','decode-0']:
 text=(A/f'{role}.log').read_text(errors='replace');logs[role]={'tracebacks':text.count('Traceback (most recent call last)'), 'no_space':text.count('No space left on device'),'selected_transport_errors':[line[:400] for line in text.splitlines() if 'KVTransferError' in line or 'NIXL transport error' in line]}
prior_spec=importlib.util.spec_from_file_location('resources',Q/'research-review-26064-26068-20261025/audit-results.py');prior=importlib.util.module_from_spec(prior_spec);prior_spec.loader.exec_module(prior)
lo=min(r['metadata']['request_start_ns'] for r in rows);hi=max(r['metadata']['request_start_ns'] for r in rows);telemetry=prior.telemetry(A,lo,hi)
for host in telemetry['hosts'].values():
 for key in ['available_memory_TiB_at_start','total_memory_TiB']:
  if key in host:host[key.replace('TiB','GiB')]=host.pop(key)
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':26475,'state':'RAW_WORKLOAD_AUDITED_JOINT_SLA_FAILED_NOT_ACCEPTED','score_eligible':False,'profiling_requests':len(rows),'good_requests':good,'ttft_breaches':badttft,'itl_breaches':baditl,'summary':summary,'smoke':smoke,'retrieval':retrieval,'runtime':runtime,'geometry_pass':geometry['passed'],'log_inspection':logs,'telemetry_request_start_envelope':telemetry,'limits':'Five-second sparse samples with uncalibrated clock skew. Existing strict head gate correctly failed; no threshold weakened, no score accepted. Official accuracy UNKNOWN.'}
(S/'review-26475.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'job':26475,'state':out['state'],'good_fraction':good/len(rows),'ttft_breaches':badttft,'itl_breaches':baditl,'smoke':smoke,'retrieval':retrieval}))
# Seal both terminal artifacts, preserving the failed run as failed.
for job in [26473,26475]:
 a=Q/f'runs/{job}';state=subprocess.check_output(['sacct','-X','-j',str(job),'-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True);assert 'RUNNING' not in state and ('COMPLETED' in state or 'FAILED' in state);(a/'scheduler-accounting.psv').write_text(state)
 if (a/'artifact-manifest.json').exists():continue
 files=[]
 for p in sorted(a.rglob('*')):
  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p.name=='artifact-manifest.json':continue
  before=p.stat();h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  assert (before.st_size,before.st_mtime_ns)==(p.stat().st_size,p.stat().st_mtime_ns)
  files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
 for p in [Q/f'runs/{job}.out',Q/f'runs/{job}.err']:files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (a/'artifact-manifest.json').write_text(json.dumps({'job':job,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scheduler_accounting':state,'files':files},indent=2)+'\n')

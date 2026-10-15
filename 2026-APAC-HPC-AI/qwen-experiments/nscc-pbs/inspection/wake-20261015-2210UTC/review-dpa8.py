"""Independent final evidence audit of DP-attention repeat, no controller mutation."""
import datetime, hashlib, json, math, re, subprocess
from pathlib import Path
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT=Path(__file__).resolve().parent
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
status=subprocess.check_output(['sacct','-X','-j','23780,23859','-n','-P','--format=JobID,State,ExitCode,Start,End'],text=True)
(OUT/'repeat-accounting.txt').write_text(status)
statuses={x[0]:dict(zip(['job','state','exit','start','end'],x)) for line in status.splitlines() if (x:=line.split('|')) and x[0]}
assert all(statuses[j]['state']=='COMPLETED' and statuses[j]['exit']=='0:0' for j in ['23780','23859']), statuses
runs=[]
for job in ['23780','23859']:
 run=ROOT/'runs'/job; export=run/'confirm/n52/artifacts/profile_export_aiperf.json'
 d=read(export); cfg=d['input_config']; phases=cfg['phases']
 assert [(p['duration'],p['concurrency']) for p in phases]==[(60,52),(120,52)]
 assert phases[0]['exclude_from_results'] and phases[1]['grace_period']==30
 assert not d['was_cancelled'] and d['error_summary']==[]
 manifest=read(run/'confirm/n52/artifacts/phase_manifest.json')
 assert len(manifest['phases'])==2
 timing=[]
 for p in manifest['phases']:
  assert not p['was_cancelled'] and p['error_request_count']==0 and p['error_summary']==[]
  assert p['total_request_count']==p['successful_request_count']>0
  seconds=(p['end_ns']-p['start_ns'])/1e9
  minimum=60 if p['phase_kind']=='warmup' else 120
  assert minimum<=seconds<=minimum+30
  timing.append(dict(kind=p['phase_kind'],elapsed_s=seconds,successful=p['successful_request_count']))
 smoke=read(run/'output-smoke.json'); failed=[c['name'] for c in smoke['cases'] if not c['passed']]
 assert smoke['total']==8 and smoke['passed']==7 and failed==['reverse']
 assert all('error' not in c for c in smoke['cases'])
 log=(run/'decode-0.log').read_text()
 ranks=sorted({int(i) for i in re.findall(r'DP(\d+) TP\d+ EP\d+\] NIXL KVManager initialized with backend: UCX',log)})
 assert ranks==list(range(8)), ranks
 assert 'ALL 2 P/D paths initialized' in (run/'pair-warmup.log').read_text()
 assert sum(' 200 ' in line for line in (run/'connection-warmup.log').read_text().splitlines())==8
 avg=lambda k:d[k]['avg']
 good=avg('goodput')*200
 assert math.isclose(avg('good_request_count')/avg('request_count'),avg('good_request_fraction'))
 stored=json.loads(subprocess.check_output(['python3',str(ROOT/'summarize.py'),str(run)],text=True))[0]
 assert math.isclose(good,stored['good_output_tokens_s']) and stored['errors']==0 and stored['cancelled_requests']==0
 files=[p for p in run.rglob('*') if p.is_file() and p.name not in ['summary.json','artifact-manifest.json','output-baseline-comparison.json']]
 files += [p for p in [ROOT/'runs'/f'{job}.out',ROOT/'runs'/f'{job}.err'] if p.exists()]
 seal=run/'artifact-manifest.json'
 if not seal.exists():
  data=dict(job=job,sealed_utc=now(),status_at_seal=statuses[job],scope='Finished artifacts inventoried after scheduler COMPLETED; not a submission-time seal. Derived summary and baseline comparison excluded.',files=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
  with seal.open('x') as f:json.dump(data,f,indent=2)
 sealed=read(seal); mismatch=[e['path'] for e in sealed['files'] if sha(ROOT/e['path'])!=e['sha256']]
 assert not mismatch
 runs.append(dict(job=job,good_tokens_s=good,sla=avg('good_request_fraction'),requests=avg('request_count'),ttft_ms=avg('time_to_first_token'),itl_ms=avg('inter_token_latency'),phase_timings=timing,nixl_initialized_ranks=ranks,smoke_failed_cases=failed,manifest_files_verified=len(sealed['files']),observed_input_mean=avg('input_sequence_length'),observed_output=d['output_sequence_length'],protocol=cfg))
a,b=[ROOT/'runs'/j/'submitted' for j in ['23780','23859']]
common=['worker.sh','benchmark.sh','topology-job.sh','output-smoke.py','nixl-conn.py','nixl-ondemand.patch','nixl-patch-metadata.json','warm-topology.py','placement.tsv','profile-serving.py','summarize.py','nixl-geometry-test.json']
payload={f:sha(a/f)==sha(b/f) for f in common};assert all(payload.values())
ca,cb=[read(ROOT/'runs'/j/'config.json') for j in ['23780','23859']]
diff={k:[ca.get(k),cb.get(k)] for k in ca.keys()|cb.keys() if ca.get(k)!=cb.get(k)}; assert set(diff)=={'experiment','purpose'}
# Endpoint addresses differ between allocations; the benchmark's other settings must match.
pa,pb=[r.pop('protocol') for r in runs]
pa['endpoint'].pop('urls',None);pb['endpoint'].pop('urls',None)
pa['artifacts'].pop('dir',None);pb['artifacts'].pop('dir',None)
assert pa==pb, 'Unexpected effective benchmark configuration difference'
mean=lambda k:sum(r[k] for r in runs)/2
controls={j:read(ROOT/'runs'/j/'summary.json')[0] for j in ['23576','23607','23778','23839']}
mnnvl=sum(controls[j]['good_output_tokens_s'] for j in ['23778','23839'])/2
result=dict(reviewed_utc=now(),runs=runs,identical_payload=payload,config_differences=diff,mean_good_tokens_s=mean('good_tokens_s'),repeat_change_percent=(runs[1]['good_tokens_s']/runs[0]['good_tokens_s']-1)*100,gain_percent_vs_controls={j:(mean('good_tokens_s')/c['good_output_tokens_s']-1)*100 for j,c in controls.items()},gain_percent_vs_mnnvl_mean=(mean('good_tokens_s')/mnnvl-1)*100,mean_ttft_ms=mean('ttft_ms'),mean_itl_ms=mean('itl_ms'),ttft_delta_ms_vs_23607=mean('ttft_ms')-controls['23607']['ttft_avg_ms'],itl_delta_ms_vs_23607=mean('itl_ms')-controls['23607']['itl_avg_ms'],existing_n54_gate_passes=all(r['good_tokens_s']>=2448.1867160875026 and r['sla']>=.95 and r['itl_ms']<=19.3 for r in runs),accuracy_verified=False,no_new_gpu_submission=True)
with (OUT/'dpa8-repeat-review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['runs','identical_payload','config_differences']},indent=2))

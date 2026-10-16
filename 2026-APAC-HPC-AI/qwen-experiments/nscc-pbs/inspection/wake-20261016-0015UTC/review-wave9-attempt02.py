"""Read-only terminal review: two wave9 candidates against both MNNVL baselines."""
import ast, copy, datetime, difflib, hashlib, json, math, re, runpy, subprocess
from pathlib import Path
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def args(p):
 line=next(l.split('server_args=',1)[1] for l in p.read_text().splitlines() if 'server_args=ServerArgs(' in l)
 return {k.arg:ast.unparse(k.value) for k in ast.parse(line,mode='eval').body.keywords}
def normalize(d):
 d=copy.deepcopy(d);d['endpoint'].pop('urls');d['artifacts'].pop('dir');return d
registry=read(ROOT/'serving-tuning/registry.json')
compare_output=runpy.run_path(str(ROOT/'watch-serving-tuning.py'))['compare_output_baseline']
status=subprocess.check_output(['sacct','-X','-n','-P','-j','23778,23839,23904,23905','--format=JobID,State,ExitCode,Start,End'],text=True)
(OUT/'terminal-accounting.txt').write_text(status)
statuses={a[0]:dict(zip(['job','state','exit','start','end'],a)) for l in status.splitlines() if (a:=l.split('|')) and a[0]}
results={};protocols={}
for job in ['23778','23839','23904','23905']:
 run=ROOT/'runs'/job
 assert statuses[job]['state']=='COMPLETED' and statuses[job]['exit']=='0:0',statuses[job]
 seal=read(run/'artifact-manifest.json')
 assert seal['job']==job
 for e in seal['files']:
  p=ROOT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
 d=read(run/'confirm/n52/artifacts/profile_export_aiperf.json');cfg=d['input_config'];protocols[job]=normalize(cfg)
 assert [(p['duration'],p['concurrency']) for p in cfg['phases']]==[(60,52),(120,52)]
 assert cfg['phases'][0]['exclude_from_results'] and cfg['phases'][1]['grace_period']==30
 assert cfg['slos']=={'time_to_first_token':3000.0,'inter_token_latency':20.0}
 assert d['error_summary']==[] and d['was_cancelled'] is False
 manifest=read(run/'confirm/n52/artifacts/phase_manifest.json');assert len(manifest['phases'])==2
 timing=[]
 for p in manifest['phases']:
  assert not p['was_cancelled'] and p['error_request_count']==0 and p['error_summary']==[]
  assert p['total_request_count']==p['successful_request_count']>0
  elapsed=(p['end_ns']-p['start_ns'])/1e9;minimum=60 if p['phase_kind']=='warmup' else 120
  assert minimum<=elapsed<=minimum+30
  timing.append(dict(kind=p['phase_kind'],elapsed_s=elapsed,requests=p['total_request_count']))
 assert timing[1]['requests']==d['request_count']['avg']
 smoke=read(run/'output-smoke.json');comparison=compare_output(smoke,ROOT/'runs/23146/output-diagnostic.jsonl')
 assert comparison['research_eligible'] and comparison['new_failed_cases']==[]
 assert smoke['passed']==7 and smoke['total']==8
 assert [c['name'] for c in smoke['cases'] if not c['passed']]==['reverse']
 avg=lambda k:d[k]['avg']
 assert math.isclose(avg('good_request_count')/avg('request_count'),avg('good_request_fraction'))
 good=avg('goodput')*200
 stored=read(run/'summary.json')[0]
 assert math.isclose(good,stored['good_output_tokens_s']) and stored['errors']==stored['cancelled_requests']==0
 # Preserve observed lengths; configured200 is not a claim every observed length equals200.
 assert d['output_sequence_length']['min']>=199 and d['output_sequence_length']['max']<=201
 raw=[json.loads(l) for l in (run/'confirm/n52/artifacts/profile_export.jsonl').open()]
 measured=[r for r in raw if r['metadata']['phase_kind']=='profiling']
 assert len(measured)==avg('request_count')
 assert all(not r['metadata']['was_cancelled'] and not r.get('error') and not r.get('errors') for r in raw)
 lengths=[r['metrics']['output_sequence_length']['value'] for r in measured]
 assert sum(lengths)==d['output_sequence_length']['sum'] and min(lengths)==d['output_sequence_length']['min'] and max(lengths)==d['output_sequence_length']['max']
 log=(run/'decode-0.log').read_text()
 mnnvl=sorted({int(n) for n in re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',log)})
 nixl=sorted({int(n) for n in re.findall(r'TP(\d+) EP\d+\] NIXL KVManager initialized with backend: UCX',log)})
 assert mnnvl==nixl==list(range(8))
 assert 'ALL 2 P/D paths initialized' in (run/'pair-warmup.log').read_text()
 assert sum(' 200 ' in l for l in (run/'connection-warmup.log').read_text().splitlines())==8
 results[job]=dict(status=statuses[job],seal_files_verified=len(seal['files']),good_tokens_s=good,sla_percent=100*avg('good_request_fraction'),ttft_ms=avg('time_to_first_token'),itl_ms=avg('inter_token_latency'),phases=timing,input_lengths=d['input_sequence_length'],output_lengths=d['output_sequence_length'],output_comparison=comparison,mnnvl_ranks=mnnvl,nixl_ranks=nixl)
for p in protocols.values():assert p==protocols['23778'],'Benchmark protocol mismatch'
common=['benchmark.sh','topology-job.sh','output-smoke.py','nixl-conn.py','nixl-ondemand.patch','nixl-patch-metadata.json','warm-topology.py','placement.tsv','profile-serving.py','summarize.py','nixl-geometry-test.json']
for job in ['23904','23905']:
 run=ROOT/'runs'/job
 entry=next(e for e in registry['entries'] if any(a['job']==job for a in e['attempts']))
 bundle=Path(entry['bundle'])
 for f,h in entry['payload_sha256'].items():assert sha(bundle/f)==sha(run/'submitted'/f)==h
 check=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=bundle,capture_output=True,text=True,check=True)
 (OUT/f'{job}-bundle-check.txt').write_text(check.stdout)
 for f in ['worker.sh','benchmark.sh','config.json','summarize.py']:assert sha(run/f)==sha(run/'submitted'/f)
 # Frozen stored scripts were captured while pending; a completed Slurm job may be purged.
 stored=ROOT/'nscc-pbs/inspection/wake-20261015-2150UTC'/f'{job}-stored.sbatch'
 if not stored.exists():stored=ROOT/'nscc-pbs/inspection/wake-20261015-2150UTC'/f'{job}-slurm.sbatch'
 assert stored.exists(),f'Missing earlier stored batch script {job}'
 assert stored.read_bytes()==(bundle/'job.sbatch').read_bytes()
 comparisons={}
 for base in ['23778','23839']:
  assert all(sha(run/'submitted'/f)==sha(ROOT/'runs'/base/'submitted'/f) for f in common)
  before=(ROOT/'runs'/base/'submitted/worker.sh').read_text();after=(run/'submitted/worker.sh').read_text()
  expected=before.replace('--flashinfer-allreduce-fusion-backend mnnvl','--flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer') if job=='23904' else before.replace('--chunked-prefill-size 4096','--chunked-prefill-size 2048')
  assert after==expected,(job,base,'Worker unexpected differences')
  (OUT/f'{job}-vs-{base}-worker.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=base,tofile=job)))
  comparisons[base]={}
  for role in ['prefill-0','prefill-1','decode-0']:
   a=args(ROOT/'runs'/base/f'{role}.log');b=args(run/f'{role}.log')
   diff={k:[a.get(k),b.get(k)] for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
   allowed={'random_seed'}|({'decode_attention_backend'} if job=='23904' and role=='decode-0' else {'chunked_prefill_size'} if job=='23905' and role.startswith('prefill') else set())
   assert not set(diff)-allowed,(job,base,role,diff)
   comparisons[base][role]=diff
  baseline=results[base];actual=results[job]
  comparisons[base]['metrics']=dict(gain_percent=100*(actual['good_tokens_s']/baseline['good_tokens_s']-1),ttft_delta_ms=actual['ttft_ms']-baseline['ttft_ms'],itl_delta_ms=actual['itl_ms']-baseline['itl_ms'])
 chunks=[int(args(run/f'{role}.log')['chunked_prefill_size']) for role in ['prefill-0','prefill-1']]
 assert chunks==([4096,4096] if job=='23904' else [2048,2048]),chunks
 decode=args(run/'decode-0.log');assert decode['cuda_graph_bs_decode']==repr(list(range(1,65)))
 if job=='23904':
  ranks=sorted({int(n) for n in re.findall(r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3',(run/'decode-0.log').read_text())})
  assert ranks==list(range(8))
 results[job].update(prefill_chunks=chunks,effective_args_vs_each_baseline=comparisons,payload_verified=True,earlier_slurm_script_verified=str(stored),common_operational_files=common)
mean=lambda k:sum(results[j][k] for j in ['23778','23839'])/2
for j in ['23904','23905']:
 results[j]['vs_baseline_mean']=dict(gain_percent=100*(results[j]['good_tokens_s']/mean('good_tokens_s')-1),ttft_delta_ms=results[j]['ttft_ms']-mean('ttft_ms'),itl_delta_ms=results[j]['itl_ms']-mean('itl_ms'))
result=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),runs=results,baseline_mean={k:mean(k) for k in ['good_tokens_s','ttft_ms','itl_ms']},full_protocol_equal=True,errors=0,cancellations=0,accuracy_verified=False,new_jobs_submitted=False,engine_seed_caveat='AIPerf2026 does not fix the unpinned engine seed; resolved ServerArgs changes recorded.')
(OUT/'wave9-final-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({j:{k:v for k,v in r.items() if k in ['good_tokens_s','sla_percent','ttft_ms','itl_ms','phases','vs_baseline_mean','prefill_chunks','seal_files_verified']} for j,r in results.items()},indent=2))

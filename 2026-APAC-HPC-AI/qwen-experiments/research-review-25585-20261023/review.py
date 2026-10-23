"""Seal and independently replay the repaired native H200 reference after cleanup."""
from pathlib import Path
from datetime import datetime,timezone
import collections,csv,hashlib,importlib.util,json,os,re,subprocess
O=Path(__file__).resolve().parent;R=O.parent;JOB='25585';run=R/'runs'/JOB
B=R/'serving-tuning-10/s38-h200-target-reference-homefix'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert JOB not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split(),'Wait for allocation cleanup'
raw=subprocess.check_output(['sacct','-X','-j',JOB,'-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True)
status=list(csv.DictReader(raw.splitlines(),delimiter='|'))[0]
assert status['JobID']==JOB and status['State']=='COMPLETED' and status['ExitCode']=='0:0',status
(O/'accounting.psv').write_text(raw)
seal=run/'artifact-manifest.json'
if not seal.exists():
 files=[p for p in run.rglob('*') if p.is_file() and p.name not in {'summary.json','artifact-manifest.json'} and '__pycache__' not in p.parts]+[R/'runs'/f'{JOB}.out',R/'runs'/f'{JOB}.err']
 rows=[]
 for p in sorted(files):
  assert not p.is_symlink();before=p.stat();digest=sha(p);after=p.stat()
  assert all(getattr(before,f)==getattr(after,f) for f in ['st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns'])
  rows.append(dict(path=str(p.relative_to(R)),bytes=after.st_size,sha256=digest))
 with seal.open('x') as output:json.dump(dict(job=JOB,sealed_utc=datetime.now(timezone.utc).isoformat(),status_at_seal=status,scope='Terminal native target-reference evidence after allocation cleanup',files=rows),output,indent=2);output.write('\n')
assert all(sha(R/x['path'])==x['sha256'] for x in json.loads(seal.read_text())['files'])
for line in (B/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);assert sha(B/name)==digest and sha(run/'submitted-payload'/name)==digest,name
IMAGE='/scratch/enroot-images/sglang-harbor.sqsh';MODEL='/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8'
head=subprocess.run(['python3','-B',str(B/'check-token-result.py'),str(run/'target-reference.json'),MODEL],env=dict(os.environ,QWEN_IMAGE_PATH=IMAGE),capture_output=True,text=True,timeout=30)
(O/'head-replay.stdout').write_text(head.stdout);(O/'head-replay.stderr').write_text(head.stderr)
assert head.returncode==0 and 'H200_TARGET_REFERENCE_SEMANTIC_GATE_PASSED' in head.stdout
assert 'H200_TARGET_REFERENCE_SEMANTIC_GATE_PASSED' in (run/'head-result-check.log').read_text()
result=json.loads((run/'target-reference.json').read_text());identity=json.loads((run/'asset-preflight.json').read_text())
assert identity==result['asset_identity'] and identity['verified_file_count']==34
context=json.loads((run/'pair-warmup-context.json').read_text());experiment=context['experiment_id']
assert result['experiment_id']==experiment and experiment.startswith('eagle3-h200-reference-'+JOB+'-')
spec=importlib.util.spec_from_file_location('warmup_semantic',B/'warmup_semantic.py');warm=importlib.util.module_from_spec(spec);spec.loader.exec_module(warm)
receipt=warm.check(run/'pair-warmup-receipts',run/'endpoints.tsv',hashlib.sha256(experiment.encode()).hexdigest()[:32]);assert receipt['pair_count']==2
roles={}
for role,n in [('prefill-0',4),('prefill-1',4),('decode-0',8)]:
 check=subprocess.run(['python3',str(B/'check-kv-ranks.py'),str(run/(role+'.log')),role],capture_output=True,text=True,check=True)
 logs=(run/(role+'.log')).read_text(errors='replace');assert 'NIXL_ERR_' not in logs and 'CUDA out of memory' not in logs
 rows=[json.loads(line) for p in (run/'resource-telemetry').glob(role+'-*.jsonl') for line in p.read_text().splitlines() if line.strip()]
 samples=[x for x in rows if x.get('kind')=='sample'];gpus=[g for x in samples for g in x.get('gpus',[])]
 uuids={g['uuid'] for g in gpus}
 def span(key):
  values=[float(g[key]) for g in gpus if g.get(key) not in (None,'N/A','[N/A]')]
  return dict(min=min(values),max=max(values)) if values else 'not_collected'
 roles[role]=dict(bf16_rank_count=n,rank_check=check.stdout.strip(),hardware_samples=len(samples),unique_sampled_gpu_uuids=len(uuids),expected_device_coverage=(len(uuids)==n),sampled_vram_mib=span('memory.used'),sampled_gpu_activity_percent=span('utilization.gpu'),sampled_power_w=span('power.draw'),server_http_status_counts=dict(collections.Counter(str(x.get('server_http_status',x.get('server_metrics_status','missing'))) for x in samples)),scope='Startup and sequential N1 diagnostic samples only; no scored interval or peak/saturation inference')
batch=(R/'runs'/f'{JOB}.out').read_text();deadlines=dict(line.split('=',1) for line in (run/'deadlines.txt').read_text().splitlines())
t0=int(deadlines['started_epoch']);times={}
for marker in ['ALL_WORKERS_READY','ALL_PAIRS_WARM','TOKEN_REFERENCE_PASS']:
 matches=re.findall(marker+r' at=(\d+)',batch);assert len(matches)==1;times[marker]=int(matches[0])-t0
assert times['ALL_WORKERS_READY']<600 and times['ALL_PAIRS_WARM']<930 and times['TOKEN_REFERENCE_PASS']<950
requests=[dict(stage=stage,name=x['name'],input_tokens=len(x['request']['input_ids']),output_ids=len(x['observed']['output_ids']),elapsed_s=x['elapsed_s']) for stage,rows in result['stages'].items() for x in rows]
assert len(requests)==8 and sum(x['output_ids'] for x in requests)==1600
review=dict(job=JOB,reviewed_utc=datetime.now(timezone.utc).isoformat(),state='H200_TARGET_REFERENCE_ACCEPTED',accepted_reference=True,payload_and_raw_hashes_verified=True,seal_sha256=sha(seal),reference_path=str(run/'target-reference.json'),reference_sha256=sha(run/'target-reference.json'),asset_manifest_sha256=identity['verification_manifest_sha256'],asset_identity_matches_pre_worker_and_result=True,head_runtime_check_and_independent_replay_pass=True,experiment_id=experiment,both_semantic_pd_receipts=receipt,actual_output_token_ids=1600,requests=requests,repeated_greedy_ids_and_finish_equal=True,roles=roles,phase_times_since_start_s=times,kv_geometry='not_collected',scored_performance_measured=False,eagle3_used=False,official_accuracy_verified=False,limits=['Eight sequential diagnostic requests are not MMLU-Pro/GPQA or a performance load test.','Second-pass prefix reuse may change timing; N1 elapsed times are not cold-cache speedup.','Native target only; no EAGLE3 state/transport/output correctness follows.','Full model/image hashes come from the retained verified manifest, with runtime fingerprints and rehashed small metadata.','Detailed KV region geometry and tensor strides are not collected in this reference.'],next_decision='One separately derived EAGLE3 correctness candidate may now be prepared with pinned draft/explicit BF16-unquant/eager-prefill, redacted geometry, semantic PD receipts and all IDs compared against this actual reference; no scoring before acceptance')
(O/'REVIEW.json').write_text(json.dumps(review,indent=2)+'\n')
(O/'REVIEW.md').write_text(f'''# Repaired H200 exact reference accepted\n\nJob **{JOB}** is terminal COMPLETED/0:0. Frozen submitted payload and raw bytes match the terminal seal. The actual client captures **8 real responses /1600 actual token IDs**, including the first token; all four A/B pairs have identical IDs and finish semantics. Both actual P/D warmup receipts replay independently, all4+4+8 BF16 rank gates pass, runtime and post-run independent head checks pass, and pre-worker/current/result asset identities agree.\n\nPhase times from allocation start: `{times}` seconds. Role-specific startup/N1 telemetry coverage, sampled GPU/VRAM/power ranges and exact request timings are retained in REVIEW.json. These are diagnostic samples, not scoring saturation or a startup-speedup comparison. Full KV geometry is not collected.\n\nThe missing HOME repair reaches the actual client and establishes the fresh H200 reference that failed25495 could not provide. No EAGLE3 has run, no performance or official accuracy was measured, and the cached second pass does not establish cold-cache timing. Only now may a separately derived EAGLE3 correctness candidate be prepared, retaining fresh draft identity and actual per-rank geometry/semantic transfer/runtime gates before exact ID comparison and any later matched throughput screen.\n\n[Machine-readable review](REVIEW.json), [actual reference](../runs/{JOB}/target-reference.json), [terminal seal](../runs/{JOB}/artifact-manifest.json).\n'''.replace('/1600','/ 1600').replace('all4+4+8','all 4+4+8').replace('failed25495','failed 25495'))
print(json.dumps(dict(job=JOB,state=review['state'],actual_output_ids=1600,phase_times_s=times),indent=2))

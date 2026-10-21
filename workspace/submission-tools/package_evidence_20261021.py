"""Package recent measured evidence without copying model weights or runtime state."""
from pathlib import Path
import csv,datetime,hashlib,json,shutil
W=Path('/home/apacsc42/workspace');R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');O=W/'submission-review/full-update-2026-10-21';T=O/'VNUHCM - TripleU';L=T/'AI_Task/logs';S=T/'AI_Task/job_scripts'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
historical=L/'historical-package-20261020';historical.mkdir()
for p in list(L.iterdir()):
 if p.is_file() and not p.name.startswith('presentation-'):shutil.move(str(p),historical/p.name)
rows=[];sources={};omitted=[]
def copy(a,b):
 b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b);sources[str(b.relative_to(T))]={'source':str(a),'sha256':sha(a)}
for job,n in [('24738',60),('24912',60),('24913',60),('24914',62),('24915',62)]:
 run=R/'runs'/job;dest=L/'measured'/job
 for name in ['summary.json','config.json','worker.sh','benchmark.sh','client-versions.txt','tokenizer-preflight.log','prefill-0.log','prefill-1.log','decode-0.log','router.log','pair-warmup.log','output-smoke.json','long-context-check.json','artifact-manifest.json']:
  if (run/name).is_file():copy(run/name,dest/name)
 for p in (run/'submitted').iterdir():
  if p.is_file() and p.suffix not in ['.sqsh','.safetensors','.gz']:copy(p,dest/'submitted'/p.name)
 phase=run/'confirm'/('n'+str(n))
 for p in phase.rglob('*'):
  if not p.is_file():continue
  if p.name=='inputs.json':
   omitted.append(dict(source=str(p),bytes=p.stat().st_size,sha256=sha(p),reason='Large generated input capture omitted from submission; raw requests and canonical exports retained, official generation protocol fixed.'))
  else:copy(p,dest/'confirm'/('n'+str(n))/p.relative_to(phase))
 row=next(r for r in json.loads((run/'summary.json').read_text()) if r['phase']=='confirm' and r['concurrency']==n)
 row.update(job=job,platform='16 H200',evidence='measured/'+job+'/confirm/n'+str(n)+'/artifacts/profile_export_aiperf.json');row.pop('export');rows.append(row)
# A separately labelled H100 result: no shared-platform speedup is inferred.
snapshot=R/'nscc-pbs/collected/222048.pbs111/20261020T061435059479Z';run=snapshot/'runs/222048.pbs111';dest=L/'h100/222048.pbs111'
for name in ['derived-summary.json','pbs-accounting.txt','review.json']:
 if (snapshot/name).is_file():copy(snapshot/name,dest/name)
for name in ['config.json','prefill-0.log','prefill-1.log','decode-0.log','router.log','output-smoke.json','long-context-check.json']:
 if (run/name).is_file():copy(run/name,dest/name)
phase=run/'confirm/n54'
for p in phase.rglob('*'):
 if p.is_file() and p.name!='inputs.json':copy(p,dest/'confirm/n54'/p.relative_to(phase))
row=json.loads((snapshot/'derived-summary.json').read_text())[0];row.update(job='222048.pbs111',platform='16 H100',evidence='h100/222048.pbs111/confirm/n54/artifacts/profile_export_aiperf.json');row.pop('export');rows.append(row)
reviewdir=L/'research-reviews';reviewdir.mkdir()
for rel in ['research-followup-20261020-0218/RESULTS.md','research-followup-20261020-0218/inspection/24915.md','research-followup-20261020-0218/h200-n62-profile.json','research-followup-20261020-0218/24915-review.json','research-followup-20261020-h100-restored/222048.pbs111-review.json','research-followup-20261020-h100-restored/RESULTS.md','cpu-envelope-balance-20261020/PAIR_REVIEW.md','startup-prefetch-confirm-20261020/PAIR_REVIEW.md','eagle3-reference-corpusfix-20261021/REVIEW.md','eagle3-pd-candidate-20261021/REVIEW.md','eagle3-dtype-probe-20261021/REVIEW.md']:
 copy(R/rel,reviewdir/rel.replace('/','__'))
write(L/'results.json',rows)
with (L/'results.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
write(L/'source-provenance.json',dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=sources,omitted_large_generated_inputs=omitted,weights_included=False,full_rank_traces_included=False,raw_artifacts_unchanged=True))
write(L/'replay-status.json',dict(source_job='24915',source_measurement_reviewed=True,portable_gpu_replay=False,static_and_mock_validation='See package-validation.json',official_accuracy_verified=False,independent_n62_repeat='24962 pending at the 21 October packaging query',performance_gate='Independent raw SLA/error/completeness check after unchanged client invocation'))
(L/'README.md').write_text('''# Measured results and reproduction status

The primary job now declares H200 N62 from reviewed job 24915, not the historical
N48 job. results.json and results.csv give exact units and evidence paths for
recent controls, N60 repeats, N62 and the separate H100 frontier. Historical
22197/22219/22415/22809 evidence remains in measured/. The former package's
metadata is preserved under historical-package-20261020/ and is not the current
deployment declaration. Original logs retain their original dates and paths.

## Latest H200 result

Job 24915: 3022.034919 good output tokens/s; 15.110174596 good requests/s.
1860 of 1884 scored requests jointly meet TTFT<=3000 ms and request-mean
ITL<=20 ms: 98.726115%, with zero request errors or cancellations. Mean TTFT
is 1022.927941 ms; mean ITL is 14.971161 ms. Its fresh same-N auto-decode
control 24914 yields 2890.878 good tokens/s; the observed increase is 4.536934%.
N62 remains a single observation, with independent repeat 24962 pending.
N60 independently yields 2990.150791 and 2989.174711 good output tokens/s.

The score is the canonical profile_export_aiperf.json goodput.avg (requests/s)
multiplied by 200, never raw output throughput or an assumed completed/120.
The SLA is per request and joint; mean latencies alone do not prove acceptance.
AIPerf's reported output length is 199–200 for this run despite fixed 200-token
request settings; the official multiplier remains 200. Warmup/diagnostic
traffic is excluded from raw profiling counts.

## Evidence supplied

The recent H200 folders include canonical exports, raw per-request JSONL,
client logs, worker/router logs, actual frozen submitted payloads and output
checks. Large generated inputs.json files are omitted, with source hashes
and sizes recorded in source-provenance.json. Full rank traces stay in the
research archive; an inspected profile summary is included. Original raw
bytes are unchanged. Paths inside original evidence may name the research
account; the portable primary scripts do not depend on those paths.

H100 job 222048 is separate: 2433.019859 good output tokens/s at N54,
98.687664% joint SLA. Hardware, kernels and load differ. Do not divide these
peaks to claim an algorithmic speedup or a universal H100-to-H200 conversion.

## Interpretation and remaining checks

research-reviews/ records tail latency, queues, KV observations, runtime and
transport review, rejected CPU/startup hypotheses and EAGLE3 integration.
H200 24915 has no continuous hardware telemetry; kernel-time sums are not
GPU activity or critical-path fractions. Later observation coverage does not
retroactively fill its missing CPU/GPU/power/network samples.

The EAGLE3 layer fixture validates a dtype repair, not serving speedup.
Its full PD repair result is uncollected while VPN access is unavailable.
No speculative configuration is promoted into the primary deployment.

The portable N62 package has shell/static checks and a GPU-free orchestration
mock replaying measured artifacts. It has not been separately GPU-replayed.
The required organiser full-set accuracy check >=99% of reference and final
re-verification remain unverified. Hand-written output checks are not that test.
The primary portable command uses 60/120/30, seed 2026, fixed 4000/200,
cold prefixes and exactly one declared concurrency. There is no parameter sweep.
''')
# The staged README was corrected after its first draft; keep the builder accurate.
for directory in [S]:
 files=[p for p in sorted(directory.rglob('*')) if p.is_file() and p.name!='SHA256SUMS']
 (directory/'SHA256SUMS').write_text(''.join('{}  {}\n'.format(sha(p),p.relative_to(directory)) for p in files))
print(json.dumps(dict(recent_rows=len(rows),copied_files=len(sources),omitted_inputs=len(omitted))))

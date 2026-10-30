#!/usr/bin/env python3
"""Stage a current-delivery AI update; keep serving code and HPC untouched."""
from pathlib import Path
import csv,datetime,hashlib,io,json,shutil
W=Path('/home/apacsc42/workspace');Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
O=W/'submission-review/ai-update-20261030';T=W/'VNUHCM - TripleU';A=O/'AI_Task'
assert not A.exists(),'Preserve an existing review stage; never rebuild over it'
shutil.copytree(T/'AI_Task',A,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
jobs=[26949,26951,26953,27077,27238,27270,27272,27274,27365,27376,27378]
copied=[];rows=[]
for job in jobs:
 source=Q/f'runs/{job}';dest=A/f'logs/measured/{job}';dest.mkdir(parents=True,exist_ok=True)
 review=Q/f'h200-full-load-review-20261026/review-{job}.json'
 assert review.is_file(),job
 r=json.loads(review.read_text());assert r['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
 s=r['summary'];rows.append({'job':job,**s})
 paths=[]
 for name in ['summary.json','config.json','head-performance-check.json','runtime-readiness.json','kv-geometry-validation.json','pair-warmup-context.json','scheduler-accounting.psv','artifact-manifest.json','prefill-0.log','prefill-1.log','decode-0.log','pair-warmup.log']:
  if (source/name).is_file():paths.append(source/name)
 for dirname in ['confirm/n64/artifacts','resource-telemetry','pair-warmup-receipts']:
  for p in (source/dirname).rglob('*'):
   if p.is_file() and p.name not in ['inputs.json'] and '__pycache__' not in p.parts:paths.append(p)
 paths.extend(p for p in (source/'submitted-payload').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 for p in paths:
  rel=p.relative_to(source);target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
  copied.append({'source':str(p),'destination':str(target.relative_to(A)),'sha256':sha(p),'bytes':p.stat().st_size})
 shutil.copy2(review,dest/'independent-review.json')
# Retain relevant negative/source study reports without claiming a serving result.
studies={
 'cache-pair':['h200-cold-prefill-cache-study-20261029/RESULTS.md','h200-cold-prefill-cache-study-20261029/comparison.json'],
 'polling':['h200-transfer-poll-final-20261029/RESULTS.md','h200-transfer-poll-final-20261029/comparison.json'],
 'decode-cap':['h200-decode-cap64-20261029/RESULTS.md','h200-decode-cap64-20261029/comparison.json'],
 'tokenizer':['h200-tokenizer-backend-final-review-20261028/REVIEW.md','h200-tokenizer-backend-final-review-20261028/comparison.json'],
 'compile-failure':['h200-decode-compile-full-20261029/FAILURE-27383.md','h200-decode-compile-full-20261029/failure-review-27383.json'],
}
for label,paths in studies.items():
 dest=A/'logs/research-20261030'/label;dest.mkdir(parents=True,exist_ok=True)
 for name in paths:
  p=Q/name;assert p.is_file(),p;shutil.copy2(p,dest/p.name)
dest=A/'logs/research-20261030/cpp-cpu-27506';dest.mkdir(parents=True,exist_ok=True)
for name in ['probe.json','deadline-supervisor.json','host-start.txt','compiler-import.log']:
 shutil.copy2(Q/'runs/27506'/name,dest/name)
# Submission recommendation is unchanged; update only its explanation.
p=A/'job_scripts/README.md';t=p.read_text()
t=t.replace('The portable entry point is statically checked and exercised with\nmock orchestration and replayed artifacts; it has no separate GPU replay yet.','Actual portable jobs 27136 and 27145 completed both semantic routes and the\nofficial GPU client, then failed in result-reader namespace/alias handling.\nTheir original FAILED states remain. The corrected exact readers passed on\ncompute CPU job 27152 for both retained raw datasets; a whole-allocation\nend-to-end run after that repair has not been performed.')
t+="""

## Reviewed selection on 30 October 2026

Keep this replicated N64 target-only configuration. The highest complete local
full pass, prefill ChunkCache job 27378, scored 3048.446289 good output tokens/s,
only 0.240921% above its fresh native control 27376. That single difference is
below the prospective 1% useful-gain gate, so it does not justify replacing the
prefix-cache policy. No speculative decoding, compile option, C++ cache or
unconfirmed graph setting is added to this primary entry.

The recovered portable raw observation 27145 is 3055.330517 good output tokens/s.
Its failed scheduler status and compute-only reader verification remain explicit.
See ../logs/measured/latest-results.md for source IDs, latency units, validity
classes and the distinction between an isolated peak and a reproduced choice.
"""
p.write_text(t)
p=A/'job_scripts/SHA256SUMS';lines=[]
for line in p.read_text().splitlines():
 _,name=line.split(maxsplit=1);name=name.lstrip('*');f=A/'job_scripts'/name
 lines.append(f'{sha(f)}  {name}')
p.write_text('\n'.join(lines)+'\n')
latest=f"""# Current AI results and recommended submission

Updated {now}, Vietnam time (UTC+7).

**Submit the replicated native N64 target-only setting.** The highest complete local full pass is 3048.446289 good output tokens/s, but its +0.240921% matched cache difference is too small to establish a useful improvement. The three-run historical N64 mean is 3044.400475; later native control 26766 reproduces that level at 3045.501509. These are distinct measurement series.

| Evidence class | Job / setting | Good output tokens/s | Interpretation |
|---|---|---:|---|
| Reproduced operating choice | 25366 / 25373 / 25487, N64 | 3044.400475 mean | Three historical full deployments |
| Separate native full control | 26766, N64 | 3045.501509 | Full local pass; no causal launcher-gain claim |
| Fresh native cache control | 27376, N64 | 3041.119598 | Comparator for the cache candidate |
| Highest complete full local pass | 27378, prefill ChunkCache | 3048.446289 | +0.240921% versus 27376; no promotion |
| Recovered portable raw observation | 27145, N64 | 3055.330517 | Original job FAILED after client; not a whole-job pass |
| Separate H100 retained peak | 222048, N54 | 2433.019859 | Different hardware and configuration; do not pool |

AIPerf Goodput is measured in qualifying requests per second. Multiply its exported value by the fixed 200 output tokens to obtain good output tokens/s. For 27378 this is 15.242231445 requests/s × 200. Do not replace exported Goodput with total token throughput or divide successful counts by an assumed 120-second wall window.

## Highest complete run: exact configuration and metrics

Job 27378 completed 0:0 in 11:41 on g1/g4 with 16 H200. It uses two TP4/EP1 prefill roles on one node and one TP8/EP8 decode on the other. Prefill DeepGEMM, chunk 8192, FA3 attention and breakable graphs are retained. The single treatment disables prefill radix prefix caching and selects ChunkCache; physical active-request BF16 KV remains enabled. Decode stays HPC-Ops, FlashInfer attention, MNNVL collectives, full graph buckets 1–64, cap 256 and transfer polling interval 1. Model weights remain the official Qwen3-235B-A22B-Instruct-2507 FP8 target, with BF16 activation/KV. No EAGLE, dynamic tokenization or torch.compile.

| Metric | Unit | Control 27376 | Candidate 27378 |
|---|---|---:|---:|
| Good output throughput | qualifying output tokens/s | 3041.119598 | 3048.446289 |
| Joint latency success | good requests / all requests | 1874 / 1900 | 1879 / 1905 |
| Good fraction | % | 98.631579 | 98.635171 |
| Mean / p95 TTFT | ms | 1119.985 / 1332.727 | 1102.185 / 1380.071 |
| Mean / p95 request-mean ITL | ms | 14.991 / 15.166 | 15.028 / 15.226 |
| TTFT / ITL violations | requests | 26 / 0 | 26 / 0 |
| Errors / cancellations | requests | 0 / 0 | 0 / 0 |
| Local smoke / retrieval | passed cases | 7/8; no new regression / 12/12 | 7/8; no new regression / 12/12 |

TTFT means waiting time to the first token. Request-mean ITL means the average time between generated tokens within one request; the table reports the average and p95 across those request-level values. Every good request must jointly satisfy TTFT ≤3000 ms and request-mean ITL ≤20 ms. At least 90% of all requests, including errors in the denominator, must pass. Mean latency alone cannot certify this condition.

Candidate p95 TTFT and mean ITL are slightly worse despite the small goodput increase. One run per arm and different generated engine seeds do not establish a causal gain. Workload seed 2026 remains fixed. Actual all-rank cache classes, source bindings, physical KV, both semantic routes and frozen raw/output gates pass.

## Later branches and decisions

| Trial | Jobs | Result | Decision |
|---|---|---|---|
| Prefill dynamic tokenizer | 26951 / 26953 vs 26949 | +0.192% / +0.270% | Below useful-gain gate; retain default |
| Prefill FlashInfer, page 1 | 27077 vs 26949 | −6.385% | Lower throughput; retain FA3 |
| Shallow EAGLE decode | 27238 vs 26949 | 2971.628430 tokens/s; −2.080318% | Close unchanged treatment |
| Transfer polling 1 / 2 / 4 | 27270 / 27272 / 27274 | 3039.053 / 3028.280 / 3016.700 tokens/s | Keep interval 1 |
| Decode request cap 64 | 27365 vs 27270 | 3046.890454 tokens/s; +0.257879% | No promotion |
| Full model decode compile | 27383 | FAILED before AIPerf: native RoPE rejects fused KV argument | No score; unchanged compile blocked |
| C++ radix CPU prerequisite | 27506 | Completed 0:0, 95 s; JIT 26.605 s; CPU fixtures pass | No Qwen integration or serving-speed claim |

The already accepted sparse compile-off graph trial 27510 is an independent startup/padding experiment. Its result must be reviewed before inclusion as a completed measurement. No further job is submitted by this delivery update.

## Portable replay and quality limits

Portable 27136 and 27145 completed both semantic P/D routes and the official GPU client, then ended FAILED in result-reader namespace/alias handling. Fixed readers passed actual compute-only job 27152 against both retained real datasets. The package includes those corrections. This does not rewrite original failed states or constitute a whole-allocation repeat after the repair.

The official full-set model-quality gate (at least 99% of the organiser's unchanged FP8 reference) remains UNKNOWN. Local smoke and retrieval do not certify it. No official ranking or global optimum is claimed.

All full runs above use closed-loop N64, requested 4000 input / 200 output tokens, seed 2026, cold prefixes, 60 s warmup / 120 s profiling / 30 s grace. Client-retokenized lengths can differ from requested counts; actual generated token IDs are not retained. Keep the official fixed ×200 multiplier and original gates.

Raw profiling JSONL, exports, configuration, submitted payloads, runtime/semantic evidence and selected role telemetry are provided in the new job directories and research reports. Large generated inputs.json, model weights and disposable caches are omitted. Historical raw originals remain in the research archive. Sparse five-second request-start-envelope telemetry does not prove a causal bottleneck; final drain, calibrated clocks, heavy kernel profiles, hot CPU threads and Xid/throttle reasons were not collected as a complete series.
"""
(A/'logs/measured/latest-results.md').write_text(latest)
with (A/'logs/README.md').open('a') as f:f.write('\n## 30 October update\n\nRead measured/latest-results.md for the current selection, peak qualifiers, metric meanings and recent trials. Native N64 remains the primary; no subthreshold candidate or failed compile is promoted. Current portable GPU/client replay and compute-only reader verification are recorded separately. research-20261030 retains complete comparisons and negative findings. Research is stopped and this update submits no jobs.\n')
# Keep all prior CSV rows and add the reviewed full runs with their exact settings.
stream=io.StringIO();oldcsv=(A/'logs/results.csv').read_text();reader=csv.DictReader(io.StringIO(oldcsv));fields=reader.fieldnames
records=list(reader)
for r in rows:
 row={k:r.get(k,'') for k in fields};row.update(platform='H200',job=r['job'],concurrency=64,chunk_tokens=8192,scope='Reviewed full local pass; selection and single-run limits in measured/latest-results.md');records.append(row)
writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(records)
(A/'logs/results.csv').write_text(stream.getvalue())
(O/'evidence-update-20261030.json').write_text(json.dumps({'updated_vietnam':now,'jobs':jobs,'copied_files':copied,'source':'Current live AI_Task, preserving all prior reader repairs and evidence','serving_code_unchanged':True,'job_scripts_documentation_and_hashes_changed':True,'official_accuracy':'UNKNOWN','new_research_jobs_submitted':False},indent=2)+'\n')
print(json.dumps({'stage':str(A),'new_reviewed_jobs':jobs,'copied_runtime_files':len(copied),'current_primary_N':64}))

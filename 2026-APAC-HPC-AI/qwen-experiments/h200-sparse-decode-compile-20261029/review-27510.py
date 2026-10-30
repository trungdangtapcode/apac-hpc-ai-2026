#!/usr/bin/env python3
"""Preserve completed sparse capture, scored protocol and interpretation."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;a=Q/'runs/27510'
r=json.loads((Q/'h200-full-load-review-20261026/review-27510.json').read_text())
c=json.loads((Q/'h200-full-load-review-20261026/review-27376.json').read_text())
assert r['state']==c['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
account=subprocess.check_output(['sacct','-X','-j','27510','-P','--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'],text=True)
assert '27510|COMPLETED|0:0|00:13:15|795|' in account
assert '27510' not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
capture={}
for job in [27376,27510]:
 text=(Q/f'runs/{job}/decode-0.log').read_text()
 pairs=re.findall(r'Capture target decode CUDA graph end\. elapsed=([0-9.]+) s, mem usage=([0-9.]+) GB',text)
 assert len(pairs)==8
 capture[str(job)]={'per_rank_seconds':[float(p[0]) for p in pairs],'per_rank_memory_native_GB_label':[float(p[1]) for p in pairs]}
(a/'scheduler-accounting.psv').write_text(account)
manifest=a/'artifact-manifest.json';assert not manifest.exists()
files=[]
for p in sorted(a.rglob('*'))+[Q/'runs/27510.out',Q/'runs/27510.err']:
 if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p==manifest:continue
 before=p.stat();digest=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat()
 assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':digest})
manifest.write_text(json.dumps({'job':27510,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':account,'files':files},indent=2)+'\n')
delta=100*(r['summary']['good_output_tokens_s']/c['summary']['good_output_tokens_s']-1)
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':'REVIEWED_SPARSE_GRAPH_LOWER_SCORE_CLOSE_UNCHANGED',
 'job':27510,'control_job':27376,'summary':r['summary'],'control_summary':c['summary'],'delta_percent':delta,
 'capture':capture,'telemetry':r['telemetry_in_admission_envelope'],'smoke':r['smoke'],'retrieval':r['retrieval'],
 'actual_GPU_hours':16*795/3600,'maximum_GPU_hours':16*17/60,'PBS_SU':0,
 'limits':'One ordered observation per setting across different times; generated seeds and startup observation differ. Sparse candidate startup observer is disabled before scoring, with a remaining proxy fast-path caveat. Native log GB is not converted to GiB. Sparse request-start-envelope gauges omit final drain; CPU/GPU activity is not a causal kernel bottleneck. Official accuracy unknown.',
 'decision':'Retain dense1..64 default, close exact sparse list without new jobs. Owner stopped research; this retrospective review is part of authorised results/slides/submission update.'}
(D/'result-27510.json').write_text(json.dumps(out,indent=2)+'\n')
(D/'RESULTS-27510.md').write_text(f"""# Sparse decode graphs: lower capture memory, no throughput gain

Reviewed 30 October 2026, Vietnam time (UTC+7). Job **27510 completed 0:0 in 13:15**, 16 H200 on g1/g4. Independent frozen raw, runtime, KV, two semantic routes, smoke and retrieval checks pass. Good output throughput is **3029.861122 tokens/s**, **{delta:.6f}%** against control 27376 at 3041.119598. Retain dense graph buckets 1–64.

The hypothesis was that 12 capture buckets could reduce startup/capture resources while preserving common batches 50–56. Actual current-job receipts prove all 12 captures on all eight decode ranks with compile off; the observer disables before benchmarking. Decode capture logs report 95.98–96.05 seconds and 0.36 GB per rank versus 101.46–101.49 seconds and 1.15 GB for the full-list control. These are native log memory labels, not total sampled VRAM. Saving 52 capture buckets did not proportionally reduce startup time, and it did not improve serving goodput.

There are 1870/1896 good requests (98.628692%), 26 TTFT and zero ITL breaches, zero errors/cancellations, smoke 7/8 without regression and retrieval 12/12. Mean/p95 TTFT is 1102.404/1240.481 ms; mean/p95 request-mean ITL is 15.136/15.324 ms. The fresh full-list control has 1119.985/1332.727 ms TTFT and 14.991/15.166 ms ITL. Lower TTFT and capture memory therefore do not imply higher useful throughput.

Inspected role logs, eight actual source/job/experiment-bound capture receipts, physical BF16 KV and semantic paths, raw requests/tails/errors, role-local queue/running/KV gauges, sampled GPU activity/VRAM and host CPU/memory, plus all 72 HTTP-200 server polls. Decode mean running count is 49.542, maximum 55, sampled queue zero and mean token occupancy 0.1142. Five-second sparse samples are bounded by profiling request starts with uncalibrated clocks; they do not prove steady-state utilization or a causal bottleneck. No complete kernel-time, hot CPU-thread, Xid/throttle-reason or final-drain profile exists.

Observed occupancy is 3.533333 GPU-hours, maximum 4.533334, zero PBS SU. All terminal artifacts are sealed. The comparator is an earlier same-config control, not an immediate randomized matched repeat; engine seeds and observer startup differ. This single observation does not establish a universal sparse-graph ranking. Official full-set accuracy remains UNKNOWN.

Decision: close this unchanged list and retain dense graphs. No new job, compile retry or background work follows: the owner stopped research, then authorised this results/presentation/submission update only. Full Qwen compile 27383 remains a separate failed native RoPE interface trial; C++ CPU 27506 is only a prerequisite pass.
""")
print(json.dumps({'state':out['state'],'delta_percent':delta}))

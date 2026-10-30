#!/usr/bin/env python3
"""Add the already accepted sparse trial's terminal review to the staged delivery."""
from pathlib import Path
import csv,hashlib,io,json,shutil
W=Path('/home/apacsc42/workspace');Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
O=W/'submission-review/ai-update-20261030';A=O/'AI_Task';source=Q/'runs/27510';dest=A/'logs/measured/27510'
assert not dest.exists();dest.mkdir()
paths=[]
for name in ['summary.json','config.json','head-performance-check.json','runtime-readiness.json','kv-geometry-validation.json','pair-warmup-context.json','scheduler-accounting.psv','artifact-manifest.json','sparse-graph-startup-gate.json','prefill-0.log','prefill-1.log','decode-0.log','pair-warmup.log']:
 p=source/name
 if p.is_file():paths.append(p)
for folder in ['confirm/n64/artifacts','resource-telemetry','pair-warmup-receipts','compile-receipts','submitted-payload']:
 paths.extend(p for p in (source/folder).rglob('*') if p.is_file() and p.name!='inputs.json' and '__pycache__' not in p.parts)
update=json.loads((O/'evidence-update-20261030.json').read_text())
for p in paths:
 t=dest/p.relative_to(source);t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
 update['copied_files'].append({'source':str(p),'destination':str(t.relative_to(A)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
review=Q/'h200-full-load-review-20261026/review-27510.json';shutil.copy2(review,dest/'independent-review.json')
r=json.loads(review.read_text());assert r['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
update['jobs'].append(27510)
(O/'evidence-update-20261030.json').write_text(json.dumps(update,indent=2)+'\n')
d=A/'logs/research-20261030/sparse-graphs';d.mkdir()
for name in ['RESULTS-27510.md','result-27510.json']:
 shutil.copy2(Q/'h200-sparse-decode-compile-20261029'/name,d/name)
shutil.copy2(Q/'h200-cpp-radix-cpu-probe-20261029/FAILURE-27387.md',A/'logs/research-20261030/cpp-cpu-27506/PREVIOUS_ENVELOPE_FAILURE.md')
p=A/'logs/measured/latest-results.md';t=p.read_text()
t=t.replace('The already accepted sparse compile-off graph trial 27510 is an independent startup/padding experiment. Its result must be reviewed before inclusion as a completed measurement. No further job is submitted by this delivery update.','Sparse compile-off graph trial **27510 completed 0:0 in 13:15** and independently passes the full local gate at **3029.861122 good output tokens/s**, −0.370208% versus earlier control 27376. It has 1870/1896 good requests (98.628692%), zero errors/cancellations, smoke 7/8 without regression and retrieval 12/12. Twelve graph buckets reduce native logged capture memory from 1.15 to 0.36 GB per rank, but capture time changes only from 101.46–101.49 to 95.98–96.05 seconds. TTFT mean/p95 is 1102.404/1240.481 ms, request-mean ITL 15.136/15.324 ms. Keep dense graphs. This single observation has generated-seed, different-time and candidate startup-observer limitations. No further job is submitted by this delivery update.')
p.write_text(t)
p=A/'logs/results.csv';reader=csv.DictReader(io.StringIO(p.read_text()));fields=reader.fieldnames;rows=list(reader);s=r['summary']
row={k:s.get(k,'') for k in fields};row.update(platform='H200',job=27510,concurrency=64,chunk_tokens=8192,scope='Full local sparse-graph pass; lower score; retain dense graph default');rows.append(row)
stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows);p.write_text(stream.getvalue())
# Current result status, including the old genuine reader repair, stays intact.
p=A/'logs/replay-status.json';data=json.loads(p.read_text());data['selection_update_20261030']={'primary':'Replicated native N64 retained','highest_complete_local_pass_job':27378,'highest_complete_local_pass_good_tokens_s':3048.4462889360616,'matched_cache_change_pct':.24092083989171176,'portable_recovered_raw_job':27145,'portable_recovered_raw_good_tokens_s':3055.330517,'sparse_trial_job':27510,'sparse_trial_good_tokens_s':3029.861121768828,'official_accuracy':'UNKNOWN','new_gpu_jobs_submitted_by_publication':False};p.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'completed_job':27510,'score':s['good_output_tokens_s'],'primary_unchanged':True,'new_research_jobs_submitted':False}))

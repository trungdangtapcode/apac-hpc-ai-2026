"""Locate actual joint-SLA failures in time without changing any scored set."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
O=Path(__file__).resolve().parent;R=O.parent
POINTS=[('24962','confirm',62),('24964','confirm',60),('25339','screen',62),('25339','screen',64),('25365','confirm',62)]
results=[]
for job,phase,n in POINTS:
 run=R/'runs'/job;A=run/f'{phase}/n{n}/artifacts';seal=json.loads((run/'artifact-manifest.json').read_text());sealed={row['path']:row for row in seal['files']}
 for path in [A/'phase_manifest.json',A/'profile_export.jsonl']:
  record=sealed[str(path.relative_to(R))];assert path.stat().st_size==record['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
 manifest=json.loads((A/'phase_manifest.json').read_text())['phases'][1];bad=[];cohort=[];all_offsets=[];good=0;itl_breaches=0
 for line in (A/'profile_export.jsonl').read_text().splitlines():
  row=json.loads(line)
  if row['metadata']['phase_kind']!='profiling':continue
  assert not row['metadata']['was_cancelled'] and not row.get('error') and not row.get('errors')
  metric=row['metrics'];ttft=metric['time_to_first_token']['value'];itl=metric['inter_token_latency']['value'];ok=ttft<=3000 and itl<=20;assert metric['good_request_count']['value']==int(ok)
  offset=(row['metadata']['request_start_ns']-manifest['start_ns'])/1e9
  good+=ok;all_offsets.append(offset);itl_breaches+=itl>20
  if offset<.100:cohort.append(dict(start_offset_s=offset,good=ok,ttft_ms=ttft,itl_ms=itl))
  if not ok:bad.append(dict(start_offset_s=offset,ttft_ms=ttft,itl_ms=itl))
 results.append(dict(job=job,phase=phase,concurrency=n,profiling_total=len(all_offsets),good_requests=good,bad_requests=len(bad),itl_breaches=itl_breaches,first_100ms_requests=len(cohort),first_100ms_good=sum(r['good'] for r in cohort),bad_request_start_offset_min_s=min(r['start_offset_s'] for r in bad),bad_request_start_offset_max_s=max(r['start_offset_s'] for r in bad),bad_starting_after_100ms=sum(r['start_offset_s']>=.1 for r in bad),arithmetic_goodput_gain_ceiling_at_unchanged_duration_percent=100*len(bad)/good,bad_request_evidence=bad,source_phase_manifest=str((A/'phase_manifest.json').relative_to(R)),source_raw_jsonl=str((A/'profile_export.jsonl').relative_to(R))))
assert all(r['bad_starting_after_100ms']==0 and r['itl_breaches']==0 for r in results)
(O/'REVIEW.json').write_text(json.dumps(dict(reviewed_utc=datetime.now(timezone.utc).isoformat(),score_definition_unchanged=True,all_scored_requests_retained=True,points=results,observation='Every joint-SLA failure in these sealed observations belongs to the initial request cohort; not a causal hardware diagnosis',next_hypothesis='Review server-side response to phase-start request burst; preserve official client timing/workload and score denominator'),indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['job','phase','concurrency','bad_requests','first_100ms_requests','bad_request_start_offset_max_s','arithmetic_goodput_gain_ceiling_at_unchanged_duration_percent']} for r in results],indent=2))

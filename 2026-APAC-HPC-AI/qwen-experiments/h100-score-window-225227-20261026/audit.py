#!/usr/bin/env python3
"""Bound sparse resource observations to profiling request admission, not startup."""
from pathlib import Path
import datetime,importlib.util,json,statistics
S=Path(__file__).resolve().parent;Q=S.parent
A=Q/'h100-review-225227-225228-20261026/curated-r2/h100-incumbent-n54-refresh-20261026/runs/225227.pbs111'
rows=[json.loads(l) for l in (A/'confirm/n54/artifacts/profile_export.jsonl').open()];rows=[r for r in rows if r['metadata']['benchmark_phase']=='profiling'];assert len(rows)==1512
lo=min(r['metadata']['request_start_ns'] for r in rows);hi=max(r['metadata']['request_start_ns'] for r in rows)
spec=importlib.util.spec_from_file_location('retained_telemetry',Q/'research-review-26064-26068-20261025/audit-results.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
t=helper.telemetry(A,lo,hi)
for h in t['hosts'].values():
 for k in ('available_memory_TiB_at_start','total_memory_TiB'):
  if k in h:h[k.replace('TiB','GiB')]=h.pop(k)
t['host_memory_unit_correction']='Historical helper divides KiB by1024**2; correct unit is GiB.'
result={'job':'225227.pbs111','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_profiling_request_start_ns':lo,'last_profiling_request_start_ns':hi,'profiling_request_count':1512,'resource_observations':t,'limits':'First-to-last profiling-request START envelope only, not exact profiling completion. Five-second samples, uncalibrated host skew. Allocation-wide means in original review remain historical different-window observations, not contradictions. Activity is not FLOPS; VRAM is not KV occupancy.'}
(S/'score-window.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(t,indent=2))

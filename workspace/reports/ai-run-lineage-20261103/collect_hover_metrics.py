#!/usr/bin/env python3
"""Collect the four performance metrics from retained run summaries, without mixing loads."""
from pathlib import Path
import json,os,re
D=Path(__file__).resolve().parent
Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
rows=json.loads((D/'runs.json').read_text());known={str(r['job_id']):r for r in rows};byid={}
for root,dirs,files in os.walk(Q):
 dirs[:]=[x for x in dirs if not (x in {'home','__pycache__','.git','node_modules','source','prepared-4k','site-packages'} or 'runtime-home' in x or x.startswith('enroot-') or (Path(root)/x).is_symlink())]
 if 'summary.json' not in files:continue
 path=Path(root)/'summary.json'
 # Only exact directory job IDs establish attribution, never a coincidental number in prose.
 matches=[x for x in path.parts if x in known]
 if not matches:continue
 job=matches[-1]
 try:
  if path.stat().st_size>2000000:continue
  value=json.loads(path.read_text())
 except (OSError,ValueError):continue
 items=value if isinstance(value,list) else [value]
 for item in items:
  if not isinstance(item,dict) or not all(k in item for k in ['good_output_tokens_s','ttft_avg_ms','itl_avg_ms','good_request_fraction']):continue
  sample={k:item[k] for k in ['good_output_tokens_s','ttft_avg_ms','itl_avg_ms','good_request_fraction']}
  if not all(isinstance(v,(int,float)) for v in sample.values()):continue
  sample.update(concurrency=item.get('concurrency'),phase=item.get('phase'),source=str(path),sla_pass=item.get('sla_pass'))
  if sample not in byid.setdefault(job,[]):byid[job].append(sample)
# Deduplicate mirrored captures of the exact same four values/load/phase. Keep distinct points.
for job,items in byid.items():
 unique={}
 for x in sorted(items,key=lambda x:x['source']):unique.setdefault(tuple(x[k] for k in ['good_output_tokens_s','ttft_avg_ms','itl_avg_ms','good_request_fraction','concurrency','phase']),x)
 byid[job]=list(unique.values())
(D/'hover-metrics.json').write_text(json.dumps(dict(metrics=['good_output_tokens_s','ttft_avg_ms','itl_avg_ms','good_request_fraction'],latency_statistic='arithmetic mean from retained summary',selection='Each distinct load/phase stays separate; no cross-load averaging or best-point cherry-picking.',jobs=byid),indent=2)+'\n')
print('Jobs with all four retained performance metrics:',len(byid))

from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
w=Path('/home/apacsc42/workspace');r=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');old=w/'submission-review/full-update-2026-10-21';o=w/'submission-review/research-update-2026-10-22';o.mkdir(exist_ok=False)
for n in ['background-manifest.json','drawing-helpers.py','requirements.txt']:shutil.copyfile(old/n,o/n)
d=json.loads((old/'presentation-data.json').read_text());d['snapshot_utc']=datetime.now(timezone.utc).isoformat();d['current']={}
for job in ['25365','25366','25373','25371']:
 review=r/f'research-review-{job}-20261022/REVIEW.json';d['current'][job]=json.loads(review.read_text());summary=r/f'runs/{job}/summary.json';d['h200'][job]=json.loads(summary.read_text())
 for p in [review,summary,r/f'runs/{job}/artifact-manifest.json']:
  d['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 ns=[64,68] if job=='25371' else [62 if job=='25365' else 64];phase='screen' if job=='25371' else 'confirm'
 for n in ns:
  for name in ['profile_export.jsonl','profile_export_aiperf.json','phase_manifest.json']:
   p=r/f'runs/{job}/{phase}/n{n}/artifacts'/name;d['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['research-review-25373-20261022/observability.json','research-review-25371-20261022/observability.json','research-review-h200-wave-20261021/REVIEW.json','nixl-native-registration-probe-20261021/REVIEW.md','eagle3-pd-eager-prefill-r3-20261021/REVIEW.md','research-followup-20261022-n68-full/slurm-receipts.json']:
 p=r/name;d['sources'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
a=d['h200']['25366'][0].copy();a.update(job='25366',source=str(r/'runs/25366/summary.json'));d['historical_records']['records']['H200']['good_output_tokens_s']={'value':a['good_output_tokens_s'],'ties':[a]}
d['historical_records']['scope']+=' Updated H200 goodput with reviewed 25366 and replication25373 on22October; other records retain original dated scan scope.'
refresh=[]
for path,before in list(d['sources'].items()):
 p=Path(path);assert p.is_file(),path;after=hashlib.sha256(p.read_bytes()).hexdigest()
 if before!=after:refresh.append(dict(path=path,prior_frozen_sha256=before,current_sha256=after));d['sources'][path]=after
(o/'source-refresh.json').write_text(json.dumps(dict(prior_snapshot=str(old/'presentation-data.json'),refreshed_sources=refresh,scope='Prior frozen deck remains intact; current safe source bytes rehashed for this new snapshot'),indent=2)+'\n')
(o/'presentation-data.json').write_text(json.dumps(d,indent=2)+'\n')
print('Frozen current presentation inputs; run build_research_update_20261022.py separately')

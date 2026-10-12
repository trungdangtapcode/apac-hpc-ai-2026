"""Read raw AIPerf exports without replacing measured metrics."""
import json,re,sys
from pathlib import Path
root=Path(sys.argv[1])
rows=[]
for p in sorted(root.glob('*/n*/artifacts/profile_export_aiperf.json')):
    d=json.loads(p.read_text())
    def metric(k):
        v=d.get(k)
        return v.get('avg') if isinstance(v,dict) else None
    goodput=metric('goodput'); frac=metric('good_request_fraction')
    client=p.parent.parent/'client.log'
    phase_stats=re.search(r'Phase profiling \(profiling\) complete \| completed=(\d+), cancelled=(\d+), errors=(\d+)',client.read_text(errors='replace')) if client.exists() else None
    if frac is None:
        good=metric('good_request_count'); count=metric('request_count'); errors=metric('error_request_count') or 0
        if good is not None and count is not None and count+errors>0: frac=good/(count+errors)
    rows.append({'export':str(p),'phase':p.relative_to(root).parts[0],
        'concurrency':int(next(part[1:] for part in p.relative_to(root).parts if part.startswith('n') and part[1:].isdigit())),
        'good_request_fraction':frac,'sla_pass':frac>=0.90 if frac is not None else None,
        'good_output_tokens_s':goodput*200 if goodput is not None else None,
        'raw_output_tokens_s':metric('output_token_throughput'),
        'ttft_avg_ms':metric('time_to_first_token'),'itl_avg_ms':metric('inter_token_latency'),
        'ttft_p95_ms':d.get('time_to_first_token',{}).get('p95'),
        'itl_p95_ms':d.get('inter_token_latency',{}).get('p95'),
        'requests':metric('request_count'),'errors':metric('error_request_count') or 0,
        'cancelled_requests':int(phase_stats[2]) if phase_stats else None})
print(json.dumps(rows,indent=2))

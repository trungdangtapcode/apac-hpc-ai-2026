"""Read raw AIPerf exports without replacing measured metrics."""
import json,sys
from pathlib import Path
root=Path(sys.argv[1])
rows=[]
for p in sorted(root.glob('n*/**/profile_export_aiperf.json')):
    d=json.loads(p.read_text())
    def metric(k):
        v=d.get(k)
        return v.get('avg') if isinstance(v,dict) else None
    goodput=metric('goodput'); frac=metric('good_request_fraction')
    if frac is None:
        good=metric('good_request_count'); count=metric('request_count'); errors=metric('error_request_count') or 0
        if good is not None and count is not None and count+errors>0: frac=good/(count+errors)
    rows.append({'export':str(p),'concurrency':int(p.relative_to(root).parts[0][1:]),
        'good_request_fraction':frac,'sla_pass':frac>=0.90 if frac is not None else None,
        'good_output_tokens_s':goodput*200 if goodput is not None else None,
        'raw_output_tokens_s':metric('output_token_throughput'),
        'ttft_avg_ms':metric('time_to_first_token'),'itl_avg_ms':metric('inter_token_latency'),
        'requests':metric('request_count'),'errors':metric('error_request_count') or 0})
print(json.dumps(rows,indent=2))

"""Classify measured SLA failures without changing the official AIPerf metrics."""
import argparse
import collections
import hashlib
import json
from pathlib import Path


def analyze(export):
    official=json.loads(export.read_text());journal=export.with_name('profile_export.jsonl')
    rows=[json.loads(line) for line in journal.open()]
    rows=[r for r in rows if r['metadata'].get('benchmark_phase')=='profiling']
    assert rows, 'No profiling requests; do not use warmup data'
    start=min(r['metadata']['request_start_ns'] for r in rows)
    groups=collections.Counter();failed=[];missing=0
    for row in rows:
        meta=row['metadata'];metrics=row['metrics']
        t=metrics.get('time_to_first_token');i=metrics.get('inter_token_latency')
        if not t or not i or meta.get('was_cancelled'):
            missing+=1;continue
        assert t['unit']=='ms' and i['unit']=='ms', 'Unexpected units'
        ttft=t['value']>3000;itl=i['value']>20
        key='both' if ttft and itl else 'ttft_only' if ttft else 'itl_only' if itl else 'good'
        groups[key]+=1
        if key!='good':
            failed.append(dict(request_id=meta['x_request_id'],type=key,
                               start_relative_s=(meta['request_start_ns']-start)/1e9,
                               ttft_ms=t['value'],itl_ms=i['value']))
    count=official['request_count']['avg'];good=official['good_request_count']['avg']
    errors=official.get('error_request_count',{}).get('avg',0)
    assert len(rows)==count and groups['good']==good and missing==0, 'Raw requests do not reconcile with official summary'
    ttft_bad=[r for r in failed if r['type'] in ('ttft_only','both')]
    return dict(export=str(export),requests=len(rows),errors=errors,
                classifications={k:groups[k] for k in ('good','ttft_only','itl_only','both')},
                official_good_requests=good,all_counts_match_official_summary=True,
                ttft_failed_starts_first_second=sum(r['start_relative_s']<=1 for r in ttft_bad),
                ttft_failed_start_range_s=[min(r['start_relative_s'] for r in ttft_bad),max(r['start_relative_s'] for r in ttft_bad)] if ttft_bad else None,
                latency_stats={k:official[k] for k in ('time_to_first_token','inter_token_latency')},
                failed_requests=failed,raw_sha256=hashlib.sha256(journal.read_bytes()).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('exports',nargs='+',type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();result=dict(scope='Profiling phase only; official score/window/thresholds untouched. Failure timing identifies an observation, not the server-side cause.',runs=[analyze(p) for p in args.exports])
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    for run in result['runs']:print(run['export'],run['classifications'],'TTFT bad starts',run['ttft_failed_start_range_s'])

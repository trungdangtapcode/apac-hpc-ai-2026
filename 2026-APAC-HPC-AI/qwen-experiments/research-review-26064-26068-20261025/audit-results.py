#!/usr/bin/env python3
"""Independently audit immutable S63 AIPerf exports after its N64-only checker bug."""
from __future__ import annotations
import collections, importlib.util, json, math, re, statistics, sys
from pathlib import Path
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
RUNS=ROOT/'runs'
REF=ROOT/'serving-tuning-11/s63-h200-load-n66/performance_gates.py'

def percentile(xs,p):
    ys=sorted(xs)
    if not ys: return None
    i=(len(ys)-1)*p; lo=int(i); hi=min(lo+1,len(ys)-1)
    return ys[lo]+(ys[hi]-ys[lo])*(i-lo)

def dynamic_gates():
    src=REF.read_text()
    src=src.replace("rows=[r for r in summary if r.get('phase')=='screen' and r.get('concurrency')==64]", "n=next(p['concurrency'] for p in expected_input['phases'] if p.get('name')=='profiling'); rows=[r for r in summary if r.get('phase')=='screen' and r.get('concurrency')==n]")
    src=src.replace("'one measured N64 point is required'", "'one measured configured-concurrency point is required'")
    src=src.replace("export_path=art/'screen/n64/artifacts/profile_export_aiperf.json'", "export_path=art/f'screen/n{n}/artifacts/profile_export_aiperf.json'")
    src=src.replace("log=(art/'screen/n64/client.log')", "log=(art/f'screen/n{n}/client.log')")
    src=src.replace("assert metric['sla_pass'] is True, 'summary SLA floor failed'", "# SLA status is reported separately so a real failing load remains auditable.")
    src=src.replace("assert request_count>0 and goodput>0 and good_fraction>=0.90", "assert request_count>0 and goodput>0")
    ns={'__name__':'dynamic_performance_gates','__file__':str(REF)}
    exec(compile(src,str(REF),'exec'),ns)
    return ns

def telemetry(run, start_ns, end_ns):
    allgpu=[]; roles={}; http=collections.Counter(); metric_series={}; uuidsets={}; host_files={}
    for path in sorted((run/'resource-telemetry').glob('*.jsonl')):
        rows=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
        if not rows: continue
        role=rows[0].get('role','unknown'); host=rows[0].get('host','unknown')
        host_files.setdefault(host,path)
        samples=[r for r in rows if r.get('kind')=='sample' and start_ns<=r.get('utc_ns',0)<=end_ns]
        gpu=[]
        for r in samples:
            http[(str(r.get('server_http_status')),str(r.get('server_metrics_status')))]+=1
            for line in r.get('server_metrics') or []:
                m=re.match(r'([^ {]+)\{([^}]*)\}\s+([-+0-9.eE]+)$',line)
                if not m: continue
                name=m.group(1)
                if name in {'sglang:num_running_reqs','sglang:num_queue_reqs','sglang:token_usage'}:
                    metric_series.setdefault((role,name),[]).append(float(m.group(3)))
            for g in r.get('gpus',[]) or []:
                uuid=g.get('uuid')
                if uuid: uuidsets.setdefault(role,set()).add(uuid)
                try: item={'util':float(g['utilization.gpu']),'mem_gib':float(g['memory.used'])/1024}
                except (KeyError,ValueError,TypeError): continue
                gpu.append(item); allgpu.append(item)
        roles[role]={'host':host,'samples':len(samples),'gpu_sample_count':len(gpu),
          'uuid_count':len(uuidsets.get(role,set())),
          'mean_gpu_active_pct':round(statistics.mean(x['util'] for x in gpu),3) if gpu else None,
          'mean_vram_gib':round(statistics.mean(x['mem_gib'] for x in gpu),3) if gpu else None}
    hosts={}
    for host,path in host_files.items():
        rows=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
        samples=[r for r in rows if r.get('kind')=='sample' and start_ns<=r.get('utc_ns',0)<=end_ns]
        if len(samples)<2: continue
        a,b=samples[0],samples[-1]; c0=a.get('node_cpu_jiffies'); c1=b.get('node_cpu_jiffies'); cpu=None
        if c0 and c1 and len(c0)>=8:
            delta=[y-x for x,y in zip(c0,c1)]; total=sum(delta); idle=delta[3]+delta[4]; cpu=round(100*(total-idle)/total,2) if total else None
        mem=a.get('node_memory') or {}
        hosts[host]={'samples':len(samples),'estimated_cpu_busy_pct':cpu,
          'available_memory_TiB_at_start':round(mem['MemAvailable_KiB']/1024**2,3) if mem.get('MemAvailable_KiB') else None,
          'total_memory_TiB':round(mem['MemTotal_KiB']/1024**2,3) if mem.get('MemTotal_KiB') else None}
    gauges={}
    for (role,name),values in metric_series.items(): gauges.setdefault(role,{})[name]={'samples':len(values),'max':max(values),'mean':round(statistics.mean(values),4)}
    return {'roles':roles,'hosts':hosts,'server_http_and_error_poll_counts':{f'http={k[0]},error={k[1]}':v for k,v in http.items()},'rank_local_server_gauges':gauges,
      'all_role_gpu_samples':len(allgpu),
      'all_role_mean_gpu_active_pct':round(statistics.mean(x['util'] for x in allgpu),3) if allgpu else None,
      'all_role_mean_vram_gib':round(statistics.mean(x['mem_gib'] for x in allgpu),3) if allgpu else None,
      'limits':'Five-second phase-bounded samples. CPU jiffies are host-wide and counted once per host. GPU active time is not FLOP utilization. Server gauges expose sampled rank-local series and are not merged across TP/EP ranks. Missing/failed polls are explicit; none are treated as zero.'}

def audit(j):
    run=RUNS/str(j); bundle=run/'submitted-payload'
    cfg=json.loads((bundle/'config.json').read_text())
    expected=json.loads((bundle/'expected-input-config.json').read_text())
    gates=dynamic_gates(); prof=gates['check_aiperf'](run,expected,200)
    smoke=gates['check_smoke'](run,bundle/'reference-output-smoke.json')
    retrieval=gates['check_retrieval'](run)
    summ=json.loads((run/'summary.json').read_text()); metric=next(r for r in summ if r.get('phase')=='screen')
    n=cfg['concurrency']; raw=json.loads((run/f'screen/n{n}/artifacts/profile_export.jsonl').read_text().splitlines()[0])
    export_rows=[]
    for line in (run/f'screen/n{n}/artifacts/profile_export.jsonl').read_text().splitlines():
        row=json.loads(line)
        if row.get('metadata',{}).get('benchmark_phase')!='profiling': continue
        m=row['metrics']; export_rows.append((float(m['time_to_first_token']['value']),float(m['inter_token_latency']['value'])))
    assert len(export_rows)==int(metric['requests'])
    bm=json.loads((run/'phase-markers.jsonl').read_text().splitlines()[0]) if False else None
    marks=[json.loads(x) for x in (run/'phase-markers.jsonl').read_text().splitlines()]
    start=next(x for x in marks if x['event']=='benchmark_start')
    end=next(x for x in marks if x['event']=='benchmark_end')
    output={
      'job_id':j,'state':'RAW_PROFILE_VALID_CHECKER_BUG' if j!=26068 else 'RAW_PROFILE_VALID_SLA_GATE_FAILED',
      'slurm_state':'FAILED','checker_error':json.loads((run/'head-performance-check.json').read_text()).get('error'),
      'configured_concurrency':n,'raw_profile_audit':prof,
      'summary':{k:metric[k] for k in ('good_request_fraction','sla_pass','good_output_tokens_s','raw_output_tokens_s','ttft_avg_ms','ttft_p95_ms','itl_avg_ms','itl_p95_ms','requests','errors','cancelled_requests')},
      'raw_request_latency_ms':{'ttft_p50':percentile([x[0] for x in export_rows],.50),'ttft_p95':percentile([x[0] for x in export_rows],.95),'ttft_p99':percentile([x[0] for x in export_rows],.99),'itl_p50':percentile([x[1] for x in export_rows],.50),'itl_p95':percentile([x[1] for x in export_rows],.95),'itl_p99':percentile([x[1] for x in export_rows],.99),'ttft_breaches':sum(a>3000 for a,b in export_rows),'itl_breaches':sum(b>20 for a,b in export_rows)},
      'output_smoke':smoke,'retrieval':retrieval,
      'runtime_readiness':json.loads((run/'runtime-readiness.json').read_text()).get('state'),
      'native_kv_geometry':json.loads((run/'kv-geometry-validation.json').read_text()).get('passed'),
      'semantic_pd_pairs':json.loads((run/'pair-warmup-context.json').read_text()).get('pair_count'),
      'telemetry':telemetry(run,start['utc_ns'],end['utc_ns'])}
    output['scoreable_local_screen']=bool(metric['sla_pass'] and metric['errors']==0 and metric['cancelled_requests']==0 and smoke['passed']>=7 and retrieval['passed']==12)
    return output

if __name__=='__main__':
    jobs=[audit(int(x)) for x in sys.argv[1:]]
    out=Path(__file__).with_name('S63-audit-results.json')
    out.write_text(json.dumps(jobs,indent=2,sort_keys=True)+'\n')
    for x in jobs:
        s=x['summary']; print(f"{x['job_id']} N{x['configured_concurrency']} {x['state']} {s['good_output_tokens_s']:.2f} good tok/s; {s['good_request_fraction']:.4%} SLA; TTFT p95 {s['ttft_p95_ms']:.2f}ms; ITL p95 {s['itl_p95_ms']:.2f}ms; {x['summary']['errors']} errors/{x['summary']['cancelled_requests']} cancelled; smoke {x['output_smoke']['passed']}/8; retrieval {x['retrieval']['passed']}/12; local gate={x['scoreable_local_screen']}")

#!/usr/bin/env python3
"""Review and seal the exact cold-prefill cache pair after terminal raw gates."""
from pathlib import Path
import ast, collections, datetime, hashlib, json, math, statistics, subprocess
D=Path(__file__).resolve().parent; Q=D.parent
def dist(values):
    values=sorted(values)
    def quant(p):
        x=(len(values)-1)*p; i=math.floor(x); j=math.ceil(x)
        return values[i]+(values[j]-values[i])*(x-i)
    return dict(count=len(values),min=values[0],mean=statistics.mean(values),
                p50=quant(.5),p95=quant(.95),p99=quant(.99),max=values[-1])
def resolved(job,role):
    lines=(Q/f'runs/{job}/{role}.log').read_text().splitlines()
    args=[line.split('server_args=',1)[1] for line in lines if 'server_args=ServerArgs(' in line]
    assert len(args)==1
    tree=ast.parse(args[0],mode='eval').body
    return {x.arg:ast.dump(x.value,include_attributes=False) for x in tree.keywords}
reviews={}
for job in (27376,27378):
    a=Q/f'runs/{job}'
    review=json.loads((Q/f'h200-full-load-review-20261026/review-{job}.json').read_text())
    assert review['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
    raw=[json.loads(line) for line in (a/'confirm/n64/artifacts/profile_export.jsonl').open()]
    raw=[r for r in raw if r['metadata']['benchmark_phase']=='profiling']
    lo=min(r['metadata']['request_start_ns'] for r in raw)
    hi=max(r['metadata']['request_start_ns'] for r in raw)
    hardware={}
    for p in (a/'resource-telemetry').glob('*.jsonl'):
        rows=[json.loads(line) for line in p.open()]
        samples=[r for r in rows if r['kind']=='sample' and lo<=r['utc_ns']<=hi]
        fields={}
        for name in ('utilization.gpu','utilization.memory','memory.used','power.draw',
                     'temperature.gpu','clocks.sm','clocks.mem'):
            values=[]; missing=0
            for row in samples:
                for gpu in row.get('gpus',[]):
                    try:
                        value=float(gpu[name]); assert math.isfinite(value)
                    except (KeyError,ValueError,AssertionError):
                        missing+=1; continue
                    values.append(value)
            fields[name]={'distribution':dist(values) if values else None,'missing_or_unsupported':missing}
        hardware[rows[0]['role']]={'samples':len(samples),'fields':fields}
    runtime=json.loads((a/'runtime-readiness.json').read_text())
    for role in ('prefill-0','prefill-1','decode-0'):
        expected='RadixCache' if job==27376 and role!='decode-0' else 'ChunkCache'
        assert runtime['roles'][role]['actual_cache_class']==expected
        assert (a/f'{role}.log').read_text().count('CACHE_LIFECYCLE_SOURCE_VERIFIED')==1
    accounting=subprocess.check_output(['sacct','-X','-j',str(job),'-P',
        '--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'],text=True)
    rows=[line.split('|') for line in accounting.splitlines()]
    terminal=[dict(zip(rows[0],row)) for row in rows[1:] if row[0]==str(job)]
    assert len(terminal)==1 and terminal[0]['State']=='COMPLETED' and terminal[0]['ExitCode']=='0:0'
    reviews[str(job)]={'job':job,'summary':review['summary'],'scheduler':terminal[0],
        'latency_distributions_ms':{k:dist([r['metrics'][k]['value'] for r in raw])
            for k in ('time_to_first_token','inter_token_latency','request_latency')},
        'hardware':hardware,'telemetry':review['telemetry_in_admission_envelope'],
        'runtime':review['runtime'],'cache_runtime':runtime,
        'smoke':review['smoke'],'retrieval':review['retrieval'],
        'ttft_breaches':review['ttft_breaches'],'itl_breaches':review['itl_breaches'],
        'reported_token_lengths':{k:dict(collections.Counter(str(r['metrics'][k]['value']) for r in raw))
            for k in ('input_sequence_length','output_sequence_length')},
        'actual_allocation_GPU_hours':16*int(terminal[0]['ElapsedRaw'])/3600,
        'maximum_reservation_GPU_hours':16*17/60,'PBS_SU':0}
    if job==27378:
        assert str(job) not in subprocess.check_output(
            ['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
        manifest=a/'artifact-manifest.json'; assert not manifest.exists()
        (a/'scheduler-accounting.psv').write_text(accounting)
        files=[]
        for p in sorted(a.rglob('*'))+[Q/f'runs/{job}.out',Q/f'runs/{job}.err']:
            if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p==manifest: continue
            before=p.stat(); digest=hashlib.sha256(p.read_bytes()).hexdigest(); after=p.stat()
            assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
            files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':digest})
        manifest.write_text(json.dumps({'job':job,'sealed_utc':datetime.datetime.now(
            datetime.timezone.utc).isoformat(),'terminal_accounting':accounting,'files':files},indent=2)+'\n')
deltas={}
for role in ('prefill-0','prefill-1','decode-0'):
    control=resolved(27376,role); treatment=resolved(27378,role)
    delta={k:[control.get(k),treatment.get(k)] for k in sorted(set(control)|set(treatment))
           if control.get(k)!=treatment.get(k)}
    allowed={'random_seed'} | ({'disable_radix_cache'} if role!='decode-0' else set())
    assert set(delta)<=allowed,(role,delta)
    if role!='decode-0':
        assert delta['disable_radix_cache']==['Constant(value=False)','Constant(value=True)']
    deltas[role]=delta
c=reviews['27376']['summary']; t=reviews['27378']['summary']
gain=100*(t['good_output_tokens_s']/c['good_output_tokens_s']-1)
assert 0<gain<1
result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'state':'PAIR_REVIEWED_CLOSE_UNCHANGED_PREFILL_CHUNK_CACHE',
    'question':'Does removing cold-workload prefix-tree bookkeeping improve useful throughput?',
    'control_job':27376,'candidate_job':27378,'configured_factor':'prefill disable_radix_cache False -> True',
    'actual_resolved_server_arg_differences':deltas,'runs':reviews,
    'good_output_tokens_s_delta_percent':gain,
    'ttft_p95_delta_percent':100*(t['ttft_p95_ms']/c['ttft_p95_ms']-1),
    'itl_mean_delta_percent':100*(t['itl_avg_ms']/c['itl_avg_ms']-1),
    'decision':'Close exact unchanged ChunkCache arm; no repeat, cap64 combination, default or submission promotion.',
    'next':'Review actual C++ CPU prerequisite and decode compile; admit distinct source-supported trials within caps.',
    'official_accuracy':'UNKNOWN',
    'limits':'One run per arm; generated engine seeds differ independently of fixed workload seed 2026. Sparse five-second hardware/server observations use first-to-last profiling request START envelope with uncalibrated clocks, not exact phase/drain coverage. No kernel-time profile, hot-thread CPU, Xid/throttle-reason record, actual generated token IDs or authoritative per-request server usage. No causal bottleneck or global-optimum claim.'}
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
report=f"""# Cold-prefill cache pair: no useful measured gain

Reviewed 29 October 2026, Vietnam time (UTC+7). Both full H200 jobs passed the independent frozen workload, runtime, KV, semantic and local output checks. The prefill ChunkCache candidate scored **{t['good_output_tokens_s']:.6f} good output tokens/s**, **+{gain:.6f}%** against fresh native control. This is below the prospective 1% useful-gain gate; close this exact arm without changing the default or submission.

| Measurement | Native control 27376 | Prefill ChunkCache 27378 |
|---|---:|---:|
| Good output tokens/s | {c['good_output_tokens_s']:.6f} | {t['good_output_tokens_s']:.6f} |
| Good requests / all requests | 1874 / 1900 | 1879 / 1905 |
| Good fraction | 98.631579% | 98.635171% |
| Errors / cancellations | 0 / 0 | 0 / 0 |
| TTFT breaches / ITL breaches | 26 / 0 | 26 / 0 |
| TTFT mean / p95, ms | {c['ttft_avg_ms']:.3f} / {c['ttft_p95_ms']:.3f} | {t['ttft_avg_ms']:.3f} / {t['ttft_p95_ms']:.3f} |
| Request-mean ITL mean / p95, ms | {c['itl_avg_ms']:.3f} / {c['itl_p95_ms']:.3f} | {t['itl_avg_ms']:.3f} / {t['itl_p95_ms']:.3f} |
| Smoke / retrieval | 7/8, no regression / 12/12 | 7/8, no regression / 12/12 |
| Scheduler | COMPLETED 0:0, 12:39 | COMPLETED 0:0, 11:41 |
| Allocation occupancy, GPU-hours | {reviews['27376']['actual_allocation_GPU_hours']:.6f} | {reviews['27378']['actual_allocation_GPU_hours']:.6f} |

The hypothesis was that cold inputs gain little from reusable prefix-tree lookup, so removing that bookkeeping might help. Only prefill disable_radix_cache changed from false to true. Actual all-rank classes changed from Python RadixCache to ChunkCache on both TP4 prefill roles, while the TP8 decode role retained ChunkCache, cap 256 and polling interval 1. The machine review checks complete resolved ServerArgs: only this intended setting and generated engine random seeds differ. Workload seed remains 2026. Physical prefill KV, source/lifecycle bindings, both semantic routes and original FP8/BF16 geometry all pass. Prefix lookup removal does not mean disabling active-request KV storage.

The score moved by only +{gain:.6f}%. TTFT mean improved, but p95 increased by {result['ttft_p95_delta_percent']:.3f}% and mean ITL increased by {result['itl_mean_delta_percent']:.3f}%. One run per setting cannot separate small treatment effects from launch/seed variation. The candidate's larger single-run score is not a confirmed useful improvement or a new global optimum.

Beyond the score, inspected raw request outcomes and p50/p95/p99/max latency, actual cache/flags, all semantic and output checks, selected traceback/transport markers, per-role server samples and available GPU/host measurements. Candidate decode has 24 samples, 100% sampled GPU activity, mean 50.708 running requests, maximum 56, zero sampled queue and mean token occupancy 0.1196. Both prefill roles average 2.917 running requests with maxima 3/4 and sampled queue maxima 3. All 72 server polls return HTTP 200. Per-role VRAM/power/temperature/clocks distributions and source/runtime evidence are in comparison.json. Five-second sparse observations do not establish GPU saturation as a causal bottleneck, nor does a zero sampled queue prove it was always empty. Missing heavy kernel profile, CPU hot threads and Xid/throttle reasons are not zero/healthy. Profiling request-start envelopes omit final drain and clocks are not calibrated.

Cost is {sum(r['actual_allocation_GPU_hours'] for r in reviews.values()):.6f} observed GPU-hours for both jobs, within their 9.066667 GPU-hour combined maximum; zero PBS SU. Complete terminal candidate artifacts, frozen payload and scheduler accounting are sealed in runs/27378/artifact-manifest.json; control seal already exists. Official full-set model accuracy remains UNKNOWN. Local smoke/retrieval cannot certify the organiser's at-least-99%-of-reference condition.

Next: preserve these losing results, close this unchanged setting, and review the distinct C++ cache prerequisite and conditional decode compile. The C++ branch retains prefix caching and changes its implementation, so it is a separate hypothesis. No blind ChunkCache rerun or cap64 combination follows from this sub-1% point result.
"""
(D/'RESULTS.md').write_text(report)
print(json.dumps({'state':result['state'],'gain_pct':gain,'candidate_good_tokens_s':t['good_output_tokens_s']}))

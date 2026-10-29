#!/usr/bin/env python3
"""Seal and interpret the completed cap sensitivity trial without promoting noise."""
from pathlib import Path
import collections,datetime,hashlib,json,math,re,statistics,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;A=Q/'runs/27365'
r=json.loads((Q/'h200-full-load-review-20261026/review-27365.json').read_text())
c=json.loads((Q/'h200-full-load-review-20261026/review-27270.json').read_text())
assert r['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
raw=[json.loads(l) for l in (A/'confirm/n64/artifacts/profile_export.jsonl').open()]
raw=[v for v in raw if v['metadata']['benchmark_phase']=='profiling']
lo=min(v['metadata']['request_start_ns'] for v in raw);hi=max(v['metadata']['request_start_ns'] for v in raw)
def dist(values):
    v=sorted(values)
    def quant(p):
        x=(len(v)-1)*p;i=math.floor(x);j=math.ceil(x)
        return v[i]+(v[j]-v[i])*(x-i)
    return {'count':len(v),'min':min(v),'mean':statistics.mean(v),'p50':quant(.5),'p95':quant(.95),'p99':quant(.99),'max':max(v)}
hardware={}
for p in (A/'resource-telemetry').glob('*.jsonl'):
    rows=[json.loads(l) for l in p.open()]
    samples=[x for x in rows if x['kind']=='sample' and lo<=x['utc_ns']<=hi]
    fields={}
    for field in ('utilization.gpu','utilization.memory','memory.used','power.draw','temperature.gpu','clocks.sm','clocks.mem'):
        values=[];missing=0
        for row in samples:
            for gpu in row.get('gpus',[]):
                try:value=float(gpu[field]);assert math.isfinite(value)
                except (KeyError,ValueError,AssertionError):missing+=1;continue
                values.append(value)
        fields[field]={'distribution':dist(values) if values else None,'missing_or_unsupported':missing}
    hardware[rows[0]['role']]={'samples':len(samples),'fields':fields}
decs=[json.loads(l) for l in (A/'resource-telemetry/decode-0-g4.jsonl').open()]
decs=[x for x in decs if x['kind']=='sample' and lo<=x['utc_ns']<=hi]
idle=[{'seconds_after_first_request_start':(x['utc_ns']-lo)/1e9,'activity_values':sorted(set(float(g['utilization.gpu']) for g in x['gpus']))} for x in decs if any(float(g['utilization.gpu'])<100 for g in x['gpus'])]
final=re.findall(r'TP0 EP0\] max_total_num_tokens=\d+,[^\n]*max_running_requests=(\d+), context_len=8192',(A/'decode-0.log').read_text())
assert final==['64']
account=subprocess.check_output(['sacct','-X','-j','27365','-P','--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'],text=True)
assert '27365|COMPLETED|0:0|00:11:43|703|' in account
assert '27365' not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
(A/'scheduler-accounting.psv').write_text(account)
manifest=A/'artifact-manifest.json'
assert not manifest.exists()
files=[]
for p in sorted(A.rglob('*'))+[Q/'runs/27365.out',Q/'runs/27365.err']:
    if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p==manifest:continue
    before=p.stat();digest=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':digest})
manifest.write_text(json.dumps({'job':27365,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':account,'files':files},indent=2)+'\n')
score=r['summary']['good_output_tokens_s'];control=c['summary']['good_output_tokens_s']
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':r['state'],'job':27365,'control_job':27270,'score_good_tokens_s':score,'control_good_tokens_s':control,'change_vs_control_pct':100*(score/control-1),'change_vs_native_individual26766_pct':100*(score/3045.501509-1),'final_scheduler_decode_cap':64,'summary':r['summary'],'ttft_breaches':r['ttft_breaches'],'itl_breaches':r['itl_breaches'],'latency_distributions_ms':{k:dist([x['metrics'][k]['value'] for x in raw]) for k in ('time_to_first_token','inter_token_latency','request_latency')},'local_smoke':r['smoke'],'local_retrieval':r['retrieval'],'runtime':r['runtime'],'telemetry':r['telemetry_in_admission_envelope'],'extended_hardware':hardware,'decode_samples_below100':idle,'reported_input_histogram':dict(collections.Counter(str(x['metrics']['input_sequence_length']['value']) for x in raw)),'reported_output_histogram':dict(collections.Counter(str(x['metrics']['output_sequence_length']['value']) for x in raw)),'actual_allocation_GPU_hours':16*703/3600,'maximum_reservation_GPU_hours':16*17/60,'PBS_SU':0,'decision':'Close unchanged cap64 sensitivity: small positive single-run result below >1% useful gain. No repeat/default/submission promotion.','official_accuracy':'UNKNOWN','limits':'Sparse request-start-envelope hardware observations; no calibrated cross-host clocks, hot-thread saturation, throttling/Xid or heavy kernel profile. Client token recount is not actual generated IDs.'}
(D/'comparison.json').write_text(json.dumps(out,indent=2)+'\n')
(D/'RESULTS.md').write_text(f'''# Decode cap64 passes but does not establish useful improvement

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual **27365 completed 0:0 in 11:43 on g1/g4**,16 H200. Source/runtime/final-scheduler/KV/two-route/local-output and full raw protocol pass. It is a valid exploratory measurement, not official model accuracy.

| Metric | Control cap256,27270 | Candidate cap64,27365 |
|---|---:|---:|
| Good output throughput,tokens/s | {control:.6f} | {score:.6f} |
| Joint SLA,percent of all requests | 98.527865 | 98.633736 |
| Total/good requests | 1902/1874 | 1903/1877 |
| Mean/p95 TTFT,ms | 1116.427/1312.170 | 1111.512/1326.607 |
| Mean/p95 request-mean ITL,ms | 14.995/15.169 | 14.998/15.159 |
| Errors/cancellations | 0/0 | 0/0 |
| TTFT/ITL breaches | 28/0 | 26/0 |
| Smoke/retrieval | 7/8 and12/12 | 7/8 and12/12 |

The single-run change is **+{out['change_vs_control_pct']:.6f}%**, below the prospective >1% useful-gain gate. It is only +{out['change_vs_native_individual26766_pct']:.6f}% above the separate previous native individual26766, too small to establish an optimization. No unchanged repeat, default or submission promotion. Keep the original baseline and close this exact cap64 sensitivity; no128sweep. Local output checks do not verify official accuracy, which remains UNKNOWN.

The exact intended change is source/runtime confirmed: requested and final TP0 scheduler cap64, with separate transfer/preallocation slots, unchanged prefill settings, graph batches1..64, image/model/precision/KV/NIXL and full requested N64 cold4000/200 seed2026/60:120:30. Every native pool source guard passes. All physical KV receipts and both semantic routes pass. No descriptor exception or quality gate was broadened.

Beyond the score,24 five-second samples show mean49.625/max56 running decode requests, no sampled decode queue and mean KV token usage0.1146. Decode activity mean95.833% versus100% in control is explained arithmetically by one of24 samples containing0% on all eight GPUs, only0.161s after the first profiling request started; the remaining23 samples have100%. This timing sensitivity prevents interpreting the activity average as a causal efficiency improvement. It does not prove the reason for that initial idle sample. Decode sampled VRAM is131.158GiB/GPU; host-wide CPU estimates are12.87% decode/12.57% prefill, not hot-thread measurements. All72 role polls returnHTTP200 and no selected transport error/Python traceback is found. Full raw latency and sampled power/temperature/clocks/memory-activity distributions are retained in comparison.json. Missing heavy kernel profile, Xid/throttling reasons and exact generated IDs remain explicit.

Client-reported token counts may differ slightly from requested fixed lengths because AIPerf uses local text tokenization; exact per-row physical IDs are uncollected. The organiser score remains exported Goodput×200. Do not redefine it with a token recount mean.

Allocation occupancy is{out['actual_allocation_GPU_hours']:.6f}GPU-hours versus maximum4.533334 reservation, noPBS_SU; this is not a metered charge. Raw requests/exports, logs, telemetry, original frozen payload and accounting are sealed in runs/27365/artifact-manifest.json. The candidate has answered the low-upside source question without revealing a useful gain. New prefill-cache pair27376/27378 and compile qualification27383 are separate hypotheses already accepted; this branch closure does not stop the research loop.
''')
print(json.dumps({'job':27365,'score':score,'vs_control_pct':out['change_vs_control_pct'],'vs_native26766_pct':out['change_vs_native_individual26766_pct'],'decision':out['decision']}))

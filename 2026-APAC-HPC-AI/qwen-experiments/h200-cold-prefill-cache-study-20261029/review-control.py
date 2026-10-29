#!/usr/bin/env python3
"""Preserve the terminal fresh cache control and its independently reviewed evidence."""
from pathlib import Path
import collections,datetime,hashlib,json,math,statistics,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;A=Q/'runs/27376'
r=json.loads((Q/'h200-full-load-review-20261026/review-27376.json').read_text())
assert r['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
def dist(v):
    v=sorted(v)
    def quant(p):
        x=(len(v)-1)*p;i=math.floor(x);j=math.ceil(x)
        return v[i]+(v[j]-v[i])*(x-i)
    return {'count':len(v),'min':v[0],'mean':statistics.mean(v),'p50':quant(.5),'p95':quant(.95),'p99':quant(.99),'max':v[-1]}
raw=[json.loads(l) for l in (A/'confirm/n64/artifacts/profile_export.jsonl').open()]
raw=[v for v in raw if v['metadata']['benchmark_phase']=='profiling']
lo=min(v['metadata']['request_start_ns'] for v in raw);hi=max(v['metadata']['request_start_ns'] for v in raw)
hardware={}
for p in (A/'resource-telemetry').glob('*.jsonl'):
    rows=[json.loads(l) for l in p.open()]
    samples=[x for x in rows if x['kind']=='sample' and lo<=x['utc_ns']<=hi]
    fields={}
    for f in ('utilization.gpu','utilization.memory','memory.used','power.draw','temperature.gpu','clocks.sm','clocks.mem'):
        vals=[];missing=0
        for row in samples:
            for gpu in row.get('gpus',[]):
                try:val=float(gpu[f]);assert math.isfinite(val)
                except (KeyError,ValueError,AssertionError):missing+=1;continue
                vals.append(val)
        fields[f]={'distribution':dist(vals) if vals else None,'missing_or_unsupported':missing}
    hardware[rows[0]['role']]={'samples':len(samples),'fields':fields}
runtime=json.loads((A/'runtime-readiness.json').read_text())
for role in ('prefill-0','prefill-1','decode-0'):
    assert runtime['roles'][role]['actual_cache_class']==('ChunkCache' if role=='decode-0' else 'RadixCache')
    assert (A/f'{role}.log').read_text().count('CACHE_LIFECYCLE_SOURCE_VERIFIED')==1
account=subprocess.check_output(['sacct','-X','-j','27376','-P','--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList'],text=True)
assert '27376|COMPLETED|0:0|00:12:39|759|' in account
assert '27376' not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
(A/'scheduler-accounting.psv').write_text(account)
manifest=A/'artifact-manifest.json';assert not manifest.exists()
files=[]
for p in sorted(A.rglob('*'))+[Q/'runs/27376.out',Q/'runs/27376.err']:
    if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p==manifest:continue
    before=p.stat();digest=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat()
    assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':digest})
manifest.write_text(json.dumps({'job':27376,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':account,'files':files},indent=2)+'\n')
out={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':27376,'state':r['state'],'purpose':'Fresh native control, not a new optimization','summary':r['summary'],'ttft_breaches':r['ttft_breaches'],'itl_breaches':r['itl_breaches'],'latency_distributions_ms':{k:dist([x['metrics'][k]['value'] for x in raw]) for k in ('time_to_first_token','inter_token_latency','request_latency')},'hardware':hardware,'telemetry':r['telemetry_in_admission_envelope'],'runtime':r['runtime'],'cache_runtime':runtime,'smoke':r['smoke'],'retrieval':r['retrieval'],'reported_token_lengths':{k:dict(collections.Counter(str(x['metrics'][k]['value']) for x in raw)) for k in ('input_sequence_length','output_sequence_length')},'actual_allocation_GPU_hours':16*759/3600,'maximum_reservation_GPU_hours':16*17/60,'PBS_SU':0,'official_accuracy':'UNKNOWN','limits':'One fresh native control. Sparse request-start-envelope samples, uncalibrated clocks, no heavy kernel/Xid/throttling/hot-thread profile. Engine seed is generated separately from fixed workload seed2026. Client token counts are text recounts, not actual generated IDs.'}
(D/'control-review-27376.json').write_text(json.dumps(out,indent=2)+'\n')
s=r['summary']
(D/'CONTROL_RESULTS.md').write_text(f'''# Fresh native cache control 27376

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual job **27376 completed 0:0 in 12:39 on g1/g4**, using 16 H200. This is our fresh control, not an optimization or the organiser reference.

The independent frozen raw/runtime/KV/semantic/output gate passes at **{s['good_output_tokens_s']:.6f} good output tokens/s**, 1874/1900 good requests (98.631579%), zero errors/cancellations, 26 TTFT and zero ITL breaches, smoke7/8 without regression and retrieval12/12. Mean/p95 TTFT is 1119.985/1332.727 ms and request-mean ITL14.991/15.166 ms. Full p50/p95/p99/max and hardware distributions are retained in control-review-27376.json.

All four ranks of each prefill use default RadixCache; all eight decode ranks use ChunkCache with native disable_radix_cache=True. Physical prefill KV is not disabled, original geometry signatures and both semantic P/D routes pass, and all three cache-lifecycle source guards are observed. No source/descriptor exception was widened. The control retains decode cap256/polling1 and all canonical requested N64 cold4000/200 seed2026/full60/120/30 parameters.

The score is +{100*(s['good_output_tokens_s']/3039.0533861728013-1):.6f}% versus earlier native27270. This is a same-setting repeat difference, not an improvement; engine random seeds and launch state vary while workload seed2026 is fixed. It provides the prospective fresh comparator for27378 prefill ChunkCache and27383 conditional decode compilation.

Raw request outcomes, tail latency, role queues/inflight/KV, server polls, selected transport/traceback markers and available CPU/GPU/VRAM/power/temperature/clocks were inspected. See machine review for actual sampled values; missing heavy kernel profile, Xid/throttle reasons and hot-thread CPU are not zeros or healthy. Samples are five-second observations in the first-to-last request-start envelope, with uncalibrated host clocks and no final-drain coverage.

Only source-supported local output checks are established; official full-set model accuracy remains UNKNOWN. The pinned rules say the organisers use the same full-set checks against their own unchanged FP8 reference and require≥99% of that score. The exact official suite/splits/command/reference score are not supplied in the retained Q1 text; model-card benchmark examples are not an authoritative fixed evaluation protocol. Do not claim the small smoke/retrieval checks or a private MMLU/GPQA subset certify that gate.

Occupancy is{16*759/3600:.6f} GPU-hours versus maximum4.533334 reservation, noPBS_SU. Complete raw outputs/frozen payload/telemetry/accounting are sealed in runs/27376/artifact-manifest.json. Preserve queued candidate positions and compare only complete local passes. Require>1% useful gain and acceptable tails before confirmation; otherwise close the exact setting. No default, slide or submission promotion follows from a control.
''')
print(json.dumps({'job':27376,'state':out['state'],'good_output_tokens_s':s['good_output_tokens_s'],'actual_GPU_hours':out['actual_allocation_GPU_hours']}))

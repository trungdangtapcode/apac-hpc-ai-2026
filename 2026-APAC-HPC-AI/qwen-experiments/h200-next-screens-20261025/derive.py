#!/usr/bin/env python3
"""Derive bounded H200 follow-ups without mutating any submitted parent."""
from pathlib import Path
import hashlib, json, shutil
ROOT = Path(__file__).resolve().parents[1]

def replace(path, old, new):
    text = path.read_text()
    assert old in text, (path, old)
    path.write_text(text.replace(old, new))

def copy(parent, name):
    dst = ROOT / 'serving-tuning-11' / name
    shutil.copytree(parent, dst, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (dst/'PARENT_CHAIN.json').write_bytes((dst/'PARENT_BUNDLE.json').read_bytes()) if (dst/'PARENT_BUNDLE.json').exists() else None
    (dst/'PARENT_BUNDLE.json').write_text(json.dumps({
        'parent_bundle':str(parent.relative_to(ROOT)),
        'parent_sha256sums_sha256':hashlib.sha256((parent/'SHA256SUMS').read_bytes()).hexdigest(),
        'derivation_script':'h200-next-screens-20261025/derive.py',
        'derivation_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    },indent=2)+'\n')
    cfg=json.loads((dst/'config.json').read_text()); cfg['experiment']=name
    replace(dst/'job.sbatch', str(parent), str(dst))
    replace(dst/'job.sbatch', parent.name+'-${SLURM_JOB_ID}', name+'-${SLURM_JOB_ID}')
    return dst,cfg

def common_gate(dst):
    p=dst/'performance_gates.py'
    replace(p,"rows=[r for r in summary if r.get('phase')=='screen' and r.get('concurrency')==64]", """phases=[p for p in expected_input['phases'] if p['kind']=='profiling']
    assert len(phases)==1, 'one configured profiling phase required'
    n=phases[0]['concurrency']
    assert type(n) is int and n>0, 'configured concurrency must be positive integer'
    assert json.loads((art/'config.json').read_text())['concurrency']==n, 'bundle concurrency differs from expected workload'
    rows=[r for r in summary if r.get('phase')=='screen' and r.get('concurrency')==n]""")
    replace(p,"'one measured N64 point is required'", "f'one measured N{n} point is required'")
    replace(p,"art/'screen/n64/artifacts/profile_export_aiperf.json'", "art/f'screen/n{n}/artifacts/profile_export_aiperf.json'")
    replace(p,"art/'screen/n64/client.log'", "art/f'screen/n{n}/client.log'")
    replace(dst/'check-performance.py',"'concurrency':64,**profile", "'concurrency':cfg['concurrency'],**profile")

def seal(dst,cfg):
    (dst/'config.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n')
    files=sorted(p for p in dst.iterdir() if p.is_file() and p.name!='SHA256SUMS')
    (dst/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))

s59=ROOT/'serving-tuning-10/s59-h200-fast-default-control'
for study_arm,policy,name,job in [
    ('control','round_robin','s65-h200-router-rr-control','ap42-s65-rr'),
    ('candidate','power_of_two','s64-h200-prefill-power-of-two','ap42-s64-pow2')]:
    dst,cfg=copy(s59,name)
    cfg.update(label=f'{name}: target-only routing {study_arm}',study_arm=study_arm,
               prefill_policy=policy,source_bundle=str(s59.relative_to(ROOT)),
               matched_pair='S65 round_robin versus S64 power_of_two; target-only runtime unchanged.',
               schema='h200-routing-short-screen-v1')
    # arm remains control: it describes target-only versus draft, independent of the routing study arm.
    common_gate(dst)
    replace(dst/'job.sbatch','ap42-s59-h200-fast-control',job)
    replace(dst/'job.sbatch','export QWEN_RESOURCE_MONITOR=1',f'export QWEN_RESOURCE_MONITOR=1\nexport QWEN_PREFILL_POLICY={policy}')
    replace(dst/'topology-job.sh','BUNDLE=$QWEN_BUNDLE','''BUNDLE=$QWEN_BUNDLE
PREFILL_POLICY=${QWEN_PREFILL_POLICY:-round_robin}
[[ "$PREFILL_POLICY" == round_robin || "$PREFILL_POLICY" == power_of_two ]] || exit 1
python3 - "$BUNDLE/config.json" "$PREFILL_POLICY" <<'PYPOLICY'
import json,sys
assert json.load(open(sys.argv[1]))['prefill_policy']==sys.argv[2]
PYPOLICY''')
    replace(dst/'topology-job.sh','--prefill-policy round_robin "${router_args[@]}"','--prefill-policy "$PREFILL_POLICY" "${router_args[@]}"')
    replace(dst/'check-performance.py',"import ast, hashlib, importlib.util, json, sys", "import ast, hashlib, importlib.util, json, re, sys")
    replace(dst/'check-performance.py',"    context=json.loads((art/'launch-context.json').read_text()); candidate=cfg['arm']=='candidate'", """    policy_log=(art/'router.log').read_text(errors='replace')
    policy_log=re.sub(r'\x1b\\[[0-9;]*m','',policy_log)
    records=[line for line in policy_log.splitlines() if 'prefill_policy:' in line]
    native={'round_robin':'Some(RoundRobin)',
            'power_of_two':'Some(PowerOfTwo { load_check_interval_secs: 5 })'}[cfg['prefill_policy']]
    assert len(records)==2, 'expected exactly two main-router startup policy records'
    assert all(f'prefill_policy: {native}, decode_policy: None' in line for line in records), 'actual main router policy mismatch'
    assert sum('Starting router on 0.0.0.0:8000' in line for line in records)==1
    context=json.loads((art/'launch-context.json').read_text()); candidate=cfg['arm']=='candidate'""")
    (dst/'README.md').write_text(f'''# {name}\n\nTarget-only H200 {study_arm} for a matched round-robin/power-of-two prefill-routing screen. Read PLAN.md. Run sbatch from qwen-experiments, where runs/ exists. All 16 GPUs, 17-minute cap, no PBS SU. No result or official accuracy pass is claimed. Historical derive.py is inherited; use the parent-bound h200-next-screens-20261025/derive.py for this bundle.\n''')
    (dst/'PLAN.md').write_text('''# H200 prefill routing: controlled short pair

S63 N66–N72 did not improve good throughput. TTFT tails grew while ITL stayed below 20 ms; sparse rank-local prefill queues reached 13–25, whereas captured decode queues were zero. This motivates testing prefill dispatch but does not prove a causal bottleneck.

S65 is a fresh round-robin control; S64 changes only main-router prefill policy to power_of_two. It compares two workers using the pinned default five-second load check interval. Native startup must show the exact PowerOfTwo struct enum, not an invented unit-like enum. Worker-local load_balance_method is a different mechanism. All target-only model/image/precision/kernel/graph/transport settings, P8-TP4/D8-TP8-EP8 topology, N64, 4000/200 tokens, seed2026, cold prefixes and 20/40/30 protocol match. Both bundles include the same configured-concurrency checker fix. No scoring settings are relaxed.

H100 full N54 pair 222302/222303 lost 4.865% under power-of-two. That negative prior is retained; this is a one-time H200 interaction screen at a different runtime/kernel/load, not a repeat of H100 or a pooled hardware comparison. See router-queue-research-20261020/PAIR_REVIEW.md and ROUTER_REVIEW_CORRECTION.md.

Require full runtime/native geometry, two semantic paths, complete raw request denominator, >=90% joint latency success (TTFT <=3000 ms; request-mean ITL <=20 ms), zero request errors/cancellations, no smoke regression below7/8, retrieval12/12, exact main-router native policy and pinned workload. Short synthetic output checks do not establish official accuracy; it remains UNKNOWN.

Advance only if candidate passes every local gate and exceeds fresh S65 control by at least3% good output tokens/s. Historical 25947 is descriptive (2757.36), never substituted for a failed fresh control. Otherwise close this exact H200 policy branch. One pair cannot establish a reproduced gain or replace the full-protocol3044.400475 frontier. If useful, require independent full matched confirmation.

Each job allocates16 H200 GPUs / two nodes for at most17 minutes. Submit control then candidate with afterany dependency; admission cap5 includes both. Preserve all logs and sampling, inspect phase-bounded GPU/CPU/VRAM/queue/KV/tails beyond the score, mark missing telemetry explicitly. No heavy profiling in scoring. Run from qwen-experiments so relative log paths exist. No PBS spending, frozen parent edits, target-weight changes or background Codex.
''')
    # Normal prose spacing is intentional even for numeric units.
    p=dst/'PLAN.md';t=p.read_text()
    for a,b in [('seed2026','seed 2026'),('below7/8','below 7/8'),('retrieval12/12','retrieval 12/12'),('least3%','least 3%'),('full-protocol3044','full-protocol 3044'),('allocates16','allocates 16'),('most17','most 17'),('cap5','cap 5')]:t=t.replace(a,b)
    p.write_text(t)
    seal(dst,cfg)

parent=ROOT/'serving-tuning-11/s62r3-h200-two-decode-tp4'
dst,cfg=copy(parent,'s62r4-h200-two-decode-tp4')
cfg.update(label='S62r4 two TP4 decode replicas with bounded first-transfer wait',
           source_bundle=str(parent.relative_to(ROOT)),
           warmup_http_timeout='remaining shared 180-second deadline; no timeout retries')
common_gate(dst)
replace(dst/'job.sbatch','ap42-s62r3-two-d4','ap42-s62r4-two-d4')
replace(dst/'warm-topology.py','timeout=max(1, min(30, int(deadline-time.time())))','timeout=max(0.1, deadline-time.time())')
with (dst/'PLAN.md').open('a') as f:f.write('''\n## S62r4 correction after actual job 26076\n\nJob26076 passed worker/runtime/KV readiness but produced no semantic receipt or AIPerf export: the inherited HTTP timeout was30 seconds even with180 seconds available to initialize all four routes. This revision lets a single in-flight HTTP request use the remaining shared180-second deadline. The outer180-second timeout and17-minute allocation cap remain. No timed-out request is retried, no output/route/runtime gate is relaxed. Historical22219 required up to150.55 seconds. This is a bounded initialization hypothesis, not a proven NIXL fix. If all four routes still fail, stop this full-topology retry branch and diagnose transport separately. All performance promotion gates above remain.\n'''.replace('Job26076','Job 26076').replace('was30','was 30').replace('with180','with 180').replace('shared180','shared 180').replace('outer180','outer 180').replace('and17','and 17').replace('Historical22219','Historical 22219').replace('to150','to 150'))
(dst/'README.md').write_text('# S62r4 bounded first-transfer retry\n\nDerived from frozen S62r3 after failure26076. Only initialization HTTP wait, configured-N performance checking and identity change; full unchanged semantic/runtime/output gates still required. No measured result. Read PLAN.md. Run sbatch from qwen-experiments.\n'.replace('failure26076','failure 26076'))
seal(dst,cfg)
print('Derived S64, S65 and S62r4; parents unchanged.')

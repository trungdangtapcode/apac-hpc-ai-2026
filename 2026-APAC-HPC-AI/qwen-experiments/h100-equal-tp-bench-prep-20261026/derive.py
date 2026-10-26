#!/usr/bin/env python3
"""Derive an 8-H100, full-workload equal-TP EAGLE3 feasibility bundle."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[3]
Q=ROOT/'2026-APAC-HPC-AI/qwen-experiments'
PREP=Q/'h100-equal-tp-bench-prep-20261026'
P=Q/'eagle3-h100-equal-tp-observer-r2-20261026'
B=Q/'eagle3-h100-equal-tp-bench-n24-20261026'
H100=Q/'nscc-pbs/h100-cpu-envelope-legacy-n54-79'
H200=Q/'serving-tuning-11/s72-h200-full-pgraph-breakable-capnative'
BASE=Q/'h100-review-225227-225228-20261026/curated-r2/h100-incumbent-n54-refresh-20261026/runs/225227.pbs111'
assert not B.exists()
# Parent was explicitly sealed; verify before selecting exact immutable source files.
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=P,check=True,stdout=subprocess.DEVNULL)
manifest=[]
for line in (P/'SHA256SUMS').read_text().splitlines():
 digest,rel=line.split(None,1);rel=rel.lstrip('*');path=Path(rel)
 assert not path.is_absolute() and '..' not in path.parts
 src=P/path
 assert src.is_file() and not src.is_symlink() and hashlib.sha256(src.read_bytes()).hexdigest()==digest
 dst=B/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);manifest.append(rel)
# Add only reviewed, small client and scoring sources; no model/cache/runtime payload.
for src in [H100/'benchmark.sh',H100/'summarize.py',H100/'output-smoke.py',H100/'long-context-check.py',H100/'reference-output-smoke.json',H200/'performance_gates.py']:
 dst=B/src.name;assert not dst.exists();shutil.copyfile(src,dst)
# Bind the exact scoring recipe to the observed official-client schema from 225227.
base_export=json.loads((BASE/'confirm/n54/artifacts/profile_export_aiperf.json').read_text())
expected=base_export['input_config']
expected['endpoint']['urls']=['DYNAMIC_ALLOCATED_ROUTER']
expected['artifacts']['dir']='DYNAMIC_ARTIFACT_DIRECTORY'
for phase in expected['phases']:
 if 'concurrency' in phase:phase['concurrency']=24
expected['runtime']['workers']=24
(B/'expected-input-config.json').write_text(json.dumps(expected,indent=2)+'\n')
# Preserve reference workload while documenting the actual dated parent baseline.
cfg=json.loads((B/'config.json').read_text());cfg.update(
 experiment_id=B.name,status='PREPARED_NOT_SUBMITTED',
 question='Can one same-node P4/D4 EAGLE3 replica pass the complete fixed-length profile and local output gates at client N24, before any replicated 16-GPU scale-up?',
 platform='NSCC ASPIRE2A+, PBS, one H100 node, eight GPUs',
 allocation={'gpus':8,'wall_seconds':1800,'max_su':512.0,'su_rate_per_gpu_hour':128,'node_exclusive':True},
 phase_seconds={'startup':850,'semantic':240,'scoring':300,'quality':250,'teardown':80},
 phase_envelope_seconds=1720,phase_envelope_margin_seconds=80,
 topology=cfg['topology'],
 aiperf_score=True,ranked=False,official_quality_verified=False,quality='UNKNOWN_NOT_EVALUATED',
 causal_locality_or_tp_claim=False,reference_score_job='225227.pbs111',reference_score_good_output_tokens_s=2399.186728,
 necessary_per_replica_threshold_tokens_s=1235.581165,
 threshold_formula='2399.186728*1.03/2; necessary if two identical independent replicas are to exceed the fresh16-H100 reference by3%, not sufficient to prove aggregate scaling.',
 benchmark={'concurrency':24,'input_tokens':4000,'output_tokens':200,'random_seed':2026,'warmup_seconds':60,'measure_seconds':120,'grace_seconds':30,'good_fraction_min':0.90,'ttft_max_ms':3000,'mean_request_itl_max_ms':20,'score_unit':'good_output_tokens_per_second = AIPerf Goodput requests_per_second * 200'},
 parent_failed_job='224560.pbs111',parent_observer_repair_job='225228.pbs111',parent_semantic_pass=True,
 parent_sources={'bundle':str(P.relative_to(Q)),'sha256sums_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest()},
 notes=['One replica feasibility only; not comparable as a leaderboard score against16-GPU reference.','Requires all eight native metadata receipts, corrected observer send_kvcache/send_aux markers, and independent successful semantic response before scoring.','Independent per-rank method returned handles do not prove transfer completion; the semantic receipt is the functional completion evidence.','No full-set99%-reference accuracy evaluation is run.']
)
(B/'config.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n')
# 30-minute PBS stage deadlines; sequential scoring follows semantic acceptance.
pc=(B/'phase-controller.py');s=pc.read_text();s=s.replace('PHASE_SECONDS = {"startup": 850, "semantic": 240, "teardown": 80}','PHASE_SECONDS = {"startup": 850, "semantic": 240, "scoring": 300, "quality": 250, "teardown": 80}')
s=s.replace('PBS_WALLTIME_SECONDS = 1200','PBS_WALLTIME_SECONDS = 1800').replace('CUMULATIVE = {"startup": 850, "semantic": 1090, "teardown": 1170}','CUMULATIVE = {"startup": 850, "semantic": 1090, "scoring": 1390, "quality": 1640, "teardown": 1720}')
pc.write_text(s)
# Derived, strictly bounded N24 official-recipe measurement. Never change frozen NIXL/source/model args.
bench=(B/'benchmark.sh');s=bench.read_text().replace('${QWEN_TUNE_NS:-48}','${QWEN_TUNE_NS:-24}')
# Drop legacy post-score diagnostic profiling and in-script smoke; the derived controller owns the timed quality phase.
start=s.index('if [[ ${QWEN_DIAGNOSTIC_PROFILE:-0} == 1 ]]; then')
s=s[:start]
bench.write_text(s)
# Set exact experiment identity and a 30-minute wall, while keeping prerequisite gates unchanged.
p=B/'benchmark.pbs';s=p.read_text().replace('ap42-equal-tp-observer-r2','ap42-equal-tp-bench-n24').replace('walltime=00:20:00','walltime=00:30:00').replace('QWEN_TELEMETRY_MAX_S=1100','QWEN_TELEMETRY_MAX_S=1650').replace('eagle3-h100-equal-tp-observer-r2-20261026','eagle3-h100-equal-tp-bench-n24-20261026');p.write_text(s)
# Add score+quality only after the independent one-request gate succeeds.
t=B/'topology-job.sh';s=t.read_text().replace('"$BUNDLE" "$T0" "$deadlines" 1170 1200','"$BUNDLE" "$T0" "$deadlines" 1720 1800')
old='''echo 'ONE_EQUAL_TP_SINGLE_NODE_SEMANTIC_PD_PASS (no output-ID or score claim)' | tee "$ART/CONTROLLER_PASS.txt"
'''
new='''echo 'ONE_EQUAL_TP_SINGLE_NODE_SEMANTIC_PD_PASS (no output-ID or score claim)' | tee "$ART/CONTROLLER_PASS.txt"

score_start=$(date +%s)
score_deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" scoring "$score_start")
score_remaining=$(python3 "$BUNDLE/phase-controller.py" remaining "$T0" scoring "$score_start" "$(date +%s)")
(( score_remaining >= 240 )) || { echo 'FATAL: insufficient reserved time for the complete N24 AIPerf measurement' >&2; exit 1; }
python3 "$BUNDLE/phase-marker.py" "$ART" score_start "$score_start" "$score_deadline"
AIPERF=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=8 \\
  --container-image="$AIPERF" --container-mounts="/scratch:/scratch,$ROOT:$ROOT" \\
  env QWEN_TUNE_NS=24 QWEN_DIAGNOSTIC_PROFILE=0 QWEN_BUNDLE="$BUNDLE" \\
    QWEN_BENCHMARK_DEADLINE="$score_deadline" QWEN_GRACE=30 \\
    bash "$BUNDLE/benchmark.sh" "${IPS[0]}:8000" "$MODEL" "$ART"
python3 "$BUNDLE/check-benchmark.py" "$ART" > "$ART/benchmark-gate.json"
python3 "$BUNDLE/phase-marker.py" "$ART" score_end "$(date +%s)" "$score_deadline"

quality_start=$(date +%s)
quality_deadline=$(python3 "$BUNDLE/phase-controller.py" deadline "$T0" quality "$quality_start")
quality_remaining=$(python3 "$BUNDLE/phase-controller.py" remaining "$T0" quality "$quality_start" "$(date +%s)")
(( quality_remaining >= 180 )) || { echo 'FATAL: insufficient time for output and retrieval checks' >&2; exit 1; }
python3 "$BUNDLE/phase-marker.py" "$ART" quality_start "$quality_start" "$quality_deadline"
set +e
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \\
  --container-image=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh --container-mounts="/scratch:/scratch,$ROOT:$ROOT" \\
  python3 "$BUNDLE/output-smoke.py" "${IPS[0]}:8000" "$ART" > "$ART/output-smoke.log" 2>&1 & smoke_pid=$!
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \\
  --container-image=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh --container-mounts="/scratch:/scratch,$ROOT:$ROOT" \\
  python3 "$BUNDLE/long-context-check.py" "${IPS[0]}:8000" "$ART" > "$ART/long-context-check.log" 2>&1 & retrieval_pid=$!
wait "$smoke_pid"; smoke_status=$?
wait "$retrieval_pid"; retrieval_status=$?
set -e
(( smoke_status == 0 && retrieval_status == 0 )) || { echo "FATAL: post-score smoke/retrieval failed: $smoke_status/$retrieval_status" >&2; exit 1; }
python3 "$BUNDLE/check-benchmark.py" "$ART" > "$ART/full-local-acceptance.json"
python3 "$BUNDLE/phase-marker.py" "$ART" quality_end "$(date +%s)" "$quality_deadline"
echo 'N24_FULL_WORKLOAD_AND_LOCAL_OUTPUT_GATES_PASS; official accuracy UNKNOWN' | tee "$ART/ACCEPTANCE.txt"
'''
assert old in s;t.write_text(s.replace(old,new))
# Config held at ART root; ensure the local reviewer knows this is N24 and a full confirmation.
cfg['benchmark_phase']='confirm';cfg['concurrency']=24;cfg['output_tokens']=200;cfg['input_tokens']=4000;cfg['random_seed']=2026
(B/'config.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n')
# Create an independent raw-input/denominator/output checker from the tested H200 local gate.
perf=(H200/'performance_gates.py').read_text()
(B/'performance_gates.py').write_text(perf)
check='''#!/usr/bin/env python3
"""Fail-closed raw AIPerf, output-smoke and retrieval acceptance for this N24 probe."""
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gates',HERE/'performance_gates.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
art=Path(sys.argv[1]);expected=json.loads((HERE/'expected-input-config.json').read_text())
try:
 score=g.check_aiperf(art,expected,200)
 smoke=g.check_smoke(art,HERE/'reference-output-smoke.json')
 retrieval=g.check_retrieval(art)
 result={'state':'PASS_LOCAL_N24_NOT_OFFICIAL_ACCURACY','score':score,'smoke':smoke,'retrieval':retrieval,'official_accuracy':'UNKNOWN'}
 print(json.dumps(result,indent=2))
 raise SystemExit(0)
except Exception as exc:
 print(json.dumps({'state':'FAIL','error':f'{type(exc).__name__}: {exc}','official_accuracy':'UNKNOWN'},indent=2));raise SystemExit(1)
'''
(B/'check-benchmark.py').write_text(check)
# Store source/derivation provenance and a bounded, readable experiment plan.
(B/'PREPARATION.json').write_text(json.dumps({'state':'PREPARED_NOT_SUBMITTED','parent_bundle':str(P.relative_to(Q)),'parent_manifest_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest(),'baseline_job':'225227.pbs111','observer_pass_job':'225228.pbs111','source_baseline_expected_input_from':'225227.pbs111 AIPerf export input_config; only concurrency/workers changed to24','max_su':512.0,'cpu_tests_to_run':['Python AST/shell syntax','hash manifest and tar agreement','replay strict scoring gates against recovered full N54 run with expected N54 schema; reject mutated summary concurrency','replay corrected pre/post semantic gates against225228 raw evidence'],'never_claim':'Leaderboard improvement,16-GPU scaleup, official accuracy, or distributed replica aggregate from one8-GPU result.'},indent=2)+'\n')
(B/'PLAN.md').write_text('''# One-node equal-TP EAGLE3 full-workload feasibility at N24

The corrected observer experiment225228 passed actual equal-TP native send_kvcache and send_aux invocation/return markers on all four prefill ranks, with no observer exceptions, eight unique H100 devices, pinned sources and one independent semantic response. This repairs the evidence gap from224560. It establishes one functional same-node request, not benchmark stability or output quality.

The fresh full N54 non-EAGLE control225227 measured2399.186728 good output tokens/s with98.015873% joint SLA, zero request errors/cancellations, smoke7/8 and retrieval12/12. Job222551 retained2407.544052 on H100. A single eight-GPU result cannot be ranked directly against either sixteen-GPU reference. This probe asks only if one P4/D4 EAGLE3 instance can sustain official fixed 4000/200 closed-loop traffic at N24 while passing local gates, before considering two independent replicas. It does not compare equal GPU resources or prove scale-up.

At 1235.581165 good output tokens/s per instance, two identical independent replicas would have a necessary arithmetic threshold for exceeding the new16-GPU reference by3% (2399.186728*1.03/2). This is only a screening threshold: routing, request distribution, startup, replication and inter-instance overhead can lower aggregate throughput. Any future16-GPU comparison needs a matched full N54 reference and combined traffic at the same workload definition.

The derived bundle preserves the exact8-GPU P4/D4 same-node placement, EAGLE3 steps2/topk1/draft3, unquantized draft, FP8 target, BF16 execution/KV policy, NIXL source, observer and all rank/device/native metadata and semantic gates. After the semantic gate passes, one full AIPerf confirmation runs with N24, fixed4000/200, seed2026, warmup60s, measurement120s, grace30s and the official TTFT3000ms / mean request ITL20ms Goodput rules. Raw per-request denominator and computed good output tokens/s are independently checked. Post-score sanity8/8 reference expects at least7/8 without regressions; generated12/12 retrieval is diagnostic only. Neither replaces the official full-set99%-reference accuracy test, which remains UNKNOWN.

The PBS limit is one exclusive H100 node,8 GPUs,30 minutes (maximum512SU). Absolute staged budgets reserve850s startup,240s semantic,300s score,250s post-score output checks and80s teardown, total1720s with80s allocation margin. If a stage cannot fit its declared time or a gate fails, the job ends with failure; no shortened profile is scored as a full result. Cost is an upper bound, not actual SU. Sampling covers allocation phases; score and diagnostic checks have explicit phase markers. Returned NIXL handles alone are not completion evidence; the semantic response remains required.

No official accuracy, leaderboard gain or16-GPU aggregate claim follows. A passing N24 test only licenses designing a separate matched two-replica experiment. Preserve every lower/failing result. No automatic retry or package promotion.
'''.replace('experiment225228','experiment 225228').replace('ranks,with','ranks, with').replace('from224560','from 224560').replace('control225227','control 225227').replace('measured2399','measured 2399').replace('with98','with 98').replace('smoke7','smoke 7').replace('retrieval12','retrieval 12').replace('Job222551','Job 222551').replace('P4/D4','P4/D4').replace('steps2','steps 2').replace('topk1','topk 1').replace('draft3','draft 3').replace('fixed4000','fixed 4000').replace('seed2026','seed 2026').replace('warmup60s','warmup 60 s').replace('measurement120s','measurement 120 s').replace('grace30s','grace 30 s').replace('TTFT3000ms','TTFT 3000 ms').replace('ITL20ms','ITL 20 ms').replace('sanity8/8','sanity 8/8').replace('atleast7/8','at least 7/8').replace('generated12/12','generated 12/12').replace('full-set99','full-set 99').replace('8GPU','8 GPU').replace('N24','N24').replace('H100node,8','H100 node, 8').replace('maximum512SU','maximum 512 SU').replace('startup,240','startup, 240').replace('semantic,300','semantic, 300').replace('score,250','score, 250').replace('checksand80s','checks and 80 s').replace('total1720s','total 1720 s').replace('margin.','margin.'))
(B/'README.md').write_text('# H100 equal-TP EAGLE3 full-workload feasibility\n\nStatus: PREPARED_NOT_SUBMITTED. Read [PLAN.md](PLAN.md) for the question, fixed workload, acceptance gates, cost cap and limits. The current result is the parent observer prerequisite at225228; this new full profile has no result.\n')
# Update manifest and immutable payload archive after all content is fixed.
for p in B.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in [*B.glob('*.sh'),*B.glob('*.pbs')]:subprocess.run(['bash','-n',str(p)],check=True)
files=sorted(p for p in B.rglob('*') if p.is_file() and p.name not in {'SHA256SUMS','payload.tar.gz'} and '__pycache__' not in p.parts)
(B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(B))+'\n' for p in files))
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
with tarfile.open(B/'payload.tar.gz','w:gz') as tar:
 for p in files+[B/'SHA256SUMS']:tar.add(p,arcname=str(p.relative_to(B)),recursive=False)
print('Derived bundle:',B)
print('Files:',len(files),'Parent listed files:',len(manifest),'Max SU:512')

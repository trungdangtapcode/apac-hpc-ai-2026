"""Prepare a review-only AI submission derived from current package and reviewed N64 evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

W = Path('/home/apacsc42/workspace')
R = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
O = W / 'submission-review/ai-update-20261028'
S = O / 'AI_Task/job_scripts'
SRC = O / 'inputs/AI_Task-before'

O.mkdir(parents=True, exist_ok=True)
owned_stage = O / 'AI_Task'
if owned_stage.exists():
    shutil.rmtree(owned_stage)
shutil.copytree(SRC, owned_stage)

# Derive primary worker flags from the successful native N64 arm while retaining
# this package's established Pyxis deployment and byte-exact measured base patch.
S = O / 'AI_Task/job_scripts'
run = R / 'runs/26766/submitted-payload'
for name in ('warm-topology.py', 'warmup_semantic.py'):
    shutil.copyfile(run / name, S / name)
worker = (run / 'worker.sh').read_text()
worker = worker.replace('export QWEN_ROLE_NAME="$name"\n', '')

start_draft = worker.find('if [[ ${QWEN_HAS_DRAFT:-0} == 1 ]]; then')
if start_draft >= 0:
    end_draft = worker.find('telemetry_flags=()', start_draft)
    worker = worker[:start_draft] + worker[end_draft:]
start = worker.find('telemetry_flags=()')
if start >= 0:
    end = worker.find('exec python3 -m sglang.launch_server', start)
    worker = worker[:start] + worker[end:]
worker = worker.replace('\"${telemetry_flags[@]}\" ', '')
(S / 'worker.sh').write_text(worker)

# Single portable Pyxis entry point, N64; semantic warmup is independently
# checked for both P/D paths, with absolute and per-command deadlines.
p = S / 'submit.sbatch'
t = p.read_text()
t = t.replace('set -euo pipefail\n', 'set -euo pipefail\nexport TRIPLEU_JOB_START_EPOCH=$(date +%s)\n')
t = t.replace('TRIPLEU_CONCURRENCY=62', 'TRIPLEU_CONCURRENCY=64')
p.write_text(t)
p = S / 'official-benchmark.sh'
t = p.read_text().replace('TRIPLEU_CONCURRENCY:-62', 'TRIPLEU_CONCURRENCY:-64')
p.write_text(t)
p = S / 'deploy-and-benchmark.sh'
t = p.read_text()
t = t.replace('SGLANG=${TRIPLEU_SGLANG_IMAGE:-/scratch/enroot-images/sglang-harbor.sqsh}', 'SGLANG=${TRIPLEU_SGLANG_IMAGE:-/scratch/enroot-images/sglang-harbor.sqsh}')
t = t.replace('MODEL=${TRIPLEU_MODEL_PATH:-/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8}', 'MODEL=${TRIPLEU_MODEL_PATH:-/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8}')
t = t.replace('local url=$1 deadline=$((SECONDS+600))', 'local url=$1 deadline=$((JOB_START_EPOCH+600))')
t = t.replace('if (( SECONDS>=deadline )); then', 'if (( $(date +%s)>=deadline )); then')
t = t.replace('mkdir -p "$ART"', 'mkdir -p "$ART"\nJOB_START_EPOCH=${TRIPLEU_JOB_START_EPOCH:?submit.sbatch must set the immutable job-start epoch}')
t = t.replace('# These are short, separate setup prompts, not the official dataset or seed.\n# Every scored request still traverses the main gateway and a prefill/decode pair.\nsrun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \\\n  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)" \\\n  env QWEN_PAIR_TIMEOUT=480 QWEN_PAIR_PARALLELISM=8 python3 "$TASK_SCRIPTS/warm-topology.py" "${IPS[0]}" "$ART" >"$ART/pair-warmup.log" 2>&1\necho "ALL_PAIRS_WARM after ${SECONDS}s"', '''# Two independent semantic P/D warmups must pass before official scoring.
# The absolute deadline is measured from job start, leaving four minutes for
# the official workload and cleanup inside the 17-minute allocation.
WARMUP_DEADLINE=$(( JOB_START_EPOCH + 780 ))
EXPERIMENT_ID="tripleu-n64-${SLURM_JOB_ID}-$(date +%s)-$$"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \\
  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)" \\
  env QWEN_EXPERIMENT_ID="$EXPERIMENT_ID" QWEN_WARMUP_DEADLINE_EPOCH="$WARMUP_DEADLINE" \\
  python3 "$TASK_SCRIPTS/warm-topology.py" "${IPS[0]}" "$ART" >"$ART/pair-warmup.log" 2>&1
python3 "$TASK_SCRIPTS/warmup_semantic.py" --check --endpoints "$ART/endpoints.tsv" \\
  --receipt-dir "$ART/pair-warmup-receipts" \\
  --run-token "$(python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest()[:32])' "$EXPERIMENT_ID")" \\
  >"$ART/pair-warmup-validation.json"
(( $(date +%s) - JOB_START_EPOCH <= 780 )) || { echo 'FATAL: semantic warmup exceeded the job-start deadline' >&2; exit 1; }
echo "ALL_PAIRS_SEMANTICALLY_WARM after ${SECONDS}s"''')
t = t.replace('run N62 once', 'run N64 once')
p.write_text(t)

config = json.loads((S/'config.json').read_text())
config.update(concurrency=[64], declared_concurrency=64, kv_dtype='auto (resolved BF16 in measured job 26766)',
              prefill_cuda_graph='breakable', decode_cuda_graph='full',
              decode_cuda_graph_batch_sizes=list(range(1,65)),
              prefill_chunk_size=8192, prefill_moe_runner_backend='deep_gemm',
              decode_moe_runner_backend='hpc_ops', decode_attention_backend='flashinfer',
              decode_allreduce_backend='mnnvl', router_policy='round_robin',
              speculative_decoding=False, dynamic_tokenization=False,
              measured_evidence_job='26766',
              benchmark_warmup_s=60, benchmark_measure_s=120, benchmark_grace_s=30,
              packaging_note='One-point N64 reproduced configuration. No sweep or post-score profiler in the primary job; semantic warmup validates both P/D routes before the official command.', semantic_warmup_deadline_from_submit_seconds=780, hard_allocation_seconds=1020)
config['decode_extra_flags'] = ['--cuda-graph-max-bs-decode','64','--cuda-graph-bs-decode',*map(str,range(1,65)),'--flashinfer-allreduce-fusion-backend','mnnvl','--decode-attention-backend','flashinfer','--moe-runner-backend','hpc_ops']
config['prefill_extra_flags'] = ['--chunked-prefill-size','8192','--moe-runner-backend','deep_gemm','--cuda-graph-backend-prefill','breakable']
config['transport_patch'] = 'hetero-tp-request-descriptors-v1 (base patch 912b7ed; no observer wrapper)'
config['transport_patch_metadata']['source'] = 'Measured and retained patch 912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f'
config['measured_evidence_job'] = '26766'
(S/'config.json').write_text(json.dumps(config, indent=2)+'\n')
env = json.loads((S/'environment.json').read_text())
env['serving_source_job'] = '26766 configuration; worker flags reproduced from successful N64 arm'
token_prov=S/'tokenizer-provenance.json'
if token_prov.exists():
    tp=json.loads(token_prov.read_text()); tp['cache']='hf-cache/models--Qwen--Qwen3-235B-A22B-Instruct-2507'; token_prov.write_text(json.dumps(tp,indent=2)+'\n')
env['precision'] = 'Published FP8 weights and BF16 activation; KV cache dtype requested auto and observed BF16 in measured job 26766'
env['transport_patch']['scope'] = 'Measured heterogeneous-TP NIXL request-descriptor patch 912b7ed; no profiler/observer wrapper in this package.'
(S/'environment.json').write_text(json.dumps(env, indent=2)+'\n')

# Compact evidence only: canonical raw exports, workload inputs, summaries,
# source provenance, per-role logs and small validation artifacts. Never copy
# private caches, weights, credential state, diagnostic traces, or profiles.
evidence = O/'AI_Task/logs/measured'
for job in ('25366','25373','25487','26766','26768','26770'):
    src = R/'runs'/job
    target = evidence/job
    target.mkdir(parents=True)
    for rel in ('summary.json','confirm/n64/client.log','config.json','endpoints.tsv','deadlines.txt','output-smoke.json','output-smoke.log','prefill-0.log','prefill-1.log','decode-0.log','router.log','pair-warmup.log','client-versions.txt','tokenizer-preflight.log','native-cleanup-before.jsonl'):
        f = src/rel
        if f.is_file():
            (target/rel).parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(f,target/rel)
    for rel in ('confirm/n64/artifacts/profile_export_aiperf.json','confirm/n64/artifacts/profile_export_aiperf.csv','confirm/n64/artifacts/profile_export.jsonl','confirm/n64/artifacts/inputs.json','confirm/n64/artifacts/phases/profiling/profile_export_aiperf.json','confirm/n64/artifacts/phases/warmup/profile_export_aiperf.json','confirm/n64/artifacts/logs/aiperf.log'):
        f=src/rel
        if f.is_file():
            (target/rel).parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(f,target/rel)
    for rel in ('submitted-payload/config.json','submitted-payload/placement.tsv','submitted-payload/SHA256SUMS','submitted-payload/nixl-patch-metadata.json','submitted-payload/model-config-binding.json','submitted-payload/asset-verification.json','submitted-payload/geometry-derivation.json','submitted-payload/SOURCE_PROVENANCE.json','submitted-payload/SOURCE_PARENT_PROVENANCE.json','submitted-payload/expected-input-config.json','submitted-payload/warm-topology.py','submitted-payload/warmup_semantic.py'):
        f=src/rel
        if f.is_file():
            name=Path(rel).name; (target/'submitted-payload').mkdir(exist_ok=True); shutil.copyfile(f,target/'submitted-payload'/name)

# Preserve the current H100 control as a separate-platform comparison.
h100root=R/'h100-review-225227-225228-20261026/curated-r2/h100-incumbent-n54-refresh-20261026/runs/225227.pbs111'
h100target=evidence/'h100/225227.pbs111'
for rel in ('config.json','client-versions.txt','confirm/n54/client.log','confirm/n54/artifacts/profile_export_aiperf.json','confirm/n54/artifacts/profile_export_aiperf.csv','confirm/n54/artifacts/profile_export.jsonl','confirm/n54/artifacts/logs/aiperf.log','output-smoke.json','long-context-check.json'):
    f=h100root/rel
    if f.is_file():
        dst=h100target/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
shutil.copyfile(R/'h100-review-225227-225228-20261026/review.json',h100target/'review-225227.json')

# Strict N64 review and the failed warmup review remain in the staged evidence.
for source,name in ((R/'h200-native-chunk-review-20261028/REVIEW.md','h200-native-chunk-review-20261028-REVIEW.md'),(R/'h200-tokenizer-warmup-repair-20261028/REVIEW.md','h200-tokenizer-warmup-failures-20261028-REVIEW.md'),(R/'h100-review-225227-225228-20261026/REVIEW.md','h100-review-225227-225228-20261026-REVIEW.md')):
    shutil.copyfile(source,evidence/name)

# Preserve the previous package report bytes under explicit historical names.
logs=O/'AI_Task/logs'
for old,new in (('README.md','historical-package-README-20261021.md'),('results.csv','historical-results-20261021.csv'),('results.json','historical-results-20261021.json'),('package-validation.json','historical-package-validation-20261021.json'),('replay-status.json','historical-replay-status-20261021.json')):
    f=logs/old
    if f.exists(): f.rename(logs/new)
logs.joinpath('README.md').write_text('''# AI submission evidence index\n\nThis directory preserves prior package evidence and adds the reviewed N64 records. The current primary point is described in `measured/latest-results.md`; full N64 source and performance reviews are retained beside the compact raw evidence. Earlier N62 results and validation outputs are historical, retained byte-for-byte under names ending in `20261021`. Do not read them as the current primary configuration.\n\nThe official full-set accuracy check against at least 99% of the organizer reference remains UNKNOWN. H100 and H200 scores are separate platform observations and are not direct matched comparisons.\n''')


latest = '''# Latest AI results and submission point\n\nUpdated 28 October 2026, Vietnam time. Primary submission is one N64 point on two H200 nodes: two TP4 prefill workers and one TP8/EP8 decode worker. The official FP8 checkpoint uses BF16 activation and KV dtype auto, resolved to BF16 in measured job 26766, DeepGEMM prefill with chunk8192 and breakable prefill graphs, HPC-Ops/FlashInfer/MNNVL decode with full graphs 1–64, round-robin routing, and no EAGLE or dynamic tokenization. The deployment remains a conventional Slurm/Pyxis job.\n\n| Evidence | Good output throughput (tokens/s) | Joint SLA pass | Requests | Errors/cancellations | Interpretation |\n|---|---:|---:|---:|---:|---|\n|25366, N64|3044.489701|98.633018%|1902; 1876 good|0 / 0|Historical full observation|\n|25373, N64|3044.074628|98.632299%|1901; 1875 good|0 / 0|Historical full observation|\n|25487, N64|3044.637094|98.632299%|1901; 1875 good|0 / 0|Historical full observation|\n|Historical mean|3044.400475|—|—|—|Three-run mean; local reference only|\n|26766, N64|3045.501509|98.580442%|1902; 1875 good|0 / 0|New native-runtime full pass; reproduces historical level, not a matched speedup|\n|26768, chunk10240|3034.088251|98.523985%|1897; 1869 good|0 / 0|Valid full run; slower than chunk8192|\n|26770, chunk12288|3020.943099|98.310454%|1894; 1862 good|0 / 0|Valid full run; slower and higher p95 TTFT|\n\nAll full profiles used closed-loop N64, 60 s warmup, 120 s measurement, 30 s grace, 4000 input tokens, 200 output tokens, seed 2026, and cold prefixes. Output throughput equals AIPerf Goodput requests/s × 200 output tokens. The selected 26766 run passed the local full protocol, smoke 7/8 with no regression and retrieval 12/12. The three newer chunk arms had 24 per-role hardware/server samples; selected resource metrics and limitations are described in the retained review. Missing telemetry is not inferred as zero.\n\nJobs 26849/26851/26853 failed during outer warmup before AIPerf; they have no performance measurements and are not candidates. Jobs 26947/26949/26951/26953 remain queued/uncertain per the dated handoff and are not represented as results.\n\nThe official full-set accuracy check against at least 99% of the organizer reference remains UNKNOWN. Local smoke/retrieval results do not certify it. H100 225227 scored 2399.186728 good output tokens/s; retained H100 222048 scored 2433.019859. These are separate-platform results and are not mixed into the H200 comparison.\n\nSee the H200 and H100 review files and per-job compact artifacts under `measured/` for exact metrics, raw exports, input configuration, runtime logs and provenance.\n'''
(evidence/'latest-results.md').write_text(latest)

# README rewritten to identify N64 and portable invocation while retaining setup.
readme = (S/'README.md').read_text()
readme = readme.replace('N62', 'N64').replace('62', '64')
readme = readme.replace('Evidence and limits', 'Evidence and limits')
readme = readme.replace('job 24915', 'job 26766')
readme = readme.replace('Its independent repeat 24964 was still pending at packaging.', 'The 26766 native-runtime run reproduces the historical N64 score level; this is not a matched runtime gain.')
readme = readme.replace('3022.034919', '3045.501509').replace('1860/1884', '1875/1902').replace('98.726115%', '98.580442%')
readme = readme.replace('the independently repeated N64 result', 'the independently repeated N64 result')
readme = readme.replace('The official published FP8 target, KV cache dtype auto, resolved BF16 in measured job 26766 and request-scoped NIXL patch are', 'The official published FP8 target runs with BF16 activations. The default KV cache dtype resolved to BF16 in measured job 26766. The request-scoped NIXL patch is')
readme = readme.replace('The organiser full-set accuracy check (at least 99% of reference) remains unverified.', 'The organiser full-set accuracy check (at least 99% of reference) remains UNKNOWN.')
readme = readme.replace('absolute 12-minute deadline inside the 17-minute allocation', 'absolute 13-minute deadline measured from job start inside the 17-minute allocation')
readme = readme.replace('run N64 once', 'run N64 once')
readme += '''\n\n## Semantic warmup and evidence update\n\nBefore scoring, the primary job starts two independent P/D routers and sends one semantic request through each route. It validates both response bodies and writes replayable receipts tied to the endpoint inventory and current run token. The warmup has a 13-minute absolute deadline from submit start, leaving at least four minutes for scoring and cleanup, and fails closed on a missing, stale or invalid receipt. The official AIPerf command is invoked once after both paths pass.\n\nThe selected primary point is reproduced by H200 job 26766 at 3045.501509 good output tokens/s. See `../logs/measured/latest-results.md` for comparison with the historical three-run N64 mean, losing larger-chunk controls, run limits and accuracy status. The measured patch is the base 912b7 NIXL change; no diagnostic observer wrapper is shipped.\n'''
(S/'README.md').write_text(readme)

# Regenerate deterministic hashes for all submission scripts.
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in sorted(S.rglob('*')) if p.is_file() and p.name!='SHA256SUMS']
(S/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(S)}\n' for p in files))

# Package evidence index; it hashes only selected safe AI evidence.
manifest=[]
for item in sorted(evidence.rglob('*')):
    if item.is_file(): manifest.append({'path':str(item.relative_to(O/'AI_Task')),'bytes':item.stat().st_size,'sha256':sha(item)})
(O/'evidence-manifest.json').write_text(json.dumps({'schema':'ai-submission-evidence-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected_jobs':['25366','25373','25487','26766','26768','26770','225227.pbs111'],'omitted':['model weights','private caches and authentication state','large profiler traces and diagnostic profiles','failed warmup-only raw trees'],'files':manifest},indent=2)+'\n')

# Rebuild copied AI_Task log manifests because evidence files were added and
# older indexes were renamed to historical snapshots. Paths stay team-relative.
log_files=[p for p in sorted((O/'AI_Task').rglob('*')) if p.is_file() and p.name not in {'SHA256SUMS','FILE_MANIFEST.json'}]
logs=O/'AI_Task/logs'
(logs/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(O)}\n' for p in log_files))
(logs/'FILE_MANIFEST.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paths_relative_to_team_directory':True,'files':[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in log_files]},indent=2)+'\n')
(O/'PREPARATION.json').write_text(json.dumps({'schema':'ai-submission-preparation-v1','prepared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_stage':'AI_Task','source_package':str(SRC),'primary_evidence_job':'26766','selected_h200_jobs':['25366','25373','25487','26766','26768','26770'],'h100_context_jobs':['225227.pbs111','222048.pbs111'],'primary_configuration':{'concurrency':64,'topology':'P4+P4/D8 EP8','prefill_chunk_size':8192,'prefill_graph':'breakable','decode_graph':'full 1..64','activation':'BF16','kv':'auto; resolved BF16 in measured job 26766','router':'round_robin','speculation':False,'dynamic_tokenization':False},'limitations':['Official full-set accuracy remains UNKNOWN.','Package is staged for review; not published or submitted.','H200 native-runtime score is a reproduction of historical N64 level, not a matched speedup.']},indent=2)+'\n')
print(O/'AI_Task')

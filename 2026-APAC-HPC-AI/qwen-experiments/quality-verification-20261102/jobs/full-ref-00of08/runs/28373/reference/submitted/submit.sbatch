#!/usr/bin/env bash
# Local quality reference only. This is not the ranked Basic entry.
# Two independent, stock SGLang FP8 replicas: TP=8 colocated on one node each.
# EP8 is required for the official block-FP8 layout; no patch, PD or backend tuning.
# Slurm uses the existing 16-H200, two-node, 17-minute Firmus allocation.
# Create LOG_DIR before sbatch; output/error are written there by Slurm.
#SBATCH --job-name=qrf00
#SBATCH --partition=hpcai
#SBATCH --nodes=2
#SBATCH --time=00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH --output=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/jobs/full-ref-00of08/logs/%j.out
#SBATCH --error=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/jobs/full-ref-00of08/logs/%j.err

set -euo pipefail
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

: "${SLURM_SUBMIT_DIR:?Submit from the frozen full-reference shard directory}"
SCRIPT_DIR=$SLURM_SUBMIT_DIR
PROJECT_ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
TASK_ROOT=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102
PREPARED_DIR=${TRIPLEU_QUALITY_PREPARED_DIR:-$TASK_ROOT/prepared-4k}
CORPUS=$PREPARED_DIR/compiled-corpus.jsonl
PREPARE_MANIFEST=$PREPARED_DIR/prepare-manifest.json
SHARD_MANIFEST=$TASK_ROOT/full-tools/full_shard_membership.json
RUNS_ROOT=$TASK_ROOT/jobs/full-ref-00of08/runs
SGLANG=${TRIPLEU_SGLANG_IMAGE:-/scratch/enroot-images/sglang-harbor.sqsh}
AIPERF=${TRIPLEU_AIPERF_IMAGE:-/scratch/enroot-images/aiperf.sqsh}
MODEL=${TRIPLEU_MODEL_PATH:-/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8}
START_EPOCH=$(date +%s)
READY_DEADLINE=$((START_EPOCH + 600))
EVALUATION_DEADLINE=$((START_EPOCH + 950))
MODEL_NAME=qwen

: "${SLURM_JOB_ID:?Submit this file with sbatch}"
: "${SLURM_SUBMIT_DIR:?Run sbatch from the full-reference shard directory}"
[[ -d "$TASK_ROOT/jobs/full-ref-00of08/logs" ]] || {
  echo "FATAL: create $TASK_ROOT/jobs/full-ref-00of08/logs before submission" >&2
  exit 1
}

JOB_DIR=$RUNS_ROOT/$SLURM_JOB_ID
ART=$JOB_DIR/reference
LOCAL_HOME=$TASK_ROOT/jobs/full-ref-00of08/runtime-home/$SLURM_JOB_ID
mkdir -p "$ART" "$LOCAL_HOME/replica-0" "$LOCAL_HOME/replica-1" "$LOCAL_HOME/router" "$LOCAL_HOME/client"

(cd "$TASK_ROOT" && sha256sum --check frozen-full8/SHA256SUMS) >"$ART/frozen-inputs-check.log"

# Fail before model startup if the offline evaluator's immutable paired inputs are absent.
for required in "$CORPUS" "$PREPARE_MANIFEST" "$SHARD_MANIFEST" "$SGLANG" "$AIPERF" "$MODEL/config.json"; do
  [[ -r "$required" ]] || { echo "FATAL: required input is not readable: $required" >&2; exit 1; }
done

# Freeze only the launcher, probe, client, and small provenance inputs; never copy weights/caches.
mkdir -p "$ART/submitted"
cp "$SCRIPT_DIR/submit.sbatch" "$SCRIPT_DIR/semantic_probe.py" "$ART/submitted/"
cp "$TASK_ROOT/client/quality_client.py" "$ART/submitted/"
cp "$MODEL/config.json" "$MODEL/tokenizer_config.json" "$MODEL/generation_config.json" \
  "$MODEL/tokenizer.json" "$MODEL/model.safetensors.index.json" "$ART/"
cp "$PROJECT_ROOT/corpus-tools/manifest.json" "$ART/dataset-manifest.json"

mapfile -t NODES < <(scontrol show hostnames "$SLURM_JOB_NODELIST")
[[ ${#NODES[@]} -eq 2 ]] || { echo "FATAL: expected 2 nodes, got ${#NODES[@]}" >&2; exit 1; }
node_ip() { getent ahostsv4 "$1" | awk 'NR==1 {print $1}'; }
IP0=$(node_ip "${NODES[0]}")
IP1=$(node_ip "${NODES[1]}")
[[ -n "$IP0" && -n "$IP1" ]] || { echo "FATAL: failed to resolve allocated node IPs" >&2; exit 1; }

PIDS=()
cleanup() {
  local pid
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null || :; done
  for pid in "${PIDS[@]}"; do wait "$pid" 2>/dev/null || :; done
}
trap cleanup EXIT INT TERM

mounts() {
  local role=$1
  printf '%s' "/scratch:/scratch,$LOCAL_HOME/$role:$HOME,$TASK_ROOT:$TASK_ROOT,/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/mmlu-pro-local-quality-20261024:/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/mmlu-pro-local-quality-20261024:ro"
}

record_provenance() {
  python3 - "$ART" "$MODEL" "$SGLANG" "$AIPERF" "$CORPUS" "$PREPARE_MANIFEST" "$SHARD_MANIFEST" "${NODES[*]}" <<'PY'
import hashlib, json, os, pathlib, sys, time
out, model, sglang, aiperf, corpus, manifest, shard_manifest, nodes = sys.argv[1:]
def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()
def file(path):
    p = pathlib.Path(path)
    st = p.stat()
    return {'path': str(p), 'size_bytes': st.st_size, 'mtime_epoch': st.st_mtime, 'sha256': sha(p)}
weights = sorted(pathlib.Path(model).glob('model-*-of-*.safetensors'))
doc = {
    'study': 'internal paired local quality comparison; not organizer certification',
    'reference_type': 'two independent stock SGLang colocated replicas, TP8/EP8 per H200 node',
    'nodes': nodes.split(), 'model_path': model,
    'model_files': [file(pathlib.Path(model) / n) for n in ('config.json','tokenizer_config.json','generation_config.json','model.safetensors.index.json')],
    'weight_shards': [{'name': p.name, 'size_bytes': p.stat().st_size, 'mtime_epoch': p.stat().st_mtime} for p in weights],
    'weight_shard_hashes': 'not computed; 230 GB of weights are not reread solely for hashing inside this 17-minute allocation',
    'images': [{'path': p, 'size_bytes': os.stat(p).st_size, 'mtime_epoch': os.stat(p).st_mtime} for p in (sglang, aiperf)],
    'client_source': file(pathlib.Path(corpus).parent.parent/'client/quality_client.py'),
    'corpus': file(corpus), 'prepare_manifest': file(manifest), 'shard_membership': file(shard_manifest),
    'slurm_job_id': os.environ.get('SLURM_JOB_ID'),
    'slurm_job_start_epoch': int(os.environ['TRIPLEU_JOB_START_EPOCH']),
    'runtime_options': {'served_model':'qwen','dtype':'bfloat16','tp_size':8,'context_length':8192,'mem_fraction_static':0.90,'ep_size':8,'transport_patch':'none','disaggregation':'disabled','custom_kernel_or_graph_flags':'none'},
    'evaluation_options': {'concurrency':64,'timeout_seconds':120,'deadline_epoch':int(os.environ['TRIPLEU_EVALUATION_DEADLINE']),'deadline_margin_seconds':10,'phase':'full-quality-shard','role':'reference','shard_index':0,'shard_count':8,'rows':1504,'selection':'stable corpus row order modulo 8'},
    'timestamp_epoch': time.time(),
}
with open(pathlib.Path(out)/'reference-provenance.json','x') as f:
    json.dump(doc, f, indent=2, sort_keys=True); f.write('\n')
PY
}

export TRIPLEU_JOB_START_EPOCH=$START_EPOCH TRIPLEU_EVALUATION_DEADLINE=$EVALUATION_DEADLINE
record_provenance
printf 'START job=%s nodes=%s start_epoch=%s\n' "$SLURM_JOB_ID" "${NODES[*]}" "$START_EPOCH" | tee "$ART/job-start.log"
cp "$SHARD_MANIFEST" "$ART/shard-membership.json"
printf 'FULL_SHARD_BEGIN role=reference shard=00/08 rows=1504 concurrency=64 TP8/EP8 model=%s\n' "$MODEL" | tee -a "$ART/job-start.log"

start_worker() {
  local role=$1 node=$2 ip=$3 port=$4
  srun --exact --overlap -N1 -n1 -w "$node" --gres=gpu:8 --cpus-per-task=64 \
    --container-image="$SGLANG" --container-mounts="$(mounts "$role")" \
    bash -lc '
      set -euo pipefail
      name=$1; port=$2; model=$3; expected="$4"
      echo "WORKER_START name=$name host=$(hostname) visible_gpus=${CUDA_VISIBLE_DEVICES:-unset}"
      nvidia-smi -L
      nvidia-smi --query-gpu=name,uuid,pci.bus_id,memory.total,memory.used,utilization.gpu --format=csv
      python3 - "$expected" <<'"'"'PATCH'"'"'
import hashlib, pathlib, sys
p=pathlib.Path("/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py")
actual=hashlib.sha256(p.read_bytes()).hexdigest()
expected=sys.argv[1]
print("UPSTREAM_CONN_SHA256",actual,flush=True)
if actual != expected: raise SystemExit("unexpected SGLang conn.py; stock reference image pin mismatch")
PATCH
      export TRITON_CACHE_DIR="/tmp/quality-ref-$name/triton" TORCHINDUCTOR_CACHE_DIR="/tmp/quality-ref-$name/inductor"
      mkdir -p "$TRITON_CACHE_DIR" "$TORCHINDUCTOR_CACHE_DIR"
      python3 - <<'"'"'VERSIONS'"'"'
from importlib.metadata import PackageNotFoundError,version
for p in ("sglang","torch","transformers"):
 try: print("PACKAGE",p,version(p))
 except PackageNotFoundError: print("PACKAGE",p,"not-installed")
VERSIONS
      exec python3 -m sglang.launch_server --model-path "$model" --served-model-name qwen \
        --trust-remote-code --tp-size 8 --ep-size 8 --context-length 8192 --dtype bfloat16 \
        --mem-fraction-static 0.90 --host 0.0.0.0 --port "$port"
    ' reference-worker "$role" "$port" "$MODEL" 28da79ad06baa8c1b725bc98983ca570f82a73b49439873831505ab7f1eef601 \
    >"$ART/$role.log" 2>&1 &
  PIDS+=("$!")
  printf '%s\t%s\t%s\n' "$role" "$ip" "$port" >> "$ART/endpoints.tsv"
}

: > "$ART/endpoints.tsv"
start_worker replica-0 "${NODES[0]}" "$IP0" 30100
start_worker replica-1 "${NODES[1]}" "$IP1" 30101

check_child_pids() {
  local pid
  for pid in "${PIDS[@]}"; do
    kill -0 "$pid" 2>/dev/null || { echo "FATAL: launch step $pid exited before readiness" >&2; return 1; }
  done
}
wait_worker() {
  local name=$1 base=$2 pending="$ART/$1-models.pending"
  while (( $(date +%s) < READY_DEADLINE )); do
    check_child_pids
    if curl -sf --max-time 2 "$base/health" -o /dev/null && \
       curl -sf --max-time 2 "$base/v1/models" -o "$pending" && \
       python3 - "$pending" "$MODEL_NAME" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); rows=d.get('data') if isinstance(d,dict) else None
raise SystemExit(0 if isinstance(rows,list) and any(isinstance(x,dict) and x.get('id')==sys.argv[2] for x in rows) else 1)
PY
    then
      mv "$pending" "$ART/$name-models.json"
      echo "READY $name url=$base elapsed=$(( $(date +%s) - START_EPOCH ))s" | tee -a "$ART/job-start.log"
      return 0
    fi
    sleep 2
  done
  echo "FATAL: $name not healthy and registered before 600-second startup deadline" >&2
  return 1
}
wait_worker replica-0 "http://${IP0}:30100"
wait_worker replica-1 "http://${IP1}:30101"

# Verify router interface from the pinned local source snapshot before starting it.
sha256sum "$PROJECT_ROOT/source/router_args.py" "$PROJECT_ROOT/source/launch_router.py" > "$ART/router-source.sha256"
srun --exact --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$SGLANG" --container-mounts="$(mounts router)" \
  python3 -m sglang_router.launch_router --worker-urls "http://${IP0}:30100" "http://${IP1}:30101" \
    --policy round_robin --host 0.0.0.0 --port 8000 >"$ART/router.log" 2>&1 &
PIDS+=("$!")

wait_router() {
  local base="http://${IP0}:8000"
  while (( $(date +%s) < READY_DEADLINE )); do
    check_child_pids
    if curl -sf --max-time 2 "$base/health" -o /dev/null && \
       curl -sf --max-time 2 "$base/v1/models" -o "$ART/router-models.pending" && \
       python3 - "$ART/router-models.pending" "$MODEL_NAME" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); rows=d.get('data') if isinstance(d,dict) else None
raise SystemExit(0 if isinstance(rows,list) and any(isinstance(x,dict) and x.get('id')==sys.argv[2] for x in rows) else 1)
PY
    then mv "$ART/router-models.pending" "$ART/router-models.json"; echo "ROUTER_READY after $(( $(date +%s)-START_EPOCH ))s"; return 0; fi
    sleep 2
  done
  echo 'FATAL: router did not become healthy and register qwen by startup deadline' >&2
  return 1
}
wait_router

python3 "$SCRIPT_DIR/semantic_probe.py" "http://${IP0}:30100" "$ART/semantic-replica-0.json"
python3 "$SCRIPT_DIR/semantic_probe.py" "http://${IP1}:30101" "$ART/semantic-replica-1.json"
python3 "$SCRIPT_DIR/semantic_probe.py" "http://${IP0}:8000" "$ART/semantic-router.json"

(( $(date +%s) + 140 < EVALUATION_DEADLINE )) || {
  echo 'FATAL: insufficient time remains for the bounded 1,504-question full shard' >&2
  exit 1
}

echo "FULL_SHARD_CLIENT_START role=reference shard=00/08 rows=1504 concurrency=64 deadline_epoch=$EVALUATION_DEADLINE" | tee -a "$ART/job-start.log"
srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \
  --container-image="$AIPERF" --container-mounts="$(mounts client)" \
  bash -lc '
    set -euo pipefail
    python3 - <<'"'"'VERSIONS'"'"'
from importlib.metadata import PackageNotFoundError,version
for p in ("aiperf","transformers","tokenizers"):
 try: print("CLIENT_PACKAGE",p,version(p))
 except PackageNotFoundError: print("CLIENT_PACKAGE",p,"not-installed")
VERSIONS
    exec python3 "$1" run --corpus "$2" --prepare-manifest "$3" --shard-index "$8" --shard-count 8 \
      --base-url "$5" --model qwen --out "$6" --concurrency 64 --timeout 120 \
      --deadline-epoch "$7" --deadline-margin 10
  ' quality-client "$TASK_ROOT/client/quality_client.py" "$CORPUS" "$PREPARE_MANIFEST" "$SHARD_MANIFEST" \
    "http://${IP0}:8000/v1" "$ART/evaluation" "$EVALUATION_DEADLINE" 0 \
  >"$ART/client.log" 2>&1

python3 "$TASK_ROOT/review_run_gate.py" "$ART/evaluation" >"$ART/measurement-validity.json"

echo "FULL_SHARD_REFERENCE_COMPLETE job=$SLURM_JOB_ID elapsed=$(( $(date +%s)-START_EPOCH ))s" | tee -a "$ART/job-start.log"

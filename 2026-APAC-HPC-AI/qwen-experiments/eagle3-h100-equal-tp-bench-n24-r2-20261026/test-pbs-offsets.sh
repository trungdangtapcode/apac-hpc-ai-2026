#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")" && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
printf 'h100n01\nh100n01\nh100n01\nh100n01\nh100n01\nh100n01\nh100n01\nh100n01\n' > "$TMP/nodefile"
export PBS_NODEFILE="$TMP/nodefile" QWEN_BUNDLE="$ROOT" APAC_PBS_DRY_RUN=1
source "$ROOT/pbs-shim.sh"
P=$(srun -N1 -n1 -w h100n01 --gres=gpu:4 --cpus-per-task=32 --container-image=fixture --container-mounts=/fixture bash "$ROOT/worker.sh" prefill-0 30100 /fixture/model 4)
D=$(srun -N1 -n1 -w h100n01 --gres=gpu:4 --cpus-per-task=32 --container-image=fixture --container-mounts=/fixture bash "$ROOT/worker.sh" decode-0 30200 /fixture/model 4)
python3 - "$P" "$D" <<'PYJSON'
import json,sys
p,d=map(json.loads,sys.argv[1:])
assert p['node']==d['node']==0
assert p['gpu_indices']==[0,1,2,3],p
assert d['gpu_indices']==[4,5,6,7],d
assert p['command'][2]=='prefill-0' and d['command'][2]=='decode-0'
print('PBS SHIM OFFSET FIXTURE PASS: one node, P GPUs 0-3, D GPUs 4-7')
PYJSON

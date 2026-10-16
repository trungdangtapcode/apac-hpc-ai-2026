#!/bin/bash
# Adapt the frozen Slurm orchestration calls to PBS task launch and Singularity.
scontrol() {
  [[ ${1:-} == show && ${2:-} == hostnames ]] || return 2
  awk '!seen[$0]++' "$PBS_NODEFILE"
}
srun() {
  local host= image= mounts= gpu=0 cpus=4 node=-1 role= offset=0 index=0
  local -a command=() nodes=()
  while (($#)); do
    case $1 in
      -w) host=$2; shift 2;;
      --container-image=*) image=${1#*=}; shift;;
      --container-mounts=*) mounts=${1#*=}; shift;;
      --gres=gpu:*) gpu=${1##*:}; shift;;
      --cpus-per-task=*) cpus=${1#*=}; shift;;
      --exact|--overlap|-N*|-n*) shift;;
      *) command=("$@"); break;;
    esac
  done
  mapfile -t nodes < <(awk '!seen[$0]++' "$PBS_NODEFILE")
  for index in "${!nodes[@]}"; do [[ ${nodes[$index]} == "$host" ]] && node=$index; done
  [[ $node != -1 && -n $image && ${#command[@]} != 0 ]] || return 2
  if ((gpu>0)); then
    # The unchanged source command is: bash ART/worker.sh ROLE PORT MODEL TP ...
    role=${command[2]}
    offset=$(awk -v role="$role" -v node="$node" '
      $1==role {print total+0;found=1;exit} $2==node {total+=$3}
      END {if(!found)exit 2}' "$QWEN_BUNDLE/placement.tsv") || return 2
  fi
  local env_json
  env_json=$(python3 -c 'import os,json;print(json.dumps({k:v for k,v in os.environ.items() if k.startswith("QWEN_")}))')
  if [[ ${APAC_PBS_DRY_RUN:-0} == 1 ]]; then
    python3 - "$node" "$offset" "$gpu" "$cpus" "${command[@]}" <<'PY'
import json,sys
print(json.dumps(dict(node=int(sys.argv[1]),gpu_indices=list(range(int(sys.argv[2]),int(sys.argv[2])+int(sys.argv[3]))),cpus=int(sys.argv[4]),command=sys.argv[5:])))
PY
    return
  fi
  pbsdsh -n "$node" -- /bin/bash -l "$QWEN_BUNDLE/pbs-container.sh" \
    "$image" "$mounts" "$offset" "$gpu" "$cpus" "$env_json" "${command[@]}"
}
export -f srun scontrol

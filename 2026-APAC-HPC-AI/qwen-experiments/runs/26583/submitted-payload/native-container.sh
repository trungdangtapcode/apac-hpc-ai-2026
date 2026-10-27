#!/usr/bin/env bash
# Run as the allocated Slurm user; keep Slurm CPU/GPU cgroups and source mounts.
set -euo pipefail
umask 077
image=$1
mount_csv=$2
shift 2
[[ $# -gt 0 && -f "$image" ]] || exit 2
export ENROOT_DATA_PATH="/tmp/apacsc42-native-${SLURM_JOB_ID:?}-${SLURM_STEP_ID:?}"
export ENROOT_MAX_PROCESSORS=8
export NVIDIA_DRIVER_CAPABILITIES=compute,utility
# NVIDIA CLI in the allocated step accepts the cgroup-visible CUDA indices; retain global IDs as evidence.
if [[ -z ${SLURM_STEP_GPUS:-} || -z ${CUDA_VISIBLE_DEVICES:-} || ${CUDA_VISIBLE_DEVICES:-} == NoDevFiles ]]; then
  export NVIDIA_VISIBLE_DEVICES=void
  export CUDA_VISIBLE_DEVICES=''
else
  export NVIDIA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES"
fi
args=(--root --rw)
IFS=, read -r -a mounts <<< "$mount_csv"
for entry in "${mounts[@]}"; do
  IFS=: read -r src dst options <<< "$entry"
  dst=${dst:-$src}
  [[ -e "$src" ]] || { echo "FATAL: missing native mount source: $src" >&2; exit 1; }
  if [[ -d "$src" ]]; then kind=dir; else kind=file; fi
  options=${options:-rw}
  [[ "$options" == ro || "$options" == rw ]] || exit 2
  args+=(--mount "$src:$dst:none:x-create=$kind,bind,$options,nosuid,nodev")
done
while IFS= read -r name; do
  case "$name" in QWEN_*|SLURM_*|CUDA_VISIBLE_DEVICES|NVIDIA_VISIBLE_DEVICES|NVIDIA_DRIVER_CAPABILITIES|HOME)
    args+=(--env "$name=${!name}");;
  esac
done < <(compgen -e)
if [[ ${APAC_NATIVE_DRY_RUN:-0} == 1 ]]; then
  python3 - "$NVIDIA_VISIBLE_DEVICES" "${CUDA_VISIBLE_DEVICES:-}" "${args[@]}" --COMMAND-- "$@" <<'PY'
import json,sys
print(json.dumps({'runtime_visible_gpu_ids':sys.argv[1],'cuda_mask':sys.argv[2],'enroot_args_and_command':sys.argv[3:]}))
PY
  exit 0
fi
[[ ! -e "$ENROOT_DATA_PATH" && ! -L "$ENROOT_DATA_PATH" ]] || exit 1
mkdir -m 700 "$ENROOT_DATA_PATH"
read -r bs blocks < <(stat -f -c '%S %a' "$ENROOT_DATA_PATH")
(( bs*blocks >= 120*1024*1024*1024 )) || { echo 'FATAL: insufficient local rootfs space' >&2; exit 1; }
child=''
cleanup() {
  result=$?
  trap - EXIT INT TERM
  [[ -z "$child" ]] || kill -TERM "$child" 2>/dev/null || :
  enroot remove --force rootfs >/dev/null 2>&1 || :
  rmdir "$ENROOT_DATA_PATH" 2>/dev/null || :
  exit "$result"
}
trap cleanup EXIT
trap 'exit 143' TERM INT
printf 'NATIVE_ALLOCATED_CONTAINER host=%s data=%s runtime_visible=%s cuda=%s image=%s\n' "$(hostname)" "$ENROOT_DATA_PATH" "$NVIDIA_VISIBLE_DEVICES" "${CUDA_VISIBLE_DEVICES:-}" "$image"
enroot create --name rootfs "$image"
enroot start "${args[@]}" rootfs "$@" &
child=$!
wait "$child"

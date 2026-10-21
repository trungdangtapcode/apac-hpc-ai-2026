#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: entry.sh RANK ARTIFACT_DIR SHARED_SCRATCH_DIR" >&2
  exit 2
fi

rank=$1
artdir=$2
sharedir=$3
[[ "$rank" == 0 || "$rank" == 1 ]] || { echo "rank must be 0 or 1" >&2; exit 2; }
mkdir -p "$artdir" "$sharedir"
chmod 700 "$sharedir"

# Match the native SGLang worker's active InfiniBand autodetection exactly.
ucx_ib=$(for device in /sys/class/infiniband/*; do
  [[ -e "$device/ports/1/link_layer" ]] || continue
  [[ "$(cat "$device/ports/1/link_layer" 2>/dev/null)" == InfiniBand ]] || continue
  [[ "$(cat "$device/ports/1/state" 2>/dev/null)" == "4: ACTIVE" ]] || continue
  printf '%s:1\n' "$(basename "$device")"
done | paste -sd,)
[[ -n "$ucx_ib" ]] || { echo "FATAL: no active InfiniBand port" >&2; exit 1; }
export UCX_NET_DEVICES="$ucx_ib"
export UCX_POSIX_USE_PROC_LINK=n

echo "NIXL_NATIVE_REGISTRATION_PROBE rank=$rank host=$(hostname) ib=$UCX_NET_DEVICES gpu=${CUDA_VISIBLE_DEVICES:-unset}"
exec python3 "$(dirname "$0")/native_probe.py" \
  --rank "$rank" --art "$artdir" --exchange-dir "$sharedir"

#!/bin/bash
set -euo pipefail
ucx_ib=$(for device in /sys/class/infiniband/*; do
 [[ $(cat "$device/ports/1/link_layer" 2>/dev/null) == InfiniBand ]] || continue
 [[ $(cat "$device/ports/1/state" 2>/dev/null) == '4: ACTIVE' ]] || continue
 printf '%s:1\n' "$(basename "$device")"
done | sort | paste -sd,)
[[ -n $ucx_ib ]] || exit 1
export UCX_NET_DEVICES="$ucx_ib" UCX_POSIX_USE_PROC_LINK=n
exec python3 -B /research/serving-tuning-11/s68-h200-nixl-four-role-probe/probe.py --role "$1" --art "$2" --exchange "$3" --deadline "$4"

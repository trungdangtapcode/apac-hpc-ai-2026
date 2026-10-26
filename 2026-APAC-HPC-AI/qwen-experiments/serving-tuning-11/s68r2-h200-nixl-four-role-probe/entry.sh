#!/bin/bash
set -euo pipefail
ucx_ib=$(for device in /sys/class/infiniband/*; do
 [[ $(cat "$device/ports/1/link_layer" 2>/dev/null) == InfiniBand ]] || continue
 [[ $(cat "$device/ports/1/state" 2>/dev/null) == '4: ACTIVE' ]] || continue
 printf '%s:1\n' "$(basename "$device")"
done | sort | paste -sd,)
[[ -n $ucx_ib ]] || exit 1
export UCX_NET_DEVICES="$ucx_ib" UCX_POSIX_USE_PROC_LINK=n
python3 - <<'PYNATIVE'
import hashlib
from pathlib import Path
p=Path('/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py')
assert hashlib.sha256(p.read_bytes()).hexdigest()=='912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f', 'effective native source mount mismatch'
print('NATIVE_SOURCE_MOUNT_VERIFIED',flush=True)
PYNATIVE
exec python3 -B /research/serving-tuning-11/s68r2-h200-nixl-four-role-probe/probe.py --role "$1" --art "$2" --exchange "$3" --deadline "$4"

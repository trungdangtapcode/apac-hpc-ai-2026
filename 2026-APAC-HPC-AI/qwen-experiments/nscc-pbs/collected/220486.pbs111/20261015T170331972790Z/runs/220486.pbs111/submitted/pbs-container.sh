#!/bin/bash -l
set -euo pipefail
image=$1; mounts=$2; offset=$3; count=$4; cpus=$5; env_json=$6
shift 6
module load singularity/4.1.5
runner_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cpu_list=$(python3 - "$offset" "$cpus" <<'PY'
import os,sys
available=sorted(os.sched_getaffinity(0));start=int(sys.argv[1])*8;count=int(sys.argv[2])
assert start+count<=len(available),(available,start,count)
print(','.join(map(str,available[start:start+count])))
PY
)
gpu_list=$(python3 - "$offset" "$count" <<'PY'
import sys
print(','.join(map(str,range(int(sys.argv[1]),int(sys.argv[1])+int(sys.argv[2])))))
PY
)
# The raw Enroot squashfs has no Singularity environment scripts. Use an
# explicit exec wrapper; SINGULARITYENV_* alone did not propagate GPU/libcuda.
exec taskset -c "$cpu_list" singularity exec --nv --cleanenv --no-home \
  --bind "$mounts" "$image" /usr/bin/env \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  LD_LIBRARY_PATH=/.singularity.d/libs:/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:/usr/local/lib \
  python3 "$runner_dir/pbs-exec.py" "$gpu_list" "$env_json" "$@"

#!/bin/bash
set -euo pipefail
image=$1; mounts=$2; offset=$3; count=$4; cpus=$5; env_json=$6
shift 6
if ! type module >/dev/null 2>&1; then
  source /cm/local/apps/environment-modules/4.5.3/init/bash
fi
module load singularity/4.1.5
runner_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cpu_list=$(python3 - "$offset" "$cpus" <<'PY'
import os,sys
available=sorted(os.sched_getaffinity(0));start=int(sys.argv[1])*8;count=int(sys.argv[2])
assert start+count<=len(available),(available,start,count)
print(','.join(map(str,available[start:start+count])))
PY
)
# Metadata queries may see the allocation mask; model exec restores the selected task budget.
allocation_cpu_list=$(python3 -c 'import os;print(",".join(map(str,sorted(os.sched_getaffinity(0)))))')
legacy_cpu_list=$cpu_list
if ((count>0)); then cpu_list=$allocation_cpu_list; fi
env_json=$(python3 - "$env_json" "$allocation_cpu_list" "$legacy_cpu_list" "$cpus" "$count" <<'PYCPUENV'
import json,sys
data=json.loads(sys.argv[1]);data.update(QWEN_ALLOCATION_CPU_MASK=sys.argv[2],QWEN_LEGACY_TASK_CPU_MASK=sys.argv[3],QWEN_TASK_CPU_BUDGET=sys.argv[4],QWEN_TASK_GPU_COUNT=sys.argv[5])
print(json.dumps(data))
PYCPUENV
)
gpu_list=$(python3 - "$offset" "$count" <<'PY'
import sys
print(','.join(map(str,range(int(sys.argv[1]),int(sys.argv[1])+int(sys.argv[2])))))
PY
)
# Isolate worker fixed /tmp cache paths from pre-existing node directories.
# Created on the allocated compute node, unique to this container process.
task_tmp=$(mktemp -d "${TMPDIR:-/tmp}/ap42-qwen.XXXXXXXX")
printf 'PRIVATE_TMP=%s\n' "$task_tmp"
# The raw Enroot squashfs has no Singularity environment scripts. Use an
# explicit exec wrapper; SINGULARITYENV_* alone did not propagate GPU/libcuda.
exec taskset -c "$cpu_list" singularity exec --nv --cleanenv --no-home \
  --bind "$mounts,$task_tmp:/tmp" "$image" /usr/bin/env \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  LD_LIBRARY_PATH=/.singularity.d/libs:/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:/usr/local/lib \
  python3 "$runner_dir/pbs-exec.py" "$gpu_list" "$env_json" "$@"

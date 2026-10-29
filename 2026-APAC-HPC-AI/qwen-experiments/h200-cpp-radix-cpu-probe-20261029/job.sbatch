#!/usr/bin/env bash
# Prepared zero-GPU diagnostic. Root admission is required before submission.
#SBATCH -J ap42-cpp-radix-cpu
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:0
#SBATCH --propagate=NONE
#SBATCH --time=00:02:00
#SBATCH -o /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.out
#SBATCH -e /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.err
set -euo pipefail
umask 077
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
B=$Q/h200-cpp-radix-cpu-probe-20261029
OLD=$Q/h200-cpp-prefill-cache-source-20261029
NATIVE=$Q/h200-kv-page-primitive-r2-20261028/native-container.sh
IMAGE=/scratch/enroot-images/sglang-harbor.sqsh
RUN=$Q/runs/${SLURM_JOB_ID:?}
job_start=$(date +%s)
deadline=$((job_start + 90))
[[ ! -L "$RUN" ]]
mkdir -p -m 700 "$RUN"
[[ ! -e "$RUN/probe.json" ]]
cd "$B"
sha256sum --check PIN_SHA256SUMS
[[ -f "$IMAGE" ]]
[[ "$(sha256sum "$NATIVE" | cut -d' ' -f1)" == a478c3d2483dc8962c17a7fd34eb8c6d58b0054e9e9b94e4cf0ca78a86daced3 ]]
[[ "$(sha256sum "$(dirname "$NATIVE")/exec.rc" | cut -d' ' -f1)" == 2e124b30113dd2abbe684d922c097aa498ce5a8a5f2255a941ff2c1e05d4e196 ]]
tmpbase=${SLURM_TMPDIR:-/tmp}
PRIV=$tmpbase/apac-cpp-radix-${SLURM_JOB_ID}
[[ ! -e "$PRIV" && ! -L "$PRIV" ]]
mkdir -m 700 "$PRIV"
mkdir -m 700 "$PRIV/home" "$PRIV/cache" "$PRIV/tmp"
finalize() {
  rc=$?
  trap - EXIT INT TERM
  set +e
  python3 - "$RUN/probe.json" "$RUN/compiler-import.log" "$rc" "$job_start" "$deadline" <<'PY'
import json,sys,time
from pathlib import Path
result_path, log_path, rc, start, deadline = sys.argv[1:]
p=Path(result_path)
if p.exists():
    try: result=json.loads(p.read_text())
    except Exception: result={"state":"FAIL_INVALID_RESULT_JSON"}
else:
    result={"state":"FAIL_NO_PROBE_RESULT"}
if result.get("state")=="RUNNING":
    result["state"]="FAIL_TIME_LIMIT_OR_SIGNAL"
result["launcher_exit_code"]=int(rc)
result["absolute_job_start_epoch"]=int(start)
result["process_deadline_epoch"]=int(deadline)
result["native_remove_end_seen"]=bool(Path(log_path).exists() and "NATIVE_REMOVE_END" in Path(log_path).read_text(errors="replace"))
result["finalized_epoch"]=int(time.time())
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(result,indent=2)+"\n")
PY
  rm -rf -- "$PRIV"
  exit "$rc"
}
trap finalize EXIT
printf 'PROBE_EXECUTION_STATE=running_diagnostic\nJOB=%s\nHOST=%s\nJOB_START_EPOCH=%s\nPROCESS_DEADLINE_EPOCH=%s\nGPU_REQUEST=0\nCPU_REQUEST=2\n' "$SLURM_JOB_ID" "$(hostname)" "$job_start" "$deadline" | tee "$RUN/host-start.txt"
remaining=$((deadline - $(date +%s)))
if (( remaining <= 0 )); then
  echo 'FATAL: process deadline elapsed before container launch' >&2
  exit 124
fi
mounts="$B:/work:ro,$RUN:/output:rw,$PRIV:/tmp/apac_cpp_radix_probe:rw"
set +e
timeout --signal=TERM --kill-after=30s "${remaining}s" \
  srun --exact --nodes=1 --ntasks=1 --cpus-per-task=2 --gres=gpu:0 \
  bash "$NATIVE" "$IMAGE" "$mounts" \
  env HOME=/tmp/apac_cpp_radix_probe/home \
      XDG_CACHE_HOME=/tmp/apac_cpp_radix_probe/cache \
      TMPDIR=/tmp/apac_cpp_radix_probe/tmp \
      TORCH_EXTENSIONS_DIR=/tmp/apac_cpp_radix_probe/cache/torch_extensions \
      MAX_JOBS=2 OMP_NUM_THREADS=2 PYTHONNOUSERSITE=1 \
      APAC_CPP_RADIX_RESULT=/output/probe.json \
      APAC_CPP_RADIX_SOURCE_ROOT=/work/evidence \
      python3 -B /work/probe.py \
  2>&1 | tee "$RUN/compiler-import.log"
status=${PIPESTATUS[0]}
set -e
printf 'PROBE_COMMAND_EXIT epoch=%s status=%s\n' "$(date +%s)" "$status" | tee -a "$RUN/host-start.txt"
exit "$status"

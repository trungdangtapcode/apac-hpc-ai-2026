#!/usr/bin/env bash
# Prepared zero-GPU R2 diagnostic. Root admission required before any submission.
#SBATCH -J ap42-cpp-radix-r2
#SBATCH -p hpcai
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:0
#SBATCH --propagate=NONE
#SBATCH --time=00:06:00
#SBATCH -o /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.out
#SBATCH -e /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/%j.err
set -euo pipefail
umask 077
Q=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
B=$Q/h200-cpp-radix-cpu-probe-r2-20261029
RUN=$Q/runs/${SLURM_JOB_ID:?}
IMAGE=/scratch/enroot-images/sglang-harbor.sqsh
NATIVE=$B/native-container.sh
job_start=$(date +%s)
deadline=$((job_start + 300))
[[ ! -L "$RUN" ]]
mkdir -p -m 700 "$RUN"
[[ ! -e "$RUN/probe.json" && ! -e "$RUN/deadline-supervisor.json" ]]
cd "$B"
sha256sum --check PIN_SHA256SUMS
[[ -f "$IMAGE" ]]
[[ "$(sha256sum "$NATIVE" | cut -d' ' -f1)" == "$(python3 -c 'import json;print(json.load(open("RUNNER_PROVENANCE.json"))["r2_native_runner_sha256"])')" ]]
tmpbase=${SLURM_TMPDIR:-/tmp}
PRIV=$tmpbase/apac-cpp-radix-r2-${SLURM_JOB_ID}
[[ ! -e "$PRIV" && ! -L "$PRIV" ]]
mkdir -m 700 "$PRIV"
mkdir -m 700 "$PRIV/home" "$PRIV/cache" "$PRIV/tmp"
finalize() {
  rc=$?
  trap - EXIT INT TERM
  set +e
  python3 - "$RUN/probe.json" "$RUN/deadline-supervisor.json" "$RUN/compiler-import.log" "$rc" "$job_start" "$deadline" <<'PY'
import json,re,sys,time
from pathlib import Path
result_path,supervisor_path,log_path,rc,start,deadline=sys.argv[1:]
result_path=Path(result_path);log_path=Path(log_path)
try: result=json.loads(result_path.read_text()) if result_path.exists() else {"state":"FAIL_NO_PROBE_RESULT"}
except Exception as exc: result={"state":"FAIL_INVALID_RESULT_JSON","read_error":repr(exc)}
try: supervisor=json.loads(Path(supervisor_path).read_text())
except Exception: supervisor={"state":"MISSING"}
log=log_path.read_text(errors='replace') if log_path.exists() else ''
create=re.search(r'NATIVE_CREATE_BEGIN epoch=(\d+).*?NATIVE_CREATE_END epoch=(\d+)',log,re.S)
result.update(launcher_exit_code=int(rc),absolute_job_start_epoch=int(start),
              process_deadline_epoch=int(deadline),native_remove_end_seen='NATIVE_REMOVE_END' in log and 'NATIVE_REMOVE_FAILED' not in log,
              finalized_epoch=int(time.time()),deadline_supervisor_state=supervisor.get('state'),
              batch_elapsed_seconds=int(time.time())-int(start))
if create:
    result['native_container_create_seconds']=int(create.group(2))-int(create.group(1))
if result.get('state')=='RUNNING': result['state']='FAIL_RUNNER_EXITED_WITH_INCOMPLETE_RESULT'
result_path.parent.mkdir(parents=True,exist_ok=True)
result_path.write_text(json.dumps(result,indent=2)+'\n')
PY
  rm -rf -- "$PRIV"
  exit "$rc"
}
trap finalize EXIT
trap 'exit 143' INT TERM
printf 'PROBE_EXECUTION_STATE=running_diagnostic\nJOB=%s\nHOST=%s\nJOB_START_EPOCH=%s\nPROCESS_DEADLINE_EPOCH=%s\nGPU_REQUEST=0\nCPU_REQUEST=4\nMEMORY_GIB=16\nWALL_SECONDS=360\n' "$SLURM_JOB_ID" "$(hostname)" "$job_start" "$deadline" | tee "$RUN/host-start.txt"
remaining=$((deadline - $(date +%s)))
if (( remaining <= 0 )); then echo 'FATAL: 300-second absolute process deadline elapsed before container launch' >&2; exit 124; fi
mounts="$B:/work:ro,$RUN:/output:rw,$PRIV:/tmp/apac_cpp_radix_probe:rw"
set +e
srun --exact --nodes=1 --ntasks=1 --cpus-per-task=4 --gres=gpu:0 \
  bash "$NATIVE" "$IMAGE" "$mounts" \
  env HOME=/tmp/apac_cpp_radix_probe/home \
      XDG_CACHE_HOME=/tmp/apac_cpp_radix_probe/cache \
      TMPDIR=/tmp/apac_cpp_radix_probe/tmp \
      TORCH_EXTENSIONS_DIR=/tmp/apac_cpp_radix_probe/cache/torch_extensions \
      MAX_JOBS=2 OMP_NUM_THREADS=2 ENROOT_MAX_PROCESSORS=4 PYTHONNOUSERSITE=1 \
      APAC_CPP_RADIX_RESULT=/output/probe.json \
      APAC_CPP_RADIX_PROCESS_DEADLINE_EPOCH="$deadline" \
      APAC_CPP_RADIX_SOURCE_ROOT=/work/evidence \
      python3 -B /work/deadline_runner.py /work/probe.py \
  2>&1 | tee "$RUN/compiler-import.log"
status=${PIPESTATUS[0]}
set -e
printf 'PROBE_COMMAND_EXIT epoch=%s status=%s\n' "$(date +%s)" "$status" | tee -a "$RUN/host-start.txt"
exit "$status"

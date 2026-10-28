#!/bin/bash
#SBATCH -J tu-iris-mpimap
#SBATCH -p iris
#SBATCH -A rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --gpus=0
#SBATCH -N 1
#SBATCH -n 56
#SBATCH -t 00:05:00
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
ROOT=${SLURM_SUBMIT_DIR:?}
JOB=${SLURM_JOB_ID:?}
OUT="$ROOT/runs/$JOB"
mkdir -m 700 "$OUT"
umask 077
verify_payload() {
    (cd "$ROOT" && sha256sum --check --status payload-sha256.txt)
}
verify_payload
T0=$SECONDS
ELAPSED_LIMIT=235 # Leave termination and scheduler-log margin inside the four-minute cap.
{
  printf 'SLURM_JOB_ID=%s\n' "$JOB"
  printf 'SLURM_JOB_NODELIST=%s\n' "${SLURM_JOB_NODELIST:-<unset>}"
  printf 'SLURM_JOB_NUM_NODES=%s\n' "${SLURM_JOB_NUM_NODES:-<unset>}"
  printf 'SLURM_NTASKS=%s\n' "${SLURM_NTASKS:-<unset>}"
  printf 'SLURM_CPUS_ON_NODE=%s\n' "${SLURM_CPUS_ON_NODE:-<unset>}"
  printf 'SLURM_JOB_PARTITION=%s\n' "${SLURM_JOB_PARTITION:-<unset>}"
  printf 'SLURM_JOB_QOS=%s\n' "${SLURM_JOB_QOS:-<unset>}"
  date -u +'%Y-%m-%dT%H:%M:%SZ'
  hostname -f
} > "$OUT/job-metadata.txt"
deadline_check() {
    if (( SECONDS - T0 > ELAPSED_LIMIT )); then
        echo "Runtime guard exceeded ${ELAPSED_LIMIT} seconds" >&2
        exit 124
    fi
}
run_limited() {
    local ceiling=$1
    shift
    local remaining=$((ELAPSED_LIMIT - (SECONDS - T0)))
    if (( remaining <= 0 )); then
        echo "No runtime remains before the internal guard" >&2
        exit 124
    fi
    local limit=$ceiling
    if (( remaining < limit )); then limit=$remaining; fi
    timeout --signal=TERM --kill-after=2s "${limit}s" "$@"
    deadline_check
}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset LD_PRELOAD LD_AUDIT
module load gcc/11
module load hpcx/2.50
{
  date -u +'%Y-%m-%dT%H:%M:%SZ'
  hostname -f
  module list 2>&1
  mpirun --version
  mpicc --version
  gcc --version
  mpicc --showme:command
  printf 'OMP_NUM_THREADS=%s\nOPENBLAS_NUM_THREADS=%s\nMKL_NUM_THREADS=%s\n' "$OMP_NUM_THREADS" "$OPENBLAS_NUM_THREADS" "$MKL_NUM_THREADS"
  printf 'LD_PRELOAD=%s\nLD_AUDIT=%s\n' "${LD_PRELOAD:-<unset>}" "${LD_AUDIT:-<unset>}"
  for variable in OMPI_MCA_rmaps_base_mapping_policy OMPI_MCA_rmaps_base_ranking_policy OMPI_MCA_hwloc_base_binding_policy PRTE_MCA_rmaps_default_mapping_policy PRTE_MCA_rmaps_default_ranking_policy PRTE_MCA_hwloc_default_binding_policy; do
    if [[ -v $variable ]]; then printf '%s=%s\n' "$variable" "${!variable}"; else printf '%s=<unset>\n' "$variable"; fi
  done
  for tool in mpirun mpicc gcc; do
    path=$(command -v "$tool")
    resolved=$(readlink -f "$path")
    printf '%s_path=%s\n%s_resolved=%s\n' "$tool" "$path" "$tool" "$resolved"
    sha256sum "$resolved"
  done
  printf 'allocated_cpu_ids='
  python3 -c 'import os; print(",".join(map(str, sorted(os.sched_getaffinity(0)))))'
  lscpu
} > "$OUT/runtime.txt"
lscpu -p=CPU,CORE,SOCKET,NODE > "$OUT/lscpu.csv"
python3 -c 'import os,json; print(json.dumps(sorted(os.sched_getaffinity(0))))' > "$OUT/allocated-cpus.json"
deadline_check
run_limited 35 mpicc -O2 -Wall -Wextra -Werror "$ROOT/affinity_probe.c" -o "$OUT/affinity_probe" > "$OUT/build.log" 2>&1
sha256sum "$ROOT/affinity_probe.c" "$OUT/affinity_probe" > "$OUT/source-binary.sha256"
ldd "$OUT/affinity_probe" > "$OUT/ldd.txt"
deadline_check
run_mode() {
    local name=$1; shift
    mkdir -m 700 "$OUT/$name"
    printf 'mpirun -np 56 %s %q %q\n' "$*" "$OUT/affinity_probe" "$name" > "$OUT/$name/command.txt"
    export PROBE_OUT="$OUT/$name"
    run_limited 40 mpirun -np 56 "$@" "$OUT/affinity_probe" "$name" > "$OUT/$name/mpirun.out" 2> "$OUT/$name/mpirun.err"
}
run_mode A-default
run_mode B-fill --map-by ppr:28:package --bind-to core --rank-by fill
run_mode C-span --map-by ppr:28:package --bind-to core --rank-by span
run_limited 20 python3 "$ROOT/analyze.py" "$OUT" > "$OUT/analysis.json"
verify_payload
printf 'Completed all three read-only placement observations. Elapsed seconds: %s\n' "$((SECONDS-T0))" > "$OUT/COMPLETE.txt"

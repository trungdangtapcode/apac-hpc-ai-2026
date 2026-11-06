#!/bin/bash
#SBATCH -J tu-iris-s40-init
#SBATCH -p iris
#SBATCH -A rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH -N 1
#SBATCH --gpus=0
#SBATCH -n 40
#SBATCH -t 00:20:00
#SBATCH -o /global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch40-cut-20261105T162039Z/init-runs/%j.sbatch.out
#SBATCH -e /global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch40-cut-20261105T162039Z/init-runs/%j.sbatch.err
set -euo pipefail
RUN_START=$SECONDS
DEADLINE_SECONDS=1140
(
  sleep "$DEADLINE_SECONDS"
  kill -TERM "$$" 2>/dev/null || true
) &
DEADLINE_WATCHDOG=$!
trap 'kill "$DEADLINE_WATCHDOG" 2>/dev/null || true' EXIT

run_bounded() {
  local cap="$1"
  shift
  local elapsed=$((SECONDS - RUN_START))
  local remaining=$((DEADLINE_SECONDS - elapsed))
  (( remaining > 0 )) || return 124
  if (( cap > remaining )); then cap="$remaining"; fi
  timeout --signal=TERM --kill-after=5s "${cap}s" "$@"
}

SHARED=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam
BUILD="$SHARED/builds/iris-gcc11-hpcx250-opt"
BASHRC="$BUILD/OpenFOAM-v2512/etc/bashrc"
ROOT="${SLURM_SUBMIT_DIR:?}"
CUT_ROOT="$(cd "$ROOT/.." && pwd)"
EXPECTED_CUT_ROOT="/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch40-cut-20261105T162039Z"
[[ "$CUT_ROOT" == "$EXPECTED_CUT_ROOT" ]]
ART="$CUT_ROOT/artifacts/cut-N40-scotch"
RUNS="$CUT_ROOT/init-runs"
KIT="$ROOT"
RANKS="${SLURM_NTASKS:?}"
JOB="${SLURM_JOB_ID:?}"
CUT_JOB=2294919

[[ "$RANKS" == 40 ]]
[[ "${SLURM_CPUS_ON_NODE:?}" == 56 ]]
test -d "$RUNS"
test -r "$BASHRC"
test -d "$ART" && test ! -L "$ART"
for path in \
  "$ART/READY" \
  "$ART/.INIT_IN_PROGRESS" "$ART/.INIT_STARTED" \
  "$RUNS/$JOB-cut-accounting.txt" "$RUNS/$JOB-cut-gate.json" \
  "$RUNS/$JOB-kit-source-before.txt" "$RUNS/$JOB-kit-source-after.txt" \
  "$RUNS/$JOB-source-before.json" "$RUNS/$JOB-source-before.stdout" \
  "$RUNS/$JOB-fields-before.json" "$RUNS/$JOB-fields-before.stdout" \
  "$RUNS/$JOB-mpi-hostnames.log" "$RUNS/$JOB-mpi-probe-review.json" \
  "$RUNS/$JOB-mpi-probe-review.stdout" "$RUNS/$JOB-mpi-probe-review-gate.json" \
  "$RUNS/$JOB-rank-proofs" \
  "$RUNS/$JOB-renumberMesh.log" "$RUNS/$JOB-potentialFoam.log" \
  "$RUNS/$JOB-applyBoundaryLayer.log" "$RUNS/$JOB-init-review.json" \
  "$RUNS/$JOB-source-after.json" "$RUNS/$JOB-source-after.stdout" \
  "$RUNS/$JOB-fields-after.json" "$RUNS/$JOB-fields-after.stdout" \
  "$RUNS/$JOB-complete.txt"; do
  test ! -e "$path" && test ! -L "$path"
done

# Refuse a reused, partially initialized, or differently partitioned artifact.
[[ -d "$ART/processor0" && -d "$ART/processor39" ]]

# Validate completed cut evidence and native scheduler accounting before any writes to ART.
run_bounded 30 sacct -n -P -j "$CUT_JOB" -o JobIDRaw,State,ExitCode,Elapsed,AllocCPUS,NodeList > "$RUNS/$JOB-cut-accounting.txt"
run_bounded 30 python3 "$KIT/verify-init.py" cut-gate --cut-root "$CUT_ROOT" --accounting "$RUNS/$JOB-cut-accounting.txt" > "$RUNS/$JOB-cut-gate.json"
run_bounded 30 bash -c 'cd "$1" && sha256sum -c payload-sha256.txt' _ "$KIT" > "$RUNS/$JOB-kit-source-before.txt"

run_bounded 30 bash -c 'date -u; hostname; lscpu' > "$RUNS/$JOB-hardware.txt"

module load gcc/11
module load hpcx/2.50
export FOAM_CONFIG_MODE=o
# OpenFOAM's bashrc may reference unset optional variables and return nonzero for missing optional paths.
set +euo pipefail
# shellcheck disable=SC1090
source "$BASHRC"
set -euo pipefail
[[ -n "${FOAM_APPBIN:-}" ]]
set +u
# shellcheck disable=SC1091
source "${WM_PROJECT_DIR:?}/bin/tools/RunFunctions"
set -u

run_bounded 30 python3 "$KIT/verify-init.py" source --kit "$KIT" --case "$ART" --output "$RUNS/$JOB-source-before.json" > "$RUNS/$JOB-source-before.stdout"
run_bounded 150 python3 "$KIT/verify-init.py" fields --case "$ART" --output "$RUNS/$JOB-fields-before.json" > "$RUNS/$JOB-fields-before.stdout"

# The qualified one-file-per-rank protocol prevents interleaved stdout from dropping identities.
MPI=(mpirun --display-map --report-bindings -np "$RANKS" --)
PROOF_DIR="$RUNS/$JOB-rank-proofs"
mkdir -m 700 "$PROOF_DIR"
run_bounded 60 "${MPI[@]}" python3 "$KIT/probe_writer.py" --proof-dir "$PROOF_DIR" > "$RUNS/$JOB-mpi-hostnames.log" 2>&1
run_bounded 30 python3 "$KIT/validate_rank_proofs.py" --proof-dir "$PROOF_DIR" --output "$RUNS/$JOB-mpi-probe-review.json" > "$RUNS/$JOB-mpi-probe-review.stdout"
run_bounded 30 python3 "$KIT/verify-init.py" probe --run-dir "$RUNS" --job-id "$JOB" > "$RUNS/$JOB-mpi-probe-review-gate.json"

# All cut, source, field, and MPI-startup gates passed. Leave this marker on any failure;
# a later attempt must use a separately reviewed artifact rather than resume or overwrite.
( set -o noclobber; printf 'job=%s\ncut_job=%s\nstate=IN_PROGRESS\n' "$JOB" "$CUT_JOB" > "$ART/.INIT_IN_PROGRESS" )

run_stage() {
  local stage="$1"
  shift
  local log="$RUNS/$JOB-$stage.log"
  local rc
  set +e
  run_bounded 210 /usr/bin/time -v -o "$RUNS/$JOB-$stage.resource.txt" "${MPI[@]}" "$@" > "$log" 2>&1
  rc=$?
  set -e
  printf '\nINIT_STAGE_RETURN_CODE=%s\n' "$rc" >> "$log"
  [[ "$rc" -eq 0 ]]
}

cd "$ART"
run_stage renumberMesh renumberMesh -constant -overwrite -parallel
run_stage potentialFoam potentialFoam -initialiseUBCs -parallel
run_stage applyBoundaryLayer applyBoundaryLayer -ybl 0.0450244 -parallel

run_bounded 30 python3 "$KIT/verify-init.py" logs --run-dir "$RUNS" --job-id "$JOB" > "$RUNS/$JOB-init-review.json"
run_bounded 30 python3 "$KIT/verify-init.py" source --kit "$KIT" --case "$ART" --output "$RUNS/$JOB-source-after.json" > "$RUNS/$JOB-source-after.stdout"
run_bounded 30 bash -c 'cd "$1" && sha256sum -c payload-sha256.txt' _ "$KIT" > "$RUNS/$JOB-kit-source-after.txt"
run_bounded 150 python3 "$KIT/verify-init.py" fields --case "$ART" --output "$RUNS/$JOB-fields-after.json" > "$RUNS/$JOB-fields-after.stdout"

# READY is created last, with organizer 13.2's exact marker format.
printf 'Iris N40 Scotch initialization passed; no solver was run.\n' > "$RUNS/$JOB-complete.txt"
test ! -e "$ART/READY" && test ! -L "$ART/READY"
( set -o noclobber; cat > "$ART/READY" <<'EOF'
N=40
method=scotch
nHierarchical=unused
mesh=occDrivAer-65M
stages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer
EOF
)
echo "13.2-init-65M-N40-scotch: PASS"

#!/bin/bash
set -euo pipefail

# START_EPOCH is set once by run-pair.sbatch before this file is sourced.
remaining_seconds() {
  echo $((INTERNAL_DEADLINE - ($(date +%s) - START_EPOCH)))
}

bounded() {
  local seconds=$1 label=$2; shift 2
  local left
  left=$(remaining_seconds)
  (( left > 0 )) || { echo "internal deadline reached before $label" >&2; return 31; }
  (( seconds > left )) && seconds=$left
  printf '%s\tstart\t%s\n' "$(date -u +%FT%TZ)" "$label" >> "$RUNROOT/phases.tsv"
  local operation_rc
  if timeout --signal=TERM --kill-after=10s "${seconds}s" "$@"; then operation_rc=0; else operation_rc=$?; fi
  printf '%s\texit=%s\t%s\n' "$(date -u +%FT%TZ)" "$operation_rc" "$label" >> "$RUNROOT/phases.tsv"
  return "$operation_rc"
}

run_bounded() { bounded "$1" "bounded batch operation" "${@:2}"; }

verify_source() {
  local src=$1 method=$2
  bounded 120 "source pin validation $method" python3 "$ROOT/lib/verify-inputs.py" \
    --source "$src" --method "$method" --pins "$ROOT/source-pins.json" --case "$ROOT/payload-case" --observations "$ROOT/source-observations.json" >> "$RUNROOT/source-validation.txt" 2>&1
  [[ -f "$src/READY" ]]
  grep -qx 'N=56' "$src/READY"
  grep -qx "method=$method" "$src/READY"
  for i in {0..55}; do [[ -d "$src/processor$i/0" && -d "$src/processor$i/constant" ]]; done
  [[ -d "$src/constant" && -f "$src/system/controlDict.noWrite" && -f "$src/system/fvSolution.fixedIter" ]]
  echo "source=$src method=$method ready_n=56 pin_review=PASS" >> "$RUNROOT/source-validation.txt"
}

run_arm() {
  local arm=$1 src=$2 method=$3 dest="$RUNROOT/$1" tleft
  tleft=$(remaining_seconds)
  (( tleft >= SOLVER_CAP + RESERVE )) || { echo "Insufficient time for $arm: ${tleft}s remain; need $((SOLVER_CAP+RESERVE))s" | tee -a "$RUNROOT/admission.txt"; return 30; }
  [[ ! -e "$dest" ]]
  mkdir -p "$dest"
  bounded 300 "pre-copy source hash $arm" python3 "$ROOT/lib/tree-manifest.py" "$src" "$dest" "$dest/source-before.json" --source-only > "$dest/source-before-hash.log" 2>&1
  bounded 600 "isolated case copy $arm" python3 "$ROOT/lib/copy-case.py" "$src" "$dest" > "$dest/copy.log" 2>&1
  bounded 300 "copy integrity and inode review $arm" python3 "$ROOT/lib/tree-manifest.py" "$src" "$dest" "$dest/source-after-copy.json" --compare-copy > "$dest/copy-validation.log" 2>&1
  bounded 120 "source pin revalidation $arm" python3 "$ROOT/lib/verify-inputs.py" \
    --source "$src" --method "$method" --pins "$ROOT/source-pins.json" --case "$ROOT/payload-case" --observations "$ROOT/source-observations.json" >> "$RUNROOT/source-validation.txt" 2>&1
  # The copy must still be identical before these intentional local controls are changed.
  [[ -f "$dest/READY" ]] || cp "$src/READY" "$dest/READY"
  cp "$dest/system/controlDict.noWrite" "$dest/system/controlDict"
  cp "$dest/system/fvSolution.fixedIter" "$dest/system/fvSolution"
  bounded 30 "derive exactly two solver controls $arm" python3 "$ROOT/lib/set-solver-control.py" "$dest"
  grep -Eq '^startFrom[[:space:]]+startTime;' "$dest/system/controlDict"
  grep -Eq '^endTime[[:space:]]+150;' "$dest/system/controlDict"
  bounded 60 "MPI affinity preflight and validation $arm" bash -c 'mpirun -np 56 -- python3 "$1/lib/affinity-probe.py" worker "$2/rank-affinity" && python3 "$1/lib/affinity-probe.py" validate "$2/rank-affinity"' _ "$ROOT" "$dest" > "$dest/affinity-preflight.log" 2>&1
  # These files are intentionally changed only in this arm-local case.
  (cd "$dest" && sha256sum system/include/caseDefinition system/controlDict system/fvSolution) > "$dest/solver-control-hashes.txt"
  date -u +%FT%TZ > "$dest/start.utc"
  tleft=$(remaining_seconds)
  (( tleft >= SOLVER_CAP + RESERVE )) || { echo "Insufficient time after bounded preflight for $arm: ${tleft}s remain" >&2; return 30; }
  local solve_cap=$SOLVER_CAP
  (( solve_cap > tleft - RESERVE )) && solve_cap=$((tleft - RESERVE))
  cd "$dest"
  set +e
  timeout --signal=TERM --kill-after=20s "${solve_cap}s" /usr/bin/time -v mpirun -np 56 -- simpleFoam -parallel > simpleFoam.log 2> resource-time.log
  local rc=$?
  set -e
  echo "$rc" > return-code.txt
  [[ $rc == 0 ]] || { echo "$arm native solve failed: $rc" >&2; return "$rc"; }
  date -u +%FT%TZ > end.utc
  bounded 300 "post-run source integrity $arm" python3 "$ROOT/lib/tree-manifest.py" "$src" "$dest" "$dest/source-after-run.json" --source-only --compare-source-snapshot > "$dest/source-after-run-hash.log" 2>&1
  echo "arm=$arm method=$method returncode=$rc" >> "$RUNROOT/arms.txt"
}

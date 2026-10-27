#!/bin/bash
set -euo pipefail
ROOT=$1
RUN=$2
PAYLOAD="$ROOT/payload"
START=$(date +%s)
DEADLINE=$((START + 555))
export OMP_NUM_THREADS=1 MPICH_RANK_REORDER_METHOD=0
PSTREAM=
CHECKMESH_BIN=
MODULE_WATCHDOG=
[ -z "${LD_PRELOAD:-}" ] || { echo 'Inherited LD_PRELOAD is disallowed' >&2; exit 1; }
[ -z "${NSCC_LATEPIN_AUDIT_DIR:-}" ] || { echo 'Inherited audit directory is disallowed' >&2; exit 1; }
unset PALS_CPU_BIND MPICH_RANK_ORDER MPICH_RANK_REORDER_FILE
phase() { printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$1" "$2" >>"$RUN/phases.tsv"; }
record_rc() { printf '{"time_utc":"%s","command":"%s","return_code":%s}\n' "$(date -u +%FT%TZ)" "$1" "$2" >>"$RUN/command-return-codes.jsonl"; }
remaining() { echo $((DEADLINE - $(date +%s))); }
fail=0
run_bounded() {
    local name=$1 cap=$2 seconds rc
    shift 2
    seconds=$(remaining)
    [ "$seconds" -gt 0 ] || return 124
    [ "$seconds" -gt "$cap" ] && seconds=$cap
    phase start "$name"
    printf '%q ' "$@" >"$RUN/commands/${name}.argv.txt"; printf '\n' >>"$RUN/commands/${name}.argv.txt"
    if timeout --signal=TERM --kill-after=3s "${seconds}s" /usr/bin/time -v -o "$RUN/resources/${name}.time.txt" -- "$@" >"$RUN/logs/${name}.stdout.txt" 2>"$RUN/logs/${name}.stderr.txt"; then rc=0; else rc=$?; fi
    record_rc "$name" "$rc"
    phase "exit=$rc" "$name"
    return "$rc"
}
payload_hash() {
    (cd "$ROOT" && find payload -type f ! -path '*/__pycache__/*' ! -name '*.pyc' -print0 | sort -z | xargs -0 sha256sum) >"$RUN/$1"
}
runtime_hash() {
    local output=$1; shift
    local -a files=()
    local file
    for file in "$@"; do
        [ -f "$file" ] && files+=("$(realpath -e "$file")")
        if [ -f "$file" ] && [[ "$file" == *ldd.stdout.txt ]]; then
            while IFS= read -r dependency; do [ -f "$dependency" ] && files+=("$(realpath -e "$dependency")"); done < <(awk '/=> \// {print $3} /^\// {print $1}' "$file")
        fi
    done
    [ "${#files[@]}" -gt 0 ] || return 1
    printf '%s\n' "${files[@]}" | sort -u | while IFS= read -r dependency; do sha256sum "$dependency"; done >"$RUN/$output"
}
finish() {
    local rc=$? runtime_rc=125; trap - EXIT; set +e
    if [ -n "${MODULE_WATCHDOG:-}" ]; then kill -TERM "$MODULE_WATCHDOG" 2>/dev/null || true; wait "$MODULE_WATCHDOG" 2>/dev/null || true; MODULE_WATCHDOG=; fi
    if [ -f "$RUN/runtime-hashes-before.txt" ]; then
        runtime_hash runtime-hashes-after.txt "$PSTREAM" "$CHECKMESH_BIN" "$RUN/latepin-pmpi-adapter.so" "$RUN/mpi-init-probe" "$RUN/logs/pstream-ldd.stdout.txt" "$RUN/logs/checkMesh-ldd.stdout.txt" "$RUN/logs/adapter-ldd.stdout.txt" "$RUN/logs/native-probe-ldd.stdout.txt"
        cmp -s "$RUN/runtime-hashes-before.txt" "$RUN/runtime-hashes-after.txt"; runtime_rc=$?
        record_rc runtime_objects_unchanged "$runtime_rc"
    fi
    phase start payload_hash_after
    payload_hash payload-sha256-after.txt; local hash_read_rc=$?
    cmp -s "$RUN/payload-sha256-before.txt" "$RUN/payload-sha256-after.txt"; local hash_compare_rc=$?
    cmp -s "$ROOT/payload-sha256.txt" "$RUN/payload-sha256-after.txt"; local hash_frozen_rc=$?
    local hash_rc=0
    if [ "$hash_read_rc" -ne 0 ] || [ "$hash_compare_rc" -ne 0 ] || [ "$hash_frozen_rc" -ne 0 ]; then hash_rc=1; fi
    record_rc payload_unchanged "$hash_rc"; phase "exit=$hash_rc" payload_hash_after
    [ "$rc" -eq 0 ] && { [ "$hash_rc" -ne 0 ] || [ "$runtime_rc" -ne 0 ]; } && rc=1
    printf '{"worker_return_code":%s,"payload_unchanged_return_code":%s,"runtime_objects_unchanged_return_code":%s,"finished_utc":"%s"}\n' "$rc" "$hash_rc" "$runtime_rc" "$(date -u +%FT%TZ)" >"$RUN/worker-status.json"
    exit "$rc"
}
trap finish EXIT
mkdir -p "$RUN/logs" "$RUN/resources" "$RUN/commands" "$RUN/arms/no-adapter/native/pre" "$RUN/arms/with-adapter/native/pre" "$RUN/arms/with-adapter/adapter-ranks" "$RUN/arms/pstream-checkmesh/adapter-ranks"
cp "$PBS_NODEFILE" "$RUN/pbs-nodefile.txt"
payload_hash payload-sha256-before.txt
cp "$ROOT/payload-sha256.txt" "$RUN/expected-payload-sha256.txt"
if cmp -s "$RUN/expected-payload-sha256.txt" "$RUN/payload-sha256-before.txt"; then rc=0; else rc=$?; fi
record_rc payload_matches_frozen_before "$rc"
[ "$rc" -eq 0 ]
phase complete payload_hash_before
PARENT_PID=$BASHPID
(
    sleeper=
    trap 'if [ -n "${sleeper:-}" ]; then kill "$sleeper" 2>/dev/null || true; wait "$sleeper" 2>/dev/null || true; fi; exit 0' TERM INT
    sleep 45 & sleeper=$!
    wait "$sleeper"
    kill -TERM "$PARENT_PID" 2>/dev/null || true
) & MODULE_WATCHDOG=$!
phase start module_setup
if . /app/apps/resetmodule >"$RUN/logs/module-reset.txt" 2>&1 && module load openfoam/2512 >"$RUN/logs/module-load.txt" 2>&1; then rc=0; else rc=$?; fi
kill -TERM "$MODULE_WATCHDOG" 2>/dev/null || true
wait "$MODULE_WATCHDOG" 2>/dev/null || true
record_rc module_setup "$rc"; phase "exit=$rc" module_setup; [ "$rc" -eq 0 ]
# Reapply runtime controls after module setup, which may alter launcher variables.
[ -z "${LD_PRELOAD:-}" ] || { echo 'OpenFOAM module introduced LD_PRELOAD' >&2; exit 1; }
[ -z "${NSCC_LATEPIN_AUDIT_DIR:-}" ] || { echo 'OpenFOAM module introduced adapter audit state' >&2; exit 1; }
unset PALS_CPU_BIND MPICH_RANK_ORDER MPICH_RANK_REORDER_FILE
export OMP_NUM_THREADS=1 MPICH_RANK_REORDER_METHOD=0
[ -z "${LD_PRELOAD:-}" ] || { echo 'Module setup introduced an unexpected preload' >&2; exit 1; }
[ -z "${NSCC_LATEPIN_AUDIT_DIR:-}" ] || { echo 'Module setup introduced an unexpected audit directory' >&2; exit 1; }
: "${FOAM_LIBBIN:?OpenFOAM module did not set FOAM_LIBBIN}" "${FOAM_MPI:?OpenFOAM module did not set FOAM_MPI}" "${WM_PROJECT_DIR:?OpenFOAM module did not set WM_PROJECT_DIR}"
for tool in cc mpiexec blockMesh decomposePar checkMesh ldd; do
    command -v "$tool" >"$RUN/logs/${tool}.path.txt"
done
printf 'WM_PROJECT_VERSION=%s\nWM_PROJECT_DIR=%s\nFOAM_MPI=%s\nOMP_NUM_THREADS=%s\nMPICH_RANK_REORDER_METHOD=%s\nPALS_CPU_BIND=unset\nMPICH_RANK_ORDER=unset\nMPICH_RANK_REORDER_FILE=unset\nLD_PRELOAD=empty\n' \
    "${WM_PROJECT_VERSION:-unknown}" "$WM_PROJECT_DIR" "$FOAM_MPI" "$OMP_NUM_THREADS" "$MPICH_RANK_REORDER_METHOD" >"$RUN/logs/selected-runtime-settings.txt"
PSTREAM="$FOAM_LIBBIN/$FOAM_MPI/libPstream.so"
case "$PSTREAM" in "$WM_PROJECT_DIR"/*) ;; *) echo 'Pstream path escaped WM_PROJECT_DIR' >&2; exit 1 ;; esac
[ -f "$PSTREAM" ]
printf '%s\n' "$PSTREAM" >"$RUN/logs/pstream-path.txt"
run_bounded pstream-ldd 10 ldd "$PSTREAM" || exit $?
run_bounded checkMesh-ldd 10 ldd "$(command -v checkMesh)" || exit $?
run_bounded checkMesh-help 10 checkMesh -help || exit $?
# The real linked library and executable must resolve to the required Cray MPICH ABI.
grep -Fq '/mpich/8.1.15/' "$RUN/logs/pstream-ldd.stdout.txt"
grep -Fq '/mpich/8.1.15/' "$RUN/logs/checkMesh-ldd.stdout.txt"
MPI_RUNTIME_LIB=$(awk '$1 ~ /libmpi.*\.so/ && $2 == "=>" && $3 ~ /^\// {print $3; exit}' "$RUN/logs/pstream-ldd.stdout.txt")
case "$MPI_RUNTIME_LIB" in */mpich/8.1.15/*) ;; *) echo 'Could not identify exact Cray MPICH 8.1.15 shared library from Pstream ldd' >&2; exit 1 ;; esac
printf '%s\n' "$MPI_RUNTIME_LIB" >"$RUN/logs/mpi-shared-library-path.txt"
run_bounded compile-native-probe 30 cc -O0 -Wall -Wextra -Werror -o "$RUN/mpi-init-probe" "$PAYLOAD/mpi-init-probe.c" || exit $?
run_bounded compile-pmpi-adapter 45 cc -shared -fPIC -Wall -Wextra -Werror -pthread -o "$RUN/latepin-pmpi-adapter.so" "$PAYLOAD/latepin-pmpi-adapter.c" "$MPI_RUNTIME_LIB" || exit $?
run_bounded adapter-ldd 10 ldd "$RUN/latepin-pmpi-adapter.so" || exit $?
run_bounded native-probe-ldd 10 ldd "$RUN/mpi-init-probe" || exit $?
grep -Fq '/mpich/8.1.15/' "$RUN/logs/adapter-ldd.stdout.txt"
grep -Fq '/mpich/8.1.15/' "$RUN/logs/native-probe-ldd.stdout.txt"
CHECKMESH_BIN=$(command -v checkMesh)
export PSTREAM CHECKMESH_BIN
runtime_hash runtime-hashes-before.txt "$PSTREAM" "$CHECKMESH_BIN" "$RUN/latepin-pmpi-adapter.so" "$RUN/mpi-init-probe" "$RUN/logs/pstream-ldd.stdout.txt" "$RUN/logs/checkMesh-ldd.stdout.txt" "$RUN/logs/adapter-ldd.stdout.txt" "$RUN/logs/native-probe-ldd.stdout.txt"
cp -a "$PAYLOAD/diagnostic-case" "$RUN/diagnostic-case"
run_bounded blockMesh 20 blockMesh -case "$RUN/diagnostic-case" || exit $?
run_bounded decomposePar 60 decomposePar -case "$RUN/diagnostic-case" -force -noFields || exit $?
[ -d "$RUN/diagnostic-case/processor511/constant/polyMesh" ] || { echo '512-way decomposePar output incomplete' >&2; exit 1; }

run_arm() {
    local arm=$1 cap=$2 rc
    shift 2
    if run_bounded "arm-${arm}" "$cap" "$@"; then rc=0; else rc=$?; fi
    [ "$rc" -eq 0 ] || fail=1
    return 0
}
run_arm no-adapter 30 mpiexec -n 512 "$RUN/mpi-init-probe" "$RUN/arms/no-adapter/native"
run_arm with-adapter 60 mpiexec -n 512 "$PAYLOAD/rank-exec.sh" "$RUN" with-adapter "$RUN/latepin-pmpi-adapter.so" -- "$RUN/mpi-init-probe" "$RUN/arms/with-adapter/native"
run_arm pstream-checkmesh 90 mpiexec -n 512 "$PAYLOAD/rank-exec.sh" "$RUN" pstream-checkmesh "$RUN/latepin-pmpi-adapter.so" -- checkMesh -parallel -case "$RUN/diagnostic-case"
phase complete three_diagnostic_arms
if [ "$fail" -ne 0 ]; then exit 1; fi
printf 'COLLECTION_FINISHED\n'

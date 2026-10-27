#!/bin/bash
set -euo pipefail
ROOT=$1
RUN=$2
PAYLOAD="$ROOT/payload"
START=$(date +%s)
DEADLINE=$((START + 255))
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1

phase() { printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$1" "$2" >>"$RUN/phases.tsv"; }
record_rc() { printf '{"time_utc":"%s","command":"%s","return_code":%s}\n' "$(date -u +%FT%TZ)" "$1" "$2" >>"$RUN/command-return-codes.jsonl"; }
remaining() { echo $((DEADLINE - $(date +%s))); }
hash_payload() { (cd "$ROOT" && sha256sum -c payload-sha256.txt) >"$RUN/$1" 2>&1; }
finish() {
    local rc=$? hash_rc
    trap - EXIT
    set +e
    phase start payload_hash_after
    hash_payload payload-sha256-after.txt
    hash_rc=$?
    record_rc payload_hash_after "$hash_rc"
    if [ "$rc" -eq 0 ] && [ "$hash_rc" -ne 0 ]; then rc=1; fi
    phase "exit=$hash_rc" payload_hash_after
    printf '{"worker_return_code":%s,"post_hash_return_code":%s,"finished_utc":"%s"}\n' "$rc" "$hash_rc" "$(date -u +%FT%TZ)" >"$RUN/worker-status.json"
    exit "$rc"
}
trap finish EXIT

phase start payload_hash_before
hash_payload payload-sha256-before.txt
record_rc payload_hash_before $?
phase complete payload_hash_before
cp "$PBS_NODEFILE" "$RUN/pbs-nodefile.txt"

phase start module_setup
parent_pid=$BASHPID
(
    trap 'if [ -n "${sleeper:-}" ]; then kill "$sleeper" 2>/dev/null || true; fi; exit 0' TERM INT
    sleep 40 & sleeper=$!
    wait "$sleeper"
    kill -TERM "$parent_pid" 2>/dev/null || true
) &
module_watchdog=$!
if . /app/apps/resetmodule >"$RUN/logs/module-reset.txt" 2>&1; then
    record_rc module_reset 0
else
    rc=$?; record_rc module_reset "$rc"; kill -TERM "$module_watchdog" 2>/dev/null || true; wait "$module_watchdog" 2>/dev/null || true; exit "$rc"
fi
if module load openfoam/2512 >"$RUN/logs/module-load.txt" 2>&1; then
    record_rc module_load_openfoam_2512 0
else
    rc=$?; record_rc module_load_openfoam_2512 "$rc"; kill -TERM "$module_watchdog" 2>/dev/null || true; wait "$module_watchdog" 2>/dev/null || true; exit "$rc"
fi
kill -TERM "$module_watchdog" 2>/dev/null || true
wait "$module_watchdog" 2>/dev/null || true
if [ -n "${LD_PRELOAD:-}" ]; then echo 'Inherited LD_PRELOAD is disallowed' >&2; exit 1; fi
unset PALS_CPU_BIND MPICH_RANK_ORDER MPICH_RANK_REORDER_FILE
export MPICH_RANK_REORDER_METHOD=0
phase complete module_setup

for tool in cc mpiexec ldd; do
    if command -v "$tool" >"$RUN/logs/$tool.path.txt" 2>&1; then record_rc "lookup_$tool" 0
    else rc=$?; record_rc "lookup_$tool" "$rc"; exit "$rc"; fi
done
seconds=$(remaining); [ "$seconds" -gt 5 ]
if timeout --signal=TERM --kill-after=2s "${seconds}s" cc --version >"$RUN/logs/cc-version.txt" 2>&1; then record_rc cc_version 0
else rc=$?; record_rc cc_version "$rc"; exit "$rc"; fi
seconds=$(remaining); [ "$seconds" -gt 5 ]
if timeout --signal=TERM --kill-after=2s "${seconds}s" mpiexec --version >"$RUN/logs/mpiexec-version.txt" 2>&1; then record_rc mpiexec_version 0
else rc=$?; record_rc mpiexec_version "$rc"; exit "$rc"; fi
printf 'OMP_NUM_THREADS=%s\nMPICH_RANK_REORDER_METHOD=%s\nPALS_CPU_BIND=unset\nMPICH_RANK_ORDER=unset\nMPICH_RANK_REORDER_FILE=unset\nLD_PRELOAD=empty\n' \
    "$OMP_NUM_THREADS" "$MPICH_RANK_REORDER_METHOD" >"$RUN/logs/selected-runtime-settings.txt"
: "${FOAM_LIBBIN:?OpenFOAM module did not set FOAM_LIBBIN}" "${FOAM_MPI:?OpenFOAM module did not set FOAM_MPI}"
pstream_path="$FOAM_LIBBIN/$FOAM_MPI/libPstream.so"
case "$pstream_path" in "$WM_PROJECT_DIR"/*) ;; *) echo 'Pstream path escaped WM_PROJECT_DIR' >&2; exit 1 ;; esac
printf '%s\n' "$pstream_path" >"$RUN/logs/pstream-path.txt"
[ -f "$pstream_path" ]
if timeout --signal=TERM --kill-after=2s 10s ldd "$pstream_path" >"$RUN/logs/pstream-ldd.txt" 2>&1; then record_rc pstream_ldd 0
else rc=$?; record_rc pstream_ldd "$rc"; exit "$rc"; fi

for item in baseline pin; do
    if [ "$item" = baseline ]; then source="$PAYLOAD/mpi-init-probe.c"; output="$RUN/mpi-init-probe"; else source="$PAYLOAD/postinit-pin-probe.c"; output="$RUN/postinit-pin-probe"; fi
    seconds=$(remaining); [ "$seconds" -gt 10 ]; [ "$seconds" -gt 30 ] && seconds=30
    phase start "compile_${item}"
    if timeout --signal=TERM --kill-after=3s "${seconds}s" cc -O0 -Wall -Wextra -Werror -o "$output" "$source" >"$RUN/logs/compile-${item}.stdout.txt" 2>"$RUN/logs/compile-${item}.stderr.txt"; then rc=0; else rc=$?; fi
    record_rc "compile_${item}" "$rc"; phase "exit=$rc" "compile_${item}"; [ "$rc" -eq 0 ]
    if timeout --signal=TERM --kill-after=2s 10s ldd "$output" >"$RUN/logs/ldd-${item}.txt" 2>&1; then record_rc "ldd_${item}" 0
    else rc=$?; record_rc "ldd_${item}" "$rc"; exit "$rc"; fi
    if grep -Fq '/mpich/8.1.15/' "$RUN/logs/ldd-${item}.txt"; then record_rc "mpich_8_1_15_${item}" 0
    else record_rc "mpich_8_1_15_${item}" 1; exit 1; fi
done

run_arm() {
    local arm=$1 executable=$2 output_dir=$3 seconds rc
    mkdir -p "$output_dir"
    seconds=$(remaining)
    if [ "$seconds" -le 0 ]; then rc=124
    else [ "$seconds" -gt 60 ] && seconds=60
        phase start "arm_${arm}"
        if (cd "$ROOT" && /usr/bin/time -v -o "$RUN/logs/arm-${arm}.resource.txt" timeout --signal=TERM --kill-after=5s "${seconds}s" mpiexec -n 512 "$executable" "$output_dir" >"$RUN/logs/arm-${arm}.stdout.txt" 2>"$RUN/logs/arm-${arm}.stderr.txt"); then rc=0; else rc=$?; fi
    fi
    record_rc "arm_${arm}" "$rc"
    phase "exit=$rc" "arm_${arm}"
    return "$rc"
}
arm_failure=0
if ! run_arm baseline "$RUN/mpi-init-probe" "$RUN/arms/baseline/native"; then arm_failure=1; fi
if ! run_arm postinit_pin "$RUN/postinit-pin-probe" "$RUN/arms/postinit_pin"; then arm_failure=1; fi
phase complete diagnostic_arms
if [ "$arm_failure" -eq 0 ]; then printf 'COLLECTION_FINISHED\n'; else printf 'COLLECTION_FINISHED_WITH_ARM_FAILURE\n'; fi
exit "$arm_failure"

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

# A watchdog bounds shell-sourced module setup while preserving its environment.
phase start module_setup
parent_pid=$BASHPID
(
    trap 'if [ -n "${sleeper:-}" ]; then kill "$sleeper" 2>/dev/null || true; fi; exit 0' TERM INT
    sleep 45 & sleeper=$!
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
test -z "${LD_PRELOAD:-}"
unset PALS_CPU_BIND MPICH_RANK_ORDER MPICH_RANK_REORDER_FILE
export MPICH_RANK_REORDER_METHOD=0
phase complete module_setup

for tool in cc mpiexec strace ldd; do
    if command -v "$tool" >"$RUN/logs/$tool.path.txt" 2>&1; then record_rc "lookup_$tool" 0
    else rc=$?; record_rc "lookup_$tool" "$rc"; exit "$rc"; fi
done
if timeout --signal=TERM --kill-after=2s 10s strace --version >"$RUN/logs/strace-version.txt" 2>&1; then record_rc strace_version 0
else rc=$?; record_rc strace_version "$rc"; exit "$rc"; fi
if timeout --signal=TERM --kill-after=2s 10s strace --help >"$RUN/logs/strace-help.txt" 2>&1; then record_rc strace_help 0
else rc=$?; record_rc strace_help "$rc"; exit "$rc"; fi
if grep -F -- '-k' "$RUN/logs/strace-help.txt" >/dev/null; then record_rc strace_stack_trace_option 0
else record_rc strace_stack_trace_option 1; echo 'strace help does not advertise -k stack traces' >&2; exit 1; fi
if timeout --signal=TERM --kill-after=2s 10s cc --version >"$RUN/logs/cc-version.txt" 2>&1; then record_rc cc_version 0
else rc=$?; record_rc cc_version "$rc"; exit "$rc"; fi
if timeout --signal=TERM --kill-after=2s 10s mpiexec --version >"$RUN/logs/mpiexec-version.txt" 2>&1; then record_rc mpiexec_version 0
else rc=$?; record_rc mpiexec_version "$rc"; exit "$rc"; fi
printf 'MPICH_RANK_REORDER_METHOD=%s\nOMP_NUM_THREADS=%s\n' "$MPICH_RANK_REORDER_METHOD" "$OMP_NUM_THREADS" >"$RUN/logs/selected-runtime-settings.txt"

phase start compile_native_probe
seconds=$(remaining)
if [ "$seconds" -le 0 ]; then rc=124
else
    if [ "$seconds" -gt 45 ]; then seconds=45; fi
    if timeout --signal=TERM --kill-after=3s "${seconds}s" cc -O0 -Wall -Wextra -o "$RUN/mpi-init-probe" "$PAYLOAD/mpi-init-probe.c" >"$RUN/logs/compile.stdout.txt" 2>"$RUN/logs/compile.stderr.txt"; then rc=0; else rc=$?; fi
fi
record_rc compile_native_probe "$rc"; phase "exit=$rc" compile_native_probe; test "$rc" -eq 0
if timeout --signal=TERM --kill-after=2s 10s ldd "$RUN/mpi-init-probe" >"$RUN/logs/probe-ldd.txt" 2>&1; then record_rc probe_ldd 0
else rc=$?; record_rc probe_ldd "$rc"; exit "$rc"; fi

phase start pstream_library_lookup
: "${FOAM_LIBBIN:?OpenFOAM module did not set FOAM_LIBBIN}" "${FOAM_MPI:?OpenFOAM module did not set FOAM_MPI}"
pstream_path="$FOAM_LIBBIN/$FOAM_MPI/libPstream.so"
case "$pstream_path" in "$WM_PROJECT_DIR"/*) ;; *) echo 'Native Pstream path escaped WM_PROJECT_DIR' >&2; exit 1 ;; esac
printf '%s\n' "$pstream_path" >"$RUN/logs/pstream-path.txt"
if [ -f "$pstream_path" ]; then rc=0; else rc=1; fi
record_rc pstream_library_lookup "$rc"; phase "exit=$rc" pstream_library_lookup
test "$rc" -eq 0
if timeout --signal=TERM --kill-after=2s 10s ldd "$pstream_path" >"$RUN/logs/pstream-ldd.txt" 2>&1; then record_rc pstream_ldd 0
else rc=$?; record_rc pstream_ldd "$rc"; exit "$rc"; fi

run_arm() {
    local arm=$1 mode=$2 rc seconds dir identity native
    dir="$RUN/arms/$arm"
    identity="$dir/entry"
    native="$dir/native"
    mkdir -p "$identity" "$native/pre"
    phase start "${arm}_native"
    seconds=$(remaining)
    if [ "$seconds" -le 0 ]; then rc=124
    else
        [ "$seconds" -gt 45 ] && seconds=45
        if /usr/bin/time -v -o "$RUN/logs/${arm}.resource.txt" timeout --signal=TERM --kill-after=5s "${seconds}s" \
             mpiexec -n 512 python3 "$PAYLOAD/rank-exec.py" "$mode" "$identity" \
             "$RUN/mpi-init-probe" "$(command -v strace)" "$native" \
             >"$RUN/logs/${arm}.stdout.txt" 2>"$RUN/logs/${arm}.stderr.txt"; then rc=0
        else rc=$?; fi
    fi
    record_rc "${arm}_native" "$rc"
    phase "exit=$rc" "${arm}_native"
}
run_arm untraced_control control
run_arm rank0_straced rank0-straced
phase complete diagnostic_arms
printf 'COLLECTION_FINISHED\n'

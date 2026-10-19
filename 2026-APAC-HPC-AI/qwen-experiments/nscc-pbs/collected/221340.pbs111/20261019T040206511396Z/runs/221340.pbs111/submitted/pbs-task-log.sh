#!/bin/bash
# Open the log on the compute task, before module/container startup.
set -euo pipefail
(( $# >= 2 )) || { echo 'Usage: pbs-task-log.sh ABSOLUTE_PREFIX COMMAND [ARG ...]' >&2; exit 2; }
prefix=$1
shift
[[ $prefix == /* ]] || { echo 'Task log prefix must be absolute' >&2; exit 2; }
# Existing run directory is created by topology-job.sh. Fail before execution
# if shared storage cannot create a private, unique task log.
original_umask=$(umask)
umask 077
log=$(mktemp -- "${prefix}.XXXXXXXX.log")
exec >>"$log" 2>&1
umask "$original_umask"
printf 'TASK_LOG_START utc=%s host=%s pid=%s log=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(hostname)" "$$" "$log"
# Do not print arguments or environment. Exec preserves PID, signals and status.
exec "$@"

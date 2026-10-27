#!/bin/bash
set -euo pipefail
if [ "$#" -lt 5 ] || [ "$4" != -- ]; then
    echo 'usage: rank-exec.sh RUN_ROOT ARM ADAPTER -- PROGRAM [ARG ...]' >&2
    exit 64
fi
RUN_ROOT=$1
ARM=$2
ADAPTER=$3
shift 4
case "$ARM" in with-adapter|pstream-checkmesh) ;; *) echo 'invalid arm name' >&2; exit 64 ;; esac
case "${PMI_RANK:-}" in ''|*[!0-9]*) echo 'missing or invalid PMI_RANK' >&2; exit 65 ;; esac
[ "$PMI_RANK" -ge 0 ] && [ "$PMI_RANK" -lt 512 ] || { echo 'PMI_RANK outside 0..511' >&2; exit 65; }
[ -z "${LD_PRELOAD:-}" ] || { echo 'LD_PRELOAD must be empty before target exec' >&2; exit 66; }
[ -z "${NSCC_LATEPIN_AUDIT_DIR:-}" ] || { echo 'adapter audit variable must not be inherited' >&2; exit 66; }
RUN_ROOT=$(realpath -e "$RUN_ROOT")
ADAPTER=$(realpath -e "$ADAPTER")
AUDIT_PARENT="$RUN_ROOT/arms/$ARM/adapter-ranks"
mkdir -p -m 700 "$AUDIT_PARENT"
AUDIT_PARENT=$(realpath -e "$AUDIT_PARENT")
case "$AUDIT_PARENT/" in "$RUN_ROOT/"*) ;; *) echo 'audit path escaped this PBS work root' >&2; exit 67 ;; esac
RANK_DIR=$(printf '%s/rank-%04d' "$AUDIT_PARENT" "$PMI_RANK")
mkdir -m 700 "$RANK_DIR"
# Set the audit directory and preload only in env immediately before exec of the target.
exec env NSCC_LATEPIN_AUDIT_DIR="$RANK_DIR" LD_PRELOAD="$ADAPTER" "$@"

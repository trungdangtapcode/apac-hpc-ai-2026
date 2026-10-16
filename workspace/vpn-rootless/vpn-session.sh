#!/usr/bin/env bash
set -uo pipefail
umask 077
VPN_SESSION_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
trap 'vpn_session_exit=$?; printf "VPN_WRAPPER_EXIT utc=%s code=%s\n" "$(date -u +%FT%TZ)" "$vpn_session_exit"' EXIT
trap 'exit 129' HUP
trap 'exit 143' TERM
trap 'exit 130' INT
printf 'VPN_WRAPPER_START utc=%s pid=%s ppid=%s\n' "$(date -u +%FT%TZ)" "$$" "$PPID"
bash "$VPN_SESSION_ROOT/vpn.sh" connect
exit $?

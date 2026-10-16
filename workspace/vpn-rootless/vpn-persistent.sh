#!/usr/bin/env bash
# Prepared launcher. Only `connect` authenticates; status/attach never start a login.
set -euo pipefail
umask 077
VPN_TERM_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
VPN_TERM_SOCKET="$VPN_TERM_ROOT/run/tmux.sock"
VPN_TERM_SESSION=nscc-vpn
mkdir -p "$VPN_TERM_ROOT/run" "$VPN_TERM_ROOT/private-logs"
chmod 700 "$VPN_TERM_ROOT/run" "$VPN_TERM_ROOT/private-logs"
case ${1:-help} in
  connect)
    if tmux -S "$VPN_TERM_SOCKET" has-session -t "$VPN_TERM_SESSION" 2>/dev/null; then
      echo 'Existing VPN terminal found; use attach or status. No new login started.'
      exit 0
    fi
    if bash "$VPN_TERM_ROOT/vpn.sh" enter true >/dev/null 2>&1; then
      echo 'An existing VPN process is present; no new login started.'
      exit 1
    fi
    VPN_TERM_LOG="$VPN_TERM_ROOT/private-logs/$(date -u +%Y%m%dT%H%M%SZ).log"
    touch "$VPN_TERM_LOG"
    chmod 600 "$VPN_TERM_LOG"
    # The tmux server owns the PTY; closing the caller does not close that PTY.
    tmux -S "$VPN_TERM_SOCKET" new-session -d -s "$VPN_TERM_SESSION" -c "$VPN_TERM_ROOT" \
      env HISTFILE=/dev/null bash --noprofile --norc
    tmux -S "$VPN_TERM_SOCKET" set-option -w -t "$VPN_TERM_SESSION" remain-on-exit on
    tmux -S "$VPN_TERM_SOCKET" pipe-pane -o -t "$VPN_TERM_SESSION" \
      "umask 077; cat >> '$VPN_TERM_LOG'"
    tmux -S "$VPN_TERM_SOCKET" send-keys -t "$VPN_TERM_SESSION" \
      "exec bash '$VPN_TERM_ROOT/vpn-session.sh'" Enter
    printf '%s\n' "$VPN_TERM_LOG" >"$VPN_TERM_ROOT/run/current-log-path"
    exec tmux -S "$VPN_TERM_SOCKET" attach-session -t "$VPN_TERM_SESSION"
    ;;
  attach)
    exec tmux -S "$VPN_TERM_SOCKET" attach-session -t "$VPN_TERM_SESSION"
    ;;
  status)
    tmux -S "$VPN_TERM_SOCKET" list-panes -t "$VPN_TERM_SESSION" \
      -F 'pane_pid=#{pane_pid} dead=#{pane_dead} exit=#{pane_dead_status}' 2>/dev/null || :
    bash "$VPN_TERM_ROOT/vpn.sh" enter ip -br addr
    ;;
  *)
    echo 'Usage: vpn-persistent.sh connect | attach | status'
    echo 'connect requires explicit user authorization and may request DUO.'
    ;;
esac

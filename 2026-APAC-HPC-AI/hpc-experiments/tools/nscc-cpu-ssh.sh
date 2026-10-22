#!/usr/bin/env bash
# Reuse the separately authenticated CPU SSH connection through the live VPN.
# The CPU hostname currently fails DNS in that namespace; its verified address
# is used with the original host-key alias. Authentication state stays outside Git.
set -euo pipefail
VPN_ROOT=/home/apacsc42/workspace/vpn-rootless
exec bash "$VPN_ROOT/vpn.sh" enter ssh -F /dev/null \
  -o BatchMode=yes -o ConnectTimeout=8 \
  -o ServerAliveInterval=15 -o ServerAliveCountMax=2 \
  -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$VPN_ROOT/known_hosts" \
  -o HostKeyAlias=aspire2a.nscc.sg -o PubkeyAuthentication=no \
  -o ControlMaster=auto -o ControlPersist=86400 \
  -o ControlPath="${NSCC_CPU_CONTROL_PATH:-$VPN_ROOT/run/cpu-r2-%C}" \
  "apacsc42@${NSCC_CPU_ADDRESS:-10.103.72.110}" "$@"

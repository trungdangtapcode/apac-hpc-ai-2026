#!/usr/bin/env bash
set -euo pipefail
VPN_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
case ${1:-help} in
  info)
    exec python3 "$VPN_ROOT/netns.py" "$VPN_ROOT/bin/snx-rs" --mode info \
      --server-name vpn1.nscc.sg --ca-cert "$VPN_ROOT/inspection/intermediate.pem"
    ;;
  shell)
    exec python3 "$VPN_ROOT/netns.py" bash --noprofile --norc
    ;;
  connect|connect-ipsec|connect-tcpt|connect-ssl)
    umask 077
    export APAC_VPN_PERSIST_CACHE="$VPN_ROOT/private-cache"
    tunnel_args=(--tunnel-type ssl)
    if [[ $1 != connect-ssl ]]; then
      transport=tcpt
      if [[ $1 == connect-ipsec ]]; then transport=udp; fi
      tunnel_args=(--tunnel-type ipsec --transport-type "$transport" --ike-lifetime 86400 --ike-persist true --use-internal-gateway-ip true
        --add-routes 10.103.71.15/32,10.103.71.16/32,10.103.72.200/32,10.103.86.73/32)
    fi
    exec python3 "$VPN_ROOT/netns.py" "$VPN_ROOT/bin/snx-rs" --mode standalone \
      --server-name vpn1.nscc.sg --ca-cert "$VPN_ROOT/inspection/intermediate.pem" \
      --login-type vpn_CISCOPROXY_LDAP --user-name apacsc42 \
      "${tunnel_args[@]}" --keychain false --no-dns true --log-level info
    ;;
  enter)
    shift
    exec python3 "$VPN_ROOT/enter.py" "$@"
    ;;
  ssh|ssh-batch)
    ssh_batch_args=()
    if [[ $1 == ssh-batch ]]; then ssh_batch_args=(-o BatchMode=yes); fi
    shift
    exec python3 "$VPN_ROOT/enter.py" ssh -F /dev/null \
      "${ssh_batch_args[@]}" \
      -o ConnectTimeout=10 -o ServerAliveInterval=10 -o ServerAliveCountMax=2 -o StrictHostKeyChecking=yes \
      -o ControlMaster=auto -o ControlPersist=86400 -o ControlPath="$VPN_ROOT/run/q-%C" \
      -o UserKnownHostsFile="$VPN_ROOT/known_hosts" \
      -o PubkeyAuthentication=no apacsc42@aspire2p.nscc.sg "$@"
    ;;
  run)
    shift
    exec python3 "$VPN_ROOT/netns.py" "$@"
    ;;
  *)
    echo 'Usage: bash vpn.sh info | connect | ssh [REMOTE_COMMAND...] | enter [COMMAND...] | shell | run COMMAND [ARGS...]'
    ;;
esac

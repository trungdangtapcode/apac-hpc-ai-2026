#!/usr/bin/env python3
"""Check namespace, tunnel and NSCC SSH transport without authenticating.

A namespace is created before VPN authentication. Its presence alone is never
reported as a usable VPN. No environment or private client state is inspected.
"""
from pathlib import Path
import datetime
import json
import subprocess

VPN = Path('/home/apacsc42/workspace/vpn-rootless/vpn.sh')
BODY = r'''
import json, socket, subprocess
result = {'state': 'TUNNEL_NOT_READY', 'ssh_authentication_tested': False}
p = subprocess.run(['ip', '-j', 'addr', 'show', 'dev', 'snx-tun'],
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
if p.returncode == 0:
    addresses = json.loads(p.stdout)
    ready = any('UP' in link.get('flags', []) and
                any(a.get('family') == 'inet' for a in link.get('addr_info', []))
                for link in addresses)
    if ready:
        result['state'] = 'TUNNEL_PRESENT_SSH_UNREACHABLE'
        try:
            with socket.create_connection(('10.103.72.110', 22), timeout=5) as peer:
                peer.settimeout(5)
                banner = peer.recv(256)
            if banner.startswith(b'SSH-'):
                result['state'] = 'SSH_SERVICE_REACHABLE_AUTH_UNTESTED'
        except OSError:
            pass
print(json.dumps(result))
'''


def check():
    observed = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p = subprocess.run(['bash', str(VPN), 'enter', 'python3', '-c', BODY],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, timeout=18)
        if p.returncode:
            result = {'state': 'NAMESPACE_UNAVAILABLE',
                      'ssh_authentication_tested': False,
                      'namespace_command_returncode': p.returncode}
        else:
            result = json.loads(p.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        result = {'state': 'PROBE_INCONCLUSIVE', 'ssh_authentication_tested': False}
    result['observed_utc'] = observed
    result['scope'] = ('Read-only transport probe. No credentials, private client output '
                       'or session material retained. SSH banner is not authenticated access.')
    return result


if __name__ == '__main__':
    print(json.dumps(check()))

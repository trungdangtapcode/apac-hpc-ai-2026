#!/usr/bin/env python3
"""Set NSCC DNS only inside our private mount/network namespace, then exec."""
import os
import ipaddress
import json
from pathlib import Path
import sys

for kind in ('net','mnt'):
    host=os.environ.pop('APAC_VPN_HOST_'+kind.upper()+'NS',None)
    if not host or host==os.readlink('/proc/self/ns/'+kind):
        raise SystemExit('Refusing to configure VPN DNS without separate network and mount namespaces')
if 'snx-tun:' in Path('/proc/net/dev').read_text():
    # Some supplied NSCC resolvers do not return the public gateway/login names.
    targets=json.loads((Path(__file__).resolve().parent/'inspection/targets.json').read_text())
    hosts=Path('/etc/hosts').read_text()
    for host in ('vpn1.nscc.sg','aspire2p.nscc.sg'):
        if host not in hosts:
            hosts+='\n'+str(ipaddress.ip_address(targets[host]))+' '+host+'\n'
    Path('/etc/hosts').write_text(hosts)
    Path('/etc/resolv.conf').write_text('nameserver 10.103.71.15\nnameserver 10.103.71.16\nsearch asp2a.nscc.sg\noptions timeout:2 attempts:2\n')
os.execvp(sys.argv[1],sys.argv[1:])

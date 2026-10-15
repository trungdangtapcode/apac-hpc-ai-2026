#!/usr/bin/env python3
"""Join a live namespace created by our own rootless VPN wrapper."""
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
matches=[]
for path in (ROOT/'run').glob('session-*/pid'):
    try:
        pid=int(path.read_text())
        command=Path(f'/proc/{pid}/cmdline').read_bytes()
        if str(ROOT/'bin/snx-rs').encode() in command and b'standalone' in command:
            matches.append(pid)
    except (OSError,ValueError):pass
if len(matches)!=1:raise SystemExit('Expected one live VPN session; start bash vpn.sh connect in another terminal.')
command=sys.argv[1:] or ['bash','--noprofile','--norc']
os.environ['APAC_VPN_HOST_NETNS']=os.readlink('/proc/self/ns/net')
os.environ['APAC_VPN_HOST_MNTNS']=os.readlink('/proc/self/ns/mnt')
os.execvp('nsenter',['nsenter','--target',str(matches[0]),'--user','--mount','--net',
                    '--preserve-credentials','--',sys.executable,str(ROOT/'inside.py'),*command])

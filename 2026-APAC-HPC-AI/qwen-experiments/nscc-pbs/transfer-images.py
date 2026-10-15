#!/usr/bin/env python3
"""Resume exact organiser images over the existing authenticated rootless VPN SSH."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import time

root=Path(__file__).resolve().parent
lock=(root/'image-transfer.lock').open('w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
ssh=['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh']
target='/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/'
status={'pid':os.getpid(),'started':time.time(),'images':{},'complete':False}
def save():
    p=root/'transfer-status.json';tmp=p.with_suffix('.tmp')
    tmp.write_text(json.dumps(status,indent=2)+'\n');tmp.replace(p)
def remote(command):
    return subprocess.check_output(ssh+['bash -lc '+shlex.quote(command)],text=True).strip()
save()
try:
    for name in ['aiperf.sqsh','sglang-harbor.sqsh']:
        src=Path('/scratch/enroot-images')/name;dst=target+name;part=dst+'.part'
        h=hashlib.sha256()
        with src.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
        digest=h.hexdigest();size=src.stat().st_size
        info={'bytes':size,'sha256':digest,'state':'CHECKING'}
        status['images'][name]=info;save()
        existing=remote('if [ -f '+shlex.quote(dst)+' ]; then sha256sum '+shlex.quote(dst)+'; fi')
        if existing and existing.split()[0]==digest:
            info['state']='VERIFIED';save();continue
        offset=int(remote('if [ -f '+shlex.quote(part)+' ]; then stat -c %s '+shlex.quote(part)+'; else echo 0; fi'))
        if offset>size:raise RuntimeError('Remote partial file exceeds source size')
        info.update(state='TRANSFERRING',resumed_from=offset);save()
        print('TRANSFERRING',name,'offset',offset,'size',size,flush=True)
        if offset<size:
            with src.open('rb') as stream:
                stream.seek(offset)
                subprocess.run(ssh+['bash -lc '+shlex.quote('cat >> '+shlex.quote(part))],
                               stdin=stream,check=True)
        actual=remote('sha256sum '+shlex.quote(part)).split()[0]
        if actual!=digest:raise RuntimeError('SHA256 mismatch for '+name)
        remote('mv -- '+shlex.quote(part)+' '+shlex.quote(dst))
        info.update(state='VERIFIED',finished=time.time());save()
        print('VERIFIED',name,digest,flush=True)
    status['complete']=True
except Exception as exc:
    status['error']=str(exc)
    print('FAILED',str(exc),flush=True)
finally:
    status['finished']=time.time();save()
raise SystemExit(0 if status['complete'] else 1)

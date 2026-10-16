#!/usr/bin/env python3
"""Run one command with rootless networking; host routes and DNS stay unchanged."""
import json
import os
from pathlib import Path
import select
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parent

def child(session,command):
    session=Path(session)
    os.umask(0o077)
    # Only this mount namespace sees these files and runtime directory.
    hosts=Path('/etc/hosts').read_text()+'\n'+(session/'hosts-extra').read_text()
    (session/'hosts').write_text(hosts)
    (session/'resolv.conf').write_text('nameserver 10.0.2.3\noptions timeout:3 attempts:2\n')
    for source,target in ((session/'hosts','/etc/hosts'),(session/'resolv.conf','/etc/resolv.conf')):
        subprocess.run(['mount','--bind',str(source),target],check=True)
    subprocess.run(['mount','-t','tmpfs','-o','mode=755','tmpfs','/run'],check=True)
    cache=os.environ.get('APAC_VPN_PERSIST_CACHE')
    if cache:
        # Private mount only: SQLite session state survives namespace teardown.
        # Never replace the host's /var/cache or write session state into notes.
        subprocess.run(['mount','--bind',cache,'/var/cache'],check=True)
    (session/'pid').write_text(str(os.getpid()))
    deadline=time.monotonic()+20
    while not (session/'network-ready').exists():
        if time.monotonic()>deadline:raise RuntimeError('Rootless network helper did not become ready')
        time.sleep(.05)
    os.execvp(command[0],command)

def dns_ip(host):
    try:return socket.gethostbyname(host)
    except socket.gaierror:
        with urllib.request.urlopen('https://dns.google/resolve?name='+host+'&type=A',timeout=12) as response:
            result=json.load(response)
        return next(a['data'] for a in result.get('Answer',[]) if a['type']==1)

def main(command):
    if not command:raise SystemExit('Usage: netns.py COMMAND [ARGS...]')
    children=[]
    cache=os.environ.get('APAC_VPN_PERSIST_CACHE')
    if cache:
        path=Path(cache)
        path.mkdir(mode=0o700,parents=True,exist_ok=True)
        if path.stat().st_uid!=os.getuid():raise RuntimeError('VPN cache is not owned by current user')
        path.chmod(0o700)
        (path/'snx-rs').mkdir(mode=0o700,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='session-',dir=ROOT/'run') as temp:
        session=Path(temp)
        targets={host:dns_ip(host) for host in ('vpn1.nscc.sg','aspire2p.nscc.sg')}
        (session/'hosts-extra').write_text(''.join(ip+' '+host+'\n' for host,ip in targets.items()))
        (ROOT/'inspection/targets.json').write_text(json.dumps(targets,indent=2)+'\n')
        try:
            proc=subprocess.Popen(['unshare','--user','--map-root-user','--net','--mount',
                                   '--propagation','private',sys.executable,str(Path(__file__).resolve()),
                                   '--child',str(session),*command])
            children.append(proc);deadline=time.monotonic()+10
            while not (session/'pid').exists():
                if proc.poll() is not None:raise RuntimeError('Cannot initialize private network/mount namespace')
                if time.monotonic()>deadline:raise RuntimeError('Namespace initialization timeout')
                time.sleep(.05)
            pid=int((session/'pid').read_text())
            read_fd,write_fd=os.pipe()
            try:
                helper=subprocess.Popen([str(ROOT/'bin/slirp4netns'),'--configure','--disable-host-loopback',
                                         '--mtu','1500','--ready-fd',str(write_fd),str(pid),'tap0'],
                                         pass_fds=(write_fd,),stdout=subprocess.DEVNULL)
                children.append(helper);os.close(write_fd);write_fd=None
                if not select.select([read_fd],[],[],15)[0] or os.read(read_fd,1)!=b'1':
                    raise RuntimeError('slirp4netns failed before network readiness')
            finally:
                os.close(read_fd)
                if write_fd is not None:os.close(write_fd)
            (session/'network-ready').touch()
            return proc.wait()
        finally:
            for proc in reversed(children):
                if proc.poll() is None:proc.terminate()
            for proc in reversed(children):
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()

if __name__=='__main__':
    try:
        if len(sys.argv)>1 and sys.argv[1]=='--child':child(sys.argv[2],sys.argv[3:])
        else:
            (ROOT/'run').mkdir(mode=0o700,exist_ok=True)
            raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:raise SystemExit(130)

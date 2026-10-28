#!/usr/bin/env python3
"""Report only filesystem capacity and the resolved Enroot data path."""
import json,os,re,subprocess
from pathlib import Path
r=subprocess.run(['enroot','info'],capture_output=True,text=True,timeout=10,check=True)
paths=[]
for line in r.stdout.splitlines():
 m=re.match(r'\s*ENROOT_DATA_PATH=(.+)$',line)
 if m:paths.append(m[1])
assert len(paths)==1,'Cannot resolve node-local Enroot data path'
data=Path(paths[0]);probe=data
while not probe.exists():probe=probe.parent
s=os.statvfs(probe);free=s.f_bavail*s.f_frsize
# The first node hosts two prefills, router and transient warmup rootfs.
# A 32 GiB per-root bound rounds up the 28.531 GiB observed image content.
minimum=(4 if os.environ['SLURM_PROCID']=='0' else 1)*32*1024**3
obj={'host':os.uname().nodename,'rank':int(os.environ['SLURM_PROCID']),'resolved_enroot_data_path':str(data),'filesystem_probe_path':str(probe),'available_bytes':free,'required_bytes':minimum,'capacity_ok':free>=minimum,'scope':'Read-only capacity estimate, not actual Pyxis image launch or GPU replay.'}
print(json.dumps(obj),flush=True)

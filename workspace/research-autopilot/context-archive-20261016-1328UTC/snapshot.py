"""Cheap queue/transfer change detection; force a research wake every six hours."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

root=Path(__file__).resolve().parent
research=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
parts={}
try:
    p=subprocess.run(['squeue','-h','-u','apacsc42','-o','%i|%T|%R'],
                     capture_output=True,text=True,timeout=15)
    parts['queue']=p.stdout if p.returncode==0 else 'scheduler-error'
except (OSError,subprocess.TimeoutExpired):
    parts['queue']='scheduler-unavailable'
try:
    p=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh',
                      'ssh-batch',"bash -lc 'qstat -u apacsc42'"],
                     capture_output=True,text=True,timeout=20)
    # Keep only ID/state: elapsed runtime would force a wake every check.
    rows=[]
    for line in p.stdout.splitlines():
        fields=line.split()
        if fields and '.pbs' in fields[0] and len(fields)>=11:
            rows.append([fields[0],fields[-2]])
    parts['pbs_queue']=sorted(rows) if p.returncode==0 else 'ssh-or-pbs-unavailable'
except (OSError,subprocess.TimeoutExpired):
    parts['pbs_queue']='ssh-or-pbs-unavailable'
for relative in ['serving-tuning/registry.json','nscc-pbs/transfer-status.json']:
    path=research/relative
    try:
        obj=json.loads(path.read_text())
        # Registry refresh timestamps alone must not wake another model turn.
        def stable(value):
            if isinstance(value,dict):
                return {k:stable(v) for k,v in value.items()
                        if not any(x in k.lower() for x in ('updated','refreshed','checked','timestamp'))}
            if isinstance(value,list):return [stable(v) for v in value]
            return value
        parts[relative]=stable(obj)
    except (OSError,ValueError):parts[relative]=None
digest=hashlib.sha256(json.dumps(parts,sort_keys=True).encode()).hexdigest()
state_path=root/'last-wake.json'
try:old=json.loads(state_path.read_text())
except (OSError,ValueError):old={}
now=time.time()
due=(root/'FORCE').exists() or digest!=old.get('digest') or now-old.get('time',0)>=21600
print(json.dumps({'time':now,'digest':digest,'due':due,'queue':parts['queue']}))
if due:
    state_path.write_text(json.dumps({'time':now,'digest':digest})+'\n')
    (root/'FORCE').unlink(missing_ok=True)
raise SystemExit(0 if due else 3)

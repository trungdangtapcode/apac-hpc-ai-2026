"""Cheap semantic job events only; no LLM for queue-reason/timestamp changes."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent
RESEARCH=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')

def slurm_rows(text):
    # Reason Priority/Resources and elapsed time are deliberately absent.
    return sorted([line.strip().split('|')[:2] for line in text.splitlines() if line.strip()])

def pbs_rows(text):
    rows=[]
    for line in text.splitlines():
        fields=line.split()
        if fields and '.pbs' in fields[0] and len(fields)>=11:
            rows.append([fields[0],fields[-2]])
    return sorted(rows)

def registry_events(registry):
    return sorted([dict(id=e['id'],state=e.get('state'),
        attempts=[dict(job=a.get('job'),state=a.get('state')) for a in e.get('attempts',[])],
        missing_ns=e.get('missing_ns'),benchmark_complete=e.get('benchmark_complete'),
        profile_complete=e.get('profile_complete')) for e in registry.get('entries',[])],key=lambda e:e['id'])

def signature(parts):
    return hashlib.sha256(json.dumps(parts,sort_keys=True).encode()).hexdigest()

def snapshot():
    parts={}
    try:
        p=subprocess.run(['squeue','-h','-u','apacsc42','-o','%i|%T'],capture_output=True,text=True,timeout=15)
        parts['slurm']=slurm_rows(p.stdout) if p.returncode==0 else 'scheduler-error'
    except (OSError,subprocess.TimeoutExpired):parts['slurm']='scheduler-unavailable'
    try:
        p=subprocess.run(['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch',"bash -lc 'qstat -u apacsc42'"],capture_output=True,text=True,timeout=20)
        parts['pbs']=pbs_rows(p.stdout) if p.returncode==0 else 'ssh-or-pbs-unavailable'
    except (OSError,subprocess.TimeoutExpired):parts['pbs']='ssh-or-pbs-unavailable'
    try:parts['registry']=registry_events(json.loads((RESEARCH/'serving-tuning/registry.json').read_text()))
    except (OSError,ValueError):parts['registry']=None
    try:
        transfer=json.loads((RESEARCH/'nscc-pbs/transfer-status.json').read_text())
        parts['transfer']={'complete':transfer.get('complete'),'states':{k:v.get('state') for k,v in transfer.get('images',{}).items()}}
    except (OSError,ValueError):parts['transfer']=None
    return parts

def main():
    parts=snapshot();digest=signature(parts);path=ROOT/'last-wake.json'
    try:old=json.loads(path.read_text())
    except (OSError,ValueError):old={}
    now=time.time();forced=(ROOT/'FORCE').exists()
    due=forced or digest!=old.get('digest') or now-old.get('time',0)>=21600
    print(json.dumps({'time':now,'digest':digest,'due':due,'forced':forced,
                      'queue':parts['slurm'],'pbs_queue':parts['pbs']}))
    if due:
        path.write_text(json.dumps({'time':now,'digest':digest})+'\n')
        (ROOT/'FORCE').unlink(missing_ok=True)
    return 0 if due else 3

if __name__=='__main__':raise SystemExit(main())

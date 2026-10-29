#!/usr/bin/env python3
"""Reclaim only this user's disposable native roots from terminal Slurm jobs."""
import argparse,json,os,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--include-current',action='store_true');a=p.parse_args()
rows=[]; roots=[]
for d in Path('/tmp').glob('apacsc42-native-*'):
 m=re.fullmatch(r'apacsc42-native-(\d+)-[\w.]+',d.name)
 if m and not d.is_symlink() and d.is_dir() and d.stat().st_uid==os.getuid():roots.append((d,m[1]))
ids=sorted({j for d,j in roots}); states={}
if ids:
 r=subprocess.run(['sacct','-n','-P','-X','-j',','.join(ids),'--format=JobID,User,State'],capture_output=True,text=True,timeout=15,check=True)
 for line in r.stdout.splitlines():
  cols=line.split('|')
  if len(cols)>=3 and cols[1]=='apacsc42':states[cols[0]]=cols[2].split()[0].rstrip('+')
terminal={'COMPLETED','FAILED','CANCELLED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','PREEMPTED','BOOT_FAIL','DEADLINE'}
for d,j in roots:
 allowed=states.get(j) in terminal or (a.include_current and j==os.environ.get('SLURM_JOB_ID'))
 row={'path':str(d),'job':j,'state':states.get(j),'allowed':allowed};rows.append(row)
 if not allowed:continue
 env=os.environ.copy();env['ENROOT_DATA_PATH']=str(d)
 # Enroot owns removal semantics; never recurse outside this exact owned root.
 r=subprocess.run(['enroot','remove','--force','rootfs'],env=env,capture_output=True,text=True,timeout=45)
 row.update(remove_returncode=r.returncode,remove_stderr=r.stderr[-600:])
 try:d.rmdir();row['removed']=True
 except OSError as exc:row.update(removed=False,error=str(exc))
s=os.statvfs('/tmp');print(json.dumps({'host':os.uname().nodename,'free_bytes':s.f_bavail*s.f_frsize,'roots':rows},indent=2))
assert all(not r['allowed'] or r.get('removed') for r in rows),'Some allowed native roots could not be removed'

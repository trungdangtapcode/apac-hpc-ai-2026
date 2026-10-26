#!/usr/bin/env python3
"""Seal terminal evidence and compare observed resources without causal claims."""
from pathlib import Path
import collections,datetime,hashlib,json,statistics,subprocess
Q=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;A=Q/'runs/26315'
state=subprocess.check_output(['sacct','-X','-j','26315','-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True);assert 'COMPLETED|0:0' in state
assert '26315' not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
(A/'scheduler-accounting.psv').write_text(state)
seal=A/'artifact-manifest.json'
if not seal.exists():
 files=[]
 for p in sorted(A.rglob('*')):
  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p.name=='artifact-manifest.json':continue
  before=p.stat();h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),p
  files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':h.hexdigest()})
 for p in (Q/'runs/26315.out',Q/'runs/26315.err'):
  files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 seal.write_text(json.dumps({'job':26315,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':state,'files':files},indent=2)+'\n')

#!/usr/bin/env python3
"""Seal terminal failed warmup evidence, without changing submitted payloads."""
from pathlib import Path
import datetime,hashlib,json,subprocess
S=Path(__file__).resolve().parent;Q=S.parent
for job in [26849,26851,26853]:
 a=Q/f'runs/{job}';state=subprocess.check_output(['sacct','-X','-j',str(job),'-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True);assert f'{job}|FAILED|1:0|' in state
 assert str(job) not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
 (a/'scheduler-accounting.psv').write_text(state)
 manifest=a/'artifact-manifest.json'
 if manifest.exists():continue
 files=[]
 for p in sorted(a.rglob('*')):
  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p.name=='artifact-manifest.json':continue
  before=p.stat();h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':h.hexdigest()})
 for p in [Q/f'runs/{job}.out',Q/f'runs/{job}.err']:files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 manifest.write_text(json.dumps({'job':job,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':state,'files':files},indent=2)+'\n')
print('Failed tokenizer warmup artifacts sealed')

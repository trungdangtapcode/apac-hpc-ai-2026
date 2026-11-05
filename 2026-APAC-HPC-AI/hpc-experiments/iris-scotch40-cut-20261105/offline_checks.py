#!/usr/bin/env python3
"""Offline integrity, syntax, and synthetic exact-count tests for N40 cut."""
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent; P=ROOT/'payload'
M=json.loads((P/'payload-sha256.json').read_text())['files']
def check(ok,label):
 print(('PASS ' if ok else 'FAIL ')+label)
 if not ok: raise SystemExit(1)
expected=['expected-mesh.json','job.sbatch','validate-cut.py','verify-payload.py']
expected += [f.relative_to(P).as_posix() for f in sorted((P/'payload-case').rglob('*')) if f.is_file()]
check(sorted(M)==sorted(expected),'manifest covers exact payload file set')
for name,digest in M.items():
 f=P/name; check(f.is_file() and not f.is_symlink() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,'sha256 '+name)
r=subprocess.run([sys.executable,str(P/'verify-payload.py'),str(P)],capture_output=True,text=True)
check(r.returncode==0,'pinned payload verifier')
r=subprocess.run([sys.executable,'-m','py_compile',str(P/'validate-cut.py'),str(P/'verify-payload.py')],capture_output=True,text=True)
check(r.returncode==0,'Python syntax')
r=subprocess.run(['bash','-n',str(P/'job.sbatch')],capture_output=True,text=True)
check(r.returncode==0,'Slurm shell syntax')
base,rem=divmod(65334765,40)
for n,should_pass in ((40,True),(39,False),(41,False)):
 with tempfile.TemporaryDirectory(prefix='scotch40-cut-check-') as td:
  c=Path(td); (c/'logFiles').mkdir(); (c/'system/include').mkdir(parents=True)
  (c/'system/include/caseDefinition').write_text('nCores 40;\ndecompositionMethod scotch;\n')
  lines=['version=v2512 scalar=64']+[f'Number of cells = {base+(i<rem)}' for i in range(40)]+['End']
  (c/'logFiles/decomposePar.log').write_text('\n'.join(lines)+'\n')
  for i in range(n):
   q=c/f'processor{i}'; (q/'constant/polyMesh').mkdir(parents=True); (q/'constant/polyMesh/boundary').write_text('synthetic\n'); (q/'0').mkdir()
   for field in ('U','p','k','omega','nut','nuTilda'): (q/'0'/field).write_text('synthetic\n')
  r=subprocess.run([sys.executable,str(P/'validate-cut.py'),'--case',str(c),'--output',str(c/'out.json')],capture_output=True,text=True)
  check((r.returncode==0)==should_pass,f'synthetic processor count {n}')

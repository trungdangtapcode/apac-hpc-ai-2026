#!/usr/bin/env python3
"""Offline runtime-gate fixtures, never real backend acceptance."""
from pathlib import Path
import json,tempfile,subprocess,shutil,re,hashlib
D=Path(__file__).resolve().parent;Q=D.parent;b=Q/'serving-tuning-11/s96-h200-prefill-flashinfer-page1'
checks=[]
with tempfile.TemporaryDirectory(prefix='ap42-fi-p1-fixture-') as tmp:
 t=Path(tmp);shutil.copy2(b/'config.json',t/'config.json');shutil.copy2(b/'check-fast-runtime.py',t/'check-fast-runtime.py')
 for role in ['prefill-0','prefill-1','decode-0']:
  s=(Q/f'runs/26949/{role}.log').read_text()
  if role.startswith('prefill'):
   s,n=re.subn(r"(?<![a-z_])attention_backend='fa3'", "attention_backend='flashinfer'",s);assert n==1,n
  (t/f'{role}.log').write_text(s)
 def run():return subprocess.run(['python3','-B',str(t/'check-fast-runtime.py'),str(t),'control'],capture_output=True,text=True)
 r=run();assert r.returncode==0,r.stdout+r.stderr;checks.append('synthetic intended arguments PASS (not GPU proof)')
 p=t/'prefill-0.log';s=p.read_text();p.write_text(s.replace("attention_backend='flashinfer'","attention_backend='fa3'"));r=run();assert r.returncode!=0 and 'attention_backend' in r.stderr;checks.append('FA3 fallback rejected');p.write_text(s)
 p.write_text(re.sub(r'(?<![a-z_])page_size=1,','page_size=16,',s));r=run();assert r.returncode!=0 and 'page_size' in r.stderr;checks.append('page16 rejected');p.write_text(s)
 p=t/'decode-0.log';s=p.read_text();p.write_text(re.sub(r"(?<![a-z_])attention_backend='fa3'","attention_backend='flashinfer'",s));r=run();assert r.returncode!=0 and 'attention_backend' in r.stderr;checks.append('unintended decode-worker backend change rejected')
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,stdout=subprocess.DEVNULL,check=True)
(D/'validation.json').write_text(json.dumps({'state':'OFFLINE_PASS_NOT_GPU_ACCEPTANCE','checks':checks,'manifest_sha256':hashlib.sha256((b/'SHA256SUMS').read_bytes()).hexdigest()},indent=2)+'\n');print(json.dumps(checks))

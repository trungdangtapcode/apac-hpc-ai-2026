#!/usr/bin/env python3
"""Verify intended argument/selected-rank gate and adversarial fallbacks offline."""
from pathlib import Path
import json,re,shutil,subprocess,tempfile
D=Path(__file__).resolve().parent;Q=D.parent;b=Q/'serving-tuning-11/s97-h200-prefill-mnnvl';checks=[]
with tempfile.TemporaryDirectory(prefix='ap42-p-mnnvl-') as tmp:
 t=Path(tmp)
 for name in ['config.json','check-fast-runtime.py']:shutil.copy2(b/name,t/name)
 for role in ['prefill-0','prefill-1','decode-0']:
  s=(Q/f'runs/26949/{role}.log').read_text()
  if role.startswith('prefill'):
   s,n=re.subn("flashinfer_allreduce_fusion_backend='auto'","flashinfer_allreduce_fusion_backend='mnnvl'",s);assert n==1
   s=s.replace('workspace initialized: backend=trtllm','workspace initialized: backend=mnnvl')
  (t/f'{role}.log').write_text(s)
 def run():return subprocess.run(['python3','-B',str(t/'check-fast-runtime.py'),str(t),'control'],capture_output=True,text=True)
 r=run();assert r.returncode==0,r.stdout+r.stderr;checks.append('synthetic intended arguments and all startup ranks accepted; not GPU proof')
 p=t/'prefill-0.log';base=p.read_text()
 p.write_text(base.replace("flashinfer_allreduce_fusion_backend='mnnvl'","flashinfer_allreduce_fusion_backend='auto'"));r=run();assert r.returncode!=0 and 'flashinfer_allreduce_fusion_backend' in r.stderr;checks.append('silent auto setting rejected')
 p.write_text(base.replace('workspace initialized: backend=mnnvl','workspace initialized: backend=trtllm'));r=run();assert r.returncode!=0;checks.append('actual TRTLLM selection rejected')
 p.write_text('\n'.join(line for line in base.splitlines() if not ('workspace initialized: backend=mnnvl, rank=3, world_size=4' in line))+'\n');r=run();assert r.returncode!=0 and 'four' in r.stderr;checks.append('missing TP3 startup rank rejected')
 p.write_text(base.replace("attention_backend='fa3'","attention_backend='flashinfer'"));r=run();assert r.returncode!=0 and 'attention_backend' in r.stderr;checks.append('unintended attention backend change rejected')
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,stdout=subprocess.DEVNULL,check=True)
(D/'validation.json').write_text(json.dumps({'state':'OFFLINE_PASS_NOT_GPU_ACCEPTANCE','fixtures':checks},indent=2)+'\n');print(json.dumps(checks))

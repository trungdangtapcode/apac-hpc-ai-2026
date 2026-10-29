#!/usr/bin/env python3
"""Adversarial CPU runtime/geometry fixtures; no actual candidate inference proof."""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,shutil,subprocess,tempfile
D=Path(__file__).resolve().parent;Q=D.parent;B=Q/'serving-tuning-11/s98-h200-shallow-eagle12';checks=[]
with tempfile.TemporaryDirectory(prefix='ap42-eagle12-fixtures-') as tmp:
 t=Path(tmp)
 for name in ['config.json','check-fast-runtime.py']:shutil.copy2(B/name,t/name)
 for role in ['prefill-0','prefill-1']:(t/f'{role}.log').write_bytes((Q/f'runs/26949/{role}.log').read_bytes())
 s=(Q/'runs/25998/decode-0.log').read_text()
 s,n=re.subn(r'speculative_num_steps=2,','speculative_num_steps=1,',s);assert n==1
 s,n=re.subn(r'speculative_num_draft_tokens=3,','speculative_num_draft_tokens=2,',s);assert n==1
 s=re.sub(r'(Capture target verify CUDA graph begin\. backend=full, num_tokens_per_req=)3',r'\g<1>2',s)
 s=re.sub(r'(Capture draft extend CUDA graph begin\. backend=full, num_tokens_per_req=)3',r'\g<1>2',s)
 s='\n'.join(x for x in s.splitlines() if not re.search(r'Capture draft decode CUDA graph (begin|end)\.',x))+'\n'
 p=t/'decode-0.log';p.write_text(s)
 def run():return subprocess.run(['python3','-B',str(t/'check-fast-runtime.py'),str(t),'candidate','64'],capture_output=True,text=True)
 r=run();assert r.returncode==0,r.stdout+r.stderr;checks.append('Intended one-step synthetic native runtime PASS; not GPU proof')
 bad=[('wrong steps',s.replace('speculative_num_steps=1,','speculative_num_steps=2,'),'speculative_num_steps'),('wrong tokens',s.replace('speculative_num_draft_tokens=2,','speculative_num_draft_tokens=3,'),'speculative_num_draft_tokens'),('missing target TP7 graph','\n'.join(x for x in s.splitlines() if not ('TP7 EP7] Capture target verify CUDA graph end.' in x))+'\n','graph capture'),('missing TP7 draft weights','\n'.join(x for x in s.splitlines() if not ('TP7 EP7] Load weight end.' in x and 'type=LlamaForCausalLMEagle3' in x))+'\n','draft model'),('stale draft decode marker',s+'[TP0 EP0] Capture draft decode CUDA graph begin. backend=full, num_tokens_per_req=1\n','one-step')]
 for label,text,reason in bad:
  p.write_text(text);r=run();assert r.returncode!=0 and reason in r.stderr,(label,r.stdout,r.stderr);checks.append('Reject '+label)
 p.write_text(s);pp=t/'prefill-0.log';raw=pp.read_text();pp.write_text(raw.replace('speculative_algorithm=None,',"speculative_algorithm='EAGLE3',"));r=run();assert r.returncode!=0 and 'speculative_algorithm' in r.stderr;checks.append('Reject draft enabled on prefill')
 # The geometry validator is byte-identical to the proven S61 version.
 assert (B/'validate_kv_geometry.py').read_bytes()==(Q/'runs/25998/submitted-payload/validate_kv_geometry.py').read_bytes()
 src=Q/'runs/25998/kv-geometry';g=t/'geometry';shutil.copytree(src,g)
 exp=json.loads(next(g.glob('*.json')).read_text())['experiment_id']
 cmd=['python3','-B',str(B/'validate_kv_geometry.py'),str(g),'--experiment-id',exp,'--expected-role','prefill-0=4','--expected-role','prefill-1=4','--expected-role','decode-0=8','--decode-draft','1']
 r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;v=json.loads(r.stdout);assert v['receipt_count']==32 and v['decode_draft_regions']['observed_regions_per_rank']==190;checks.append('Existing actual 188P/190D geometry replay PASS; not new candidate proof')
 gp=next(x for x in g.glob('*.json') if json.loads(x.read_text())['role_name']=='decode-0');doc=json.loads(gp.read_text());doc['kv_regions'].pop();gp.write_text(json.dumps(doc));r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode!=0;checks.append('Reject changed decode region count')
for p in B.rglob('*'):
 if p.suffix=='.py':ast.parse(p.read_text())
 if p.suffix in ['.sh','.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
(D/'validation.json').write_text(json.dumps({'state':'OFFLINE_FIXTURES_PASS_NOT_CANDIDATE_GPU_ACCEPTANCE','checks':checks},indent=2)+'\n');print(json.dumps(checks,indent=2))

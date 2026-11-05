"""Collect bounded initialization logs and seal the initialized 48-rank source."""
from pathlib import Path
import sys,json,hashlib,base64,tarfile,io
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E.parent/'tools'));from iris_bridge import run_json
root=json.loads((E/'deployment.json').read_text())['root']
seal=(E.parent/'iris-solver-rank-interleave40-20261105/seal_tree.py').read_text().replace('from __future__ import annotations','').replace('range(56)','range(48)')
body='ROOT='+repr(root)+'\nSEAL='+repr(seal)+'''\nfrom pathlib import Path
import hashlib,base64,subprocess,datetime,os
r=Path(ROOT);files={}
paths=sorted((r/'init-runs').glob('2294915-*'))+sorted((r/'init-runs').glob('2294915.sbatch.*'))+[r/'artifacts/cut-N48-scotch/READY']
assert 15<len(paths)<50
for p in paths:
 assert p.is_file() and not p.is_symlink();b=p.read_bytes();assert len(b)<1500000;files[str(p.relative_to(r))]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'base64':base64.b64encode(b).decode()}
p=subprocess.run(['sacct','-j','2294915','--noheader','--parsable2','-o','JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=20)
scope={'__name__':'source_inventory'};exec(compile(SEAL,'<frozen-inventory48>','exec'),scope,scope)
src=r/'artifacts/cut-N48-scotch';core=scope['inventory'](src);extra={};directories=[]
for base,dirs,names in os.walk(src,followlinks=False):
 for name in dirs:
  q=Path(base)/name
  if not q.is_symlink():directories.append(str(q.relative_to(src)))
 for name in names:
  q=Path(base)/name;rel=str(q.relative_to(src))
  if rel not in core['files'] and rel not in core['symlinks']:
   assert q.is_file() and not q.is_symlink();extra[rel]=scope['sha256'](q)
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','root':ROOT,'files':files,'accounting':{'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr},'accepted_source_manifest':core,'supplementary_source_manifest':{'source':str(src),'files':extra,'symlinks':{},'directories':sorted(directories)},'inventory_code_sha256':hashlib.sha256(SEAL.encode()).hexdigest()}
'''
r=run_json(body,timeout=120);out=E/'completed-2294915';out.mkdir(exist_ok=True)
with tarfile.open(out/'raw-evidence.tar.gz','w:gz') as tar:
 for name,item in r['files'].items():
  b=base64.b64decode(item.pop('base64'));assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'];p=out/'collected'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);ti=tarfile.TarInfo(name);ti.size=len(b);tar.addfile(ti,io.BytesIO(b))
for key in ['accepted_source_manifest','supplementary_source_manifest']:(E/(key.replace('_','-')+'.json')).write_text(json.dumps(r.pop(key),indent=2,sort_keys=True)+'\n')
(out/'collection.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'files':len(r['files']),'accounting':r['accounting']}))

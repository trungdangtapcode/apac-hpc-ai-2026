from pathlib import Path
import sys,json,hashlib,base64,tarfile,io
E=Path('/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch40-cut-20261105');sys.path.insert(0,str(E.parent/'tools'));from iris_bridge import run_json
root=json.loads((E/'deployment.json').read_text())['root']
body='ROOT='+repr(root)+'''\nfrom pathlib import Path
import hashlib,base64,subprocess,datetime
r=Path(ROOT);paths=['kit/runs/2294919.out','kit/runs/2294919.err','kit/runs/2294919-source-before.json','kit/runs/2294919-source-after.json','kit/runs/2294919-mesh-before.json','kit/runs/2294919-cut-validation.json','kit/runs/2294919-hardware.log','artifacts/cut-N40-scotch/logFiles/decomposePar.log','artifacts/cut-N40-scotch/logFiles/decomposePar.resource.txt','artifacts/cut-N40-scotch/logFiles/restore0Dir.log']
files={}
for name in paths:
 p=r/name;assert p.is_file() and not p.is_symlink();b=p.read_bytes();assert len(b)<2000000;files[name]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'base64':base64.b64encode(b).decode()}
p=subprocess.run(['sacct','-j','2294919','--noheader','--parsable2','-o','JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=20)
result={'utc':datetime.datetime.utcnow().isoformat()+'Z','root':ROOT,'files':files,'accounting':{'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}}
'''
r=run_json(body,timeout=60);out=E/'completed-2294919';out.mkdir(exist_ok=True)
with tarfile.open(out/'raw-evidence.tar.gz','w:gz') as tar:
 for name,item in r['files'].items():
  b=base64.b64decode(item.pop('base64'));assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'];p=out/'collected'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);ti=tarfile.TarInfo(name);ti.size=len(b);tar.addfile(ti,io.BytesIO(b))
(out/'collection.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'files':len(r['files']),'accounting':r['accounting']}))

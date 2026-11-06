"""Collect exact terminal initialization evidence and inventories without copying mesh fields."""
from pathlib import Path
import sys,json,hashlib,base64,tarfile,io
E=Path(__file__).resolve().parent
sys.path.insert(0,str(E.parent/'tools'))
from iris_bridge import run_json
root=json.loads((E/'submission-receipt.json').read_text())['root'];job='2294998'
seal=(E.parent/'iris-solver-rank-interleave40-20261105/seal_tree.py').read_text()
assert seal.count('range(56)')==2
seal=seal.replace('range(56)','range(40)')
body='ROOT='+repr(root)+'\nJOB='+repr(job)+'\nSEAL='+repr(seal)+r'''
from pathlib import Path
import hashlib,base64,subprocess,datetime,os,json
r=Path(ROOT);runroot=r/'init-runs';art=r/'artifacts/cut-N40-scotch'
assert (art/'READY').is_file() and not (art/'READY').is_symlink()
paths=sorted(p for p in runroot.glob(JOB+'-*') if p.is_file() and not p.is_symlink())
paths+=sorted(p for p in runroot.glob(JOB+'.sbatch.*') if p.is_file() and not p.is_symlink())
paths += sorted(p for p in (runroot/(JOB+'-rank-proofs')).glob('rank-*.json') if p.is_file() and not p.is_symlink())
paths += [art/'READY']
assert 15 < len(paths) < 80
files={}
for p in paths:
 b=p.read_bytes();assert len(b)<1500000
 rel=str(p.relative_to(r));files[rel]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'base64':base64.b64encode(b).decode()}
p=subprocess.run(['sacct','-j',JOB,'-P','-o','JobID,JobName,State,ExitCode,ElapsedRaw,AllocCPUS,NodeList,MaxRSS,TotalCPU'],capture_output=True,text=True,timeout=20)
scope={'__name__':'sealed_source_inventory'};exec(compile(SEAL,'<frozen-inventory40>','exec'),scope,scope)
core=scope['inventory'](art)
extra={};directories=[]
for base,dirs,names in os.walk(art,followlinks=False):
 for name in dirs:
  q=Path(base)/name
  if not q.is_symlink():directories.append(str(q.relative_to(art)))
 for name in names:
  q=Path(base)/name;rel=str(q.relative_to(art))
  if rel not in core['files'] and rel not in core['symlinks']:
   assert q.is_file() and not q.is_symlink();extra[rel]=scope['sha256'](q)
result={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':JOB,'root':ROOT,'files':files,
'accounting':{'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr},'ready':(art/'READY').read_text(),
'accepted_source_manifest':core,'supplementary_source_manifest':{'source':str(art),'files':extra,'symlinks':{},'directories':sorted(directories)},
'inventory_code_sha256':hashlib.sha256(SEAL.encode()).hexdigest()}
'''
d=run_json("print(\"\\n\",flush=True)\n"+body,timeout=240)
out=E/('completed-'+job);assert not out.exists();out.mkdir()
with tarfile.open(out/'raw-evidence.tar.gz','w:gz') as tar:
 for name,item in d['files'].items():
  b=base64.b64decode(item.pop('base64'),validate=True);assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256']
  f=out/'collected'/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  ti=tarfile.TarInfo(name);ti.size=len(b);tar.addfile(ti,io.BytesIO(b))
raw=(out/'raw-evidence.tar.gz').read_bytes();d['archive_bytes']=len(raw);d['archive_sha256']=hashlib.sha256(raw).hexdigest()
(E/'accepted-source-manifest.json').write_text(json.dumps(d.pop('accepted_source_manifest'),indent=2,sort_keys=True)+'\n')
(E/'supplementary-source-manifest.json').write_text(json.dumps(d.pop('supplementary_source_manifest'),indent=2,sort_keys=True)+'\n')
(out/'collection.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'job_id':job,'terminal_accounting':d['accounting'],'file_records':len(d['files']),'core_files':len(json.loads((E/'accepted-source-manifest.json').read_text())['files']),'core_symlinks':len(json.loads((E/'accepted-source-manifest.json').read_text())['symlinks']),'archive_bytes':len(raw),'source':str(E/'accepted-source-manifest.json')}))

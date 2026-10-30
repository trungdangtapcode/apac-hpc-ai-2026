from pathlib import Path,PurePosixPath
import datetime,fcntl,hashlib,json,posixpath,shutil,stat,zipfile
from lxml import etree as E
W=Path('/home/apacsc42/workspace');T=W/'VNUHCM - TripleU';O=W/'submission-review/ai-investigation-update-20261030';old=W/'submission-review/ai-reasoning-update-20261030'
O.mkdir(exist_ok=True);(O/'inputs').mkdir(exist_ok=True);(O/'slides').mkdir(exist_ok=True)
assert not (O/'inputs/combined-before-ai-update.pptx').exists(), 'Preserve an existing audited baseline'
sha=lambda b:hashlib.sha256(b).hexdigest()
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def relpart(p):
 a=PurePosixPath(p);return str(a.parent/'_rels'/(a.name+'.rels'))
def resolve(p,t):return posixpath.normpath(posixpath.join(posixpath.dirname(p),t)) if not t.startswith('/') else t.lstrip('/')
with (W/'.submission-publication.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 deck=T/'Presentation/TripleU_APAC2026_Presentation.pptx'
 shutil.copy2(deck,O/'inputs/combined-before-ai-update.pptx')
 shutil.copy2(old/'TripleU_APAC2026_Presentation.pdf',O/'inputs/combined-before-ai-update.pdf')
 with zipfile.ZipFile(deck) as z:
  parts={n:z.read(n) for n in z.namelist()}
 rels={r.get('Id'):r.get('Target') for r in E.fromstring(parts['ppt/_rels/presentation.xml.rels'])}
 seq=[resolve('ppt/presentation.xml',rels[n.get('{'+ns['r']+'}id')]) for n in E.fromstring(parts['ppt/presentation.xml']).find('p:sldIdLst',ns)]
 assert len(seq)==40
 closure=set()
 def walk(p):
  if p in closure:return
  closure.add(p);r=relpart(p)
  if r in parts:
   closure.add(r)
   for x in E.fromstring(parts[r]):
    if x.get('TargetMode')!='External':walk(resolve(p,x.get('Target')))
 for p in seq[32:]:walk(p)
 hpc={str(p.relative_to(T)):sha(p.read_bytes()) for p in (T/'HPC_Task').rglob('*') if p.is_file()}
 modes={str(p.relative_to(T)):stat.S_IMODE(p.stat().st_mode) for p in (T/'HPC_Task').rglob('*')}
 with zipfile.ZipFile(W/'VNUHCM - TripleU.zip') as z:
  zip_hpc={n:sha(z.read(n)) for n in z.namelist() if n.startswith(T.name+'/HPC_Task/') and not n.endswith('/')}
  mismatch=[p for p,h in hpc.items() if zip_hpc.get(T.name+'/'+p)!=h]
 before={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'presentation':{'sha256':sha(deck.read_bytes()),'hpc_dependency_closure_parts':{p:sha(parts[p]) for p in sorted(closure)}},'hpc_task_files':hpc,'hpc_modes':modes,'zip_hpc_files':zip_hpc,'preexisting_folder_zip_HPC_differences':mismatch,'preservation_policy':'Preserve current folder HPC and existing ZIP HPC independently. Do not include other worker unpublished changes in ZIP.'}
 (O/'HPC_BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
 for name in ['drawing-helpers.py','background-manifest.json','presentation-data.json','requirements.txt']:
  shutil.copy2(old/'slides'/name,O/'slides'/name)
 data=json.loads((O/'slides/presentation-data.json').read_text());data['snapshot_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
 for p in [Q/'h200-cold-prefill-cache-study-20261029/comparison.json',Q/'h200-decode-cap64-20261029/comparison.json',Q/'h200-decode-compile-full-20261029/failure-review-27383.json',Q/'runs/27506/probe.json']:
  data['sources'][str(p)]=sha(p.read_bytes())
 (O/'slides/presentation-data.json').write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps({'stage':str(O),'HPC_folder_files':len(hpc),'HPC_protected_pptx_parts':len(closure),'HPC_zip_files':len(zip_hpc),'preexisting_differences':len(mismatch)}))

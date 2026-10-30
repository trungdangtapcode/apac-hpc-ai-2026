#!/usr/bin/env python3
"""Publish report-only AI changes while preserving both existing HPC surfaces."""
from pathlib import Path
import copy,datetime,fcntl,hashlib,json,os,shutil,stat,subprocess,zipfile
from lxml import etree as E
from pptx import Presentation
W=Path('/home/apacsc42/workspace');T=W/'VNUHCM - TripleU';Z=W/'VNUHCM - TripleU.zip';O=W/'submission-review/ai-journey-update-20261030'
sha=lambda b:hashlib.sha256(b).hexdigest()
enc=lambda x:(json.dumps(x,indent=2)+'\n').encode()
def inv(root):
 return {str(p.relative_to(root)):p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}
def atomic(p,b,mode=0o644):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.ai30-tmp');assert not tmp.exists();tmp.write_bytes(b);tmp.chmod(mode);tmp.replace(p)
def manifests(d,now):
 mf='AI_Task/logs/FILE_MANIFEST.json';gs='AI_Task/logs/SHA256SUMS'
 d[mf]=enc({'created_utc':now.isoformat(),'paths_relative_to_team_directory':True,'files':[{'path':p,'bytes':len(b),'sha256':sha(b)} for p,b in sorted(d.items()) if p not in [mf,gs]]})
 d[gs]=''.join(sha(b)+'  '+os.path.relpath(p,'AI_Task/logs')+'\n' for p,b in sorted(d.items()) if p!=gs).encode()
def main():
 with (W/'.submission-publication.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  before=inv(T);now=datetime.datetime.now(datetime.timezone.utc)
  before_hpc={p:sha(b) for p,b in before.items() if p.startswith('HPC_Task/')}
  modes={str(p.relative_to(T)):stat.S_IMODE(p.stat().st_mode) for p in (T/'HPC_Task').rglob('*')}
  protected=json.loads((O/'HPC_BEFORE.json').read_text())['presentation']
  assert sha(before['Presentation/TripleU_APAC2026_Presentation.pptx'])==protected['sha256'],'Current deck changed; preserve other worker edit'
  deck=(O/'TripleU_APAC2026_Presentation.pptx').read_bytes()
  merge=json.loads((O/'merge-validation.json').read_text());assert merge['passed'] and sha(deck)==merge['pptx_sha256']
  with zipfile.ZipFile(O/'TripleU_APAC2026_Presentation.pptx') as z:
   assert z.testzip() is None
   for p,h in protected['hpc_dependency_closure_parts'].items():assert sha(z.read(p))==h,p
  pres=Presentation(O/'TripleU_APAC2026_Presentation.pptx');assert len(pres.slides)==40
  texts='\n'.join(s.text for sl in list(pres.slides)[:32] for s in sl.shapes if s.has_text_frame)
  for phrase in ['3,048.45','3,044.40','3,055.33','3,029.86','30 October 2026']:assert phrase in texts,phrase
  assert not any(s in texts for s in ['No HPC task scripts','README.md','FILE_MANIFEST'])
  backgrounds=[]
  for sl in pres.slides:
   pictures=[s for s in sl.shapes if s.shape_type==13 and s.left==0 and s.top==0]
   assert pictures; backgrounds.append(sha(pictures[0].image.blob))
  assert len(set(backgrounds))==40
  staged={'AI_Task/'+p:b for p,b in inv(O/'AI_Task').items() if '__pycache__' not in Path(p).parts and not p.endswith('.pyc')}
  # No serving implementation is promoted by this report.
  code_prefix='AI_Task/job_scripts/'
  ignored={'README.md','SHA256SUMS'}
  oldcode={p:sha(b) for p,b in before.items() if p.startswith(code_prefix) and p.rsplit('/',1)[-1] not in ignored}
  newcode={p:sha(b) for p,b in staged.items() if p.startswith(code_prefix) and p.rsplit('/',1)[-1] not in ignored}
  assert oldcode==newcode,'Serving implementation unexpectedly changed'
  subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=O/'AI_Task/job_scripts',check=True,stdout=subprocess.DEVNULL)
  with zipfile.ZipFile(Z) as old:
   assert old.testzip() is None
   infos={x.filename:copy.copy(x) for x in old.infolist()}
   zipbefore={n[len(T.name)+1:]:old.read(n) for n in old.namelist() if n.startswith(T.name+'/') and not n.endswith('/')}
  zip_hpc={p:sha(b) for p,b in zipbefore.items() if p.startswith('HPC_Task/')}
  differences=sorted(p for p in before_hpc if before_hpc[p]!=zip_hpc.get(p))
  base_report={'passed':True,'updated_utc':now.isoformat(),'scope':'AI report, recent evidence and32AI slides only; no research jobs','primary_implementation_unchanged':True,'primary_concurrency':64,'official_accuracy':'UNKNOWN','HPC_folder_files_preserved':len(before_hpc),'HPC_ZIP_files_preserved':len(zip_hpc),'HPC_slide_dependency_parts_preserved':len(protected['hpc_dependency_closure_parts']),'HPC_folder_vs_ZIP_preexisting_differences':differences,'HPC_policy':'Current live HPC files and existing ZIP HPC contents preserved independently. Unpublished other-worker HPC changes are not introduced into ZIP. Global manifests describe each surface separately.','organiser_upload':False,'distinct_slide_backgrounds':40}
  staged['AI_Task/logs/report-update-20261030.json']=enc(base_report)
  newdeck={'Presentation/TripleU_APAC2026_Presentation.pptx':deck}
  folder={p:b for p,b in before.items() if not p.startswith('AI_Task/')};folder.update(staged);folder.update(newdeck);manifests(folder,now)
  archive={p:b for p,b in zipbefore.items() if not p.startswith('AI_Task/')};archive.update(staged);archive.update(newdeck);manifests(archive,now)
  tmp=O/'VNUHCM - TripleU.reviewed.zip'
  with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for name,i in infos.items():
    if i.is_dir():z.writestr(copy.copy(i),b'')
   for p,b in sorted(archive.items()):
    name=T.name+'/'+p;info=copy.copy(infos[name]) if name in infos else zipfile.ZipInfo(name,now.timetuple()[:6])
    if name not in infos:info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(stat.S_IFREG|0o644)<<16
    z.writestr(info,b)
  with zipfile.ZipFile(tmp) as z:
   assert z.testzip() is None
   for p,b in archive.items():assert sha(z.read(T.name+'/'+p))==sha(b),p
   for p in zip_hpc:
    a=infos[T.name+'/'+p];b=z.getinfo(T.name+'/'+p)
    assert (a.date_time,a.external_attr,a.comment)==(b.date_time,b.external_attr,b.comment),p
  assert inv(T)==before,'Concurrent delivery edit; no publication performed'
  backup=W/'submission-archive'/('before-ai-journey-'+now.strftime('%Y%m%dT%H%M%SZ'));backup.mkdir()
  changed=[p for p,b in folder.items() if before.get(p)!=b]
  assert all(p.startswith(('AI_Task/','Presentation/')) for p in changed)
  for p in changed:
   if p in before:atomic(backup/p,before[p],stat.S_IMODE((T/p).stat().st_mode))
  shutil.copy2(Z,backup/Z.name);shutil.copy2(W/'VNUHCM - TripleU.zip.sha256',backup/'VNUHCM - TripleU.zip.sha256')
  for p in changed:atomic(T/p,folder[p],stat.S_IMODE((T/p).stat().st_mode) if (T/p).exists() else 0o644)
  for p in before.keys()-folder.keys():assert p.startswith('AI_Task/');(T/p).unlink()
  atomic(Z,tmp.read_bytes());atomic(W/'VNUHCM - TripleU.zip.sha256',(sha(tmp.read_bytes())+'  VNUHCM - TripleU.zip\n').encode())
  actual=inv(T);assert actual==folder
  assert {p:sha(b) for p,b in actual.items() if p.startswith('HPC_Task/')}==before_hpc
  assert {str(p.relative_to(T)):stat.S_IMODE(p.stat().st_mode) for p in (T/'HPC_Task').rglob('*')}==modes
  for root in [T/'AI_Task/job_scripts',T/'AI_Task/logs']:subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=root,check=True,stdout=subprocess.DEVNULL)
  base_report.update(zip_sha256=sha(Z.read_bytes()),zip_bytes=Z.stat().st_size,pptx_sha256=sha(deck),backup=str(backup),changed_files=len(changed),zip_crc_verified=True,all_folder_hashes_verified=True,HPC_modes_and_ZIP_metadata_preserved=True)
  (O/'publication-validation.json').write_bytes(enc(base_report))
  print(json.dumps(base_report,indent=2))
if __name__=='__main__':main()

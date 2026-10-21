"""Validate and publish the whole reviewed Qwen package, preserving its predecessor."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,zipfile
from pptx import Presentation
from lxml import etree
W=Path('/home/apacsc42/workspace');O=W/'submission-review/full-update-2026-10-21';T=O/'VNUHCM - TripleU';L=T/'AI_Task/logs';S=T/'AI_Task/job_scripts';C=O/'TripleU_APAC2026_Presentation.pptx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
assert json.loads((L/'package-validation.json').read_text())['passed']
assert {p.name for p in T.iterdir()}=={'AI_Task','HPC_Task','Presentation'}
assert not any(p.is_file() for p in (T/'HPC_Task').rglob('*'))
assert json.loads((S/'config.json').read_text())['declared_concurrency']==62
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=S,check=True,capture_output=True)
prs=Presentation(C);assert len(prs.slides)==32
visible=[s.text for slide in prs.slides for s in slide.shapes if s.has_text_frame]
notes=[slide.notes_slide.notes_text_frame.text for slide in prs.slides]
vi=re.compile('[đĐăĂưƯơƠấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựỵỷỹ]')
assert all(n.strip() for n in notes) and not any(vi.search(t) for t in visible+notes)
for text in ['3,022.03','2,433.02','98.726%','EAGLE3','21 October 2026']:
 assert any(text in t for t in visible),text
for text in ['README','AI_Task/','HPC_Task/','No HPC task scripts','FILE_MANIFEST','folder structure']:
 assert not any(text.lower() in t.lower() for t in visible),text
for p in S.rglob('*'):
 if p.is_file() and 'hf-cache' not in p.parts and p.suffix in ['.md','.py','.sh','.sbatch']:
  assert not vi.search(p.read_text()),str(p)
layout=json.loads((O/'layout-validation.json').read_text());assert layout['text_within_boxes'] and layout['boxes_within_slides']
data=json.loads((O/'presentation-data.json').read_text())
for path,digest in data['sources'].items():assert sha(Path(path))==digest,path
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
bgs=json.loads((O/'background-manifest.json').read_text())['slides'];assert len({b['sha256'] for b in bgs})==32
with zipfile.ZipFile(C) as z:
 assert z.testzip() is None
 for i,bg in enumerate(bgs,1):
  rels=etree.fromstring(z.read('ppt/slides/_rels/slide{}.xml.rels'.format(i)));mapping={r.get('Id'):r.get('Target') for r in rels};xml=etree.fromstring(z.read('ppt/slides/slide{}.xml'.format(i)));digests=[]
  for blip in xml.findall('.//a:blip',ns):
   target=mapping.get(blip.get('{'+ns['r']+'}embed'),'')
   if target.startswith('../media/'):digests.append(hashlib.sha256(z.read('ppt/'+target[3:])).hexdigest())
  assert bg['sha256'] in digests,i
  alpha={int(e.get('val')) for e in xml.findall('.//a:gradFill/a:gsLst/a:gs/a:srgbClr/a:alpha',ns)}
  assert ({92000,84000} if i==24 else {91000,82000}).issubset(alpha)
 assert 'customXml/assetCredits.xml' in z.namelist()
shutil.copyfile(C,T/'Presentation'/C.name)
now=datetime.datetime.now(datetime.timezone.utc)
report=dict(checked_utc=now.isoformat(),passed=True,slides=32,main_slides=24,appendix_slides=8,distinct_backgrounds=32,source_hashes_checked=len(data['sources']),english_slides_and_notes=True,native_gradients=True,script_primary='H200 N62, derived from reviewed 24915',portable_gpu_replay=False,official_accuracy_verified=False,render_method='PDF/previews share drawing coordinates; not an Office render',organiser_upload_performed=False)
write(L/'presentation-validation.json',report);write(L/'presentation-backgrounds.json',dict(slides=bgs))
# Attribution is unchanged because all 32 source photographs and the theme are retained.
(O/'PRESENTER_NOTES.md').write_text('# Presenter notes — 21 October 2026\n\n'+'\n\n'.join('## Slide {}: {}\n\n{}'.format(i+1,slide.shapes[0].text if slide.shapes[0].has_text_frame else 'Research talk',notes[i]) for i,slide in enumerate(prs.slides)))
files=[p for p in sorted(T.rglob('*')) if p.is_file() and p not in [L/'FILE_MANIFEST.json',L/'SHA256SUMS']]
write(L/'FILE_MANIFEST.json',dict(created_utc=now.isoformat(),paths_relative_to_team_directory=True,files=[dict(path=str(p.relative_to(T)),bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
files=[p for p in sorted(T.rglob('*')) if p.is_file() and p!=L/'SHA256SUMS']
(L/'SHA256SUMS').write_text(''.join('{}  {}\n'.format(sha(p),os.path.relpath(p,L)) for p in files))
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=L,check=True,capture_output=True)
ztmp=O/'updated-package.zip'
with zipfile.ZipFile(ztmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(T,T.name+'/')
 for p in sorted(T.rglob('*')):z.write(p,str(Path(T.name)/p.relative_to(T)))
with zipfile.ZipFile(ztmp) as z:
 assert z.testzip() is None
 assert {Path(n).parts[1] for n in z.namelist() if len(Path(n).parts)>1}=={'Presentation','AI_Task','HPC_Task'}
 assert not any(n.startswith(T.name+'/HPC_Task/') and not n.endswith('/') for n in z.namelist())
 assert hashlib.sha256(z.read(T.name+'/Presentation/'+C.name)).hexdigest()==sha(C)
 for p in files:assert hashlib.sha256(z.read(str(Path(T.name)/p.relative_to(T)))).hexdigest()==sha(p)
# Prepare the new folder before moving the old delivery into its dated archive.
ready=W/('.submission-ready-'+now.strftime('%Y%m%dT%H%M%SZ'));assert not ready.exists();shutil.copytree(T,ready)
backup=W/'submission-archive'/('before-full-update-'+now.strftime('%Y%m%dT%H%M%SZ'));backup.mkdir()
for name in ['VNUHCM - TripleU.zip','VNUHCM - TripleU.zip.sha256']:
 if (W/name).exists():shutil.copy2(W/name,backup/name)
(W/T.name).rename(backup/T.name)
ready.rename(W/T.name)
shutil.copyfile(ztmp,W/'VNUHCM - TripleU.zip')
(W/'VNUHCM - TripleU.zip.sha256').write_text('{}  VNUHCM - TripleU.zip\n'.format(sha(ztmp)))
report.update(backup=str(backup),pptx_sha256=sha(C),zip_sha256=sha(ztmp),zip_bytes=ztmp.stat().st_size,zip_crc_verified=True,package_checksums_verified=True,component_checks=len(json.loads((L/'package-validation.json').read_text())['checks']))
write(O/'publication-validation.json',report)
print(json.dumps(report,indent=2))

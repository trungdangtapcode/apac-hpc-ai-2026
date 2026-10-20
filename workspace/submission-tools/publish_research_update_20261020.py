"""Validate the research deck, replace only the presentation and reseal the package."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
from pptx import Presentation
from lxml import etree

W=Path('/home/apacsc42/workspace')
O=W/'submission-review/research-update-2026-10-20'
T=W/'VNUHCM - TripleU'
L=T/'AI_Task/logs'
C=O/'TripleU_APAC2026_Presentation.pptx'
S=T/'AI_Task/job_scripts'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()}
assert {p.name for p in T.iterdir()}=={'AI_Task','HPC_Task','Presentation'}
assert not any(p.is_file() for p in (T/'HPC_Task').rglob('*'))
for name in ['job_scripts','logs']:assert (T/'HPC_Task'/name).is_dir()
p=Presentation(C)
assert len(p.slides)==32
visible=[sh.text for slide in p.slides for sh in slide.shapes if sh.has_text_frame]
notes=[s.notes_slide.notes_text_frame.text for s in p.slides]
vi=re.compile('[đĐăĂưƯơƠấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựỵỷỹ]')
assert not any(vi.search(s) for s in visible+notes)
for text in ['3,022.03','2,430.89','98.726%','328.900 ms','13.495 ms','303.288 ms','17.138 ms']:
 assert any(text in v for v in visible),text
for banned in ['README','AI_Task/','HPC_Task/','No HPC task scripts','FILE_MANIFEST','folder structure']:
 assert not any(banned.lower() in v.lower() for v in visible),banned
assert all(n.strip() for n in notes)
layout=json.loads((O/'layout-validation.json').read_text())
assert layout['text_within_boxes'] and layout['boxes_within_slides']
data=json.loads((O/'presentation-data.json').read_text())
for path,digest in data['sources'].items():
 assert sha(Path(path))==digest,path
raw=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24915/confirm/n62/artifacts/profile_export.jsonl')
counts=dict(requests=0,good=0,ttft_breaches=0,itl_breaches=0)
for line in raw.read_text().splitlines():
 row=json.loads(line)
 if row['metadata'].get('phase_kind',row['metadata'].get('benchmark_phase'))!='profiling':continue
 assert not row['metadata']['was_cancelled'] and not row.get('error') and not row.get('errors')
 ttft=row['metrics']['time_to_first_token']['value'];itl=row['metrics']['inter_token_latency']['value']
 counts['requests']+=1;counts['good']+=ttft<=3000 and itl<=20;counts['ttft_breaches']+=ttft>3000;counts['itl_breaches']+=itl>20
assert counts==data['raw_latest_sla']==dict(requests=1884,good=1860,ttft_breaches=24,itl_breaches=0)
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
bgs=json.loads((O/'background-manifest.json').read_text())['slides']
with zipfile.ZipFile(C) as z:
 assert z.testzip() is None
 for i,bg in enumerate(bgs,1):
  rels=etree.fromstring(z.read('ppt/slides/_rels/slide{}.xml.rels'.format(i)))
  mapping={r.get('Id'):r.get('Target') for r in rels}
  xml=etree.fromstring(z.read('ppt/slides/slide{}.xml'.format(i)))
  digests=[]
  for blip in xml.findall('.//a:blip',ns):
   target=mapping.get(blip.get('{'+ns['r']+'}embed'),'')
   if target.startswith('../media/'):
    digests.append(hashlib.sha256(z.read('ppt/'+target[3:])).hexdigest())
  assert bg['sha256'] in digests,('missing background',i)
  alpha={int(e.get('val')) for e in xml.findall('.//a:gradFill/a:gsLst/a:gs/a:srgbClr/a:alpha',ns)}
  assert ({92000,84000} if i==24 else {91000,82000}).issubset(alpha)
 assert len({b['sha256'] for b in bgs})==32
 assert 'customXml/assetCredits.xml' in z.namelist()
now=datetime.datetime.now(datetime.timezone.utc)
report=dict(checked_utc=now.isoformat(),passed=True,slides=32,main_slides=24,appendix_slides=8,theme='Metropolis-adapted',english_slides_and_notes=True,all_text_and_boxes_within_bounds=True,distinct_backgrounds=32,background_on_every_slide=True,native_gradients=True,raw_latest_sla_requests=1884,raw_latest_sla_passed=1860,source_hashes_checked=len(data['sources']),research_results_not_official_score=True,script_files_unchanged=True,official_accuracy_verified=False,package_primary_script_still_historical_N48=True,presentation_scope='Complete research presentation; this update does not promote a new official re-run script.',render_method='PDF/previews generated from shared PPTX coordinates, not from Office/LibreOffice.')
(O/'publication-validation.json').write_text(json.dumps(report,indent=2)+'\n')
archive=W/'submission-archive'/('before-research-deck-'+now.strftime('%Y%m%dT%H%M%SZ'))
archive.mkdir(parents=True)
for f in [T/'Presentation/TripleU_APAC2026_Presentation.pptx',W/'VNUHCM - TripleU.zip',W/'VNUHCM - TripleU.zip.sha256',L/'FILE_MANIFEST.json',L/'SHA256SUMS',L/'presentation-credits.txt',L/'presentation-backgrounds.json',L/'presentation-validation.json']:
 if f.exists():shutil.copy2(f,archive/f.name)
target=T/'Presentation/TripleU_APAC2026_Presentation.pptx'
tmp=target.with_suffix('.pptx.tmp');shutil.copyfile(C,tmp);tmp.replace(target)
(L/'presentation-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(L/'presentation-backgrounds.json').write_text(json.dumps({'slides':bgs},indent=2)+'\n')
credits='Presentation visual design and asset credits\n\nMetropolis theme adaptation: Matthias Vogelgesang and contributors; CC BY-SA 4.0.\nhttps://github.com/matze/mtheme\nTheme licence is separate from original TripleU presentation content and charts.\nIcons: Lucide; ISC licence. '+(W/'submission-tools/design-assets/lucide-LICENSE').read_text()+'\n\nEvery slide uses a distinct sourced infrastructure background. Images are reference illustrations, not photographs of the contest installations. Native gradients retain the previous visual style. No AI-generated image was added.\n\n'
for bg in bgs:
 credits+='Slide {}\nSource: {}\nReference: {}\nCredit: {}\nLicence: {}\nLicence URL: {}\nSHA256: {}\n\n'.format(bg['slide'],bg['source'],bg.get('reference_page',''),bg.get('credit',''),bg.get('license',''),bg.get('license_url',''),bg['sha256'])
(L/'presentation-credits.txt').write_text(credits)
assert before=={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()}
files=[p for p in sorted(T.rglob('*')) if p.is_file() and p not in [L/'FILE_MANIFEST.json',L/'SHA256SUMS']]
(L/'FILE_MANIFEST.json').write_text(json.dumps(dict(created_utc=now.isoformat(),paths_relative_to_team_directory=True,files=[dict(path=str(p.relative_to(T)),bytes=p.stat().st_size,sha256=sha(p)) for p in files]),indent=2)+'\n')
files=[p for p in sorted(T.rglob('*')) if p.is_file() and p!=L/'SHA256SUMS']
(L/'SHA256SUMS').write_text(''.join('{}  {}\n'.format(sha(p),os.path.relpath(p,L)) for p in files))
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=L,check=True,capture_output=True,text=True)
zip_tmp=O/'updated-package.zip.tmp'
with zipfile.ZipFile(zip_tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(T,T.name+'/')
 for p in sorted(T.rglob('*')):z.write(p,str(Path(T.name)/p.relative_to(T)))
with zipfile.ZipFile(zip_tmp) as z:
 assert z.testzip() is None
 assert hashlib.sha256(z.read(T.name+'/Presentation/'+target.name)).hexdigest()==sha(C)
 assert not any(n.startswith(T.name+'/HPC_Task/') and not n.endswith('/') for n in z.namelist())
 assert {Path(n).parts[1] for n in z.namelist() if len(Path(n).parts)>1}=={'Presentation','AI_Task','HPC_Task'}
zip_target=W/'VNUHCM - TripleU.zip';zip_tmp.replace(zip_target)
zip_target.with_suffix('.zip.sha256').write_text('{}  {}\n'.format(sha(zip_target),zip_target.name))
report.update(backup=str(archive),pptx=str(target),zip=str(zip_target),zip_sha256=sha(zip_target),zip_crc_verified=True,all_package_checksums_verified=True)
(O/'publication-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

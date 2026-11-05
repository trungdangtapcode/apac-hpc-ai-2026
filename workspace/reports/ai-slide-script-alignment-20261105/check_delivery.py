"""Check the exact user-facing deck, PDF and all active short-script copies."""
from pathlib import Path
import re,json,hashlib,zipfile,posixpath
from lxml import etree as E
from pptx import Presentation
import fitz
R=Path(__file__).resolve().parent;W=R.parents[1];D=W/'VNUHCM - TripleU/Presentation';S=W/'reports/ai-final-report-20261030'
norm=lambda x:' '.join(x.split())
ppt=D/'TripleU_APAC2026_Presentation.pptx';p=Presentation(ppt);pdf=fitz.open(D/'TripleU_APAC2026_Presentation.pdf');main=fitz.open(D/'TripleU_APAC2026_Main_Talk.pdf')
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(ppt) as z:
 rel={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
 ordered=[rel[e.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')] for e in E.fromstring(z.read('ppt/presentation.xml')).find('p:sldIdLst',ns)]
 rawtexts=[norm(' '.join(E.fromstring(z.read(n)).xpath('//a:t/text()',namespaces=ns))) for n in ordered]
 objtexts=[norm(' '.join(s.text for s in slide.shapes if s.has_text_frame)) for slide in p.slides]
 assert rawtexts==objtexts,'XML and object reading disagree'
 with zipfile.ZipFile(R/'inputs/before.pptx') as before:
  changed=[n for n in z.namelist() if z.read(n)!=before.read(n)]
  assert len(changed)==8
  assert all(n in {ordered[i] for i in [0,2,5,7,10,12,15,30]} for n in changed)
route=[]
for lang in ['EN','VI']:
 f=S/f'TALK_SCRIPT_{lang}.md';s=f.read_text()
 heads=re.findall(r'^## (Script|Backup script) (\d+) — PPTX page (\d+) — (.+)$',s,re.M)
 assert len(heads)==20
 for kind,index,page,title in heads:
  i=int(index);assert int(page)==i+1
  assert norm(title) in rawtexts[i]
  # Title is not just linked to an obsolete embedded slide: it also appears on the actual rendered PDF page.
  assert norm(title) in norm(pdf[i].get_text()),(lang,page,'PDF title')
  if i<16:assert norm(title) in norm(main[i].get_text()),(lang,page,'main PDF title')
  route.append({'language':lang,'script_index':i,'actual_pptx_page':int(page),'title':title,'active_pptx_and_pdf_titles_match':True})
pack=W/'VNUHCM - TripleU/AI_Task/logs/TALK_SCRIPT_EN.md'
assert pack.read_bytes()==(S/'TALK_SCRIPT_EN.md').read_bytes()
for i,anchors in {0:['4,000','200'],2:['17 layouts explored','Different client loads'],5:['source and destination','720'],7:['DeepGEMM prefill','+1.8%'],9:['+5.30%','+125.34 ms','-1.64 ms'],10:['+1.08%','+0.08%','1% cutoff'],11:['1,875 / 1,902','27 miss TTFT','0 miss ITL','0 request errors'],12:['3,051.52','model registration'],13:['10.41%','4.52%','0.14%'],14:['0.37%','2.08%'],15:['99.9154%','12,032'],30:['3,051.52']}.items():
 for anchor in anchors:
  assert anchor in rawtexts[i],(i,anchor,'PPTX')
  assert anchor in norm(pdf[i].get_text()),(i,anchor,'PDF')
assert '17 layouts explored' not in rawtexts[1]
assert '17 layouts explored' in rawtexts[2]
base=fitz.open(W/'submission-review/ai-narrative-12min-20261103/TripleU_APAC2026_Presentation.pdf')
assert len(p.slides)==len(pdf)==42 and len(main)==24
for i in range(34,42):assert pdf[i].get_pixmap().samples==base[i].get_pixmap().samples
files=[ppt,D/'TripleU_APAC2026_Presentation.pdf',D/'TripleU_APAC2026_Main_Talk.pdf',S/'TALK_SCRIPT_EN.md',S/'TALK_SCRIPT_VI.md',pack]
r={'passed':True,'route_entries':route,'packaged_english_identical':True,'xml_reader_matches_pptx_object_reader':True,'pdf_content_anchor_checks':True,'hpc_parts_and_pdf_preserved':True,'checked_files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'render_limit':'PDF is the retained coordinate rendering with checked overlays. Microsoft Office execution not tested.','script_commit':'Script copies excluded from Git capture.'}
(R/'DELIVERY_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS: 40 bilingual spoken sections / actual PPTX and PDF page routes; packaged English identical; content anchors checked; HPC unchanged.')

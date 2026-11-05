"""Check condition/measurement association, active routes and preserved HPC."""
from pathlib import Path
from pptx import Presentation
import fitz,json,re,hashlib,zipfile,posixpath
from lxml import etree as E
R=Path(__file__).resolve().parent;W=R.parents[1];ppt=R/'TripleU_APAC2026_Presentation.pptx';p=Presentation(ppt);pdf=fitz.open(R/'TripleU_APAC2026_Presentation.pdf');before=fitz.open(R/'inputs/before.pdf')
norm=lambda s:' '.join(s.split());texts=[norm(' '.join(s.text for s in sl.shapes if s.has_text_frame)) for sl in p.slides]
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(ppt) as z,zipfile.ZipFile(R/'inputs/before.pptx') as old:
 assert z.testzip() is None
 changed=[n for n in z.namelist() if z.read(n)!=old.read(n)]
 rel={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
 order=[rel[e.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')] for e in E.fromstring(z.read('ppt/presentation.xml')).find('p:sldIdLst',ns)]
 for i,n in enumerate(order):
  root=E.fromstring(z.read(n));ids=root.xpath('//p:cNvPr/@id',namespaces=ns);assert len(ids)==len(set(ids)),n
  if i>=16:assert z.read(n)==old.read(n),'Appendix or HPC slide changed'
  if i>=34:
   rp=posixpath.dirname(n)+'/_rels/'+posixpath.basename(n)+'.rels';assert z.read(rp)==old.read(rp)
# For all three metrics the value is under its own named treatment column.
shapes=p.slides[9].shapes
conditions={'SGLang AUTO':4.55,'HPC-Ops':7.45,'Change':10.25}
for name,x in conditions.items():
 s=next(s for s in shapes if s.has_text_frame and s.text==name);assert abs(s.left/914400-x)<.01
expected=[('2,838.85',4.55,3.42),('2,989.17',7.45,3.42),('+5.30%',10.25,3.45),('822.29',4.55,4.33),('947.63',7.45,4.33),('+125.34 ms',10.25,4.36),('16.58',4.55,5.24),('14.93',7.45,5.24),('-1.64 ms',10.25,5.27)]
for val,x,y in expected:
 s=next(s for s in shapes if s.has_text_frame and s.text==val);assert abs(s.left/914400-x)<.01 and abs(s.top/914400-y)<.01
anchors={7:['Default prefill path vs DeepGEMM prefill','+1.8%','Same decode, chunk 4096, 56 requests'],9:['SGLang AUTO','HPC-Ops','vs AUTO','First-token wait','Token gap','Keep HPC-Ops'],10:['62 to 64 requests','64 to 68 requests'],13:['Control: DeepGEMM prefill / chunk 8192','HPC-Ops prefill + chunk 4096','Goodput vs control','fresh no_grad control'],14:['Dense vs sparse CUDA graphs','No speculation vs EAGLE3','Goodput -0.37%','Goodput -2.08%'],15:['LOCAL QUALITY: SCORE RETENTION','Optimised / stock correct answers','9,452 / 9,460']}
for i,items in anchors.items():
 for a in items:assert a in texts[i],(i,a);assert a in norm(pdf[i].get_text()),(i,'PDF',a)
for i in range(34,42):assert pdf[i].get_pixmap().samples==before[i].get_pixmap().samples
for i in range(16,34):assert pdf[i].get_pixmap().samples==before[i].get_pixmap().samples
# The accepted historical values, models and exact benchmark configurations are not edited.
script_data={}
for lang in ['EN','VI']:
 f=W/'reports/ai-final-report-20261030'/f'TALK_SCRIPT_{lang}.md';s=f.read_text();sections=re.findall(r'^## (Script|Backup script) (\d+) — PPTX page (\d+) — (.+)$',s,re.M);assert len(sections)==20
 for _,i,page,title in sections:assert int(page)==int(i)+1 and norm(title) in texts[int(i)]
 script_data[lang]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'all_20_routes_match':True,'capture':'uncommitted per owner instruction'}
pack=W/'VNUHCM - TripleU/AI_Task/logs/TALK_SCRIPT_EN.md';assert pack.read_bytes()==(W/'reports/ai-final-report-20261030/TALK_SCRIPT_EN.md').read_bytes()
assert len(p.slides)==42 and len(pdf)==42 and len(fitz.open(R/'TripleU_APAC2026_Main_Talk.pdf'))==24
r={'passed':True,'changed_main_pages':[8,10,11,14,15,16],'condition_value_column_checks':len(expected),'package_integrity_checks':'ZIP passes; active shape IDs unique; all appendix and HPC slide XML unchanged','hpc_and_ai_appendix_pdf_pixels_identical':True,'scripts':script_data,'packaged_english_identical':True,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [ppt,R/'TripleU_APAC2026_Presentation.pdf',R/'TripleU_APAC2026_Main_Talk.pdf']},'changed_parts':changed,'scope_limit':'Coordinate-PDF visual review and package checks; Microsoft PowerPoint repair/render behaviour not reproduced.'}
(R/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS: named condition columns, all metric associations, both20-section routes, PDFs and protected HPC/appendix.')

"""Make the experimental conditions visible beside their measured results."""
from pathlib import Path
import zipfile,json,re,hashlib,io,copy,posixpath
from lxml import etree as E
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import fitz
from PIL import Image,ImageDraw
W=Path('/home/apacsc42/workspace');R=W/'reports/ai-comparison-labels-20261105'
INK='#23373B';ORANGE='#EB811B';GRAY='#737F82';RED='#A94442';GREEN='#236950'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
zin=zipfile.ZipFile(R/'inputs/before.pptx');parts={n:zin.read(n) for n in zin.namelist()}
rels={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(parts['ppt/_rels/presentation.xml.rels'])}
order=[rels[e.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')] for e in E.fromstring(parts['ppt/presentation.xml']).find('p:sldIdLst',ns)]
roots={i:E.fromstring(parts[order[i]]) for i in range(34)};ops=[];erase={}
def text_of(sp):return '\n'.join(''.join(p.xpath('a:r/a:t/text()',namespaces=ns)) for p in sp.findall('.//a:p',ns))
def bounds(sp):
 off=sp.find('.//a:xfrm/a:off',ns);ext=sp.find('.//a:xfrm/a:ext',ns)
 if off is None or ext is None:return None
 return [int(off.get('x'))/914400,int(off.get('y'))/914400,int(ext.get('cx'))/914400,int(ext.get('cy'))/914400]
def remove(i,old):
 matches=[s for s in roots[i].findall('.//p:sp',ns) if text_of(s)==old];assert len(matches)==1,(i,old)
 s=matches[0];erase.setdefault(i,[]).append(bounds(s));s.getparent().remove(s)
def clear_body(i):
 for s in list(roots[i].find('p:cSld/p:spTree',ns)):
  b=bounds(s)
  if b and b[1]>=1.35 and b[1]<6.95:
   erase.setdefault(i,[]).append(b);s.getparent().remove(s)
def text(i,value,x,y,w,h,size=20,color=INK,bold=False,old=None):
 if old:remove(i,old)
 fam='Helvetica-Bold' if bold else 'Helvetica';lines=[]
 for para in value.split('\n'):
  cur=''
  for word in para.split():
   trial=(cur+' '+word).strip()
   if cur and stringWidth(trial,fam,size)>w*72:lines.append(cur);cur=word
   else:cur=trial
  lines.append(cur)
 assert len(lines)*size*1.18<=h*72+.5,(i,value,lines,h)
 p=Presentation();sl=p.slides.add_slide(p.slide_layouts[6]);b=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=b.text_frame;tf.clear();tf.word_wrap=False;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 for j,line in enumerate(lines):
  pp=tf.paragraphs[0] if j==0 else tf.add_paragraph();pp.text=line;pp.font.name='Arial';pp.font.size=Pt(size);pp.font.bold=bold;pp.font.color.rgb=RGBColor.from_string(color[1:]);pp.space_before=pp.space_after=Pt(0);pp.line_spacing=Pt(size*1.18)
 el=copy.deepcopy(b._element);c=el.find('p:nvSpPr/p:cNvPr',ns);c.set('id',str(max(int(e.get('id')) for e in roots[i].findall('.//p:cNvPr',ns))+1));c.set('name',f'Experimental condition label {len(ops)+1}')
 tree=roots[i].find('p:cSld/p:spTree',ns);ext=tree.find('p:extLst',ns)
 if ext is None:tree.append(el)
 else:tree.insert(list(tree).index(ext),el)
 ops.append(dict(slide=i,type='text',text=value,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,lines=lines))
def line(i,x,y,w,color=GRAY):
 p=Presentation();sl=p.slides.add_slide(p.slide_layouts[6]);from pptx.enum.shapes import MSO_CONNECTOR
 b=sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(y),Inches(x+w),Inches(y));b.line.color.rgb=RGBColor.from_string(color[1:]);b.line.width=Pt(.8)
 el=copy.deepcopy(b._element);el.find('p:nvCxnSpPr/p:cNvPr',ns).set('id',str(max(int(e.get('id')) for e in roots[i].findall('.//p:cNvPr',ns))+1));roots[i].find('p:cSld/p:spTree',ns).append(el);ops.append(dict(slide=i,type='line',x=x,y=y,w=w,color=color))
# 08: identify the otherwise invisible prefill comparison arm.
text(7,'Experimental evidence | H200: N48 diagnostic profile / N56 prefill comparison',.87,1.02,11.6,.28,11,GRAY,False,old='Experimental evidence · prioritise what to test | H200 · N48 profile and separate N64 observations')
remove(7,'Prefill: many tokens together / Decode: one token per request')
remove(7,'Test DeepGEMM prefill, hold decode fixed: +1.8% goodput; repeat confirms.')
text(7,'Why test prefill separately? It processes many prompt tokens together.',1.,5.22,11.2,.45,21,ORANGE,True)
text(7,'Default prefill path  vs  DeepGEMM prefill',1.,5.90,7.5,.45,22,INK,True)
text(7,'+1.8%',9.7,5.83,2.4,.65,30,ORANGE,True)
text(7,'Same decode, chunk 4096, 56 requests; repeated gain. Retain DeepGEMM.',1.,6.53,11.2,.39,17,INK)
# 10: table rows carry metric names; columns carry the actual experimental conditions.
clear_body(9)
text(9,'Only the decode expert backend changes; prefill and load stay fixed.',.95,1.48,11.5,.5,23,INK,True)
text(9,'SGLang AUTO',4.55,2.24,2.8,.48,23,GRAY,True)
text(9,'HPC-Ops',7.45,2.24,2.75,.48,24,ORANGE,True)
text(9,'Change',10.25,2.24,2.15,.45,21,INK,True)
text(9,'Control: automatic choice',4.55,2.77,2.8,.33,14,GRAY)
text(9,'Selected decode backend',7.45,2.77,2.8,.33,14,ORANGE)
text(9,'vs AUTO',10.25,2.77,2.15,.33,14,GRAY)
rows=[(3.35,'Good output','tokens/s  |  higher is better','2,838.85','2,989.17','+5.30%',ORANGE),(4.26,'First-token wait','Mean TTFT, ms  |  lower is better','822.29','947.63','+125.34 ms',RED),(5.17,'Token gap','Mean ITL, ms  |  lower is better','16.58','14.93','-1.64 ms',GREEN)]
for y,label,unit,auto,hpc,delta,col in rows:
 line(9,.95,y-.13,11.4,'#CCD3D4');text(9,label,.95,y,3.4,.43,22,INK,True);text(9,unit,.95,y+.46,3.4,.30,12,GRAY)
 text(9,auto,4.55,y+.07,2.75,.55,27,GRAY);text(9,hpc,7.45,y+.07,2.75,.55,27,col,True);text(9,delta,10.25,y+.10,2.25,.48,20 if '125' in delta else 23,col,True)
text(9,'Keep HPC-Ops: more qualifying output; first tokens arrive later.',.95,6.25,11.5,.44,21,INK,True)
text(9,'HPC-Ops repeat: within 0.04% of its first run. Same 16 H200, 60 requests.',.95,6.79,11.4,.28,13,GRAY)
# 11: name client requests in the comparison, not unexplained N codes.
text(10,'62 to 64 requests',1.,1.85,3.6,.56,21,GRAY,True,old='N62 → N64')
text(10,'64-request repeat',5.1,1.85,3.6,.56,21,GRAY,True,old='N64 REPEAT')
text(10,'64 to 68 requests',9.05,1.85,3.6,.56,21,GRAY,True,old='N64 → N68')
# 14: name the recipes, measured metric and role of each independent control.
clear_body(13)
text(13,'All candidates run on H200, against fresh H200 controls.',1.,1.48,11.2,.49,24,INK,True)
text(13,'Control: DeepGEMM prefill / chunk 8192; HPC-Ops decode; 64 requests.',1.,2.16,11.2,.42,19,INK)
text(13,'H100-derived change tested on H200',1.,2.94,7.0,.45,21,GRAY,True)
text(13,'Goodput vs control',8.2,2.94,4.,.45,21,GRAY,True)
for y,label,detail,value,col in [(3.64,'HPC-Ops prefill + chunk 4096','Port the H100 serving recipe at 64 requests','-10.41%',RED),(4.52,'Same port, chunk raised to 8192','Recover some loss; still below H200 recipe','-4.52%',RED),(5.40,'Inference mode: prefill-only or decode-only','Each compared with fresh no_grad control','< +0.14%',INK)]:
 line(13,1.,y-.13,11.2,'#CCD3D4');text(13,label,1.,y,7.0,.43,22,INK,True);text(13,detail,1.,y+.45,7.0,.32,15,GRAY);text(13,value,8.2,y+.05,4.,.57,28,col,True)
text(13,'Keep the H200 recipe: no tested port clears the 1% gain cutoff.',1.,6.49,11.2,.46,21,INK,True)
# 15: each rejection names its own baseline instead of presenting disembodied deltas.
clear_body(14)
text(14,'Two separate trials; each delta is relative to its own control.',1.,1.48,11.2,.46,21,INK,True)
for x in [1.,7.]:line(14,x,2.27,5.15,ORANGE)
text(14,'Dense vs sparse CUDA graphs',1.,2.49,5.1,.86,23,INK,True)
text(14,'Keep all graph sizes, or capture fewer?',1.,3.47,5.1,.63,18,GRAY)
text(14,'Capture memory per GPU rank',1.,4.18,5.1,.41,18,INK)
text(14,'1.15 GB to 0.36 GB',1.,4.69,5.1,.55,27,INK,True)
text(14,'Goodput -0.37%',1.,5.50,5.1,.56,26,RED,True)
text(14,'Retain dense graphs',1.,6.23,5.1,.48,21,INK,True)
text(14,'No speculation vs EAGLE3',7.,2.49,5.1,.86,23,INK,True)
text(14,'EAGLE3 drafts tokens, then verifies them.',7.,3.47,5.1,.63,18,GRAY)
text(14,'Shallow draft setting worked,',7.,4.18,5.1,.41,18,INK)
text(14,'but useful output fell.',7.,4.69,5.1,.55,24,INK,True)
text(14,'Goodput -2.08%',7.,5.50,5.1,.56,26,RED,True)
text(14,'Retain non-speculative decode',7.,6.23,5.1,.48,20,INK,True)
text(14,'Graph comparison uses an earlier control; request seeds differ.',1.,6.82,11.2,.23,13,GRAY)
# 16: the retained recipe and quality ratio name what the reported numbers belong to.
text(15,'LOCAL QUALITY: SCORE RETENTION',7.,1.96,5.1,.42,16,GRAY,True,old='FULL LOCAL QUALITY CHECK')
text(15,'DeepGEMM prefill / HPC-Ops decode',1.,4.18,5.2,.32,15,GRAY)
text(15,'Optimised / stock correct answers\n9,452 / 9,460',7.,3.57,5.1,.61,16,INK,False,old='of measured stock-reference accuracy')
# Notes state conditions too, without copying the uncommitted spoken script.
notes_updates={7:'Prefill comparison: default prefill path (no explicit MoE runner override) versus DeepGEMM, same decode and chunk 4096, N56. 24263/24291 initial, 24320/24327 repeat. This is distinct from the N48 diagnostic profile.',9:'All three rows compare SGLang automatic decode expert implementation (24912) with HPC-Ops decode (24913) on 16 H200 at N60; same DeepGEMM prefill/chunk 8192, workload, attention and communication. Positive TTFT delta means slower first token. Negative ITL delta means faster streaming. Repeat goodput differs about 0.033% from original HPC-Ops treatment. Recipe-level observation, not kernel-isolated causality.',13:'All displayed ports are measured on H200. Full H100-recipe port uses HPC-Ops prefill/chunk 4096 vs fresh H200 DeepGEMM/chunk 8192 control (both HPC-Ops decode). Chunk8192 port still loses. Phase-only inference_mode tests have independent fresh no_grad control. Percentages are goodput changes, not GPU hardware conversion.',14:'Separate trials with separate controls: dense vs sparse capture graph sizes uses an earlier control and differing request seeds; non-speculative vs shallow EAGLE3 is a separate pair. Capture memory is not total sampled VRAM. Only tested alternatives are rejected.',15:'Quality number is reference-score retention: 9452/9460, not 99.9% absolute accuracy. Same 12032 questions per deployment. Local full-set comparison, not organiser certification.'}
changed=sorted({o['slide'] for o in ops})
# Update only relevant AI notes parts; leave every other package member unchanged.
for i,note in notes_updates.items():
 slidepart=order[i];rp=posixpath.dirname(slidepart)+'/_rels/'+posixpath.basename(slidepart)+'.rels'; rr=E.fromstring(parts[rp]);nr=next(e for e in rr if e.get('Type').endswith('/notesSlide'));np=posixpath.normpath(posixpath.dirname(slidepart)+'/'+nr.get('Target'));root=E.fromstring(parts[np]);bodies=root.xpath('//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]/p:txBody',namespaces=ns)
 if bodies:
  body=bodies[0]
  for el in list(body):
   if el.tag=='{'+ns['a']+'}p':body.remove(el)
  pp=E.SubElement(body,'{'+ns['a']+'}p');run=E.SubElement(pp,'{'+ns['a']+'}r');E.SubElement(run,'{'+ns['a']+'}t').text=note
  parts[np]=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
for i in changed:parts[order[i]]=E.tostring(roots[i],xml_declaration=True,encoding='UTF-8',standalone=True)
out=R/'TripleU_APAC2026_Presentation.pptx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for info in zin.infolist():z.writestr(copy.copy(info),parts[info.filename])
# PDF: preserve background/images and replace text in the same editable coordinates.
doc=fitz.open(R/'inputs/before.pdf')
for i in changed:
 page=doc[i]
 for x,y,w,h in erase.get(i,[]):page.add_redact_annot(fitz.Rect(x*72,y*72,(x+w)*72,(y+h)*72),fill=False)
 if erase.get(i):page.apply_redactions(images=0,graphics=0)
 b=io.BytesIO();cv=canvas.Canvas(b,pagesize=(13.333333*72,7.5*72))
 for o in [o for o in ops if o['slide']==i]:
  if o['type']=='line':cv.setStrokeColor(o['color']);cv.setLineWidth(.8);cv.line(o['x']*72,(7.5-o['y'])*72,(o['x']+o['w'])*72,(7.5-o['y'])*72);continue
  cv.setFillColor(o['color']);cv.setFont('Helvetica-Bold' if o['bold'] else 'Helvetica',o['size'])
  for j,t in enumerate(o['lines']):cv.drawString(o['x']*72,(7.5-o['y'])*72-o['size']*.94-j*o['size']*1.18,t)
 cv.save();overlay=fitz.open(stream=b.getvalue(),filetype='pdf');page.show_pdf_page(page.rect,overlay,0)
doc.save(R/'TripleU_APAC2026_Presentation.pdf',garbage=3,deflate=True)
m=fitz.open();m.insert_pdf(doc,from_page=0,to_page=15);m.insert_pdf(doc,from_page=34,to_page=41);m.save(R/'TripleU_APAC2026_Main_Talk.pdf',garbage=3,deflate=True)
thumbs=[]
for i in range(16):
 pix=doc[i].get_pixmap(matrix=fitz.Matrix(.7,.7));im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((480,270));thumbs.append(im)
 if i in changed:doc[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(R/f'page-{i+1:02d}.png')
sheet=Image.new('RGB',(2000,1200),'#dce1e1');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+276),f'PPTX page {i+1:02d}',fill=INK)
sheet.save(R/'OVERVIEW.jpg',quality=92)
(R/'EDITS.json').write_text(json.dumps(ops,indent=2)+'\n')
print('Built pages', [i+1 for i in changed])

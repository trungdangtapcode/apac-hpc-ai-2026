from pathlib import Path
import zipfile, json, re, hashlib, io, copy, posixpath
from lxml import etree as E
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
import fitz
W=Path('/home/apacsc42/workspace'); R=W/'reports/ai-slide-script-alignment-20261105'
PAPER='#FAFAFA';INK='#23373B';ORANGE='#EB811B';GRAY='#737F82'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
zin=zipfile.ZipFile(R/'inputs/before.pptx'); parts={n:zin.read(n) for n in zin.namelist()}
rels={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(parts['ppt/_rels/presentation.xml.rels'])}
order=[rels[e.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')] for e in E.fromstring(parts['ppt/presentation.xml']).find('p:sldIdLst',ns)]
roots={i:E.fromstring(parts[order[i]]) for i in range(34)}
changes=[]
def add(i,text,x,y,w,h,size=19,color=INK,bold=False,old=None):
 root=roots[i]; removed=None
 if old:
  matches=[s for s in root.findall('.//p:sp',ns) if '\n'.join(''.join(t.text or '' for t in p.findall('a:r/a:t',ns)) for p in s.findall('.//a:p',ns))==old]
  assert len(matches)==1,(i,old,len(matches))
  s=matches[0]; off=s.find('.//a:xfrm/a:off',ns);ext=s.find('.//a:xfrm/a:ext',ns)
  removed=[int(off.get('x'))/914400,int(off.get('y'))/914400,int(ext.get('cx'))/914400,int(ext.get('cy'))/914400]
  s.getparent().remove(s)
 p=Presentation(); p.slide_width=Inches(13.333333);p.slide_height=Inches(7.5)
 slide=p.slides.add_slide(p.slide_layouts[6]);box=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
 tf=box.text_frame;tf.clear();tf.word_wrap=False;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
 fam='Helvetica-Bold' if bold else 'Helvetica';leading=size*1.18
 lines=[]
 for para in text.split('\n'):
  cur=''
  for word in para.split():
   trial=(cur+' '+word).strip()
   if cur and stringWidth(trial,fam,size)>w*72:lines.append(cur);cur=word
   else:cur=trial
  lines.append(cur)
 assert len(lines)*leading<=h*72+0.5,(i,text,lines,h)
 for j,line in enumerate(lines):
  pp=tf.paragraphs[0] if j==0 else tf.add_paragraph();pp.text=line;pp.font.name='Arial';pp.font.size=Pt(size);pp.font.bold=bold;pp.font.color.rgb=RGBColor.from_string(color[1:]);pp.space_before=pp.space_after=Pt(0);pp.line_spacing=Pt(leading)
 el=copy.deepcopy(box._element);c=el.find('p:nvSpPr/p:cNvPr',ns);c.set('id',str(max(int(e.get('id')) for e in root.findall('.//p:cNvPr',ns))+1));c.set('name','Aligned speech anchor '+str(len(changes)+1))
 root.find('p:cSld/p:spTree',ns).append(el)
 changes.append(dict(slide=i,old=old,removed_rect=removed,text=text,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,lines=lines))
# Each addition supplies an anchor for an already spoken fact, rather than a new experiment.
add(0,'4,000 input tokens  /  200 output tokens',.95,3.0,11.3,.34,18,'#FFFFFF')
add(2,'17 layouts explored',7.65,5.05,4.6,.5,24,ORANGE,True)
add(2,'Different client loads: feasibility evidence, not a controlled ranking.',1.,6.63,11.2,.34,16,GRAY)
add(5,'Merge only if both source and destination ranges are contiguous.\nPartial-token slices keep their spacing; required bytes stay unchanged.',1.,5.57,11.2,.66,18,INK,False,'Correctness invariant: transfer the same byte ranges')
add(7,'Kernel activity can overlap; these groups are not a request-time breakdown.',1.,2.32,11.2,.36,17,GRAY)
add(7,'Prefill: many tokens together  /  Decode: one token per request',1.,5.37,11.2,.49,22,ORANGE,True,'Why test execution choices separately for prefill and decode?')
add(7,'Test DeepGEMM prefill, hold decode fixed: +1.8% goodput; repeat confirms.',1.,6.17,11.2,.59,19,INK,False,'Different token shapes can favor different implementations. Test the service.')
add(10,'Full-run gain below our 1% cutoff',9.05,4.05,3.6,1.1,20,INK,False,'Full-run gain: too small')
add(10,'More in-flight requests can trade higher throughput for longer first-token waits.',1.,6.60,11.2,.34,16,GRAY)
add(12,'Startup failure: router healthy before model registration; wait for model + live workers.',1.,2.40,11.2,.39,17,GRAY)
add(15,'MMLU-Pro: same 12,032 questions per service',7.,4.18,5.2,.32,15,GRAY)
add(30,'28197: 3,051.52 good output tokens/s; complete entry verified.',1.,6.38,11.3,.46,18,ORANGE,False,'Retain failures; qualify each repair; a complete run closes the deployment gap.')
# Bytes outside changed slide XML are copied without reconstruction.
changed_indices=sorted({c['slide'] for c in changes})
for i in changed_indices:parts[order[i]]=E.tostring(roots[i],xml_declaration=True,encoding='UTF-8',standalone=True)
out=R/'TripleU_APAC2026_Presentation.pptx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for info in zin.infolist():z.writestr(copy.copy(info),parts[info.filename])
# Match the established coordinate PDF while leaving every unchanged page unaltered.
base=W/'submission-review/ai-narrative-12min-20261103/TripleU_APAC2026_Presentation.pdf'
doc=fitz.open(base)
for i in changed_indices:
 page=doc[i]
 for c in [c for c in changes if c['slide']==i and c['removed_rect']]:
  x,y,w,h=c['removed_rect'];page.add_redact_annot(fitz.Rect(x*72,y*72,(x+w)*72,(y+h)*72),fill=False)
 if any(c['slide']==i and c['removed_rect'] for c in changes):page.apply_redactions(images=0,graphics=0)
 b=io.BytesIO(); cv=canvas.Canvas(b,pagesize=(13.333333*72,7.5*72))
 for c in [c for c in changes if c['slide']==i]:
  cv.setFillColor(c['color']);cv.setFont('Helvetica-Bold' if c['bold'] else 'Helvetica',c['size'])
  for j,line in enumerate(c['lines']):cv.drawString(c['x']*72,(7.5-c['y'])*72-c['size']*.94-j*c['size']*1.18,line)
 cv.save();overlay=fitz.open(stream=b.getvalue(),filetype='pdf');page.show_pdf_page(page.rect,overlay,0)
doc.save(R/'TripleU_APAC2026_Presentation.pdf',garbage=3,deflate=True)
main=fitz.open();main.insert_pdf(doc,from_page=0,to_page=15);main.insert_pdf(doc,from_page=34,to_page=41);main.save(R/'TripleU_APAC2026_Main_Talk.pdf',garbage=3,deflate=True)
(R/'CHANGES.json').write_text(json.dumps(changes,indent=2)+'\n')
# Overview and all changed page renders are inspectable without opening Office.
from PIL import Image,ImageDraw
thumbs=[]
for i in range(16):
 pix=doc[i].get_pixmap(matrix=fitz.Matrix(.7,.7));im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((480,270));thumbs.append(im)
 if i in changed_indices:doc[i].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(R/f'slide-{i:02d}.png')
sheet=Image.new('RGB',(2000,1200),'#dce1e1');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
 x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+276),f'Script {i} / deck {i+1}',fill='#23373B')
sheet.save(R/'OVERVIEW.jpg',quality=92)
# Check preservation, title order, exact anchors and backup visibility.
with zipfile.ZipFile(out) as z:
 changed=[n for n in parts if zin.read(n)!=z.read(n)]
 assert set(changed)=={order[i] for i in changed_indices}
 assert all(z.read(n)==zin.read(n) for n in parts if n not in changed)
 check=Presentation(out);assert len(check.slides)==42
 for c in changes:assert ' '.join(c['text'].split()) in ' '.join(' '.join(s.text for s in check.slides[c['slide']].shapes if s.has_text_frame).split()),c['text']
 for i in range(34,42):assert doc[i].get_pixmap().samples==fitz.open(base)[i].get_pixmap().samples
r=dict(passed=True,slides=42,main_ai_slides=16,ai_backup_slides=18,hpc_slides=8,changed_slide_indices=changed_indices,changed_parts=changed,all_other_package_parts_identical=True,hpc_pdf_pixels_identical=True,script_numbering='0–15 (deck pages 1–16)',render_scope='Existing coordinate PDF plus matching editable text overlays; not an Office rendering',files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [out,R/'TripleU_APAC2026_Presentation.pdf',R/'TripleU_APAC2026_Main_Talk.pdf']})
(R/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))

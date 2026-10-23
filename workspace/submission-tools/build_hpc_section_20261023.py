#!/usr/bin/env python3
"""Build a standalone, eight-slide HPC section in the TripleU Metropolis style.

The source deck is deliberately not opened or modified by this builder.
"""
from pathlib import Path
import json, math, hashlib
from PIL import Image
import fitz
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

WORK = Path('/home/apacsc42/workspace')
OUT = WORK/'submission-review/hpc-update-20261023/slide-section'
ASSETS = WORK/'submission-tools/design-assets'
BGDIR = ASSETS/'background-candidates'
OUT.mkdir(parents=True, exist_ok=True)
PREV = OUT/'previews'; PREV.mkdir(exist_ok=True)
W, H = 13.333333, 7.5
PAPER, INK, ORANGE, GRAY, PALE, WHITE, RED = '#FAFAFA','#23373B','#EB811B','#737F82','#E5E9E9','#FFFFFF','#A94442'
PHOTOS = [20,30,33,40,44,55,63,69]
DOWNLOADS = {x['id']:x for x in json.loads((BGDIR/'downloads.json').read_text())}
prs = Presentation(); prs.slide_width=Inches(W); prs.slide_height=Inches(H)
prs.core_properties.title='APAC HPC-AI 2026 — OpenFOAM CPU research'
prs.core_properties.author='VNUHCM - TripleU'
prs.core_properties.subject='Eight-slide HPC section; research through 23 October 2026'
pdf_path=OUT/'HPC-section.pdf'; pdf=Canvas(str(pdf_path),pagesize=(W*72,H*72))
layout=[]; slides=[]

def rgb(c): return RGBColor.from_string(c.lstrip('#'))
def addshape(s,kind,x,y,w,h,fill=None,line=None,lw=1):
    sh=s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill: sh.fill.solid(); sh.fill.fore_color.rgb=rgb(fill)
    else: sh.fill.background()
    if line: sh.line.color.rgb=rgb(line); sh.line.width=Pt(lw)
    else: sh.line.fill.background()
    return sh

def rect(x,y,w,h,c,stroke=None,lw=1):
    pdf.setFillColor(HexColor(c)) if c else None
    pdf.setStrokeColor(HexColor(stroke)) if stroke else None
    pdf.setLineWidth(lw)
    pdf.rect(x*72,(H-y-h)*72,w*72,h*72,fill=int(bool(c)),stroke=int(bool(stroke)))

def line(x1,y1,x2,y2,c=INK,lw=1.2):
    sh=prs.slides[-1].shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1),Inches(y1),Inches(x2),Inches(y2))
    sh.line.color.rgb=rgb(c); sh.line.width=Pt(lw)
    pdf.setStrokeColor(HexColor(c));pdf.setLineWidth(lw);pdf.line(x1*72,(H-y1)*72,x2*72,(H-y2)*72)

def wrapped(text,w,size,bold=False):
    font='Helvetica-Bold' if bold else 'Helvetica'; out=[]
    for para in str(text).split('\n'):
        if not para: out.append(''); continue
        cur=''
        for word in para.split():
            test=(cur+' '+word).strip()
            if stringWidth(test,font,size)>w*72 and cur: out.append(cur);cur=word
            else: cur=test
        out.append(cur)
    return out

def text(s,txt,x,y,w,h,size=20,color=INK,bold=False,align='left'):
    lines=wrapped(txt,w,size,bold); leading=size*1.18
    if leading*len(lines)>h*72+.5: raise ValueError(f'Overflow on slide {len(prs.slides)}: {txt!r}')
    fam='Arial'; b=OxmlElement('a:latin'); b.set('typeface',fam)
    box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame
    tf.clear();tf.word_wrap=False;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,val in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=val;p.font.name=fam;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_before=p.space_after=Pt(0);p.line_spacing=Pt(leading)
        pdf.setFont('Helvetica-Bold' if bold else 'Helvetica',size);pdf.setFillColor(HexColor(color))
        xx=x*72
        if align=='center': xx+=(w*72-stringWidth(val,'Helvetica-Bold' if bold else 'Helvetica',size))/2
        pdf.drawString(xx,(H-y)*72-size*.94-i*leading,val)
    layout.append({'slide':len(prs.slides),'x':x,'y':y,'w':w,'h':h,'size_pt':size,'text':str(txt)})
    return box

def photo_overlay(index):
    imgpath=BGDIR/DOWNLOADS[PHOTOS[index-1]]['file']
    im=Image.open(imgpath).convert('RGB').resize((1600,900))
    paper=Image.new('RGB',im.size,tuple(int(PAPER[i:i+2],16) for i in (1,3,5)))
    faint=Image.blend(paper,im,.14)
    pdf.drawImage(ImageReader(faint),0,0,W*72,H*72,mask='auto')
    s=prs.slides[-1]
    pic=s.shapes.add_picture(str(imgpath),0,0,width=Inches(W),height=Inches(H))
    wash=addshape(s,MSO_SHAPE.RECTANGLE,0,0,W,H,PAPER)
    # Native translucent paper overlay; photo remains distinct underneath.
    fill=wash._element.spPr.solidFill
    clr=fill.srgbClr
    alpha=OxmlElement('a:alpha');alpha.set('val','86000');clr.append(alpha)

def start(title,idx,notes,source):
    s=prs.slides.add_slide(prs.slide_layouts[6]);slides.append(s)
    s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(PAPER)
    photo_overlay(idx)
    # Metropolis signature: dark gradient title band, quiet footer, orange rule.
    band=addshape(s,MSO_SHAPE.RECTANGLE,0,0,W,.84,INK)
    band.fill.gradient();band.fill.gradient_angle=0
    for stop,col in zip(band.fill.gradient_stops,(INK,'#375C6A')): stop.color.rgb=rgb(col)
    rect(0,0,W,.84,INK)
    text(s,title,.66,.18,12,.48,25,WHITE,True)
    text(s,'TripleU  /  APAC HPC-AI 2026',.66,7.10,8,.20,9,GRAY)
    text(s,f'{idx+32:02d} / 40',11.85,7.06,.82,.24,10,GRAY,align='right')
    rect(0,7.465,W,.035,PALE);rect(0,7.465,W*(32+idx)/40,.035,ORANGE)
    bg=DOWNLOADS[PHOTOS[idx-1]]
    s.notes_slide.notes_text_frame.text=notes+'\n\nResearch sources: '+source+'\nBackground attribution: '+json.dumps({'author':'NVIDIA','credit':'NVIDIA; NVIDIA reference imagery; all rights retained.','license':'NVIDIA reference imagery; all rights retained.','source':bg['source'],'reference_page':bg.get('reference_page'),'role':'Faint atmospheric backdrop; reference imagery, not the contest cluster.'},ensure_ascii=False)
    return s

def end(): pdf.showPage()

SRC4='/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md'
SRC2='/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-density-review-20261022/RESULTS.md'
GUIDE='/home/apacsc42/workspace/reports/hpc-research-journey-20261023/'

# 1 — task and metric
s=start('The task: same 65-million-cell airflow calculation',1,
"We optimize execution of the official OpenFOAM v2512 car-flow case, not its mathematics. The mesh contains 65,334,765 cells. The job completes the prescribed preparation and 150 solver iterations on four nodes. The measured metric is the solver's average wall-clock seconds per time step, beginning with the second solver iteration; lower is better. The retained final drag coefficient is a physical sanity signal, not the performance score.",SRC4+'; '+GUIDE+'FOUNDATIONS.md')
text(s,'65.3 million',.95,1.38,6.2,.76,36,ORANGE,True);text(s,'mesh cells',.98,2.16,5.8,.42,22,INK)
text(s,'4 nodes',.95,3.00,4.4,.65,32,INK,True);text(s,'512 MPI ranks · 128 per node',.98,3.69,5.0,.54,19,GRAY)
text(s,'150 steps',7.2,1.40,4.6,.66,32,INK,True);text(s,'149 timed samples',7.23,2.12,4.8,.44,19,GRAY)
text(s,'Metric',7.2,3.04,4.5,.44,20,ORANGE,True);text(s,'Average seconds per solver step',7.2,3.54,5.2,.54,22,INK,True)
text(s,'Lower is better · every required step stays in the run',7.22,4.24,5.2,.82,18,GRAY)
rect(.95,5.58,11.45,.025,PALE)
text(s,'Fixed calculation, better use of CPU resources',.97,5.90,11.2,.60,25,INK,True)
end()

# 2 — pipeline / concepts
s=start('The whole required pipeline comes before the score',2,
"MPI means Message Passing Interface: separate solver processes exchange information about cells at partition boundaries. Mesh decomposition assigns cells to ranks; CPU affinity maps ranks to CPUs. These are different decisions. A complete run includes mesh decomposition, renumbering, potential-flow initialization, boundary-layer setup, and the 150-step simpleFoam solve. Skipping preparation or solver work would not be a valid comparison.",SRC4+'; '+GUIDE+'FOUNDATIONS.md')
steps=[('01','decomposePar','Assign mesh cells to ranks'),('02','renumberMesh','Reorder local cell data'),('03','potentialFoam','Initialize flow fields'),('04','applyBoundaryLayer','Apply prescribed boundary layer'),('05','simpleFoam','Run all 150 solver steps')]
for i,(n,h,b) in enumerate(steps):
 x=.78+i*2.49
 rect(x,1.72,2.18,2.63,WHITE,'#D8DEDF',.8);text(s,n,x+.18,1.90,.60,.42,18,ORANGE,True);text(s,'applyBoundary\nLayer' if h=='applyBoundaryLayer' else h,x+.18,2.43,1.84,.74,18,INK,True);text(s,b,x+.18,3.20,1.82,.92,18,GRAY)
 if i<4: text(s,'→',x+2.21,2.70,.28,.40,19,ORANGE,True)
text(s,'Decomposition',.93,4.90,3.2,.42,20,INK,True);text(s,'Which cells belong to each MPI rank?',.93,5.39,5.4,.54,18,GRAY)
text(s,'CPU affinity',6.73,4.90,3.2,.42,20,INK,True);text(s,'Which CPU runs each rank?',6.73,5.39,5.1,.54,18,GRAY)
end()

# 3 — journey loser
s=start('A smaller partition cut did not make the solver faster',3,
"The NUMA-aware decomposition hypothesis was that grouping work by memory locality might reduce communication and improve speed. Its graph cut fell by 10.63%, but the solver mean worsened from 13.881 to 14.359 seconds per step, a 3.4416% slowdown. The comparison also changed other partition properties, so the cut alone cannot explain the runtime. We closed the unchanged branch. A separate offline mapping reduced a graph cut by 4.5741% but has no measured solver result.",GUIDE+'JOURNEY.md; '+GUIDE+'figures/research-journey.png')
text(s,'NUMA-aware idea',.95,1.42,5.0,.52,25,INK,True);text(s,'Reduce remote-memory / interface cost',.98,2.02,5.2,.54,18,GRAY)
text(s,'−10.63%',.98,2.86,4.4,.70,33,ORANGE,True);text(s,'graph cut',1.0,3.56,4.4,.40,18,GRAY)
line(5.75,3.30,7.1,3.30,INK,2.0);text(s,'≠',6.17,2.84,.55,.56,27,RED,True,align='center')
text(s,'+3.4416%',7.55,2.86,4.3,.70,33,RED,True);text(s,'slower solver mean',7.58,3.56,4.4,.40,18,GRAY)
rect(.98,4.64,11.26,.035,PALE)
text(s,'Lesson',.98,5.02,1.7,.42,20,ORANGE,True);text(s,'A graph proxy is not a runtime measurement.',2.2,4.98,9.8,.55,23,INK,True)
text(s,'Cause not measured: MPI wait, bandwidth, frequency, power, page residency',.99,5.80,11.3,.48,18,GRAY)
end()

# 4 scaling chart
s=start('Observed scaling changed which decomposition led',4,
"These are separately allocated observations at 128 ranks per node, not an identical-work strong-scaling experiment. Endpoints are 40, 80 and 150 solver steps. Hierarchical led the two-node pair at 7.169996913 seconds per step versus Scotch at 7.462835189. At four nodes, Scotch led at 3.677906731 versus hierarchical at 3.819929017. Different allocations and endpoint lengths limit causal claims.",SRC2+'; '+SRC4+'; '+GUIDE+'figures/observed-scaling.png')
groups=[('1 node · 40 steps',14.450756959,14.366262732,'Scotch','Hierarchical'),('2 nodes · 80 steps',7.462835189,7.169996913,'Scotch','Hierarchical'),('4 nodes · 150 steps',3.677906731,3.819929017,'Scotch','Hierarchical')]
for i,(lab,sc,hi,_,__) in enumerate(groups):
 y=1.52+i*1.47;text(s,lab,.98,y,3.0,.35,18,INK,True)
 maxv=15
 for j,(name,val,col) in enumerate([('Scotch',sc,ORANGE),('Hierarchical',hi,INK)]):
  yy=y+.42+j*.39;text(s,name,.98,yy,1.45,.34,18,GRAY)
  bw=val/maxv*7.0;rect(2.58,yy+.045,bw,.25,col);text(s,f'{val:.3f}',2.75+bw,yy-.01,1.70,.34,18,INK,True)
text(s,'Best observed choice depends on node count and rank density',.99,6.08,11.3,.55,22,ORANGE,True)
text(s,'Different allocations and endpoints make this descriptive, not causal.',.99,6.57,11.3,.34,18,GRAY)
end()

# 5 six config compare
s=start('At four nodes, the winner depends on ranks per node',5,
"The six reviewed four-node logs all complete 150 steps with 149 timed samples. At 64 and 96 ranks per node, hierarchical has the lower observed mean; at 128, Scotch is lower. Requested CPU counts differ across some configurations, and these are separate allocations. We therefore describe measured candidate means, not a causal effect or a universal best method. The lowest mean is 3.677906731 seconds per step for Scotch-128.",SRC4)
vals=[('Scotch · 64',10.309943538,ORANGE),('Hierarchical · 64',4.488921327,INK),('Scotch · 96',7.146018748,ORANGE),('Hierarchical · 96',4.922347604,INK),('Scotch · 128',3.677906731,ORANGE),('Hierarchical · 128',3.819929017,INK)]
for i,(lab,val,col) in enumerate(vals):
 y=1.43+i*.73;text(s,lab,.95,y,2.75,.36,18,INK,True);bw=val/11*6.0;rect(3.72,y+.035,bw,.27,col);text(s,f'{val:.3f} s/step',3.87+bw,y-.005,2.5,.33,18,INK,True)
text(s,'128 ranks per node → lowest reviewed mean: Scotch',.98,6.15,11.3,.54,22,ORANGE,True)
text(s,'Separate allocations; compare these as observed means, not causal effects.',.98,6.62,11.3,.34,18,GRAY)
end()

# 6 tails
s=start('Keep the slow step in the mean; inspect the tail',6,
"Scotch-128 has a median of 3.298742 seconds, p95 of 3.795740 seconds, and maximum of 35.883552 seconds at solver Time 119. All 149 timed samples remain in the arithmetic mean. The review did not collect enough hardware counters to attribute the spike to MPI, CPU scheduling, memory or I/O. The sample-size warning motivates independent repeats; it does not authorize removing the slow point or changing the prescribed endpoint.",SRC4+'; '+GUIDE+'figures/iteration-spikes.png')
text(s,'3.298742 s',.96,1.56,3.55,.62,29,INK,True);text(s,'median',.98,2.20,3.2,.32,18,GRAY)
text(s,'3.795740 s',4.85,1.56,3.55,.62,29,INK,True);text(s,'95th percentile',4.87,2.20,3.2,.32,18,GRAY)
text(s,'35.883552 s',8.76,1.56,3.75,.62,29,RED,True);text(s,'maximum · Time 119',8.78,2.20,3.3,.32,18,GRAY)
line(1.05,3.33,12.15,3.33,PALE,2);rect(1.05,3.20,.15,.25,ORANGE);rect(9.85,3.08,.22,.50,RED)
text(s,'149/149 samples retained',.98,4.06,5.8,.48,22,INK,True);text(s,'Official-style arithmetic mean includes every measured step.',.99,4.65,8.6,.43,18,GRAY)
text(s,'Cause unknown',.99,5.48,2.5,.40,20,ORANGE,True);text(s,'No measured MPI wait, bandwidth, frequency, power or page residency',3.72,5.44,8.8,.64,18,GRAY)
end()

# 7 reproducibility
s=start('A reproducible candidate needs more than a fast log',7,
"The best reviewed four-node native mean is a candidate observation, not an accepted official score. The independent confirmation job 25940700 was submitted on 23 October at 12:51 UTC. A fresh scheduler query at 15:06 UTC still showed Q/q5 with the comment Not Running: Insufficient amount of resource: node_pool. No result is available. The job is configured to re-run the full preparation and 150-step solve on four exclusive nodes. Its fresh 54-file bundle requires source/mesh identity, explicit stage returns, startup 512-physical-core/four-host proof, and zero-field seals. These are required proofs, not completed checks.",SRC4+'; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/scheduler-status.json; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-four-node-confirm-20261023/submission.json')
text(s,'Reviewed candidate',.96,1.46,4.7,.44,21,GRAY,True);text(s,'3.677906731',.96,2.02,5.2,.74,37,ORANGE,True);text(s,'seconds per step · Scotch-128 · 149 samples',.99,2.84,5.5,.56,18,INK)
line(6.43,1.50,6.43,4.26,PALE,1.2)
text(s,'Independent repeat',6.88,1.46,4.8,.44,21,GRAY,True);text(s,'25940700',6.88,2.04,4.8,.68,34,INK,True);text(s,'Q/q5 · 15:06 UTC\nNot running: node_pool insufficient\nNo result',6.91,2.84,5.1,1.00,18,GRAY)
checks=['Frozen 54-file input bundle','Full initialization + 150 steps','Explicit stage return codes','512 physical cores on 4 hosts','Source, mesh and output seals']
text(s,'Proof required from the queued confirmation',.98,4.23,8.5,.34,18,INK,True)
for i,v in enumerate(checks):
 x=.98+(i%3)*4.00;y=4.60+(i//3)*.77;rect(x,y+.11,.10,.10,ORANGE);text(s,v,x+.27,y,3.55,.65,18,INK)
end()

# 8 conclusion and next
s=start('What we learned — and the next measurement',8,
"The research has narrowed choices, rejected the unchanged NUMA-aware branch, and identified Scotch-128 as the lowest mean among six reviewed four-node native observations. This is not a proven global optimum or accepted score. At 15:06 UTC on 23 October, job 25940700 was still Q/q5; PBS reported Not Running because node_pool resources were insufficient. No result was available. Next review its complete terminal proof and all iteration tails, then use bounded matched sampling to investigate stability before choosing another configuration.",GUIDE+'JOURNEY.md; '+GUIDE+'TALK_TRACK.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/scheduler-status.json; /home/apacsc42/workspace/notes/HPC_CURRENT.md')
for i,(num,hd,body) in enumerate([('01','Measure the whole job','Keep preparation, all steps and provenance.'),('02','Trust runtime evidence','A smaller graph cut is not a speedup.'),('03','Preserve every sample','Tails matter; causes need instrumentation.'),('04','Confirm independently','Review job 25940700 before the next choice.')]):
 x=.95+i*3.08;text(s,num,x,1.62,.80,.54,27,ORANGE,True);text(s,hd,x,2.37,2.78,.78,20,INK,True);text(s,body,x,3.36,2.78,1.12,18,GRAY)
rect(.96,5.15,11.37,.035,PALE)
text(s,'23 Oct 15:06 UTC · 25940700 still Q/q5; node_pool insufficient; no result',.98,5.48,11.2,.60,19,INK,True)
text(s,'Next: review tails, terminal proof and bounded hardware samples',.98,6.14,11.2,.44,18,ORANGE,True)
end()

assert len(prs.slides)==8
prs.save(OUT/'HPC-section.pptx');pdf.save()
# Render one-page PNG previews from the PDF, and concise content/layout evidence.
doc=fitz.open(pdf_path)
for i,page in enumerate(doc,1): page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(PREV/f'slide-{i:02d}.png')
content=[]
for i,s in enumerate(slides,1):
 visible=[sh.text for sh in s.shapes if getattr(sh,'has_text_frame',False) and sh.text.strip()]
 content.append({'slide':i,'title':visible[0],
                 'visible_text':[sh.text for sh in s.shapes if getattr(sh,'has_text_frame',False) and sh.text.strip()],
                 'speaker_notes_en':s.notes_slide.notes_text_frame.text,
                 'background_attribution':{'author':'NVIDIA','credit':'NVIDIA; NVIDIA reference imagery; all rights retained.','license':'NVIDIA reference imagery; all rights retained.','source':DOWNLOADS[PHOTOS[i-1]]['source'],'reference_page':DOWNLOADS[PHOTOS[i-1]].get('reference_page'),'sha256':DOWNLOADS[PHOTOS[i-1]]['sha256']}})
(OUT/'slide-content.json').write_text(json.dumps(content,indent=2)+'\n')
(OUT/'SPEAKER_NOTES.md').write_text('# HPC section speaker notes\n\nTarget duration: 3–4 minutes. The slides are numbered 33–40 for integration after the existing 32 AI slides. Sources and background credits are in each PowerPoint slide’s Notes pane and `slide-content.json`.\n\n'+'\n\n'.join(f"## Slide {x['slide']} · {x['title']}\n\n"+x['speaker_notes_en'].split('\n\nResearch sources:')[0] for x in content)+'\n')
(OUT/'layout-validation.json').write_text(json.dumps({'slide_count':len(prs.slides),'slide_size_inches':[W,H], 'minimum_body_font_pt':18,
 'note':'Body text is at least 18 pt except the quiet footer and slide numbers. Charts use native editable PowerPoint shapes.',
 'text_boxes':layout,'backgrounds':[{'slide':i,'id':DOWNLOADS[PHOTOS[i-1]]['id'],'file':DOWNLOADS[PHOTOS[i-1]]['file'],'sha256':DOWNLOADS[PHOTOS[i-1]]['sha256'],'source':DOWNLOADS[PHOTOS[i-1]]['source']} for i in range(1,9)]},indent=2)+'\n')
print(OUT/'HPC-section.pptx')

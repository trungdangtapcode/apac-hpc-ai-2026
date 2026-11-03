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
OUT = WORK/'submission-review/hpc-iris-slides-20261103/slide-section'
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
prs.core_properties.subject='Eight-slide HPC section; reviewed research through 3 November 2026'
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
    text(s,f'{idx+34:02d} / 42',11.85,7.06,.82,.24,10,GRAY,align='right')
    rect(0,7.465,W,.035,PALE);rect(0,7.465,W*(34+idx)/42,.035,ORANGE)
    bg=DOWNLOADS[PHOTOS[idx-1]]
    s.notes_slide.notes_text_frame.text=notes+'\n\nResearch sources: '+source+'\nBackground attribution: '+json.dumps({'author':'NVIDIA','credit':'NVIDIA; NVIDIA reference imagery; all rights retained.','license':'NVIDIA reference imagery; all rights retained.','source':bg['source'],'reference_page':bg.get('reference_page'),'role':'Faint atmospheric backdrop; reference imagery, not the contest cluster.'},ensure_ascii=False)
    return s

def end(): pdf.showPage()

SRC4='/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md'
SRC2='/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/shared-cpu-density-review-20261022/RESULTS.md'
GUIDE='/home/apacsc42/workspace/reports/hpc-research-journey-20261023/'

# 1 — task and metric
s=start('The task: same 65-million-cell airflow calculation',1,
"We optimize execution of the official OpenFOAM v2512 car-flow case, not its mathematics. This slide describes the completed NSCC reference reproduction; Iris screening uses one node and 56 ranks with explicitly shorter horizons. The mesh contains 65,334,765 cells. The job completes the prescribed preparation and 150 solver iterations on four nodes. The measured metric is the solver's average wall-clock seconds per time step, beginning with the second solver iteration; lower is better. The retained final drag coefficient is a physical sanity signal, not the performance score.",SRC4+'; '+GUIDE+'FOUNDATIONS.md')
text(s,'65.3 million',.95,1.38,6.2,.76,36,ORANGE,True);text(s,'mesh cells',.98,2.16,5.8,.42,22,INK)
text(s,'NSCC: 4 nodes',.95,3.00,4.4,.65,32,INK,True);text(s,'512 MPI ranks · 128 per node',.98,3.69,5.0,.54,19,GRAY)
text(s,'150 steps',7.2,1.40,4.6,.66,32,INK,True);text(s,'149 timed samples',7.23,2.12,4.8,.44,19,GRAY)
text(s,'Metric',7.2,3.04,4.5,.44,20,ORANGE,True);text(s,'Average seconds per solver step',7.2,3.54,5.2,.54,22,INK,True)
text(s,'Lower is better · every required step stays in the run',7.22,4.24,5.2,.82,18,GRAY)
rect(.95,5.58,11.45,.025,PALE)
text(s,'Iris screens use shorter horizons; they are not official scores.',.97,5.90,11.2,.60,25,INK,True)
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
s=start('Early lesson: a smaller graph cut did not mean faster',3,
"The NUMA-aware decomposition hypothesis was that grouping work by memory locality might reduce communication and improve speed. Its graph cut fell by 10.63%, but the solver mean worsened from 13.881 to 14.359 seconds per step, a 3.4416% slowdown. The comparison also changed other partition properties, so the cut alone cannot explain the runtime. We closed the unchanged branch. A separate offline mapping reduced a graph cut by 4.5741% but has no measured solver result.",GUIDE+'JOURNEY.md; '+GUIDE+'figures/research-journey.png')
text(s,'NUMA-aware idea',.95,1.42,5.0,.52,25,INK,True);text(s,'Reduce remote-memory / interface cost',.98,2.02,5.2,.54,18,GRAY)
text(s,'−10.63%',.98,2.86,4.4,.70,33,ORANGE,True);text(s,'graph cut',1.0,3.56,4.4,.40,18,GRAY)
line(5.75,3.30,7.1,3.30,INK,2.0);text(s,'≠',6.17,2.84,.55,.56,27,RED,True,align='center')
text(s,'+3.4416%',7.55,2.86,4.3,.70,33,RED,True);text(s,'slower solver mean',7.58,3.56,4.4,.40,18,GRAY)
rect(.98,4.64,11.26,.035,PALE)
text(s,'Lesson',.98,5.02,1.7,.42,20,ORANGE,True);text(s,'A graph proxy is not a runtime measurement.',2.2,4.98,9.8,.55,23,INK,True)
text(s,'Cause not measured: MPI wait, bandwidth, frequency, power, page residency',.99,5.80,11.3,.48,18,GRAY)
end()


COMPARE='/home/apacsc42/workspace/reports/hpc-iris-comparison-20261103/'
GRAPH='/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/completed-2294390/RESULTS.md'

# 4 — explicit definitions and observed minima; not a ranking.
s=start('Three Iris recipes: lowest observed completed means',4,
"On Iris, one node and 56 MPI ranks run the full-size physical mesh. The organizer uses Scotch decomposition, default MPI placement and uncollated output. The supplied teammate settings use the same Scotch source, socket/core MPI mapping and collated output; this ports runtime settings to Iris, not the entire Gadi environment. Our lowest individual completed arm uses hierarchical zyx decomposition plus graph-based rank placement. Its mean is 21.051168941923077 seconds per step in job 2294390 B1-graph, with only 14 steps / 13 measured intervals. Organizer job 2294640 A1-scotch reaches 22.35823713823077 over 40 / 39; teammate job 2294637 B1-teammate reaches 22.396949742666667 over 40 / 39. These are the lowest whole-arm arithmetic means, not fastest individual steps. They come from separate allocations and different horizons; do not rank optimizations by these minima. Our plain zyx also completed 50 steps at 21.112004724 and 150 at 21.229593669, but neither proves a stable matched win.",COMPARE+'BEST_RECORDED.md; '+COMPARE+'BEST_RECORDED_EVIDENCE.json')
text(s,'One Iris node · 56 MPI ranks · full-size mesh',.95,1.18,11.5,.45,21,GRAY)
text(s,'Recipe and tested change',.98,1.93,6.7,.4,19,INK,True)
text(s,'Mean s/step',7.55,1.93,2.3,.4,19,INK,True)
text(s,'Steps / samples',10.0,1.93,2.4,.4,19,INK,True)
rows=[('Ours: hierarchical zyx + graph placement','Change partitioning and rank-to-core assignment','21.0512','14 / 13'),('Organizer: Scotch + default MPI','Uncollated output','22.3582','40 / 39'),('Teammate settings ported to Iris','Scotch + socket/core mapping + collated output','22.3969','40 / 39')]
for i,(name,detail,val,n) in enumerate(rows):
 y=2.55+i*1.05
 line(.98,y-.16,12.3,y-.16,PALE,1)
 text(s,name,.98,y,6.3,.4,21,INK,True);text(s,detail,1.0,y+.43,6.4,.4,17,GRAY)
 text(s,val,7.55,y+.08,2.3,.5,26,INK,True);text(s,n,10.2,y+.12,2.1,.4,21,INK)
text(s,'Different allocations and horizons: these minima are not a matched ranking.',.98,6.06,11.55,.8,21,ORANGE,True)
end()

# 5 — compare treatments only to their own allocation's control.
s=start('Matched comparisons give a different answer',5,
"Each row is a separate Iris allocation with two candidate and two control arms. The shown means pool the equal-length arms within each row; changes are relative to that row's own organizer control. Job 2294637: teammate 24.745277978102565 versus organizer 27.873469742846154 seconds per step, 11.2228% lower, 40 steps / 39 intervals per arm. Both adjacent comparisons favor the candidate, but same-treatment drift is about 18–21% and the organizer sample recommendation exceeds 39. This is a favorable short-run signal, not a stable final score or proof of the runtime mechanism. Job 2294640: plain hierarchical zyx 29.64902420125641 versus Scotch 26.901084925358974, 10.2150% slower, 40 / 39. Job 2294644: xzy 29.06256515409804 versus Scotch 26.360000645833335, 10.2525% slower, 52 / 51. That reversed-order check overturns the earlier 0.7097% lower time from job 2294643. No complete matched three-way test establishes that our configurations beat the teammate. Native output, work, source and force-coefficient checks are retained in the linked reviews.",COMPARE+'README.md; '+COMPARE+'EVIDENCE.json')
text(s,'Candidate versus its own control · mean seconds per step',.96,1.20,11.5,.45,21,GRAY)
cols=[(.98,'Candidate'),(5.10,'Control'),(7.45,'Candidate'),(10.10,'Time change')]
for x,label in cols:text(s,label,x,1.97,2.7,.4,19,INK,True)
rows=[('Teammate settings','40 steps per arm','27.8735','24.7453','−11.22%',ORANGE),('Our plain zyx','40 steps per arm','26.9011','29.6490','+10.21%',RED),('Our xzy: reverse check','52 steps per arm','26.3600','29.0626','+10.25%',RED)]
for i,(label,sub,a,b,pct,col) in enumerate(rows):
 y=2.65+i*1.02;line(.98,y-.15,12.25,y-.15,PALE,1)
 text(s,label,.98,y,4.1,.4,21,INK,True);text(s,sub,1.0,y+.43,4.1,.36,18,GRAY)
 text(s,a,5.10,y+.10,2.15,.5,24,INK);text(s,b,7.45,y+.10,2.25,.5,24,INK);text(s,pct,10.1,y+.10,2.20,.5,24,col,True)
text(s,'Negative = faster. Each row uses its own control; do not rank rows by seconds.',.98,5.94,11.4,.47,18,GRAY)
text(s,'Teammate signal is promising; our stable matched win is still unproven.',.98,6.45,11.4,.42,20,ORANGE,True)
end()

# 6 — retain the historical tail example, explicitly dated.
# 6 tails
s=start('Keep every measured step; investigate slow tails',6,
"Historical NSCC job 25921488 from 23 October, mean 3.677906731 seconds per step: Scotch-128 has a median of 3.298742 seconds, p95 of 3.795740 seconds, and maximum of 35.883552 seconds at solver Time 119. All 149 timed samples remain in the arithmetic mean. The review did not collect enough hardware counters to attribute the spike to MPI, CPU scheduling, memory or I/O. The sample-size warning motivates independent repeats; it does not authorize removing the slow point or changing the prescribed endpoint.",SRC4+'; '+GUIDE+'figures/iteration-spikes.png')
text(s,'3.298742 s',.96,1.56,3.55,.62,29,INK,True);text(s,'median',.98,2.20,3.2,.32,18,GRAY)
text(s,'3.795740 s',4.85,1.56,3.55,.62,29,INK,True);text(s,'95th percentile',4.87,2.20,3.2,.32,18,GRAY)
text(s,'35.883552 s',8.76,1.56,3.75,.62,29,RED,True);text(s,'maximum · Time 119',8.78,2.20,3.3,.32,18,GRAY)
line(1.05,3.33,12.15,3.33,PALE,2);rect(1.05,3.20,.15,.25,ORANGE);rect(9.85,3.08,.22,.50,RED)
text(s,'NSCC, 23 Oct: 149/149 samples retained',.98,4.06,10.8,.48,22,INK,True);text(s,'Official-style arithmetic mean includes every measured step.',.99,4.65,8.6,.43,18,GRAY)
text(s,'Cause unknown',.99,5.48,2.5,.40,20,ORANGE,True);text(s,'No measured MPI wait, bandwidth, frequency, power or page residency',3.72,5.44,8.8,.64,18,GRAY)
end()


# 7 — directly answer why the graph screen is shorter than the 40-step runs.
s=start('Why the 21.051 s/step result used only 14 steps',7,
"The 14-step horizon was a deliberate short screen for graph-based rank placement within a bounded 50-minute allocation, not an official or final 40-step comparison. The previous allocation's slow last baseline motivated a reversed B-A-A-B order, where B is graph placement and A is identity placement on the same hierarchical zyx source. Job 2294390 completed all four arms. The first graph arm averaged 21.051168942 seconds per step, but the repeated graph arm averaged 38.462425. Across the complete cycle, graph placement was 5.3685% slower than its identity control. Same-treatment drift was +43.0147% for control and +82.7092% for candidate; the direction was not robust. We closed this unchanged performance branch rather than promoting the selected fast arm. Plain zyx was separately tested for 40 steps in job 2294640 and lost 10.2150%; it is not the same configuration as zyx plus graph placement. A fair future promotion must hold recipe, hardware, input, horizon and measurement definition fixed, retain all samples, and survive a reversed-order repeat. The current records contain no completed matched 40-step three-way win.",GRAPH+'; '+COMPARE+'README.md')
text(s,'14-step screen',.98,1.40,5.4,.55,28,INK,True)
text(s,'Graph-based rank placement',.99,2.00,5.4,.45,21,GRAY)
text(s,'21.051 s/step',.98,2.77,5.4,.68,35,ORANGE,True)
text(s,'Fastest arm: 13 measured intervals',1.0,3.52,5.35,.5,19,GRAY)
line(6.4,1.50,6.4,4.25,PALE,1.4)
text(s,'Complete reversed test',6.95,1.40,5.35,.55,26,INK,True)
text(s,'Graph → identity → identity → graph',6.97,2.00,5.1,.78,19,GRAY)
text(s,'5.37% slower',6.95,2.92,5.3,.66,33,RED,True)
text(s,'Overall result: close this branch',6.97,3.66,5.1,.5,20,INK)
line(.98,4.53,12.26,4.53,PALE,1.2)
text(s,'Plain zyx already ran 40 steps — a different configuration.',.98,4.92,11.4,.55,23,INK,True)
text(s,'Its matched mean was 10.21% slower. Neither test supports promotion.',.98,5.69,11.4,.65,21,GRAY)
end()

# 8 — current platform-specific conclusion, no stale pending-job claim.
s=start('What we can defend — and what remains to test',8,
"Our best reviewed NSCC run is job 25940700, 3.364622070 seconds per step over 150 steps / 149 measured intervals on four nodes and 512 ranks. This is our reproduction of the organizer's recipe, not a new optimization. The old 23 October slides described this job as queued; that status is historical and is superseded here. The organizer's separate NSCC reference is 3.210832548, and the supplied teammate log on Gadi is 2.079045460. Different machines and allocations prevent attributing these raw-time gaps to configuration. On Iris, the teammate runtime settings have a qualified 11.22% lower-time signal; our decomposition and graph-placement variants have not established a stable matched win. The next investigated factor is preparation memory policy. Qualification job 2294675 changed aggregate file-page distribution across NUMA nodes, but did not run OpenFOAM and does not prove a solver speedup. The separate native test is excluded from this deck until reviewed; this slide makes no live scheduler claim. The presentation separates completed observation, baseline reproduction, matched evidence and future hypothesis.",COMPARE+'README.md; /home/apacsc42/workspace/notes/HPC_CURRENT.md; /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-preparation-numa-qualify-r2-20261103/completed-2294675/RESULTS.md')
text(s,'NSCC: reference reproduction',.98,1.38,6.5,.5,25,INK,True)
text(s,'3.3646 s/step',.98,2.05,6.0,.75,37,ORANGE,True)
text(s,'4 nodes · 512 ranks · 150 steps',1.0,2.90,5.9,.46,21,GRAY)
text(s,'Same organizer recipe; not our new optimization.',1.0,3.54,5.5,.85,20,INK)
line(6.62,1.45,6.62,4.36,PALE,1.2)
text(s,'Iris: qualified recipe signal',7.05,1.38,5.2,.52,24,INK,True)
text(s,'11.22% lower time',7.05,2.10,5.1,.65,29,ORANGE,True)
text(s,'Teammate settings versus matched control',7.07,2.91,5.0,.76,20,GRAY)
text(s,'Repeat drift limits confidence.',7.07,3.83,5.0,.43,20,INK)
line(.98,4.70,12.25,4.70,PALE,1.2)
text(s,'Next factor: preparation memory placement',.98,5.05,11.4,.5,23,INK,True)
text(s,'Mechanism observed; solver benefit still requires a valid matched result.',.98,5.78,11.4,.72,21,GRAY)
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
(OUT/'SPEAKER_NOTES.md').write_text('# HPC section speaker notes\n\nTarget duration: 3–4 minutes. The slides are numbered 35–42 for integration after the existing 34 AI slides (16 main plus 18 hidden backups). Sources and background credits are in each PowerPoint slide’s Notes pane and `slide-content.json`.\n\n'+'\n\n'.join(f"## Slide {x['slide']} · {x['title']}\n\n"+x['speaker_notes_en'].split('\n\nResearch sources:')[0] for x in content)+'\n')
(OUT/'layout-validation.json').write_text(json.dumps({'slide_count':len(prs.slides),'slide_size_inches':[W,H], 'minimum_body_font_pt':17,
 'note':'Body text is at least 17 pt except the quiet footer and slide numbers. Charts use native editable PowerPoint shapes.',
 'text_boxes':layout,'backgrounds':[{'slide':i,'id':DOWNLOADS[PHOTOS[i-1]]['id'],'file':DOWNLOADS[PHOTOS[i-1]]['file'],'sha256':DOWNLOADS[PHOTOS[i-1]]['sha256'],'source':DOWNLOADS[PHOTOS[i-1]]['source']} for i in range(1,9)]},indent=2)+'\n')
print(OUT/'HPC-section.pptx')

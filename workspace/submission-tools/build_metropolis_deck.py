"""Metropolis-adapted technical deck: editable diagrams, sourced assets, real data."""
import json
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import fitz

WORK=Path('/home/apacsc42/workspace')
FINAL=WORK/'VNUHCM - TripleU'
OUT=WORK/'submission-review/metropolis-ambient-backgrounds-2026-10-13'
OUT.mkdir(parents=True,exist_ok=True)
ASSETS=OUT/'assets';ASSETS.mkdir(exist_ok=True)
EXTERNAL=Path(__file__).parent/'design-assets'
BACKGROUND_MANIFEST=json.loads((EXTERNAL/'slide-backgrounds.json').read_text())
BACKGROUNDS=BACKGROUND_MANIFEST['slides']
assert len(BACKGROUNDS)==19 and len({r['sha256'] for r in BACKGROUNDS})==19
DATA=json.loads((WORK/'submission-review/english-2026-10-12/Presentation/presentation-data.json').read_text())
old=Presentation(FINAL/'Presentation/TripleU_APAC2026_Presentation.pptx')
note_source=WORK/'submission-review/metropolis-2026-10-12/original-speaker-notes.json'
if note_source.exists():NOTES=json.loads(note_source.read_text())
else:
    NOTES=[s.notes_slide.notes_text_frame.text for s in old.slides]
    note_source.write_text(json.dumps(NOTES,indent=2)+'\n')
NOTES=[
 'Our task is to serve Qwen3-235B on sixteen H200 GPUs with disaggregated prefill and decode. Each request contains about 4000 input tokens and produces 200 output tokens. We optimise the serving configuration and KV-transfer path while retaining the published FP8 model computation.',
 'The selected configuration reaches 1912.30 good output tokens per second at concurrency 48. A total of 97.44% of requests satisfy both latency limits. This is a 14.78% end-to-end improvement over our previous best configuration. The gain combines topology, concurrency and transport changes.',
 'Goodput is determined per request. Time to the first token must be at most 3000 milliseconds, and the average interval between output tokens must be at most 20 milliseconds. At least 90% of requests must meet both limits. Increasing raw throughput alone is insufficient.',
 'The platform has two nodes with eight H200 GPUs each, connected through InfiniBand NDR. We use the official FP8 checkpoint and BF16 KV cache. SGLang provides inference and NIXL provides cross-node KV transfer. No tensor-parallel group spans both nodes.',
 'The selected topology uses two four-GPU prefill workers on the first node and one eight-GPU decode worker on the second. Prefill uses TP4/EP1; decode uses TP8/EP8. There are two possible KV-transfer paths. Every request is prefilled on a prefill worker and decoded on the decode worker.',
 'The starting layout has four TP2 prefill workers and two TP4/EP4 decode workers. Widening prefill to TP4 reduces the number of replicas to two. The selected layout also widens decode to TP8/EP8. These choices trade replica count for parallelism within each request, so we compare them under the latency gate.',
 'We explore seventeen usable arrangements across 8+8, 4+12 and 12+4 GPU splits. We vary tensor parallelism and test concurrency 16, 32, 40 and 48. Fourteen originals and three distinct EP2 replacements are measured. The original TP8/EP1 layouts cannot load the FP8 block geometry and remain separate from their replacements.',
 'We initialise the serving workers and all P/D connections before benchmarking. The official client performs 60 seconds of warmup, 120 seconds of measurement and 30 seconds of grace. The workload is closed-loop: each completed request is immediately replaced, sustaining the chosen concurrency.',
 'The short sweep shows throughput rising with concurrency, while the fraction satisfying both SLAs decreases. At N48, the selected layout still passes the 90% gate. We use short runs to screen settings, then confirm the selected operating point with the full measurement duration.',
 'All bars show long measurements on the same sixteen-GPU platform. The selected TP4-to-TP8/EP8 layout reaches 1912.30 good tokens per second, compared with 1666.01 for the previous best. The alternative TP8/EP2 layout is slower. These comparisons measure the complete configuration rather than isolate the patch alone.',
 'The scatter plot shows time to first token and mean inter-token latency for each request. Of 1211 requests, 1180 meet both limits. Thirty-one miss a limit; no request errors or cancellations occurred. The distribution matters because aggregate averages alone cannot establish the 90% gate.',
 'Cold KV-transfer setup can stall before the measured workload begins. The original path timed out after 480 seconds. With request-scoped descriptor preparation, workers were ready at 269 seconds and all P/D paths were warm at 303 seconds. Those timestamps include worker and connection setup, not just the KV copy. The benchmark latency thresholds are unchanged.',
 'FP8 quantisation uses 128-wide blocks. TP8/EP1 creates 192-wide expert shards, leaving a partial block. EP2 distributes experts into two groups and gives effective TP4, creating 384-wide shards that fit exactly three blocks. All experts and weights are retained; this is a different parallelism configuration, not model pruning.',
 'The original NIXL path prepares descriptors for the entire KV pool. Our patch prepares them for the request pages instead. For the illustrated TP8-source geometry, the full pool contains about 403.8 million source entries per rank, whereas a contiguous 4000-token request can be coalesced to 188 entries. Head mapping, byte ranges and notifications are preserved. The two transport paths passed 720 and 936 CPU range comparisons and served GPU benchmarks.',
 'At N48, the mean time to first token is about 1482 milliseconds against a 3000-millisecond limit. Mean ITL is 16.79 milliseconds against a 20-millisecond limit. Decode latency is closer to its threshold. These means illustrate headroom; the actual acceptance decision remains per request and is shown by the distribution.',
 'Latency and output quality are separate checks. The selected configuration passes the latency gate. We retain the published FP8 weights, BF16 KV and the same model computation. Full-set accuracy evaluation against the organisers reference remains the next validation step; we do not claim that it is already complete.',
 'The selected operating point is two TP4 prefill workers, one TP8/EP8 decode worker and concurrency 48. It delivers 1912.30 good output tokens per second with 97.44% of requests satisfying both SLAs. The key changes are the parallelism balance and request-scoped KV descriptor preparation.',
 'This alternative uses TP8/EP2 prefill and TP8/EP8 decode. Its N40 and N48 sweeps fail the 90% gate despite higher throughput. Long N32 passes with 1507.96 good tokens per second and 95.38% SLA, so it is viable but slower than the selected layout.',
 'Invite questions about tensor and expert parallelism, the KV-transfer optimisation, and throughput under the latency constraints. Explain that all sixteen GPUs are used, the model computation is retained, and the full-set accuracy check is still outstanding.'
]
best=DATA['best'];previous=DATA.get('previous_best',DATA['declared_basic']);baseline=DATA['baseline'];equal=DATA['equal_patch']
assert best['job']=='22415' and best['concurrency']==48
W,H=13.333333,7.5
PAPER='#FAFAFA';INK='#23373B';ORANGE='#EB811B';GRAY='#737F82';PALE='#E5E9E9';RED='#A94442';WHITE='#FFFFFF'
FONT='Helvetica';BOLD='Helvetica-Bold';MONO='Courier'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':16,'figure.facecolor':PAPER,
 'axes.facecolor':'none','text.color':INK,'axes.labelcolor':INK,'xtick.color':GRAY,'ytick.color':GRAY,
 'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#CCD3D4'})

def save_plot(fig,name):
    fig.savefig(ASSETS/(name+'.png'),dpi=200,bbox_inches='tight',transparent=True)
    fig.savefig(ASSETS/(name+'.svg'),bbox_inches='tight',transparent=True)
    plt.close(fig);return ASSETS/(name+'.png')

sweeps=sorted([m for m in DATA['results'] if m['job']=='22415' and m['phase']=='sweep'],key=lambda m:m['concurrency'])
fig,axes=plt.subplots(1,2,figsize=(12,4.1),gridspec_kw={'width_ratios':[1.15,1]})
ns=[m['concurrency'] for m in sweeps];x=np.arange(4)
axes[0].bar(x,[m['raw_output_tokens_s'] for m in sweeps],.65,color=PALE,label='All output')
axes[0].bar(x,[m['good_output_tokens_s'] for m in sweeps],.40,color=ORANGE,label='Good output')
axes[0].set_xticks(x,ns);axes[0].set_ylim(0,2300);axes[0].set_ylabel('Output tokens / second');axes[0].set_xlabel('Concurrent requests')
axes[0].legend(frameon=False,fontsize=12,loc='upper left')
for i,m in enumerate(sweeps):axes[0].text(i,m['good_output_tokens_s']+55,f"{m['good_output_tokens_s']:,.0f}",ha='center',fontsize=13,color=INK)
fractions=[m['good_request_fraction']*100 for m in sweeps]
axes[1].plot(ns,fractions,'o-',color=ORANGE,lw=2.2,ms=7)
axes[1].axhline(90,color=RED,lw=1.4,ls='--')
axes[1].text(17,89.2,'90% gate',color=RED,fontsize=12,va='top')
for n,v in zip(ns,fractions):axes[1].annotate(f'{v:.2f}%',(n,v),(0,12),textcoords='offset points',ha='center',fontsize=13)
axes[1].set_xticks(ns);axes[1].set_ylim(85,105);axes[1].set_xlabel('Concurrent requests');axes[1].set_ylabel('Requests passing both SLAs (%)')
fig.tight_layout(w_pad=2.7);sweep_plot=save_plot(fig,'winning-sweeps')

comp=[best,previous,equal,baseline]
fig,ax=plt.subplots(figsize=(12,4.15))
labels=['Selected · TP4 → TP8/EP8 · N48','TP4 → TP4/EP4 · N40','TP8/EP2 → TP8/EP8 · N32','Reference · TP2 → TP4/EP4 · N32']
bars=ax.barh(np.arange(4),[m['good_output_tokens_s'] for m in comp],color=[ORANGE,INK,GRAY,'#BAC3C5'],height=.54)
ax.set_yticks(np.arange(4),labels,fontsize=15);ax.invert_yaxis();ax.set_xlim(0,2300);ax.set_xlabel('Good output tokens / second')
ax.set_xticks([0,500,1000,1500,2000]);ax.grid(axis='x',alpha=.20);ax.set_axisbelow(True)
for bar,m in zip(bars,comp):ax.text(bar.get_width()+32,bar.get_y()+bar.get_height()/2,f"{m['good_output_tokens_s']:,.2f}",va='center',fontsize=17,fontweight='bold')
fig.tight_layout();compare_plot=save_plot(fig,'long-run-comparison')

points=[]
for line in (FINAL/'AI_Task/logs/measured/22415/confirm/n48/artifacts/profile_export.jsonl').open():
    r=json.loads(line)
    if r['metadata'].get('benchmark_phase')!='profiling':continue
    metrics=r['metrics'];points.append((metrics['time_to_first_token']['value'],metrics['inter_token_latency']['value']))
points=np.asarray(points);passed=(points[:,0]<=3000)&(points[:,1]<=20)
assert len(points)==1211 and int(passed.sum())==1180
fig,ax=plt.subplots(figsize=(8.5,4.65))
ax.axvspan(0,3000,color='#EDF2F0');ax.scatter(points[passed,0],points[passed,1],s=13,alpha=.28,color=INK,label='Pass both')
ax.scatter(points[~passed,0],points[~passed,1],s=31,alpha=.85,color=ORANGE,label='Miss a limit')
ax.axvline(3000,color=RED,ls='--',lw=1.4);ax.axhline(20,color=RED,ls='--',lw=1.4)
ax.set_xlim(0,max(7000,float(points[:,0].max())*1.06));ax.set_ylim(0,max(26,float(points[:,1].max())*1.06));ax.set_xlabel('Time to first token (ms)');ax.set_ylabel('Per-request mean ITL (ms)')
ax.legend(frameon=False,fontsize=12,loc='upper left');fig.tight_layout();sla_plot=save_plot(fig,'per-request-sla')

prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H)
prs.core_properties.title='TripleU — Qwen3 PD inference on 16 H200 GPUs'
prs.core_properties.author='VNUHCM - TripleU'
prs.core_properties.subject='Metropolis-adapted technical presentation; declared Basic N48 winning stack'
# Put the theme in the PPTX itself, rather than only painting per-slide objects.
theme=next(part for part in prs.part.package.iter_parts() if str(part.partname)=='/ppt/theme/theme1.xml')
from lxml import etree
t=etree.fromstring(theme.blob);nsmap={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
t.set('name','TripleU / Metropolis')
scheme=t.find('.//a:clrScheme',nsmap);scheme.set('name','Metropolis')
for name,color in [('dk1',INK),('lt1',PAPER),('dk2','#604C38'),('lt2',WHITE),('accent1',ORANGE),('accent2',GRAY),('accent3',RED),('accent4','#14B03D'),('accent5','#BAC3C5'),('accent6','#506C72')]:
    e=scheme.find('a:'+name,nsmap)
    for child in list(e):e.remove(child)
    child=etree.SubElement(e,'{'+nsmap['a']+'}srgbClr');child.set('val',color[1:])
for e in t.findall('.//a:fontScheme//a:latin',nsmap):e.set('typeface','Arial')
theme._blob=etree.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)

pdf=Canvas(str(OUT/'TripleU_APAC2026_Presentation.pdf'),pagesize=(W*72,H*72))
outline=[];bounds=[]
def rgb(c):return RGBColor.from_string(c[1:])

class Slide:
    def __init__(self,title,source='',notes='',cover=False,dark=False):
        self.s=prs.slides.add_slide(prs.slide_layouts[6]);self.n=len(prs.slides)
        self.title=title;self.source=source;self.lines=[];self.notes=notes;self.bg=INK if dark else PAPER
        self.s.background.fill.solid();self.s.background.fill.fore_color.rgb=rgb(self.bg)
        pdf.setFillColor(HexColor(self.bg));pdf.rect(0,0,W*72,H*72,fill=1,stroke=0)
        background=BACKGROUNDS[self.n-1]
        self.image(EXTERNAL/background['file'],0,0,W,H,crop=True,focus=background['focus'])
        if dark:self.gradient_rect(0,0,W,H,INK,'#355D68',.92,.84)
        else:self.gradient_rect(0,0,W,H,PAPER,'#F3F7F7',.91,.82)
        if not cover:
            self.gradient_rect(0,0,W,.84,INK,'#375C6A')
            self.text(title,.66,.21,12,.46,26,WHITE)
        # Quiet footer; progress bar is the Metropolis visual signature.
        # Submission provenance is metadata, not audience-facing slide text.
        self.text('TripleU  /  APAC HPC-AI 2026',.66,7.10,8,.20,9,GRAY if not dark else '#B5C1C3')
        self.text(f'{self.n:02d}',12.18,7.06,.5,.28,11,GRAY if not dark else '#B5C1C3')
        self.rect(0,7.465,W,.035,PALE if not dark else '#3F5459')
        self.rect(0,7.465,W*self.n/19,.035,ORANGE)
    def rect(self,x,y,w,h,fill,stroke=None,width=1):
        shape=self.s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        if fill:shape.fill.solid();shape.fill.fore_color.rgb=rgb(fill)
        else:shape.fill.background()
        if stroke:shape.line.color.rgb=rgb(stroke);shape.line.width=Pt(width)
        else:shape.line.fill.background()
        if fill:pdf.setFillColor(HexColor(fill))
        if stroke:pdf.setStrokeColor(HexColor(stroke));pdf.setLineWidth(width)
        pdf.rect(x*72,(H-y-h)*72,w*72,h*72,fill=int(bool(fill)),stroke=int(bool(stroke)))
        return shape
    def gradient_rect(self,x,y,w,h,start,end,start_alpha=1,end_alpha=1):
        shape=self.s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        shape.line.fill.background();shape.fill.gradient();shape.fill.gradient_angle=0
        for stop,color,alpha in zip(shape.fill.gradient_stops,(start,end),(start_alpha,end_alpha)):
            stop.color.rgb=rgb(color)
            clr=stop._gs.find('{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
            opacity=OxmlElement('a:alpha');opacity.set('val',str(round(alpha*100000)));clr.append(opacity)
        pdf.saveState()
        if start_alpha==end_alpha==1:
            clip=pdf.beginPath();clip.rect(x*72,(H-y-h)*72,w*72,h*72);pdf.clipPath(clip,stroke=0)
            pdf.linearGradient(x*72,(H-y)*72,(x+w)*72,(H-y)*72,[HexColor(start),HexColor(end)])
        else:
            # Render one continuous alpha overlay for the PDF. Adjacent
            # translucent vector strips can show antialiasing seams.
            # The PPTX uses the editable native gradient above, and original
            # photographs are never raster-edited or flattened into the tint.
            a=np.array([int(start[i:i+2],16) for i in (1,3,5)])/255
            b=np.array([int(end[i:i+2],16) for i in (1,3,5)])/255
            samples=np.linspace(0,1,2048)
            colors=(a[None,:]*(1-samples[:,None])+b[None,:]*samples[:,None])*255
            alpha=(start_alpha*(1-samples)+end_alpha*samples)*255
            row=np.column_stack((colors,alpha)).round().astype(np.uint8)
            overlay=Image.fromarray(np.broadcast_to(row[None,:,:],(2,2048,4)).copy())
            pdf.drawImage(ImageReader(overlay),x*72,(H-y-h)*72,w*72,h*72,mask='auto')
        pdf.restoreState()
        return shape
    def line(self,x1,y1,x2,y2,color=INK,width=1.2):
        shape=self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2))
        shape.line.color.rgb=rgb(color);shape.line.width=Pt(width)
        pdf.setStrokeColor(HexColor(color));pdf.setLineWidth(width);pdf.line(x1*72,(H-y1)*72,x2*72,(H-y2)*72)
    def arrow(self,x1,y1,x2,y2,color=INK,width=1.7):
        self.line(x1,y1,x2-.10,y2,color,width)
        triangle=self.s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,Inches(x2-.14),Inches(y2-.075),Inches(.15),Inches(.15))
        triangle.rotation=90;triangle.fill.solid();triangle.fill.fore_color.rgb=rgb(color);triangle.line.fill.background()
        path=pdf.beginPath();path.moveTo(x2*72,(H-y2)*72);path.lineTo((x2-.13)*72,(H-y2+.07)*72);path.lineTo((x2-.13)*72,(H-y2-.07)*72);path.close()
        pdf.setFillColor(HexColor(color));pdf.drawPath(path,fill=1,stroke=0)
    def text(self,text,x,y,w,h,size=20,color=INK,bold=False,mono=False):
        fam=MONO if mono else BOLD if bold else FONT
        lines=[]
        for paragraph in str(text).split('\n'):
            if not paragraph:lines.append('');continue
            current=''
            for word in paragraph.split():
                candidate=(current+' '+word).strip()
                if pdfmetrics.stringWidth(candidate,fam,size)>w*72 and current:lines.append(current);current=word
                else:current=candidate
            lines.append(current)
        leading=size*1.18
        if leading*len(lines)>h*72+.5:raise ValueError(f'Slide {self.n} text overflow: {text!r} ({leading*len(lines):.1f}>{h*72:.1f})')
        for line in lines:
            if pdfmetrics.stringWidth(line,fam,size)>w*72+.5:raise ValueError(f'Slide {self.n} unbreakable word overflow: {line}')
        box=self.s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame
        tf.clear();tf.word_wrap=False;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
            p.font.name='Courier New' if mono else 'Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
            p.space_before=p.space_after=Pt(0);p.line_spacing=Pt(leading)
            pdf.setFont(fam,size);pdf.setFillColor(HexColor(color));pdf.drawString(x*72,(H-y)*72-size*.94-i*leading,line)
        self.lines.append(str(text));bounds.append({'slide':self.n,'x':x,'y':y,'w':w,'h':h,'text':str(text)})
        return box
    def image(self,path,x,y,w,h,crop=False,focus=.5):
        iw,ih=Image.open(path).size
        if not crop:
            scale=min(w/iw,h/ih);pw,ph=iw*scale,ih*scale;px=x+(w-pw)/2;py=y+(h-ph)/2
            self.s.shapes.add_picture(str(path),Inches(px),Inches(py),Inches(pw),Inches(ph))
            pdf.drawImage(str(path),px*72,(H-py-ph)*72,pw*72,ph*72,mask='auto')
        else:
            fraction=min(1,(w/h)/(iw/ih));vfrac=min(1,(iw/ih)/(w/h))
            left=max(0,min(1-fraction,focus-fraction/2));right=1-left-fraction;top=(1-vfrac)/2
            picture=self.s.shapes.add_picture(str(path),Inches(x),Inches(y),Inches(w),Inches(h));picture.crop_left=left;picture.crop_right=right
            picture.crop_top=picture.crop_bottom=top
            pdf.saveState();clip=pdf.beginPath();clip.rect(x*72,(H-y-h)*72,w*72,h*72);pdf.clipPath(clip,stroke=0)
            fullw=w/fraction;fullh=h/vfrac
            pdf.drawImage(str(path),(x-left*fullw)*72,(H-y-h-top*fullh)*72,fullw*72,fullh*72);pdf.restoreState()
    def icon(self,name,x,y,size=.45):self.image(EXTERNAL/(name+'.png'),x,y,size,size)
    def chips(self,x,y,count,size=.37,color=ORANGE,gap=.12):
        for i in range(count):
            self.rect(x+i*(size+gap),y,size,size,None,color,1.5)
            self.rect(x+i*(size+gap)+.11,y+.11,size-.22,size-.22,color)
    def end(self):
        self.s.notes_slide.notes_text_frame.text=self.notes
        outline.append({'number':self.n,'title':self.title,'text':self.lines,'speaker_notes_en':self.notes})
        pdf.showPage()

# 01 — title / genuine product asset, not another metric dashboard.
s=Slide('Qwen3 PD inference',cover=True,source='Local evidence · job 22415 · organiser accuracy and official re-run pending',notes=NOTES[0])
s.text('APAC HPC-AI 2026  /  QWEN TASK',.76,.76,10,.4,14,ORANGE,bold=True)
s.text('Qwen3-235B\nPD inference\non 16 H200s',.76,1.57,7.2,2.66,43,bold=True)
s.line(.78,4.60,7.45,4.60,ORANGE,1.5)
s.text('VNUHCM - TripleU',.78,4.97,7,.48,24)
s.text('13 October 2026',.78,5.66,7,.36,17,GRAY)
s.end()

# 02 — one result, one simple comparison, no cards.
s=Slide('Performance at N48',notes=NOTES[1])
s.text('1,912.30',.75,1.55,8.4,1.28,76,bold=True)
s.text('good output tokens / second',.83,3.04,8.1,.57,27)
s.text('97.44%',9.45,1.79,3.1,.86,44,ORANGE,bold=True)
s.text('within both SLAs',9.48,2.91,3.1,.74,21)
s.line(.83,4.06,12.5,4.06,PALE,1.1)
s.text('Previous best',.84,4.65,2.52,.40,18,GRAY)
s.rect(3.52,4.68,6.3*previous['good_output_tokens_s']/best['good_output_tokens_s'],.41,GRAY)
s.text('1,666.01',10.05,4.60,2.5,.48,24)
s.text('Declared N48',.84,5.47,2.52,.40,18)
s.rect(3.52,5.50,6.3,.41,ORANGE)
s.text('+14.78%',10.05,5.42,2.5,.48,24,ORANGE,bold=True)
s.end()

# 03 — request lifecycle visual.
s=Slide('The latency gate',source='Official workload: 4000 input / 200 output tokens; TTFT ≤ 3000ms and mean ITL ≤ 20ms',notes=NOTES[2])
s.text('4,000-token prompt',.84,1.53,5,.51,25)
s.text('200 generated tokens',7.51,1.53,5,.51,25)
s.rect(.87,2.57,4.22,.91,INK);s.text('PREFILL',1.10,2.86,3.7,.41,21,WHITE)
s.arrow(5.33,3.02,6.81,3.02,ORANGE,2)
for i in range(10):s.rect(7.1+i*.48,2.59,.30,.88,ORANGE if i<3 else PALE)
s.line(.88,4.13,7.24,4.13,GRAY,1.2);s.line(.88,4.02,.88,4.24,GRAY);s.line(7.24,4.02,7.24,4.24,GRAY)
s.text('Time to first token ≤ 3,000 ms',1.09,4.48,6.05,.48,23)
s.line(7.81,4.13,8.29,4.13,GRAY);s.line(7.81,4.02,7.81,4.24,GRAY);s.line(8.29,4.02,8.29,4.24,GRAY)
s.text('Mean ITL ≤ 20 ms',7.68,4.48,4.77,.48,23)
s.text('≥ 90% of requests must pass both. Errors stay in the denominator.',.91,5.72,11.66,.68,25,ORANGE)
s.end()

# 04 — hardware / provenance.
s=Slide('Two nodes. Sixteen H200 GPUs.',source='Contest allocation: 2 × HGX H200; photo: NVIDIA H200 product page, not the contest installation',notes=NOTES[3])
s.image(EXTERNAL/'nvidia-h200.jpg',.73,1.43,6.10,4.83,crop=True,focus=.67)
s.icon('cpu',7.30,1.44,.52);s.text('16 GPUs',8.05,1.45,4.5,.64,32,bold=True)
s.icon('network',7.30,2.44,.52);s.text('InfiniBand NDR',8.05,2.47,4.5,.59,25)
s.line(7.31,3.37,12.56,3.37,PALE)
for i,(label,value) in enumerate([('MODEL','Published Qwen3 FP8'),('KV CACHE','BF16, verified in worker logs'),('SERVER','SGLang 0.5.17 / NIXL 1.3.2'),('CLIENT','AIPerf 0.12.0')]):
 y=3.71+i*.59;s.text(label,7.34,y,1.25,.28,10,GRAY,bold=True);s.text(value,8.71,y-.025,3.94,.42,17)
s.end()

# 05 — native editable 16-GPU map.
s=Slide('Winning topology: TP4 prefill → TP8 / EP8 decode',source='P8-TP4_D8-TP8-EP8 · two P/D paths · every scored request uses the gateway',notes=NOTES[4])
s.icon('server',.88,1.39,.42);s.text('NODE 0  /  PREFILL',1.49,1.44,4.6,.42,20,bold=True)
s.icon('server',7.70,1.39,.42);s.text('NODE 1  /  DECODE',8.31,1.44,4.45,.42,20,bold=True)
s.rect(.87,2.18,4.53,1.50,None,GRAY,1);s.text('Worker P0  ·  TP4 / EP1',1.15,2.39,4,.43,20);s.chips(1.25,3.07,4,.37,ORANGE,.32)
s.rect(.87,4.10,4.53,1.50,None,GRAY,1);s.text('Worker P1  ·  TP4 / EP1',1.15,4.31,4,.43,20);s.chips(1.25,4.99,4,.37,ORANGE,.32)
s.rect(7.69,2.18,4.76,3.42,None,GRAY,1);s.text('Worker D0  ·  TP8 / EP8',7.97,2.48,4.25,.50,22)
s.chips(8.14,3.53,4,.40,INK,.48);s.chips(8.14,4.50,4,.40,INK,.48)
s.arrow(5.41,2.94,7.61,2.94,ORANGE);s.arrow(5.41,4.83,7.61,4.83,ORANGE)
s.text('KV cache\nNIXL',5.63,3.50,1.83,1.02,21,ORANGE)
s.text('8 GPUs',2.27,6.04,2.86,.42,22,bold=True);s.text('8 GPUs',9.13,6.04,2.86,.42,22,bold=True)
s.end()

# 06 — physical layouts, not three identical text cards.
s=Slide('From the provided layouts to the selected split',source='Long local runs: 22197 / 22219 / 22415; N32 / N40 / N48 respectively',notes=NOTES[5])
for x,title,pt,dt,rate,col in [(1.0,'07',2,4,'1,297.02',GRAY),(5.08,'09',4,4,'1,666.01',INK),(9.22,'Selected',4,8,'1,912.30',ORANGE)]:
 s.text(title,x,1.42,3.2,.62,29,col,bold=True)
 s.text('PREFILL',x,2.31,3.2,.28,12,GRAY,bold=True)
 for i in range(8//pt):s.rect(x+i*.76,2.83,.54,.75,None,col,1.6)
 s.text(f'{8//pt} workers × TP{pt}',x,3.80,3.6,.53,19)
 s.text('DECODE',x,4.47,3.2,.28,12,GRAY,bold=True)
 for i in range(8//dt):s.rect(x+i*.76,4.98,.54,.50,col)
 s.text(f"{8//dt} {'worker' if dt==8 else 'workers'} × TP{dt}/EP{dt}",x,5.65,3.63,.46,18)
 s.text(rate,x,6.19,3.4,.46,23,col,bold=True)
s.end()

# 07 — visible finite search matrix.
s=Slide('Seventeen usable layouts measured',source='14 exact originals + 3 explicit EP2 replacements; incompatible TP8/EP1 originals remain labelled',notes=NOTES[6])
def matrix(x,y,p,d,tps,cell):
 s.text(f'P{p} + D{d} GPUs',x,y,len(tps)*cell+.85,.49,21,bold=True)
 s.text('Decode TP',x+.78,y+.76,len(tps)*cell,.27,12,GRAY)
 for j,tp in enumerate(tps):s.text(str(tp),x+.81+j*cell,y+1.23,cell,.34,17,GRAY)
 for i,tp in enumerate(tps):
  s.text(str(tp),x,y+1.84+i*cell,.49,.37,17,GRAY)
  for j,dt in enumerate(tps):
   xx=x+.75+j*cell;yy=y+1.78+i*cell
   s.rect(xx,yy,cell-.11,cell-.11,ORANGE if tp==8 else INK)
   s.text('EP2' if tp==8 else '4N',xx+.13,yy+.20,cell-.35,.41,15,WHITE,bold=True)
matrix(.82,1.45,8,8,[2,4,8],1.00)
matrix(5.03,1.45,4,12,[2,4],1.00)
matrix(9.02,1.45,12,4,[2,4],1.00)
s.text('Prefill TP',.85,6.22,3.4,.27,12,GRAY)
s.text('All layouts: N16 / N32 / N40 / N48',5.04,5.82,7.34,.68,24)
s.end()

# 08 — single-job protocol, timing shown to scale.
s=Slide('Benchmark protocol',notes=NOTES[7])
s.icon('timer',.87,1.46,.48);s.text('Initialise workers  →  warm P/D paths  →  sustain N48',1.64,1.52,10.5,.64,27)
s.text('Official client timeline',.89,2.73,11.6,.52,24)
x=.90;scale=11.60/210
for duration,label,col in [(60,'60s\nwarmup',GRAY),(120,'120s\nmeasurement',ORANGE),(30,'30s\ngrace',INK)]:
 w=duration*scale;s.rect(x,3.66,w,1.12,col);s.text(label,x+.17,3.83,w-.34,.82,21,WHITE);x+=w
s.text('Only this window contributes to goodput.',4.50,5.12,6.43,.54,23,ORANGE)
s.text('Closed loop: completion immediately triggers the next request, sustaining N48.',.90,6.03,11.6,.58,20)
s.end()

# 09 / 10 / 11 — large scientific figures.
s=Slide('Load selection: N48 passes the short sweep',source='Job 22415 · exploratory 10 / 20 / 30 runs; confirmation uses a separate 120s window',notes=NOTES[8])
s.image(sweep_plot,.60,1.33,12.12,4.76)
s.text('Short N48: 1,788.65 good tokens/s  ·  90.95% SLA',.92,6.26,11.65,.37,20)
s.end()
s=Slide('Long-run comparison: +14.78% over the previous best',source='All bars: passing local 60 / 120 / 30 confirmations on the same 16-H200 platform',notes=NOTES[9])
s.image(compare_plot,.70,1.29,11.91,4.87)
s.text('Topology, concurrency and transport changed; this is an end-to-end gain.',.91,6.27,11.7,.36,19,GRAY)
s.end()
s=Slide('Per-request latency: 1,180 of 1,211 pass both limits',notes=NOTES[10])
s.image(sla_plot,.55,1.36,8.6,4.95)
s.text('97.44%',9.54,1.96,3.2,.88,45,ORANGE,bold=True)
s.text('31 miss a limit\n0 errors\n0 cancellations',9.59,3.27,2.86,1.39,21)
s.text('TTFT mean 1,482 ms\nITL mean 16.79 ms',9.59,5.04,2.86,1.0,17,GRAY)
s.end()

# 12 — diagnostics with a visible before/after, not a generic list of issues.
s=Slide('Cold KV-transfer setup',notes=NOTES[11])
s.text('Whole-pool descriptors',.86,1.48,5.3,.59,27,RED,bold=True)
s.text('480s',.90,2.40,5.3,1.01,55,RED,bold=True)
s.text('Pair warmup timed out.\nMeasurement could not begin.',.93,3.80,5.3,1.05,24)
s.line(6.48,1.44,6.48,6.34,PALE,1.4)
s.text('Request-scoped descriptors',7.12,1.48,5.3,.59,24,INK,bold=True)
s.text('COMPLETED',7.17,2.52,5.3,.83,34,bold=True)
s.text('Workers ready at 269s.\nAll P/D paths warm at 303s.\nFour sweeps + long N32.',7.19,3.75,5.18,1.65,23)
s.text('Connection setup is separate from the measured latency window.',.92,6.14,11.62,.49,19,GRAY)
s.end()

# 13 — block geometry made visual.
s=Slide('FP8 block alignment requires a distinct EP2 variant',source='MoE intermediate dimension 1536; FP8 block_n = 128; all 128 experts and published weights retained',notes=NOTES[12])
s.text('TP8 / EP1',.91,1.50,5.0,.61,29,RED,bold=True)
s.text('1536 ÷ 8 = 192',.95,2.51,5.01,.78,34)
s.rect(.99,3.74,2.0,1.10,INK);s.text('128',1.57,4.04,1.05,.47,24,WHITE)
s.rect(3.05,3.74,1.00,1.10,RED);s.text('64',3.26,4.04,.70,.47,24,WHITE)
s.text('A partial block remains.',.99,5.30,5.1,.58,23,RED)
s.line(6.47,1.43,6.47,6.16,PALE,1.4)
s.text('TP8 / EP2',7.14,1.50,5.0,.61,29,bold=True)
s.text('1536 ÷ 4 = 384',7.18,2.51,5.01,.78,34)
for i in range(3):
 s.rect(7.21+i*1.66,3.74,1.59,1.10,ORANGE);s.text('128',7.54+i*1.66,4.04,1.02,.47,24,WHITE)
s.text('Three complete 128-wide blocks.',7.21,5.30,5.04,.87,23)
s.end()

# 14 — asset is the algorithm, with native editable pool/page visual.
s=Slide('NIXL: describe the request, not the whole KV pool',source='Geometry example: TP8 source, 94 layers, 4,000 contiguous tokens; not every TP4→TP8 transfer has 188 entries',notes=NOTES[13])
s.text('Whole-pool plan',.93,1.45,5.2,.47,25,bold=True)
for row in range(7):
 for col in range(17):s.rect(.99+col*.28,2.27+row*.25,.21,.15,ORANGE if row==3 and 5<=col<=8 else '#C4CDCF')
s.text('403.8 million',.99,4.41,5.1,.87,40,GRAY,bold=True)
s.text('source entries / rank',1.03,5.52,4.95,.47,23,GRAY)
s.arrow(6.10,3.28,7.01,3.28,ORANGE,2.1)
s.text('Request-scoped plan',7.44,1.45,5.2,.47,25,bold=True)
for row in range(4):
 for col in range(6):s.rect(7.54+col*.49,2.36+row*.36,.34,.24,ORANGE)
s.text('188',7.49,4.41,4.91,.87,46,ORANGE,bold=True)
s.text('coalesced entries / request',7.53,5.52,4.91,.47,23)
s.text('Example: TP8 source, 94 layers, 4,000 contiguous tokens. Byte-range checks: 720 + 936 cases.',.95,6.27,11.62,.35,15)
s.end()

# 15 — operating-point headroom, rather than package instructions.
s=Slide('Latency headroom at N48',notes=NOTES[14])
s.text('Mean latency relative to the per-request limits',.92,1.48,11.48,.62,27)
for y,label,value,limit,unit in [(2.59,'TTFT',best['ttft_avg_ms'],3000,'ms'),(4.42,'ITL',best['itl_avg_ms'],20,'ms')]:
 s.text(label,.96,y,2.1,.52,26,bold=True)
 s.rect(3.01,y+.07,7.23,.48,PALE)
 s.rect(3.01,y+.07,7.23*value/limit,.48,ORANGE)
 s.text(f'{value:,.2f} {unit}',3.01,y+.77,4.27,.44,22)
 s.text(f'Limit: {limit:,} {unit}',10.47,y+.02,2.06,.89,19,GRAY)
s.text('Decode latency is closer to its limit; more load reduces headroom.',.98,6.13,11.56,.61,24,ORANGE)
s.end()

# 16 — two distinct evaluation gates, factual and uncrowded.
s=Slide('Latency and accuracy are separate acceptance checks',source='Full-set accuracy threshold: 99% of the organisers own FP8 reference score; no accuracy pass is claimed',notes=NOTES[15])
s.icon('timer',.93,1.47,.50);s.text('Latency',1.69,1.53,4.71,.61,30,bold=True)
s.text('97.44%',.98,2.74,5.0,1.18,62,ORANGE,bold=True)
s.text('Passing local measurement\nRequired: at least 90%',1.02,4.36,5.12,1.23,24)
s.line(6.45,1.51,6.45,6.10,PALE,1.4)
s.icon('shield-check',7.13,1.47,.50);s.text('Accuracy',7.89,1.53,4.47,.61,30,bold=True)
s.text('Next step',7.17,2.88,5.0,1.02,44,GRAY,bold=True)
s.text('Full-set output-quality checks\nTarget: ≥99% of reference\nFP8 weights remain unchanged',7.21,4.20,5.02,1.72,23)
s.end()

# 17 — concise closing, not another three-column dashboard.
s=Slide('Selected operating point',dark=True,notes=NOTES[16])
s.text('TP4 prefill  →  TP8 / EP8 decode',.84,1.47,11.71,.70,34,WHITE)
s.text('1,912.30',.88,2.68,10.7,1.40,76,WHITE,bold=True)
s.text('good output tokens / second',.98,4.32,11.1,.61,29,WHITE)
s.line(.95,5.35,12.4,5.35,ORANGE,1.6)
s.text('N48  ·  16 H200  ·  97.44% SLA  ·  request-scoped NIXL descriptors',.98,5.76,11.5,.77,24,'#D5DFE1')
s.end()

# 18 — actual final job, clearly marked appendix.
s=Slide('Appendix · alternative TP8 / EP2 prefill',notes=NOTES[17])
table=[('SHORT SWEEP','GOOD TOKENS/S','SLA','GATE'),('N16','933.50','98.15%','Pass'),('N32','1,393.62','93.02%','Pass'),('N40','1,624.14','89.50%','Fail'),('N48','1,708.25','86.06%','Fail')]
for i,row in enumerate(table):
 y=1.65+i*.73
 if i==0:s.rect(.89,y,11.56,.55,INK)
 else:s.line(.90,y+.53,12.44,y+.53,PALE)
 for xx,ww,val in zip([1.08,4.00,8.33,10.71],[2.5,3.96,2.0,1.41],row):
  s.text(val,xx,y+.10,ww,.38,14 if i==0 else 22,WHITE if i==0 else RED if i>=3 else INK,bold=i==0)
s.text('Long N32: 1,507.96 good tokens/s  ·  95.38% SLA',.97,5.81,11.53,.68,27,ORANGE)
s.end()

# 19 — discussion. Asset attribution is stored as non-presentational metadata.
credit=('Visual design adapted from Metropolis by Matthias Vogelgesang, CC BY-SA 4.0, '
 'https://github.com/matze/mtheme. The reusable theme adaptation retains CC BY-SA 4.0; '
 'presentation content and original TripleU charts/diagrams are separate from the theme license. '
 'Third-party assets retain their respective rights. Nineteen distinct atmospheric infrastructure '
 'photographs are used as backgrounds; no foreground product image is reused as a background. '
 'The foreground H200 product image is from https://www.nvidia.com/en-us/data-center/h200/. '
 'All are reference imagery, not photographs of the contest cluster. '
 'Icons: Lucide, ISC/MIT licenses, https://github.com/lucide-icons/lucide. '
 'Arial was selected for cross-platform PowerPoint compatibility. No AI-generated illustration is used. '
 + ' Background sources: ' + '; '.join(f"Slide {r['slide']}: {r['source']} (reference: {r['reference_page']}; credit: {r['credit']}; license: {r['license_url']})" for r in BACKGROUNDS))
s=Slide('Discussion',notes=NOTES[18])
s.text('Questions?',.94,1.85,11.41,1.42,67,bold=True)
for i,(icon,label) in enumerate([('cpu','Tensor and expert parallelism'),('network','Cross-node KV transfer'),('timer','Throughput under latency constraints')]):
 y=4.02+i*.72;s.icon(icon,1.02,y,.38);s.text(label,1.70,y+.025,10.50,.50,24)
s.end()

assert len(prs.slides)==19
for b in bounds:
    assert b['x']>=0 and b['y']>=0 and b['x']+b['w']<=W+.01 and b['y']+b['h']<=H+.01,b
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
from pptx.opc.constants import RELATIONSHIP_TYPE as RT, CONTENT_TYPE as CT
asset_xml=etree.Element('assetCredits');asset_xml.text=credit
credit_part=Part(PackURI('/customXml/assetCredits.xml'),CT.XML,prs.part.package,etree.tostring(asset_xml,xml_declaration=True,encoding='UTF-8'))
prs.part.relate_to(credit_part,RT.CUSTOM_XML)
prs.save(OUT/'TripleU_APAC2026_Presentation.pptx');pdf.save()
(OUT/'slide-content.json').write_text(json.dumps(outline,indent=2)+'\n')
(OUT/'layout-validation.json').write_text(json.dumps({'slides':19,'all_text_within_boxes':True,
    'all_boxes_within_slide':True,'profiling_points_rechecked':1211,'good_requests_rechecked':1180,
    'theme':'Metropolis-adapted','native_editable_diagrams':True,'english_only':True,
    'subtle_native_gradients':True,'tinted_image_backgrounds':list(range(1,20)),
    'distinct_background_images':19,'no_background_reused':True,
    'render_note':'PDF/previews are generated from the same explicit coordinates as PPTX, not an Office rendering.'},indent=2)+'\n')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf');thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5));p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(2000,math.ceil(len(thumbs)/4)*300),'#E2E7E8');draw=ImageDraw.Draw(sheet)
sheet_font=ImageFont.truetype('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf',12)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f"{i+1:02d} {outline[i]['title'][:65]}",fill=INK,font=sheet_font)
sheet.save(OUT/'Presentation_Overview.jpg',quality=93)
(OUT/'theme.json').write_text(json.dumps({'reference':'https://github.com/matze/mtheme','palette':{'ink':INK,'accent':ORANGE,'paper':PAPER},
 'fonts':{'native_pptx':'Arial / Courier New','pdf':'Helvetica / Courier'},'asset_provenance':str(EXTERNAL/'asset-provenance.json'),
 'adaptation_license':'CC BY-SA 4.0','asset_credit':credit,
 'gradient':{'header':[INK,'#375C6A'],'light_tint_alpha':[.91,.82],'dark_tint_alpha':[.92,.84]},
 'distinct_background_images':19,'no_background_reused':True,
 'background_manifest':BACKGROUND_MANIFEST,'background_image_on_every_slide':True},indent=2)+'\n')
print(json.dumps({'slides':19,'theme':'Metropolis-adapted','output':str(OUT),'request_gate_rechecked':'1180/1211'},indent=2))

"""Editable PowerPoint and matching PDF, generated from frozen measured data."""
import json
import math
import os
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw,ImageFont
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import fitz

ROOT=Path(os.environ.get('TRIPLEU_SUBMISSION_ROOT','/home/apacsc42/workspace/VNUHCM - TripleU'))
OUT=ROOT/'Presentation'
DATA=json.loads((OUT/'presentation-data.json').read_text())
ASSETS=OUT/'assets';ASSETS.mkdir(exist_ok=True)
W,H=13.333333,7.5
BG='#F3F6FA';INK='#15223B';MUTED='#53647C';GREEN='#008C78';ORANGE='#BE641F';BLUE='#3275C7';WHITE='#FFFFFF';LINE='#D9E1EA'
FONT='/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf'
BOLD='/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DejaVu',FONT));pdfmetrics.registerFont(TTFont('DejaVu-Bold',BOLD))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.edgecolor':LINE,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,
                     'text.color':INK,'figure.facecolor':WHITE,'axes.facecolor':WHITE})

def plot_save(fig,name):
    fig.savefig(ASSETS/(name+'.png'),dpi=180,bbox_inches='tight',facecolor=WHITE)
    fig.savefig(ASSETS/(name+'.svg'),bbox_inches='tight',facecolor=WHITE)
    plt.close(fig)
    return ASSETS/(name+'.png')

rows=DATA['results'];best=DATA['best'];baseline=DATA['baseline'];patch=DATA['patch']
declared=DATA.get('previous_best',DATA['declared_basic']);equal=DATA['equal_patch']
best_rate=f"{best['good_output_tokens_s']:,.2f}"
best_fraction=f"{best['good_request_fraction']:.2%}"
total_requests=int(best['requests']);good_requests=round(total_requests*best['good_request_fraction'])
snapshot_date=datetime.fromisoformat(DATA['snapshot_utc']).strftime('%d %B %Y')
best_sweep=sorted([m for m in rows if m['job']==best['job'] and m['phase']=='sweep'],key=lambda m:m['concurrency'])
assert len(best_sweep)==4 and best['job']=='22415'
fig,axs=plt.subplots(1,2,figsize=(11.6,3.4),gridspec_kw={'width_ratios':[1.2,1]})
ns=[m['concurrency'] for m in best_sweep];xx=np.arange(4)
axs[0].bar(xx-.18,[m['raw_output_tokens_s'] for m in best_sweep],.34,color='#CAD6E5',label='Raw output tokens/s')
axs[0].bar(xx+.18,[m['good_output_tokens_s'] for m in best_sweep],.34,color=GREEN,label='Good output tokens/s')
axs[0].set_xticks(xx,ns);axs[0].set_xlabel('Closed-loop concurrency N');axs[0].set_ylabel('Tokens/s');axs[0].legend(frameon=False,fontsize=9,loc='upper left')
axs[0].set_ylim(0,2300)
fractions=[100*m['good_request_fraction'] for m in best_sweep]
axs[1].plot(ns,fractions,'o-',color=GREEN,lw=2.5,markersize=8)
axs[1].axhline(90,color=ORANGE,ls='--',lw=1.5,label='90% gate')
for n,f in zip(ns,fractions):axs[1].annotate(f'{f:.1f}%',(n,f),xytext=(0,9),textcoords='offset points',ha='center',fontsize=11)
axs[1].set_xticks(ns);axs[1].set_ylim(65,107);axs[1].set_xlabel('Closed-loop concurrency N');axs[1].set_ylabel('Requests passing both SLAs (%)');axs[1].legend(frameon=False,fontsize=10,loc='lower left')
fig.tight_layout(w_pad=2.2);sweep_chart=plot_save(fig,'best-concurrency-sweep')

comp=[best,declared,equal,baseline]
fig,ax=plt.subplots(figsize=(10.3,3.4))
labels=['P8-TP4 + D8-TP8/EP8 / N48\nBest local, patched','09 / N40\nPrevious best, unpatched','TP8/EP2 + TP8/EP8 / N32\nFinal repaired layout','07 / N32\nMeasured baseline']
bars=ax.barh(np.arange(4),[m['good_output_tokens_s'] for m in comp],color=[GREEN,BLUE,ORANGE,'#8292AC'],height=.58)
ax.set_yticks(np.arange(4),labels,fontsize=11);ax.invert_yaxis();ax.set_xlim(0,2260);ax.set_xlabel('Good output tokens per second')
for b,m in zip(bars,comp):ax.text(b.get_width()+24,b.get_y()+b.get_height()/2,f"{m['good_output_tokens_s']:,.2f}",va='center',fontsize=12,fontweight='bold')
ax.grid(axis='x',alpha=.22);ax.set_axisbelow(True);fig.tight_layout();compare_chart=plot_save(fig,'long-run-comparison')

points=[]
jsonl=(ROOT/best['export']).with_name('profile_export.jsonl')
for line in jsonl.open():
    r=json.loads(line)
    if r['metadata'].get('benchmark_phase')!='profiling':continue
    m=r['metrics'];ttft=m.get('time_to_first_token',{}).get('value');itl=m.get('inter_token_latency',{}).get('value')
    if ttft is not None and itl is not None:points.append((ttft,itl))
points=np.array(points);passed=(points[:,0]<=3000)&(points[:,1]<=20)
assert int(passed.sum())==good_requests and len(points)==total_requests
fig,ax=plt.subplots(figsize=(7.2,4.1))
ax.scatter(points[passed,0],points[passed,1],s=12,alpha=.28,c=GREEN,label='Pass both limits')
ax.scatter(points[~passed,0],points[~passed,1],s=25,alpha=.75,c=ORANGE,label='Miss at least one limit')
ax.axvline(3000,c=ORANGE,ls='--');ax.axhline(20,c=ORANGE,ls='--')
ax.set_xlabel('Time to first token (ms)');ax.set_ylabel('Per-request mean ITL (ms)');ax.legend(frameon=False,fontsize=10,loc='upper left')
ax.set_xlim(0,max(3500,points[:,0].max()*1.06));ax.set_ylim(0,max(26,points[:,1].max()*1.08));fig.tight_layout();sla_chart=plot_save(fig,'best-request-sla')

prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H)
prs.core_properties.title='TripleU | APAC HPC-AI 2026 | Qwen PD inference'
prs.core_properties.author='VNUHCM - TripleU'
prs.core_properties.subject='Latest local winner, complete usable topology coverage, and replay status'
pdf=Canvas(str(OUT/'TripleU_APAC2026_Presentation.pdf'),pagesize=(W*72,H*72))
outline=[];bounds=[]

def rgb(c):return RGBColor.from_string(c.lstrip('#'))

class Slide:
    def __init__(self,title,tag='QWEN / AI TASK',source='',notes='',dark=False):
        self.s=prs.slides.add_slide(prs.slide_layouts[6]);self.n=len(prs.slides);self.dark=dark
        self.background=INK if dark else BG
        self.s.background.fill.solid();self.s.background.fill.fore_color.rgb=rgb(self.background)
        pdf.setFillColor(HexColor(self.background));pdf.rect(0,0,W*72,H*72,fill=1,stroke=0)
        self.rect(.62,.46,.40,.055,GREEN)
        self.text(tag,1.15,.36,11,.30,11,MUTED if not dark else '#A9BCCF',True)
        self.text(title,.65,.96,12,1.02,28,WHITE if dark else INK,True)
        self.rect(.65,6.92,12.05,.01,LINE if not dark else '#3A4B62')
        self.text('VNUHCM - TripleU  |  APAC HPC-AI 2026',.65,7.04,7,.24,9,MUTED if not dark else '#A9BCCF')
        self.text(f'{self.n:02d}',12.20,7.00,.5,.3,11,GREEN,True)
        if source:self.text(source,.65,6.50,12,.30,9,MUTED if not dark else '#A9BCCF')
        self.title=title;self.notes=notes
        self.lines=[]
    def rect(self,x,y,w,h,color,radius=False):
        shape=self.s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        shape.fill.solid();shape.fill.fore_color.rgb=rgb(color);shape.line.fill.background()
        if radius:
            shape.adjustments[0]=.08
        pdf.setFillColor(HexColor(color));pdf.rect(x*72,(H-y-h)*72,w*72,h*72,fill=1,stroke=0)
        return shape
    def text(self,text,x,y,w,h,size=18,color=INK,bold=False):
        # Wrap explicitly with the same font used in the PDF, keeping line breaks
        # fixed in PowerPoint so edits remain readable on different systems.
        fam='DejaVu-Bold' if bold else 'DejaVu'
        wrapped=[]
        for block in str(text).split('\n'):
            if not block:wrapped.append('');continue
            current=''
            for word in block.split():
                candidate=(current+' '+word).strip()
                if pdfmetrics.stringWidth(candidate,fam,size)>w*72 and current:
                    wrapped.append(current);current=word
                else:current=candidate
            wrapped.append(current)
        line_height=size*1.24
        if len(wrapped)*line_height>h*72+.6:
            raise RuntimeError(f'Slide {self.n} text overflow: {text[:80]!r}; {len(wrapped)*line_height:.1f} > {h*72:.1f}')
        box=self.s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
        tf=box.text_frame;tf.clear();tf.word_wrap=False;tf.vertical_anchor=MSO_ANCHOR.TOP
        tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        for i,line in enumerate(wrapped):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
            p.font.name='DejaVu Sans';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
            p.space_before=Pt(0);p.space_after=Pt(0);p.line_spacing=Pt(line_height)
            pdf.setFont(fam,size);pdf.setFillColor(HexColor(color));pdf.drawString(x*72,(H-y)*72-size*.94-i*line_height,line)
        if hasattr(self,'lines'):self.lines.append(str(text))
        bounds.append({'slide':self.n,'x':x,'y':y,'w':w,'h':h,'text':str(text)})
        return box
    def image(self,path,x,y,w,h):
        img=Image.open(path);iw,ih=img.size
        scale=min(w/iw,h/ih);pw,ph=iw*scale,ih*scale
        px=x+(w-pw)/2;py=y+(h-ph)/2
        self.s.shapes.add_picture(str(path),Inches(px),Inches(py),width=Inches(pw),height=Inches(ph))
        pdf.drawImage(str(path),px*72,(H-py-ph)*72,width=pw*72,height=ph*72)
    def card(self,x,y,w,h,label,value,detail,color=GREEN):
        self.rect(x,y,w,h,WHITE,True);self.rect(x+.22,y+.22,.07,.4,color)
        self.text(label,x+.4,y+.22,w-.65,.6,13,MUTED,True)
        self.text(value,x+.25,y+1.02,w-.5,.72,31,color,True)
        self.text(detail,x+.25,y+1.94,w-.5,h-2.10,15,MUTED)
    def end(self):
        self.s.notes_slide.notes_text_frame.text=self.notes
        outline.append({'number':self.n,'title':self.title,'text':self.lines,'speaker_notes_en':self.notes})
        pdf.showPage()

s=Slide('Serving the full model. Meeting the latency gate.',tag='TRIPLEU / APAC HPC-AI 2026',dark=True,
 source='Local measurements; organiser re-run and accuracy validation pending.',
 notes='Our declared Qwen Basic result serves the official FP8 checkpoint on 16 H200 GPUs with plain prefill/decode disaggregation. The winning measured configuration is P8-TP4_D8-TP8-EP8 at N48, with our request-scoped NIXL descriptor patch. It achieves 1912.30 good output tokens/s and 97.44% SLA. These are local measurements, not an official organiser score.')
s.text('Qwen3-235B-A22B\nPD disaggregated inference',.70,2.17,7.7,1.5,32,WHITE,True)
s.text('VNUHCM - TripleU',.72,4.09,7,.55,24,'#87E0CB',True)
s.text(f'Evidence snapshot  |  {snapshot_date}',.72,4.95,7,.4,16,'#B6C5D5')
s.rect(9.18,2.15,3.45,3.8,'#24344E',True)
s.text('BEST INTERNAL RESULT',9.45,2.57,2.92,.6,12,'#B6C5D5',True)
s.text(best_rate,9.45,3.42,2.94,.76,30,'#87E0CB',True)
s.text(f'good output tokens/s\n{best_fraction} SLA fraction\nN48 / 16 H200',9.45,4.45,2.94,1.06,17,WHITE)
s.end()

s=Slide('Best measured stack, with explicit limits',source='Evidence: job 22415 / confirm / N48; canonical AIPerf export.',
 notes='Job 22415 used the long 60/120/30 protocol. Of 1211 profiling requests, 1180 met both latency limits; there were no request errors or cancellations. The primary packaged Slurm job now deploys this exact layout and patch, then runs the official client once at N48. Full-set accuracy and official organiser re-verification are pending.')
s.card(.65,2.26,3.85,3.85,'GOOD OUTPUT RATE',best_rate,f"req/s goodput × 200\n{best['good_output_tokens_s']/200:.5f} good req/s")
s.card(4.72,2.26,3.85,3.85,'REQUESTS WITHIN BOTH SLAs',best_fraction,f'{good_requests:,} / {total_requests:,} requests\n0 errors; 0 cancellations')
s.card(8.79,2.26,3.85,3.85,'VALIDATION STATUS','Pending','Full-set accuracy\nOrganiser official re-run',ORANGE)
s.end()

s=Slide('Throughput counts only when latency passes',source='Task Rules + 2026-09-25 addendum, included under AI_Task/logs/rules/.',
 notes='TTFT measures the wait for the first token. The per-request average ITL measures the time between output tokens. A good request must meet both TTFT at most 3000 ms and mean ITL at most 20 ms. At least 90% must pass; errors remain in the denominator. The synthetic Shakespeare performance workload is distinct from full-set model accuracy checks.')
s.card(.65,2.17,3.85,3.55,'WORKLOAD','4,000 → 200','Synthetic Shakespeare inputs\nOfficial FP8 checkpoint')
s.card(4.72,2.17,3.85,3.55,'PER-REQUEST SLA','3,000 / 20','TTFT ≤ 3,000 ms\nMean ITL ≤ 20 ms')
s.card(8.79,2.17,3.85,3.55,'POINT ACCEPTANCE','≥ 90%','Requests must pass both\nErrors stay in denominator')
s.text('Closed-loop load: a completed request is immediately replaced, sustaining N concurrent requests.',.8,5.98,11.8,.6,17,MUTED)
s.end()

s=Slide('One platform, one unchanged checkpoint',source='Image metadata, SHA256 and model metadata: AI_Task/job_scripts/environment.json.',
 notes='The platform is two eight-GPU H200 nodes connected by InfiniBand. We reuse the exact organiser SGLang and AIPerf images. SGLang is version 0.5.17, the router 0.3.2, NIXL 1.3.2 and AIPerf 0.12.0. The published FP8 weights are unchanged; worker logs confirm BF16 KV. The included module is a read-only serving-source overlay, not a rebuilt or requantised model.')
items=[('COMPUTE','2 × HGX H200 nodes / 16 GPUs total'),('NETWORK','InfiniBand NDR between the two nodes'),('MODEL','Qwen3-235B-A22B-Instruct-2507-FP8'),('SERVING','SGLang 0.5.17 / router 0.3.2 / NIXL 1.3.2'),('CLIENT','AIPerf 0.12.0; pinned official tokenizer'),('PRECISION','Published FP8 weights / BF16 KV (auto, verified in logs)')]
for i,(label,value) in enumerate(items):
 y=2.14+i*.64;s.rect(.65,y,12,.56,WHITE);s.text(label,.87,y+.13,2.1,.28,11,GREEN,True);s.text(value,3.12,y+.10,9.0,.38,17)
s.end()

s=Slide('Best layout: 2 prefill + 1 decode worker',source='P8-TP4_D8-TP8-EP8 / N48; hetero-tp-request-descriptors-v1; job 22415.',
 notes='Node 0 has two prefill workers, each TP4/EP1 using four GPUs. Node 1 has one decode worker, TP8/EP8 using eight GPUs. NIXL transfers KV across the two possible P/D pairs. All scored requests target the OpenAI-compatible gateway, rather than worker endpoints. No tensor-parallel group spans both nodes.')
s.rect(.7,2.3,5.05,3.25,WHITE,True);s.rect(7.55,2.3,5.05,3.25,WHITE,True)
s.text('NODE 0  /  8 H200',.98,2.55,4.4,.38,17,GREEN,True);s.text('NODE 1  /  8 H200',7.83,2.55,4.4,.38,17,BLUE,True)
for k in range(2):
 yy=3.27+k*.85;s.rect(1.02,yy,4.34,.68,'#E9F0F7',True);s.text(f'Prefill worker {k}  ·  4 GPUs  ·  TP4 / EP1',1.17,yy+.18,4.06,.30,13,GREEN,True)
s.rect(7.87,3.27,4.34,1.53,'#E9F0F7',True)
s.text('Decode worker 0\n8 GPUs  ·  TP8 / EP8',8.08,3.57,3.92,.85,18,BLUE,True)
s.text('KV cache\nNIXL →',5.96,3.65,1.36,.87,17,GREEN,True)
s.text('AIPerf N48 → OpenAI-compatible gateway :8000 → Prefill → Decode → streamed tokens',.92,5.89,11.6,.6,17,MUTED)
s.end()

s=Slide('Starting layouts establish our measured reference',source='07 and 09 are organiser-provided starting layouts; the team extends the search and transport.',
 notes='Layouts 07 and 09 are organiser-provided starting examples, not libraries or models created by our team. Layout 07 uses four TP2 prefill workers; 09 uses two TP4 prefill workers. Both use two TP4/EP4 decode workers. The previous best was 09/N40. We extend the topology search, select load and patch KV descriptor preparation. The improvement does not isolate one variable.')
s.rect(.65,2.16,5.83,3.68,WHITE,True);s.rect(6.73,2.16,5.83,3.68,WHITE,True)
s.text('Reference layout 07',.95,2.47,5.18,.50,23,BLUE,True)
s.text('Prefill: 4 workers × TP2\nDecode: 2 workers × TP4 / EP4\nNode split: 8 + 8 GPUs\nLong run: N32',.95,3.28,5.10,1.92,20)
s.text('Previous best layout 09',7.03,2.47,5.18,.50,23,GREEN,True)
s.text('Prefill: 2 workers × TP4\nDecode: 2 workers × TP4 / EP4\nNode split: 8 + 8 GPUs\nLong run: N40',7.03,3.28,5.10,1.92,20)
s.text('Trade-off: fewer prefill replicas, wider tensor parallelism; measure the balance under the SLA.',.8,6.02,11.9,.45,16,MUTED)
s.end()

s=Slide('A 17-layout search, with measured coverage',source='AI_Task/logs/COVERAGE.md; pending and failed runs are not counted as completed measurements.',
 notes='The finite search contains 17 topology arrangements across 8+8, 4+12 and 12+4 GPU splits, with compatible TP2/4/8 values. Fourteen exact originals and three explicit EP2 replacements have all four measured sweep points. Three TP8/EP1 originals remain FP8-block-incompatible. Replacements are named separately; failed deployments never count as measurements.')
table=[('GPU SPLIT P + D','PREFILL TP','DECODE TP','LAYOUTS'),('8 + 8','2 / 4 / 8','2 / 4 / 8','9'),('4 + 12','2 / 4','2 / 4','4'),('12 + 4','2 / 4','2 / 4','4')]
for i,row in enumerate(table):
 y=2.17+i*.63;s.rect(.65,y,12,.57,INK if i==0 else WHITE)
 for x,w,text in zip([.85,4.8,7.4,10.4],[3.7,2.3,2.7,1.6],row):s.text(text,x,y+.15,w,.26,11 if i==0 else 15,WHITE if i==0 else INK,i==0)
s.text(f"{DATA['measured_originals']}/17 originals measured",.85,5.18,6.2,.7,28,GREEN,True)
s.text(f"+ {DATA['measured_variants']} measured EP2 variants",7.3,5.22,5.1,.65,20,BLUE,True)
s.text('Each completed topology has N16, N32, N40 and N48 actual measurement exports.',.85,6.07,11.7,.4,15,MUTED)
s.end()

s=Slide('Screen quickly; confirm at the full duration',
 source='Exploratory 10/20/30 vs long 60/120/30; original canonical exports retained.',
 notes='Exploratory runs use 10-second warmup, 20-second measurement and 30-second grace. They screen configurations and are not official scoring runs. Long confirmation uses 60/120/30. The declared entry performs only the official N48 point, without a sweep. Separate setup prompts initialize every P/D path without using the official dataset or seed and without changing official warmup.')
for x,label,detail,color in [(.7,'Deploy + initialize','All P/D paths\nSeparate setup prompts',BLUE),(4.8,'Explore','N16 / 32 / 40 / 48\n10s + 20s + 30s',MUTED),(8.9,'Long confirmation','Best N48 / latest N32\n60s + 120s + 30s',GREEN)]:
 s.rect(x,2.4,3.7,2.0,WHITE,True);s.text(label,x+.25,2.74,3.18,.61,19,color,True);s.text(detail,x+.25,3.48,3.15,.7,16)
s.text('Official timing',.85,4.90,3,.4,18,INK,True)
for x,w,label,c in [(3.3,2.35,'60s warmup',BLUE),(5.65,4.70,'120s measurement',GREEN),(10.35,1.55,'30s grace',ORANGE)]:
 s.rect(x,4.80,w,.75,c);s.text(label,x+.1,5.03,w-.18,.27,11,WHITE,True)
s.text('A short sweep and a long confirmation use different windows; their difference is not an optimisation gain.',.85,6.03,11.8,.6,16,MUTED)
s.end()

s=Slide('Winner sweeps select N48; the long run confirms it',
 source='Job 22415 exploratory sweep: 10s warmup / 20s measurement / 30s grace.',
 notes='All four winning-layout sweeps passed the 90% gate. Short N48 produced 1788.65 good tokens/s with 90.95% SLA. The long N48 confirmation produced 1912.30 with 97.44%. These windows have different durations and populations; their difference is not an optimisation speedup. We select the long confirmation as the declared performance evidence.')
s.rect(.65,2.12,12,3.95,WHITE,True);s.image(sweep_chart,.89,2.24,11.48,3.66)
s.text('N48 sweep: 1,788.65 good tokens/s; 90.95% SLA. Long N48: 1,912.30; 97.44% SLA.',.85,6.08,11.8,.4,15,GREEN,True)
s.end()

s=Slide(f"Best long run: +{DATA['gain_over_declared_pct']:.2f}% over the previous best",
 source='Jobs 22415, 22219, 22809 and 22197: long 60/120/30 runs on 16 H200.',
 notes='The winning long run is 14.78% above the previous long result of 1666.01. All bars show passing long measurements on the same 16-H200 platform. Topology, concurrency and transport differ, so this is an observed end-to-end gain, not an isolated NIXL patch speedup. Repeated matched A/B testing remains useful. The baseline is our local run, not the organisers reference score.')
s.rect(.65,2.15,12,3.8,WHITE,True);s.image(compare_chart,.87,2.32,11.48,3.44)
s.text('Observed gain includes topology, concurrency and transport changes. Repeated matched A/B is still needed.',.85,6.12,11.7,.42,14,MUTED)
s.end()

s=Slide('Check the gate per request, not from averages',
 source='Job 22415 / confirm N48: 1,211 profiling-phase records in the original JSONL.',
 notes='The original JSONL contains 1211 profiling records. Recomputing both per-request limits gives 1180 good requests, exactly matching the 97.44% aggregate fraction. Thirty-one miss a limit; none error or cancel. Aggregate means alone cannot determine whether 90% pass. The displayed TTFT and ITL statistics are performance metrics, not accuracy scores.')
s.rect(.65,2.13,7.73,4.11,WHITE,True);s.image(sla_chart,.9,2.22,7.2,3.87)
s.text(f'{good_requests:,} / {total_requests:,}',8.75,2.51,3.9,.61,25,GREEN,True)
s.text('requests pass both limits',8.78,3.15,3.7,.53,17)
s.text(f"Mean TTFT: {best['ttft_avg_ms']:,.2f} ms\nMean ITL: {best['itl_avg_ms']:.2f} ms\nP95 TTFT: {best['ttft_p95_ms']:,.2f} ms\nP95 ITL: {best['itl_p95_ms']:.2f} ms",8.78,4.02,3.7,1.63,16,MUTED)
s.end()

s=Slide('Failures remain evidence; actual exports count',
 source='Immutable payloads and failed logs remain included; recovery registry distinguishes EP2 variants.',
 notes='Failures expose three practical issues: FP8 expert shard dimensions, slow cold KV path setup, and distributed port collisions. Job 22778 failed before measurement and is not counted as finished. The repaired equal-TP job 22809 has four sweep exports and a long N32 confirmation. A successful repaired run does not prove that a single suspected cause explained every earlier timeout.')
items=[('FP8 sharding','TP8 / EP1 gives a 192-wide expert shard; FP8 block size is 128.','Use a distinct EP2 variant; keep the EP1 original incompatible.'),
       ('Cold P/D transfer','22778 timed out before measurement; patched 22809 completes.','Request-scoped descriptors; setup deadlines do not relax benchmark SLAs.'),
       ('Distributed ports','A deployment hit EADDRINUSE before producing metrics.','Assign explicit distinct ports; preserve the failed logs and source.')]
for i,(label,cause,fix) in enumerate(items):
 y=2.13+i*1.35;s.rect(.65,y,12,1.19,WHITE,True);s.text(label,.92,y+.22,2.15,.55,16,ORANGE,True);s.text(cause,3.34,y+.16,8.96,.53,16);s.text(fix,3.34,y+.72,8.96,.32,12,MUTED)
s.end()

s=Slide('EP2 makes TP8 compatible with FP8 blocks',
 source='Checkpoint: MoE intermediate size 1536, 128 experts; image loader requires block_n = 128.',
 notes='TP partitions matrices inside each expert; EP distributes expert groups. With TP8/EP1, the 1536-wide dimension produces a 192-wide shard, incompatible with 128-wide FP8 blocks. EP2 gives effective TP4 and 384-wide shards, exactly three blocks, while retaining all 128 experts and weights. These are explicit variants. The winning layout uses prefill TP4/EP1 and decode TP8/EP8.')
s.rect(.65,2.22,5.81,3.3,WHITE,True);s.rect(6.77,2.22,5.81,3.3,WHITE,True)
s.text('TP8 / EP1',.96,2.54,5.2,.57,26,ORANGE,True);s.text('128 experts / 1 expert group\n1536 ÷ 8 = 192\n192 is not divisible by 128',.96,3.43,5.1,1.6,20)
s.text('TP8 / EP2',7.08,2.54,5.2,.57,26,GREEN,True);s.text('64 experts / group × 2 groups\n1536 ÷ 4 = 384\n384 = 3 × 128',7.08,3.43,5.1,1.6,20)
s.text('All 3 EP2 replacements are measured. All experts and weights are retained; the originals stay labelled.',.85,5.93,11.7,.65,17,MUTED)
s.end()

s=Slide('NIXL: two request-scoped transport patches',
 source='Heterogeneous TP: jobs 22294 / 22415. Equal TP8: job 22809. Original source and diffs included.',
 notes='We patch SGLang integration with NIXL, not the underlying NIXL library. The heterogeneous-TP patch passed 720 CPU byte-range comparisons and is used by winning job 22415. The separate restricted equal-TP8 patch passed 936 range cases and five fallback guards; job 22809 confirms GPU operation. For contiguous TP8-to-TP4 or TP8-to-TP8 copies, 4000 tokens need 188 descriptors. This count is not universal for TP4-to-TP8 geometry. Geometry checks do not replace model accuracy.')
s.rect(.65,2.15,7.15,3.99,WHITE,True)
s.text('Full-pool descriptor plan',.98,2.46,6.5,.45,19,ORANGE,True)
s.text('≈ 403.8 million source entries / rank',.98,3.11,6.5,.55,21,ORANGE,True)
s.text('Request-scoped plan',.98,4.08,6.5,.45,19,GREEN,True)
s.text('188 entries: contiguous TP8→TP4 or TP8→TP8',.98,4.73,6.5,.61,17,GREEN,True)
s.text('Byte ranges, head mapping and notifications retained.',.98,5.49,6.5,.40,13,MUTED)
s.text('720 + 936',8.28,2.42,3.8,.63,30,GREEN,True)
s.text('CPU range cases\nBoth patches GPU-tested',8.3,3.08,3.85,.83,17)
s.text('1,507.96',8.28,4.14,3.8,.62,28,BLUE,True)
s.text('latest equal-TP / N32\n95.38% SLA; no errors',8.3,4.82,3.85,.91,16)
s.end()

s=Slide('The primary job deploys the winning stack',
 source='AI_Task/job_scripts/submit.sbatch; README.md; nixl.patch; measured job 22415.',
 notes='The primary submit.sbatch now selects the measured winning TP4-to-TP8/EP8 layout, concurrency 48 and the exact NIXL module hash. It allocates 16 GPUs, deploys three workers and the gateway, initializes two P/D pairs, then invokes the unchanged official AIPerf command in the same job. Image/model metadata, the patch as text, pinned tokenizer cache and package-relative replay instructions support reconstruction under a dedicated account.')
items=[('01','Winning layout','2 prefill TP4 / EP1 + 1 decode TP8 / EP8; N48; all 16 H200.'),
       ('02','Enabled patch','Read-only NIXL module mount; source hash checked by every worker.'),
       ('03','One Slurm job','Deploy, initialize both P/D paths, run the locked official command once.'),
       ('04','Reconstruction','Exact organiser images; published model; portable paths; offline cache.')]
for i,(n,label,detail) in enumerate(items):
 y=2.11+i*1.0;s.rect(.65,y,12,.87,WHITE,True);s.text(n,.92,y+.22,.7,.40,20,GREEN,True);s.text(label,1.90,y+.25,2.4,.40,17,INK,True);s.text(detail,4.42,y+.22,7.83,.51,15,MUTED)
s.end()

s=Slide('Correctness claims follow the available evidence',
 source='Qwen addendum Q1/Q2; accuracy pass line: at least 99% of organiser reference score.',
 notes='The model checkpoint and precision remain unchanged; all requests use plain PD without speculative decoding or skipped computation. The descriptor patch is intended to preserve byte geometry, but local latency and CPU geometry checks do not establish the full-set accuracy gate. The organisers accuracy threshold is 99% of their own FP8 reference score. No accuracy pass, official score or verified Bonus claim is made.')
items=[('Published FP8 weights and BF16 KV, unchanged','Worker logs / source',GREEN),
       ('Plain PD on 16 GPUs; no speculative decoding','Configured / local logs',GREEN),
       ('Best long run / N48 latency gate','97.44% pass fraction',GREEN),
       ('Full-set accuracy ≥ 99% of reference','Not yet tested',ORANGE),
       ('Organiser reconstruction + official scored re-run','Pending',ORANGE)]
for i,(claim,status,c) in enumerate(items):
 y=2.17+i*.71;s.rect(.65,y,12,.63,WHITE);s.text(claim,.93,y+.17,8.0,.36,16);s.text(status,9.13,y+.18,3.18,.35,13,c,True)
s.text('Local latency evidence is available. Official acceptance and any Bonus validation remain pending.',.85,5.98,11.7,.50,15,MUTED)
s.end()

s=Slide('Topology coverage complete; submission work remains',
 source=f"Snapshot: {DATA['snapshot_utc']}. Job 22809 completed 11 October, 23:18 UTC.",
 notes='Fourteen original layouts plus three explicit EP2 replacements are measured at all four concurrency points. Measuring a layout does not imply that it passes the SLA. The Qwen package contains the winning entry, source patch, English presentation and raw evidence. The full-set accuracy check, packaged orchestration GPU replay and official re-run remain separate validation steps. HPC results were not supplied for this Qwen-scoped workspace.')
s.rect(.65,2.15,5.83,3.90,WHITE,True);s.rect(6.73,2.15,5.83,3.90,WHITE,True)
s.text('Measured coverage',.97,2.48,5.2,.59,23,GREEN,True)
s.text('14 original + 3 EP2 layouts\nAll four concurrency sweeps\nWinning long-run evidence\nBoth NIXL patches and logs',.97,3.42,5.15,1.9,18)
s.text('Still outstanding',7.05,2.48,5.2,.59,23,ORANGE,True)
s.text('Full-set accuracy check\nPackaged job GPU replay\nHPC/OpenFOAM evidence\nOfficial upload and re-run',7.05,3.42,5.15,1.9,18)
s.end()

s=Slide('Current winner: TP4 prefill + TP8 / EP8 decode',tag='TRIPLEU / DISCUSSION',dark=True,
 source='Job 22415 / N48; hetero-tp-request-descriptors-v1; long 60/120/30 measurement.',
 notes='The declared current winner is 1912.30 good output tokens/s with 97.44% SLA at N48 on 16 H200 GPUs. The organisers supply the checkpoint, images, cluster and locked benchmark. Our contribution is topology/load selection and request-scoped descriptor preparation. All usable search layouts are measured. Official acceptance still depends on organiser reconstruction and accuracy checks.')
s.text(best_rate,.78,2.25,8.6,1.18,58,'#87E0CB',True)
s.text('good output tokens per second',.82,3.58,10,.61,25,WHITE)
s.text(f'{best_fraction} request SLA fraction  ·  N48 / 16 H200  ·  Official FP8 model',.82,4.67,11.5,.74,20,'#B6C5D5')
s.text('Accuracy and organiser re-verification remain pending.',.82,5.80,11.5,.52,18,'#B6C5D5')
s.end()

s=Slide('Appendix: the final repaired layout and selection',tag='APPENDIX / Q&A',
 source='Job 22809 / equal-tp8-request-descriptors-v1; sweeps 10/20/30 and confirm 60/120/30.',
 notes='Job 22809 completed the final repaired P8-TP8-EP2_D8-TP8-EP8 layout with four short sweeps and a long N32 confirmation. N40 and N48 reached only 89.50% and 86.06% SLA, below the 90% gate. N32 passed with 1507.96 good tokens/s and 95.38% SLA, but did not beat job 22415. Unpatched job 22750 points remain distinct and are not combined into the patched sweep.')
facts=[('Final layout','P8-TP8-EP2_D8-TP8-EP8; job 22809 completed.'),
       ('N32 long run','1,507.96 good tokens/s; 95.38% SLA; no errors/cancels.'),
       ('N40 / N48 short sweeps','89.50% / 86.06% SLA: both miss the 90% gate.'),
       ('Selection','Job 22415 remains the best passing long measurement.'),
       ('Interpretation','Measured coverage does not mean every layout passes SLA.')]
for i,(label,detail) in enumerate(facts):
 y=2.12+i*.8;s.text(label,.83,y,3.55,.62,15,GREEN,True);s.text(detail,4.62,y,7.7,.62,16)
s.end()

for b in bounds:
    assert b['x']>=0 and b['y']>=0 and b['x']+b['w']<=W+.01 and b['y']+b['h']<=H+.01,b
prs.save(OUT/'TripleU_APAC2026_Presentation.pptx');pdf.save()
(OUT/'slide-content.json').write_text(json.dumps(outline,indent=2,ensure_ascii=False)+'\n')
md=['# TripleU APAC2026 — slide guide','',f"Data snapshot: {DATA['snapshot_utc']}",'',
    'English slides and speaker notes. Suggested duration: 15–20 minutes for the main 18 slides. Appendix is for Q&A.','']
for slide in outline:
    md.extend([f"## {slide['number']:02d}. {slide['title']}",''])
    md.extend('- '+line.replace('\n',' / ') for line in slide['text'])
    md.extend(['','**Speaker notes:** '+slide['speaker_notes_en'],''])
(OUT/'TripleU_APAC2026_Presentation.md').write_text('\n'.join(md),encoding='utf-8')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf')
thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25))
    p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(4*500,math.ceil(len(thumbs)/4)*310),'#DDE5EF');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*310+10;sheet.paste(im,(x,y));draw.text((x,y+275),f"{i+1:02d} · {outline[i]['title'][:58]}",font=ImageFont.truetype(FONT,12),fill=INK)
sheet.save(OUT/'Presentation_Overview.jpg',quality=90)
(OUT/'layout-validation.json').write_text(json.dumps({'slides':len(outline),'all_text_within_boxes':True,
  'all_boxes_within_slide':True,'pdf_pages':len(doc),'profiling_points_rechecked':total_requests,'good_requests_rechecked':good_requests,'evidence_job':best['job'],
  'render_note':'PDF and PNG previews use the same explicit layout/font model as the native editable PPTX, not a LibreOffice rendering.'},indent=2)+'\n')
print(json.dumps({'slides':len(prs.slides),'pptx':str(OUT/'TripleU_APAC2026_Presentation.pptx'),
                 'pdf':str(OUT/'TripleU_APAC2026_Presentation.pdf'),'observed_gain_pct':DATA['relative_gain_pct']},indent=2))

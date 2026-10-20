"""Build the complete English research talk using the established Metropolis style."""
import json
import math
import hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.oxml.xmlchemy import OxmlElement
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from lxml import etree
import fitz

WORK = Path('/home/apacsc42/workspace')
ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = WORK/'submission-review/research-update-2026-10-20'
ASSETS = OUT/'assets'
ASSETS.mkdir(exist_ok=True)
EXTERNAL = WORK/'submission-tools/design-assets'
DATA = json.loads((OUT/'presentation-data.json').read_text())
BACKGROUNDS = json.loads((OUT/'background-manifest.json').read_text())['slides']
W, H = 13.333333, 7.5
PAPER, INK, ORANGE, GRAY, PALE, RED, WHITE = '#FAFAFA', '#23373B', '#EB811B', '#737F82', '#E5E9E9', '#A94442', '#FFFFFF'
FONT, BOLD, MONO = 'Helvetica', 'Helvetica-Bold', 'Courier'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'figure.facecolor':PAPER,'axes.facecolor':'none','text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#BAC3C5'})
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
prs.core_properties.title = 'TripleU — Qwen serving: from topology to phase-specific kernels'
prs.core_properties.author = 'VNUHCM - TripleU'
prs.core_properties.subject = 'Research update through 20 October 2026; H200 and H100 measured separately'
theme = next(p for p in prs.part.package.iter_parts() if str(p.partname)=='/ppt/theme/theme1.xml')
t = etree.fromstring(theme.blob)
ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
t.set('name','TripleU / Metropolis')
for name,color in [('dk1',INK),('lt1',PAPER),('dk2','#375C6A'),('lt2',WHITE),('accent1',ORANGE),('accent2',GRAY),('accent3',RED)]:
    e=t.find('.//a:clrScheme/a:'+name,ns)
    for child in list(e):e.remove(child)
    etree.SubElement(e,'{'+ns['a']+'}srgbClr').set('val',color[1:])
for e in t.findall('.//a:fontScheme//a:latin',ns):e.set('typeface','Arial')
theme._blob=etree.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True)
pdf = Canvas(str(OUT/'TripleU_APAC2026_Presentation.pdf'),pagesize=(W*72,H*72))
outline, bounds = [], []
def rgb(c):return RGBColor.from_string(c[1:])
exec((OUT/'drawing-helpers.py').read_text(),globals())


def point(job,n=None,platform='h200'):
    points=DATA[platform][job]
    return next(p for p in points if p['phase']=='confirm' and (n is None or p['concurrency']==n))


def slide(title,notes,source='',**kwargs):
    # Sources remain in speaker notes and the research manifest, not folder-tour text.
    return Slide(title,notes=notes+('\n\nResearch sources: '+source if source else ''),**kwargs)


def table(s,headers,rows,widths=None,y=1.55,row_h=.63,size=18):
    widths=widths or [11.6/len(headers)]*len(headers)
    x0=.86
    s.rect(x0,y,11.6,.54,INK)
    for i,row in enumerate([headers]+rows):
        yy=y+(0 if i==0 else .63+(i-1)*row_h)
        x=x0
        if i:s.line(x0,yy+row_h-.08,12.46,yy+row_h-.08,PALE,.8)
        for val,w in zip(row,widths):
            s.text(str(val),x+.12,yy+.10,w-.24,.40,13 if i==0 else size,WHITE if i==0 else INK,bold=i==0)
            x+=w


def bullets(s,items,x=.96,y=1.55,w=11.3,size=25,gap=1.1):
    for i,(heading,body) in enumerate(items):
        yy=y+i*gap
        s.rect(x,yy+.09,.075,.38,ORANGE)
        s.text(heading,x+.25,yy,w-.25,.50,size,bold=True)
        s.text(body,x+.25,yy+.58,w-.25,.76,19,GRAY)


def chart(name,draw,figsize=(12,4.4)):
    fig,ax=plt.subplots(figsize=figsize)
    draw(fig,ax)
    fig.tight_layout()
    p=ASSETS/(name+'.png')
    fig.savefig(p,dpi=180,bbox_inches='tight',transparent=True)
    fig.savefig(ASSETS/(name+'.svg'),bbox_inches='tight',transparent=True)
    plt.close(fig)
    return p


# 01
s=slide('Qwen serving', 'We present the research journey through 20 October: topology, transport repair, phase-specific kernels, controlled replication and resource observability. The workload is 4000 input and 200 output tokens. H200 and H100 results are separate systems. The new N62 H200 observation is not independently repeated; the N60 interaction is reproduced. Official full-set quality is still unverified.',cover=True)
s.text('APAC HPC-AI 2026  /  QWEN TASK',.8,.8,11,.4,15,ORANGE,bold=True)
s.text('Qwen serving:\nfrom topology to\nmeasured kernel interactions',.8,1.65,11.4,2.7,41,bold=True)
s.line(.83,4.85,11.9,4.85,ORANGE,1.6)
s.text('VNUHCM - TripleU',.84,5.19,11,.5,26)
s.text('Research update · 20 October 2026',.86,5.96,11,.4,18,GRAY);s.end()
# 02
s=slide('Two measured frontiers', 'Highest H200 individual observation: 24915, N62, 3022.034919 good output tokens/s, 98.7261% joint SLA. It passes complete local protocol/runtime/output checks but still needs an independent N62 repeat. N60 independently repeats at 2990.150791 and 2989.174711. Highest H100 individual is 221590, N54, 2430.890867. These peaks use different hardware, runner and load settings, and must not be plotted as a matched algorithmic comparison. Full organiser quality remains unverified.', '24915 full review; 24738/24913; full-protocol historical scan; H100 221590')
for x,label,rate,detail in [(.9,'16 H200','3,022.03','N62 · 98.726% joint SLA'),(7.15,'16 H100','2,430.89','N54 · highest individual run')]:
 s.text(label,x,1.52,5.2,.48,24,ORANGE,bold=True);s.text(rate,x,2.33,5.25,1.12,53,bold=True);s.text('good output tokens/s',x,3.68,5.1,.52,24);s.text(detail,x,4.60,5.22,.63,20)
s.line(6.53,1.48,6.53,5.65,PALE)
s.text('N60 H200 gain reproduced · N62 repeat and official quality remain open',.96,6.13,11.4,.58,20,GRAY);s.end()
# 03
s=slide('Optimise useful throughput under a latency gate', 'Each request must satisfy both time to first token at most 3,000 ms and mean inter-token latency at most 20 ms. At least 90% of evaluated requests must meet both. Errors remain in the denominator. Goodput is qualifying requests per second; multiplying by 200 gives the good output tokens per second reported here. Mean latencies alone do not establish the per-request gate.', 'Qwen task rules and 25 September addendum')
s.text('4,000 input tokens → 200 output tokens',.94,1.43,11.4,.65,30,bold=True)
table(s,['METRIC','WHAT IT MEASURES','LIMIT / UNIT'],[['TTFT ↓','Wait for the first token','≤ 3,000 ms'],['Mean ITL ↓','Interval between tokens','≤ 20 ms'],['Joint SLA ↑','Requests meeting both limits','≥ 90%'],['Goodput ↑','Qualifying service throughput','req/s × 200 = good tokens/s']],widths=[2.2,5.6,3.8],y=2.46,row_h=.65,size=20)
s.text('Per-request pass/fail decides goodput. Errors count against the service.',.99,6.12,11.5,.57,23,ORANGE)
s.end()
# 04
s=slide('One workload, two deployment systems', 'Both platforms provide two eight-GPU nodes, but they are not interchangeable experimental environments. Firmus uses H200, Slurm and Enroot; NSCC ASPIRE 2A+ uses H100 80GB, PBS and Singularity. We stage the same serving and client image artifacts and official FP8 checkpoint. CPU, driver, network, launcher, node cache and timing can still differ. A hardware-specification ratio is not a performance conversion.', 'Qwen rules; NSCC asset contract; matched-anchor audit')
table(s,['','FIRMUS','NSCC ASPIRE 2A+'],[['Allocation','2 × 8 H200','2 × 8 H100 80GB'],['Scheduler','Slurm','PBS'],['Container launcher','Enroot','Singularity'],['Serving / client','SGLang / AIPerf','Same staged image artifacts'],['Model','Qwen3-235B FP8','Same checkpoint']],widths=[3.1,4.25,4.25],row_h=.70,size=19)
s.text('Keep platform, topology, backend and load in every comparison.',.98,6.28,11.4,.52,23,ORANGE)
s.end()
# 05
s=slide('Separate prompt processing from token generation', 'The selected layout dedicates the first node to two prefill workers, each using tensor parallelism four and expert parallelism one. The second node runs one decode worker using TP8 and EP8. Requests enter through the gateway; NIXL transfers KV state between the roles. Tensor parallel groups stay within a node. Round-robin selects a prefill worker; all generated tokens are produced on the decode side.', 'Same 2xTP4/EP1 prefill and TP8/EP8 decode layout in current incumbents')
s.text('NODE 0 · PREFILL',.95,1.45,5.1,.5,23,bold=True);s.text('NODE 1 · DECODE',7.55,1.45,5.0,.5,23,bold=True)
for y,label in [(2.38,'P0 · TP4 / EP1'),(4.38,'P1 · TP4 / EP1')]:
 s.rect(.95,y,4.5,1.35,None,GRAY);s.text(label,1.18,y+.17,4.0,.43,23);s.chips(1.42,y+.84,4,.32,ORANGE,.40)
s.rect(7.55,2.38,4.8,3.35,None,GRAY);s.text('D0 · TP8 / EP8',7.86,2.70,4.2,.50,25);s.chips(8.05,3.73,4,.38,INK,.49);s.chips(8.05,4.66,4,.38,INK,.49)
s.arrow(5.48,3.01,7.45,3.01,ORANGE);s.arrow(5.48,4.98,7.45,4.98,ORANGE);s.text('KV state\nNIXL',5.66,3.60,1.75,.96,19,ORANGE)
s.text('2 prefill workers × 4 GPUs + 1 decode worker × 8 GPUs = 16 GPUs',.98,6.26,11.4,.48,21)
s.end()
# 06
s=slide('Topology search established the serving layout', 'We explored the balance between replication and parallelism. The original 07 and 09 names were identifiers, not software versions. The 07 configuration used four TP2 prefill workers and two TP4/EP4 decode workers. The next layout widened prefill to TP4. The selected split also widened decode to TP8/EP8. We explored 17 usable arrangements across 8+8, 4+12 and 12+4 GPU splits, retaining incompatible originals and EP2 replacements separately. These initial operating points differ in load and transport history.', '22197; 22219; 22415; prior topology campaign')
table(s,['LAYOUT','PREFILL','DECODE','N','GOOD TOKENS/S'],[['07','4 × TP2','2 × TP4/EP4','32','1,297.02'],['09','2 × TP4','2 × TP4/EP4','40','1,666.01'],['Selected split','2 × TP4','1 × TP8/EP8','48','1,912.30']],widths=[2.3,2.5,3.0,.8,3.0],row_h=.86,size=19)
s.text('17 usable arrangements across P8+D8, P4+D12 and P12+D4',.99,5.17,11.4,.60,25,bold=True)
s.text('Historical end-to-end progression; load and transport also changed.',1.0,6.06,11.3,.54,21,GRAY)
s.end()
# 07
s=slide('Make KV-transfer setup scale with the request', 'Cold disaggregated serving initially stalled while preparing whole-pool KV descriptors. The request-scoped patch constructs descriptors for the pages actually transferred and coalesces contiguous ranges. A representative TP8 source geometry drops from approximately 403.8 million source entries per rank for the pool to 188 coalesced entries for one contiguous 4,000-token request. These numbers are descriptor counts, not a measured speedup factor. The range mapping tests retained head mapping, byte ranges and notifications. Connection warming uses separate traffic before the official client warmup.', 'NIXL patch metadata; 720 + 936 range checks; historical cold-start logs')
s.text('Whole KV pool',.96,1.49,5.4,.55,28,bold=True);s.text('Request pages only',7.18,1.49,5.2,.55,28,ORANGE,bold=True)
s.text('403.8 million',.98,2.49,5.4,.86,39,bold=True);s.text('188',7.22,2.40,5.0,1.05,61,ORANGE,bold=True)
s.text('source entries per rank',1.0,3.59,5.1,.55,23);s.text('coalesced entries per request',7.24,3.59,5.0,.81,23)
s.line(6.52,1.48,6.52,5.5,PALE)
s.text('Preserve the transfer mapping. Warm every P/D path before scoring.',1.0,5.51,11.4,.8,26)
s.text('Descriptor geometry example, not a 2-million-fold inference speedup.',1.0,6.42,11.3,.37,17,GRAY)
s.end()
# 08
s=slide('FP8 block geometry constrains parallelism', 'A failed TP8/EP1 prefill deployment exposed a block-alignment constraint. The model MoE intermediate size is 1,536 and FP8 block width is 128. With EP1, MoE tensor parallelism eight produces 192-element partitions, which do not divide by 128. With EP2, effective MoE tensor parallelism is four, producing 384-element partitions. This retains all weights and experts. The TP8/EP2 replacement is a combined layout change, not an isolated TP speedup. Failure before benchmarking is not a measured throughput result.', 'Exact staged SGLang source; failed job 24282; corrected trial 24321')
for x,title,formula,nblocks,col in [(.98,'TP8 / EP1','1,536 ÷ 8 = 192',1,RED),(7.12,'TP8 / EP2','1,536 ÷ 4 = 384',3,INK)]:
 s.text(title,x,1.54,5.05,.6,30,col,bold=True);s.text(formula,x,2.54,5.1,.65,30)
 for i in range(nblocks):s.rect(x+i*1.63,3.70,1.52,1.0,ORANGE if nblocks==3 else INK);s.text('128',x+.34+i*1.63,3.97,.95,.5,25,WHITE)
 if nblocks==1:s.rect(x+1.65,3.70,.76,1.0,RED);s.text('64',x+1.78,3.99,.6,.4,20,WHITE)
s.text('Partial block → load failure',1.0,5.19,5.2,.85,24,RED);s.text('Three full blocks → compatible geometry',7.14,5.19,5.14,.85,24)
s.text('Compatibility is necessary; startup, SLA and output quality still need testing.',1.0,6.29,11.4,.45,19,GRAY)
s.end()
# 09
s=slide('A repeatable experiment loop', 'We combine source research with observed runtime, output checks, failures and cost before choosing a trial. Each useful hypothesis gets a control and a stopping rule. Exploratory short sweeps screen configurations; records in this talk use full 60/120/30 confirmations. We retain raw exports, per-request data, submitted payloads, logs and terminal artifacts. Candidate gains require runtime activation checks and independent replication. An exited job without a valid export is not a successful experiment. Loading time is also a resource cost: H100 is billed at 128 SU per GPU-hour, making a 16-GPU, 45-minute cap 1,536 SU. Three submitted jobs reserve 4,608 SU and run sequentially; prefetch targets startup cost rather than assumed throughput gains.', 'Research plans; payload hashes; sealed reviews')
for i,(n,head,body) in enumerate([('01','Hypothesis','Use logs, traces and source'),('02','Controlled trial','Change a defined factor'),('03','Validate','Protocol, runtime, SLA, output'),('04','Replicate or close','Confirm gains; stop losers')]):
 x=.96+i*3.14;s.text(n,x,1.53,2.8,.7,34,ORANGE,bold=True);s.text(head,x,2.53,2.87,1.02,25,bold=True);s.text(body,x,3.72,2.87,1.24,21)
s.line(.98,5.43,12.36,5.43,PALE)
s.text('60 s warmup  →  120 s measurement  →  30 s grace',1.0,5.80,11.4,.64,29)
s.text('Closed loop · 4,000 input / 200 output tokens · per-request SLA accounting',1.0,6.49,11.4,.34,16,GRAY)
s.end()
# 10
milestones=[('Initial 07\nN32',1297.02),('Initial 09\nN40',1666.01),('PD split\nN48',1912.30),('FI + MNNVL\nN52',2631.09),('Prefill DG\nN56',2715.84),('DG + HPC\nN58',2938.63),('N60\nreplicated',2989.17),('N62\nsingle',3022.03)]
def progression(fig,ax):
 x=np.arange(len(milestones));values=[r[1] for r in milestones]
 ax.bar(x,values,color=[GRAY]*3+[INK]*2+[ORANGE]*3,width=.65)
 for i,y in enumerate(values):ax.text(i,y+42,f'{y:,.0f}',ha='center',fontsize=11,fontweight='bold')
 ax.set_xticks(x,[r[0] for r in milestones],fontsize=10);ax.set_ylim(0,3400);ax.set_ylabel('Good output tokens/s');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
p=chart('h200-research-progression',progression)
s=slide('H200 journey: recover, specialise, then reproduce', 'The historical progression spans different loads and configurations, not a single cumulative causal ablation. We recovered the 16-GPU split and request-scoped NIXL transfer, combined FlashInfer attention with MNNVL, introduced DeepGEMM prefill, increased its chunk to 8192, and found an interaction with HPC-Ops decode. N58 and N60 treatment gains reproduce. New N62 is a single accepted observation and needs its own repeat.', 'Historical retained milestones; 24724/24737/24819; 24738/24913; 24915')
s.image(p,.78,1.40,11.8,4.68);s.text('Historical milestones · loads and runtime settings change across stages',1.0,6.32,11.3,.43,19,GRAY);s.end()
# 11
s=slide('Backend combinations matter', 'At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.', '23777; 23778; 23904; 23974')
table(s,['H200 · N52','JOB','GOOD TOKENS/S','SLA'],[['FlashInfer decode only','23777','2,440.39','98.947%'],['MNNVL decode only','23778','2,592.16','99.007%'],['MNNVL fresh control','23974','2,594.03','99.009%'],['MNNVL + FlashInfer','23904','2,631.09','99.022%']],widths=[4.4,1.5,3.2,2.5],row_h=.77,size=20)
s.text('Combine attention and collective tuning; measure the combination directly.',.99,6.13,11.3,.64,24,ORANGE);s.end()
# 12
def hm(job):return DATA['latest']['h200'][job]['point']['metrics']
loads=np.array([58,60,62]);auto=np.array([hm(j)['good_tokens_s'] for j in ['24736','24912','24914']])
groups=[['24724','24737','24819'],['24738','24913'],['24915']]
hpc=np.array([np.mean([hm(j)['good_tokens_s'] for j in g]) for g in groups])
def frontier(fig,ax):
 ax.plot(loads,auto,'o-',color=INK,label='Auto decode · fresh control points',linewidth=2.2)
 ax.plot(loads,hpc,'-',color=ORANGE,label='HPC-Ops decode · means where repeated',linewidth=2.5)
 ax.scatter(loads[:2],hpc[:2],s=55,color=ORANGE,zorder=4);ax.scatter([62],[hpc[-1]],s=70,facecolors=PAPER,edgecolors=ORANGE,zorder=4)
 for x,y in zip(loads,hpc):ax.annotate(f'{y:,.1f}',(x,y),xytext=(0,10),textcoords='offset points',ha='center',fontsize=12)
 ax.set_xticks(loads,['N58','N60','N62']);ax.set_ylabel('Good output tokens/s');ax.set_ylim(2700,3100);ax.legend(loc='lower right',fontsize=11);ax.grid(alpha=.16)
p=chart('h200-current-load-frontier',frontier)
s=slide('The runner interaction extends useful load', 'Both series use DeepGEMM prefill chunk8192 with the same layout, precision, transport and scoring protocol. Auto controls are 24736/24912/24914. HPC-Ops N58 has three observations; N60 has two; N62 has one. H200 N62 reaches 3022.035, about 4.54% above fresh auto N62 2890.878. We do not infer unrestricted concurrency growth. The N62 treatment still needs an independent repeat; mean summaries and sparse logs do not identify the bottleneck.', 'H200 reviewed N58/N60/N62 points and exact source hashes')
s.image(p,.78,1.37,11.8,4.75);s.text('N58: 3 treatment runs · N60: 2 · N62: 1, awaiting repeat',.99,6.29,11.4,.51,22,ORANGE);s.end()
# 13
s=slide('Profile the deployed interaction', 'Job 24819 repeats the winning N58 deployment, then collects a separate N48 diagnostic: 425 successful requests and 16 sealed nonempty rank traces. Decode named HPC group GEMM accounts for 21.642%, MNNVL allreduce/RMSNorm 23.479% and FlashInfer paged attention 15.064% of summed recorded kernel duration. They are descriptive sums, not a partition of end-to-end wall time or predicted speedups. Old controller parse/stop errors remain recorded; actual trace coverage is checked separately. The new profiler response fix is deployed only in later derived bundles.', '24819 sealed traces; H200_PROFILE.md; observability correction')
table(s,['DECODE COMPONENT','SUMMED KERNEL TIME','RESEARCH QUESTION'],[['HPC group GEMM','21.64%','MoE implementation'],['MNNVL collective / norm','23.48%','Communication strategy'],['FlashInfer attention','15.06%','Phase-specific backend']],widths=[4.4,3.2,4.0],row_h=.88,size=20)
s.text('Select the next hypothesis from traces, logs and matched outcomes.',1.0,5.47,11.3,.76,25,ORANGE)
s.text('Separate N48 profile · summed GPU durations are not wall-time shares',1.0,6.42,11.3,.36,18,GRAY);s.end()
# 14
s=slide('The N60 gain survives an independent deployment', 'Fresh auto-decode control 24912 versus HPC-Ops decode repeat 24913, both DeepGEMM prefill chunk8192 at N60. Goodput rises 5.295%, first-token latency rises 125.335 ms and ITL falls 1.644 ms. The original treatment 24738 scored 2990.151; its independent repeat scores 2989.175, only 0.033% lower. This reproduces the interaction rather than establishing a universal HPC-Ops effect. Runtime, raw per-request SLA, short nonregression and 12 long checks pass; full organiser quality remains open.', '24912/24913 full reviews; 24738 original treatment')
table(s,['METRIC','AUTO CONTROL','HPC-OPS REPEAT'],[['Good tokens/s ↑','2,838.853','2,989.175'],['Mean TTFT ↓','822.292 ms','947.627 ms'],['Mean ITL ↓','16.579 ms','14.934 ms'],['Joint SLA ↑','98.7599%','98.8178%']],widths=[3.5,4.05,4.05],row_h=.72,size=22)
s.text('+5.30% goodput · original and repeat differ by only 0.033%',.99,6.16,11.3,.62,25,ORANGE,bold=True);s.end()
# 15
raw=ROOT/'runs/24915/confirm/n62/artifacts/profile_export.jsonl'
points=[]
for line in raw.open():
 r=json.loads(line)
 if r.get('metadata',{}).get('phase_kind',r.get('metadata',{}).get('benchmark_phase'))!='profiling':continue
 m=r.get('metrics',{});points.append((m['time_to_first_token']['value'],m['inter_token_latency']['value']))
a=np.asarray(points);good=(a[:,0]<=3000)&(a[:,1]<=20)
assert len(a)==1884 and good.sum()==1860,(len(a),good.sum())
def scatter(fig,ax):
 ax.axvspan(0,3000,color='#E8F0ED',alpha=.65);ax.scatter(a[good,0],a[good,1],s=10,alpha=.26,color=INK);ax.scatter(a[~good,0],a[~good,1],s=24,color=ORANGE,alpha=.9)
 ax.axvline(3000,color=RED,ls='--');ax.axhline(20,color=RED,ls='--');ax.set_xlabel('Time to first token (ms)');ax.set_ylabel('Per-request mean ITL (ms)');ax.set_xlim(0,max(3400,a[:,0].max()*1.07));ax.set_ylim(0,max(24,a[:,1].max()*1.08))
p=chart('n62-request-sla',scatter,figsize=(9,4.7))
s=slide('Tail latency explains the requests we lose', 'Raw N62 H200 job 24915 has 1884 scored requests: 1860 meet both limits, 24 miss TTFT, none miss request-mean ITL, and none error or cancel. Joint SLA is 98.7261%. Passing average latency does not remove the first-token tail. The score is locally accepted; an independent N62 repeat and official quality remain open. Separately, the H100 FlashInfer/FA3 comparison also loses 22 requests to TTFT in each run, with zero request-mean ITL breaches. These are different runs, not one pooled result.', '24915 raw request rows and terminal review; H100 raw failure component inspection')
s.image(p,.60,1.38,8.55,4.98);s.text('98.726%',9.38,1.85,3.0,.86,39,ORANGE,bold=True);s.text('1,860 / 1,884 pass\n24 miss TTFT\n0 miss ITL\n0 request errors',9.42,3.10,2.96,2.05,21);s.end()
# 16
s=slide('H100 must find its own kernel and load combination', 'Earlier MNNVL paired repeats improved N32/N34 by 7.52/8.24 percent and combining MNNVL with attention extended useful capacity. The later both-phase HPC-Ops incumbent at N54 reaches 2430.891 as the highest individual observation. Fresh controls remain around 2421 to 2431, not an official rank or confidence interval. H100 uses prefill chunk4096, unlike H200 DeepGEMM chunk8192. Hardware, runner, load and configuration interactions must be measured independently.', 'Historical paired MNNVL reviews; 221590 retained full-protocol export; 222027 fresh control')
bullets(s,[('Control the comparison','MNNVL repeats: +7.52% at N32; +8.24% at N34 versus fresh controls.'),('Keep a platform-specific incumbent','Both-phase HPC-Ops · FlashInfer decode · chunk4096 · N54.'),('Measure the new interaction','Peak 2,430.89; fresh attention control 2,420.95 good tokens/s.')],gap=1.55,size=25);s.end()
# 17
s=slide('FA3: faster first token does not guarantee goodput', 'Only decode attention changes in the H100 N54 pair. FlashInfer control 222027 versus FA3 222028 both pass the local protocol/runtime/output gates, and FA3 execution is verified on eight decode ranks. Mean TTFT falls 118.922 ms, while mean ITL rises 0.773 ms. Across roughly 199 token intervals that adds about 154 ms, outweighing the first-token gain. Measured mean end-to-end latency rises from 4337.853 to 4372.813 ms; goodput falls 0.812%. This is one matched pair, not a universal FA3 ranking or precise kernel-level explanation. Prefill continues using FA3.', '222027/222028 full reviews and extended inspections; scoped interpretation')
table(s,['H100 · N54','FLASHINFER','FA3'],[['Good tokens/s ↑','2,420.945','2,401.284'],['Mean TTFT ↓','713.199 ms','594.276 ms'],['Mean ITL ↓','18.214 ms','18.988 ms'],['Mean request latency ↓','4,337.853 ms','4,372.813 ms']],widths=[4.2,3.7,3.7],row_h=.75,size=21)
s.text('Keep FlashInfer for this decode setting; FA3 remains our prefill backend.',1.0,6.26,11.3,.60,22,ORANGE);s.end()
# 18
s=slide('Compare matched systems, not unrelated peaks', 'Comparing H100 N50 with H200 N56 changes both the platform and the workload. For a calibrated comparison we hold the combo configuration and N52 load fixed. Selected runtime fields, the model, checkpoint precision, BF16 KV, worker placement, CUDA graphs, backends and client protocol match. The audited differences include engine random seeds; unobserved or unbalanced hardware and runtime conditions remain. We report a system association, not a causal GPU-only multiplier.', 'Matched-anchor audit and cross-platform report')
bullets(s,[('Hold the workload fixed','Same model, N52, 4,000/200 tokens and full benchmark protocol.'),('Hold the serving plan fixed','Two TP4/EP1 prefill workers; TP8/EP8 decode; same backends and images.'),('Keep the remaining limits visible','CPU, NIC, driver, launcher, cache and time can still differ.')],gap=1.55,size=26);s.end()
# 19
s=slide('A local N52 calibration, not a universal multiplier', 'The matched combo N52 anchor uses two H100 allocations and four H200 allocations. Their means are 2,215.460 and 2,632.181 good tokens/s, producing an empirical system ratio of 1.188096805. This is one calibration load for one configuration. Repeat measurements at one load do not identify a cross-platform function or a prediction interval. We do not apply this factor to TTFT, ITL, SLA or other backend branches.', 'H100 221052/221058; H200 23904/23973/23975/24174')
s.text('Same combo · same N52 · full protocol',1.0,1.48,11.3,.55,27,bold=True)
for x,label,value,sub in [(1.02,'H100 mean','2,215.460','2 allocations'),(7.14,'H200 mean','2,632.181','4 allocations')]:
 s.text(label,x,2.43,5.0,.5,25,ORANGE);s.text(value,x,3.15,5.2,.91,46,bold=True);s.text(sub,x,4.34,5.0,.43,21,GRAY)
s.text('Observed system ratio = 1.188096805',1.0,5.40,11.3,.70,32,bold=True)
s.text('One load and one configuration do not establish a hardware conversion rule.',1.0,6.38,11.4,.43,19,GRAY);s.end()
# 20
s=slide('Freeze the forecast, then test it on H200', 'Before the held-out H200 N50 result was available, we froze a prediction of 2,642.244 good tokens/s from the H100 N50 mean and the N52 ratio. We predeclared a 2% operational tolerance. Job 24272 measured 2,601.629, an error of minus 1.5371%, so this one local check is within tolerance. However, the result lies outside the earlier input-only sensitivity range, which omitted model error. We retain that negative finding, do not refit the frozen factor, and do not claim broad predictive validity.', 'Frozen prediction and hashes; held-out 24272 review; cross-platform report')
table(s,['HELD-OUT N50 TEST','VALUE'],[['Frozen prediction','2,642.244 good tokens/s'],['Measured H200 · job 24272','2,601.629 good tokens/s'],['Signed prediction error','−1.5371%'],['Predeclared tolerance','±2% · passed at this point only']],widths=[5.4,6.2],row_h=.77,size=23)
s.text('Outside the earlier sensitivity range: uncertainty was incomplete.',1.0,6.16,11.3,.65,25,ORANGE);s.end()
# 21
s=slide('Negative results narrow the next hypothesis', 'The grad-mode trials were flat, so we do not combine unproved gains. Forced NCCL Simple showed only a single +0.23% observation and no established useful gain. Its activation is proved by sealed TUNING decisions, not kernel-name guesses; representative LL symbols do not identify actual protocol. Isolated H100 collective microbenchmarks reject forced one-shot and disabling PDL. Their percentages describe microseconds per collective at 54 tokens, not full-serving goodput. H100 decode FA3 loses 0.81% goodput in one pair and stays closed at this setting.', 'Phase-specific inference review; NCCL correction; graph32 one-shot and PDL screens; H100 attention pair')
table(s,['CHANGE','SCOPE','OBSERVATION','DECISION'],[['Inference mode','Serving','No useful gain','Keep default'],['Forced Simple','Serving','+0.23%, unestablished','Keep automatic'],['Forced one-shot','Kernel','71–74% slower · 54 tokens','Keep AUTO'],['PDL disabled','Kernel','18–23% slower · 54 tokens','Keep PDL on'],['FA3 decode · H100','Serving','−0.81% goodput','Keep FlashInfer']],widths=[3.1,1.6,4.1,2.8],row_h=.72,size=17)
s.text('Kernel microseconds, serving goodput and deployment failures are distinct.',1.0,6.34,11.3,.43,19,GRAY);s.end()
# 22
s=slide('Latency passes; official quality is still open', 'The new H200 N62 result passes local per-request latency/error, protocol, runtime and diagnostic output checks. Its 98.7261% joint SLA exceeds 90%, but this does not establish the required full-set quality at 99 percent of reference. The small output suite retains seven of eight passes with the known reverse failure and no new regressions; twelve long retrieval cases pass. N60 treatment replication is established; N62 still needs independent repetition. No official leaderboard score or full-set MMLU-Pro/GPQA result is claimed.', '24915 complete review; unchanged local output baseline and quality policy')
for x,title,value,body in [(1.0,'Latency SLA','98.726%','Per-request gate passed\nRequired: at least 90%'),(7.1,'Official quality','Not verified','Target: ≥99% of reference\nFull-set evaluation remains')]:
 s.text(title,x,1.56,5.1,.55,30,bold=True);s.text(value,x,2.55,5.25,.95,42,ORANGE,bold=True);s.text(body,x,3.95,5.15,1.15,24)
s.text('Local checks: short nonregression and long 12/12; they are not full-set accuracy.',1.0,6.20,11.3,.65,21,GRAY);s.end()
# 23
s=slide('Measure the observer before trusting the next gain', 'Six derived pilots were submitted, three on each cluster. Observer-off interval1 versus observer-on interval1 measures combined sampling/metrics overhead. Observer-on interval2 compares native decode receive-poll frequency with an equally observed control. Sources agree across seven files in both runtime images; local tests execute the actual selector. Numerical kernels, token work, transport and full workload remain. Hardware/server samples run every five seconds; support, UUID mapping, phase alignment and overhead must be validated. The new profiler accepts successful empty/text control responses and still preserves HTTP failures. Validation is in progress, not a new measured gain.', '24926/24927/24928; 222048/222049/222050; telemetry implementation, source and local validations')
labels=[('01','Observer off','Default receive interval 1'),('02','Observed control','Same interval + resource sampling'),('03','Observed candidate','Decode receive interval 2')]
for i,(number,title,detail) in enumerate(labels):
 x=.95+i*4.16;s.text(number,x,1.57,3.7,.67,37,ORANGE,bold=True);s.text(title,x,2.57,3.7,.55,25,bold=True);s.text(detail,x,3.38,3.7,1.10,22)
 if i<2:s.arrow(x+3.47,2.00,x+3.99,2.00,ORANGE)
s.text('GPU activity % · VRAM MiB · power W · CPU/RAM · queue and network counters',1.0,5.42,11.3,.74,22)
s.text('Align to the scored phase. Missing data is unknown. Repeat useful gains.',1.0,6.40,11.3,.36,18,GRAY);s.end()
# 24
s=slide('What the campaign has established', 'We moved from topology and request-scoped KV transfer through combined attention/collectives and phase-specific MoE kernels. The N60 H200 interaction reproduces around 2989 to 2990 good output tokens/s, 5.295 percent above the fresh same-load auto control. The new N62 observation is 3022.035 but has not independently repeated. H100 has its own N54 frontier and rejected decode FA3 tradeoff. The next work measures observer overhead, validates a native polling hypothesis and completes quality evaluation; no global optimum or official score is claimed.',cover=True,dark=True)
s.text('Topology → transport → kernels → replication',.90,.95,11.7,.85,29,WHITE,bold=True)
s.text('3,022.03',.90,2.27,11.7,1.15,62,WHITE,bold=True)
s.text('good tokens/s · 16 H200 · N62 · single accepted observation',.96,3.70,11.6,.62,24,'#D5DEDF')
s.text('N60 independently repeats: 2,990.15 and 2,989.17',.96,4.70,11.5,.57,27,ORANGE,bold=True)
s.line(.96,5.70,12.10,5.70,ORANGE,1.4)
s.text('Confirm the next gain. Preserve model work. Verify full-set quality.',.96,6.15,11.4,.60,24,WHITE);s.end()
# 25
records=DATA['historical_records']['records']['H200']
rows=[]
for key,label,unit in [('good_output_tokens_s','Goodput ↑','tokens/s'),('ttft_avg_ms','Mean TTFT ↓','ms'),('itl_avg_ms','Mean ITL ↓','ms'),('good_request_fraction','Joint SLA ↑','%')]:
 record=records[key];p=record['ties'][0];v=record['value']*(100 if key=='good_request_fraction' else 1)
 detail='Many tied lower-load points' if len(record['ties'])>1 else ('Independent repeat pending' if key=='good_output_tokens_s' and 'H200'=='H200' else 'Different operating point')
 rows.append([label,f"{v:,.3f} {unit}",str(p['job']).replace('.pbs111','')+' / '+str(p['concurrency']),detail])
s=slide('Appendix · H200 metric records', 'Observed records across the retained full 60/120/30 and 4000/200 exports with reported passing SLA and zero errors/cancellations. This scan is not a fresh runtime/quality audit of every old observation. Throughput, minimum latency and 100 percent SLA can come from different deployments and loads; do not combine them into a fictional configuration. H100 minimum TTFT 220720 retains incomplete runtime proof; local records are not official ranking. Full source hashes are in the frozen presentation inputs.', 'Current full-protocol historical scan; complete reviews for current peak')
table(s,['METRIC','OBSERVED RECORD','JOB / N','INTERPRETATION'],rows,widths=[2.3,3.0,2.5,3.8],row_h=.86,size=17)
s.text('Records use different operating points; they do not describe one winning setup.',1.0,6.19,11.4,.60,21,GRAY);s.end()
# 26
records=DATA['historical_records']['records']['H100']
rows=[]
for key,label,unit in [('good_output_tokens_s','Goodput ↑','tokens/s'),('ttft_avg_ms','Mean TTFT ↓','ms'),('itl_avg_ms','Mean ITL ↓','ms'),('good_request_fraction','Joint SLA ↑','%')]:
 record=records[key];p=record['ties'][0];v=record['value']*(100 if key=='good_request_fraction' else 1)
 detail='Many tied lower-load points' if len(record['ties'])>1 else ('Independent repeat pending' if key=='good_output_tokens_s' and 'H100'=='H200' else 'Different operating point')
 rows.append([label,f"{v:,.3f} {unit}",str(p['job']).replace('.pbs111','')+' / '+str(p['concurrency']),detail])
s=slide('Appendix · H100 metric records', 'Observed records across the retained full 60/120/30 and 4000/200 exports with reported passing SLA and zero errors/cancellations. This scan is not a fresh runtime/quality audit of every old observation. Throughput, minimum latency and 100 percent SLA can come from different deployments and loads; do not combine them into a fictional configuration. H100 minimum TTFT 220720 retains incomplete runtime proof; local records are not official ranking. Full source hashes are in the frozen presentation inputs.', 'Current full-protocol historical scan; complete reviews for current peak')
table(s,['METRIC','OBSERVED RECORD','JOB / N','INTERPRETATION'],rows,widths=[2.3,3.0,2.5,3.8],row_h=.86,size=17)
s.text('Records use different operating points; they do not describe one winning setup.',1.0,6.19,11.4,.60,21,GRAY);s.end()
# 27
s=slide('Appendix · exact settings behind the current results', 'The H200 N62 single peak and reproduced N60 treatment share the deployment shown here. H100 highest individual and current incumbent use both-phase HPC-Ops at N54, with FlashInfer decode attention. Both keep FA3 prefill attention, TP4/EP1 prefill replicas and TP8/EP8 decode, native FP8 checkpoint and BF16 KV. MNNVL remains automatic strategy with PDL enabled. CUDA graph decode sizes are dense 1 through 64. Hardware, MoE runners, prefill chunk and load differ, so peaks are not a matched platform comparison.', '24915/24913 submitted payloads and resolved arguments; H100 incumbent records')
table(s,['SETTING','H200 N60 / N62','H100 N54'],[['Prefill / decode','2×TP4/EP1 → TP8/EP8','Same layout'],['Prefill chunk','8,192 tokens','4,096 tokens'],['Prefill / decode MoE','DeepGEMM / HPC-Ops','HPC-Ops / HPC-Ops'],['Attention P / D','FA3 / FlashInfer','FA3 / FlashInfer'],['Collective / graphs','MNNVL / dense 1–64','MNNVL / dense 1–64'],['Checkpoint / KV','Native FP8 / BF16','Native FP8 / BF16']],widths=[4.2,3.7,3.7],row_h=.65,size=17);s.end()
# 28
s=slide('Appendix · topology failures remain separate', 'In the first 17-job wave, only eight layouts produced measurements and nine failed before a useful benchmark. We corrected the earlier mistake of treating terminal scheduler states as completed measurements. Recovery addressed environment, registration, slow path warmup and FP8 block alignment. The final usable-layout accounting kept 14 compatible originals and three explicitly named EP2 replacements separate from the incompatible TP8/EP1 originals. No failed original receives a replacement result under its name.', 'Historical topology review; recovery records; prior 17-layout presentation')
bullets(s,[('Initial wave','8 layouts measured; 9 failed before a usable benchmark.'),('Recovery work','Fix container launch, worker registration and every P/D warmup path.'),('Keep configuration identity','14 compatible originals + 3 distinct EP2 replacement layouts.')],gap=1.55,size=27);s.end()
# 29
s=slide('Appendix · what the benchmark actually measures', 'The synthetic serving workload exercises a fixed prompt and answer length; it is not the same dataset as the accuracy evaluation. The client sustains a concurrency target and streams output through the gateway. Workers and every prefill/decode path are warmed separately using different traffic before the official client warmup. Only the scored window feeds the reported metrics, following AIPerf accounting. Grace allows outstanding requests to settle; it is not another steady-state benchmark. Do not recompute goodput by blindly dividing completed requests by 120.', 'Qwen workload and addendum; normalized AIPerf configs')
bullets(s,[('Serving dataset','Synthetic prompts: 4,000 input tokens and 200 requested output tokens.'),('Closed-loop API traffic','Keep N requests in flight; each completion triggers a replacement.'),('Quality dataset is separate','Full-set MMLU-Pro / GPQA scoring checks retained model quality.')],gap=1.55,size=26);s.end()
# 30
s=slide('Appendix · the jobs behind the new decisions', 'These are decision-linked research IDs, not packaging instructions. Original topology and transport work remain in earlier slides. N58 interaction repeats on 24724/24737/24819. N60 treatment 24738 and 24913 compare with fresh auto control 24912. N62 24915 compares with 24914 and needs an independent treatment repeat. H100 222027/222028 is the scoped attention pair; 222022/222023/222026 are isolated collective screens. New observed polling pilots are submitted and validation is in progress, not claimed results.', 'Frozen reviewed sources and definite submission receipts')
table(s,['DECISION','H200 JOBS','H100 JOBS'],[['Topology / KV transfer','22197, 22219, 22415','220562, 220575'],['N58 interaction repeats','24724, 24737, 24819','Platform-specific tuning'],['N60 / N62 comparisons','24912–24915; 24738','221590 incumbent'],['Attention / micro screens','24819 diagnostic','222027/28; 222022/23/26'],['Observed polling pilots','24926, 24927, 24928','222048, 222049, 222050']],widths=[3.6,4.0,4.0],row_h=.75,size=16)
s.text('Retain negative runs, control failures and corrected interpretations.',1.0,6.31,11.3,.45,19,GRAY);s.end()
# 31
s=slide('Appendix · preserve the context of rejected branches', 'FP8 KV N52 and decode DeepGEMM originally failed the latency gate. Early chunk8192 lost under the older automatic runner but later won with DeepGEMM prefill: the interaction changed, so the old rejection was not universal. One-request prefill batching lost 1.73 percent; original TP8/EP1 failed FP8 geometry before scoring. DeepEP low-latency and DP-attention comparisons did not beat their relevant contemporary controls. Preserve different controls, configurations and failure categories. A single observation does not prove an option always loses.', 'Retained full-protocol historical reports; 24281/24282; later DeepGEMM chunk interaction')
table(s,['BRANCH','OBSERVATION','LESSON'],[['FP8 KV · N52','10.75% joint SLA','Latency failure'],['DeepGEMM decode · early','84.72% joint SLA','Different phase / context'],['Chunk8192 · older runner','Lost; later DG interaction wins','Revisit only a new hypothesis'],['Single-request prefill','−1.73% goodput','Do not retry unchanged'],['Prefill TP8 / EP1','FP8 alignment failure','No valid measurement'],['DeepEP / DP attention','Below contemporary controls','Retain scoped negatives']],widths=[3.8,4.5,3.3],row_h=.62,size=16)
s.text('A deployment failure, latency failure and slow passing result are different outcomes.',1.0,6.38,11.3,.38,17,GRAY);s.end()
# 32
s=slide('Discussion', 'Questions may focus on worker balance, request-scoped NIXL transfer, phase-specific kernels, controlled replication, first-token tails, observer overhead and cross-platform comparison. N60 interaction is repeated; the new N62 single observation still requires confirmation. Official full-set accuracy remains unverified. Source-linked notes and native editable diagrams are retained; background photographs are reference infrastructure imagery, not contest-installation photographs.',cover=False)
s.text('Questions?',.98,1.75,11.3,1.34,66,bold=True)
for i,(icon,label) in enumerate([('cpu','Phase-specific kernels and reproduced gains'),('network','KV transfer and matched platform comparisons'),('timer','Tail latency, observer cost and retained quality')]):
 y=4.04+i*.72;s.icon(icon,1.02,y,.38);s.text(label,1.72,y+.015,10.55,.48,23)
s.end()

assert len(prs.slides)==32
for b in bounds:
    assert b['x']>=0 and b['y']>=0 and b['x']+b['w']<=W+.01 and b['y']+b['h']<=H+.01,b
assert len({r['sha256'] for r in BACKGROUNDS})==32
for r in BACKGROUNDS:assert hashlib.sha256((EXTERNAL/r['file']).read_bytes()).hexdigest()==r['sha256']
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
from pptx.opc.constants import RELATIONSHIP_TYPE as RT, CONTENT_TYPE as CT
credit='Theme adaptation: Metropolis, Matthias Vogelgesang and contributors, CC BY-SA 4.0, https://github.com/matze/mtheme. Original TripleU research charts and presentation content are separate from the theme licence. Icons: Lucide ISC. Backgrounds are separately sourced reference infrastructure photographs, not contest-installation photographs. Full attribution: '+json.dumps(BACKGROUNDS)
e=etree.Element('assetCredits');e.text=credit
part=Part(PackURI('/customXml/assetCredits.xml'),CT.XML,prs.part.package,etree.tostring(e,encoding='UTF-8',xml_declaration=True));prs.part.relate_to(part,RT.CUSTOM_XML)
prs.save(OUT/'TripleU_APAC2026_Presentation.pptx');pdf.save()
(OUT/'slide-content.json').write_text(json.dumps(outline,indent=2)+'\n')
(OUT/'layout-validation.json').write_text(json.dumps(dict(slides=32,main_slides=24,appendix_slides=8,text_within_boxes=True,boxes_within_slides=True,distinct_backgrounds=32,english_only=True,raw_sla_checked=dict(job='24915',requests=len(a),passed=int(good.sum())),render_note='PDF and previews use the same drawing coordinates as PPTX; they are not an Office rendering.'),indent=2)+'\n')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf');thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25));p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(2000,math.ceil(len(thumbs)/4)*300),'#E2E7E8');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f"{i+1:02d} {outline[i]['title'][:68]}",fill=INK)
sheet.save(OUT/'Presentation_Overview.jpg',quality=93)
print(json.dumps(dict(output=str(OUT),slides=len(prs.slides),main_slides=24,appendix=8)))

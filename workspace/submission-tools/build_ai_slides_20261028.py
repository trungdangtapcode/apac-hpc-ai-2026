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
OUT = WORK/'submission-review/ai-update-20261028/slides'
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
prs.core_properties.subject = 'Research update through 28 October 2026; H200 and H100 measured separately'
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


POLISHED_NOTES = {}

def readable_notes(text):
    import re
    text=re.sub(r'\b(through|full|mean|scores|about|source|by|at|only|least|all|passes|retains|smoke|retrieval|job|incumbent|observation|seed)(?=\d)',r'\1 ',text)
    text=re.sub(r'(\d)(ms|GB|seconds)\b',r'\1 \2',text)
    return text

def slide(title,notes,source='',**kwargs):
    # Sources remain in speaker notes and the research manifest, not folder-tour text.
    return Slide(title,notes=readable_notes(POLISHED_NOTES.get(title,notes))+('\n\nResearch sources: '+source if source else ''),**kwargs)


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
s=slide('Qwen serving', 'Research through 28 October 2026: topology recovery, request-scoped KV transfer, phase-specific kernels, full-protocol replication, negative trials and deployment reliability. Historical N64 three-run mean is 3044.400475 good output tokens/s, with separate new-runtime full26766 at3045.501509. Full N68 gains only0.083056% in its matched pair and is not promoted. H100 stays separate. Official full-set accuracy remains unverified.',cover=True)
s.text('APAC HPC-AI 2026  /  QWEN TASK',.8,.8,11,.4,15,ORANGE,bold=True)
s.text('Qwen serving:\nfrom topology to\nreproduced performance',.8,1.65,11.4,2.7,41,bold=True)
s.line(.83,4.85,11.9,4.85,ORANGE,1.6)
s.text('VNUHCM - TripleU',.84,5.19,11,.5,26)
s.text('Research update · 28 October 2026',.86,5.96,11,.4,18,GRAY);s.end()
# 02
s=slide('Two measured frontiers, kept separate', 'The selected H200 N64 point has three historical full runs with mean3044.400475; a new native-runtime full observation26766 passes at3045.501509 and98.580442% joint SLA. Do not pool these launcher regimes or claim a causal runtime improvement. H100 highest retained individual222048 is2433.019859 atN54; fresh full225227 gives2399.186728. These are separate platform/configuration series, not a matched algorithmic comparison or official accuracy pass. N68 full gain0.083056% does not clear our useful-gain gate.', '25366/25373/25487 full reviews;26766 independent raw review;222048 retained export;225227 fresh full review')
for x,label,rate,detail in [(.9,'16 H200','3,044.40','N64 · historical three-run mean'),(7.15,'16 H100','2,433.02','N54 · retained individual peak')]:
 s.text(label,x,1.52,5.2,.48,24,ORANGE,bold=True);s.text(rate,x,2.33,5.25,1.12,53,bold=True);s.text('good output tokens/s',x,3.68,5.1,.52,24);s.text(detail,x,4.60,5.22,.80,19)
s.line(6.53,1.48,6.53,5.65,PALE)
s.text('Fresh full checks: H200 3,045.50  /  H100 2,399.19 good tokens/s',.96,6.13,11.4,.58,20,GRAY);s.end()
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
milestones=[('Initial 07\nN32',1297.02),('Initial 09\nN40',1666.01),('PD split\nN48',1912.30),('FI + MNNVL\nN52',2631.09),('Prefill DG\nN56',2715.84),('DG + HPC\nN58',2938.63),('N60\nrepeated',2989.17),('N62\nrepeated',3022.55),('N64\n3 repeats',3044.40)]
def progression(fig,ax):
 x=np.arange(len(milestones));values=[r[1] for r in milestones]
 ax.bar(x,values,color=[GRAY]*3+[INK]*2+[ORANGE]*4,width=.65)
 for i,y in enumerate(values):ax.text(i,y+42,f'{y:,.0f}',ha='center',fontsize=11,fontweight='bold')
 ax.set_xticks(x,[r[0] for r in milestones],fontsize=10);ax.set_ylim(0,3400);ax.set_ylabel('Good output tokens/s');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
p=chart('h200-research-progression',progression)
s=slide('H200 journey: recover, specialise, then reproduce', 'The historical progression spans different loads and configurations, not a single cumulative causal ablation. We recovered the 16-GPU split and request-scoped NIXL transfer, combined FlashInfer attention with MNNVL, introduced DeepGEMM prefill, increased its chunk to 8192, and found an interaction with HPC-Ops decode. N58 and N60 treatment gains reproduce. N62 repeats at3022.034919/3023.072304; N64 repeats at3044.489701/3044.074628. Observation settings also differ across this historical journey; it is not one cumulative causal ablation.', 'Historical retained milestones; 24724/24737/24819; 24738/24913; 24915')
s.image(p,.78,1.40,11.8,4.68);s.text('Historical milestones · loads and runtime settings change across stages',1.0,6.32,11.3,.43,19,GRAY);s.end()
# 11
s=slide('Backend combinations matter', 'At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.', '23777; 23778; 23904; 23974')
table(s,['H200 · N52','JOB','GOOD TOKENS/S','SLA'],[['FlashInfer decode only','23777','2,440.39','98.947%'],['MNNVL decode only','23778','2,592.16','99.007%'],['MNNVL fresh control','23974','2,594.03','99.009%'],['MNNVL + FlashInfer','23904','2,631.09','99.022%']],widths=[4.4,1.5,3.2,2.5],row_h=.77,size=20)
s.text('Combine attention and collective tuning; measure the combination directly.',.99,6.13,11.3,.64,24,ORANGE);s.end()
# 12
s=slide('The next load step survives a full repeat', 'Fresh equally observed full N62 control 25365 versus full N64 candidate 25366 improves1.082867%. Independent N64 deployment 25373 differs from the source by−0.013634%; the two-run mean is3044.282165. Same serving topology, precision, transport and observation; source operational bytes differ only in load/provenance. Same sampled GPU UUID sets limit hardware diversity. Two runs do not establish a confidence interval or a global optimum.', '25365/25366 matched full proof; 25373 replication and telemetry')
table(s,['FULL 60 / 120 / 30','N62 CONTROL','N64 SOURCE','N64 REPEAT'],[['Good tokens/s','3,011.875','3,044.490','3,044.075'],['Joint SLA','98.7227%','98.6330%','98.6323%'],['TTFT mean · ms','1,037.630','1,110.463','1,113.240'],['ITL mean · ms','14.958','15.003','14.993'],['Errors / cancellations','0 / 0','0 / 0','0 / 0']],widths=[3.8,2.6,2.6,2.6],row_h=.70,size=19)
s.text('Source +1.083% versus N62 · N64 repeats within 0.014%',1.0,6.35,11.3,.43,22,ORANGE,bold=True);s.end()
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
raw=ROOT/'runs/26766/confirm/n64/artifacts/profile_export.jsonl'
points=[]
for line in raw.open():
 r=json.loads(line)
 if r.get('metadata',{}).get('benchmark_phase')!='profiling':continue
 m=r['metrics'];points.append((m['time_to_first_token']['value'],m['inter_token_latency']['value']))
a=np.asarray(points);good=(a[:,0]<=3000)&(a[:,1]<=20)
assert len(a)==1902 and good.sum()==1875

def scatter(fig,ax):
 ax.axvspan(0,3000,color='#E8F0ED',alpha=.65);ax.scatter(a[good,0],a[good,1],s=10,alpha=.26,color=INK);ax.scatter(a[~good,0],a[~good,1],s=24,color=ORANGE,alpha=.9)
 ax.axvline(3000,color=RED,ls='--');ax.axhline(20,color=RED,ls='--');ax.set_xlabel('Time to first token (ms)');ax.set_ylabel('Per-request mean ITL (ms)');ax.set_xlim(0,max(3400,a[:,0].max()*1.07));ax.set_ylim(0,24)
p=chart('n64-latest-request-sla',scatter,figsize=(9,4.7))
s=slide('The reproduced N64 service still loses first-token tails', 'Full new-runtime job 26766 passes the independently replayed protocol and local output gates at 3045.501509 good output tokens/s. Exactly 1875 of 1902 profiling requests satisfy both limits: 27 fail TTFT, none fail request-mean ITL, and errors/cancellations are zero. TTFT mean/p95 is 1108.869/1311.693 ms; ITL mean/p95 is 15.0075/15.1930 ms. All 27 failures start within 13.004085 ms of profiling admission. This is an initial-cohort association, not a proven causal bottleneck. Every failed request stays in the denominator.', '26766 raw profile, independent full review and sealed native-runtime payload')
s.image(p,.60,1.38,8.55,4.98);s.text('98.580%',9.38,1.85,3.0,.86,39,ORANGE,bold=True);s.text('1,875 / 1,902 pass\n27 miss TTFT\n0 miss ITL\n0 request errors',9.42,3.10,2.96,2.05,21);s.end()

# 16
s=slide('H100 has its own operating point and uncertainty', 'H100 retained highest individual 222048 is 2433.019859 good output tokens/s. A fresh full N54 control 225227 passes local gates at 2399.186728 and 98.015873% joint SLA, with zero request errors/cancellations. H100 uses both-phase HPC-Ops and chunk 4096, whereas H200 uses DeepGEMM prefill and chunk 8192. The fresh control is lower and must remain visible. These peaks are neither matched hardware tests nor a performance multiplier. Equal-TP H100 EAGLE transport has a functional response, but no accepted aggregate replica performance result is available.', '222048 raw retained evidence; 225227/225228 independent review; later failed launcher retained')
table(s,['H100 OBSERVATION','GOOD TOKENS/S','INTERPRETATION'],[['Retained individual peak','2,433.02','N54; historical'],['Fresh full N54 control','2,399.19','98.016% joint SLA'],['Prefill / decode','HPC-Ops / HPC-Ops','Chunk 4096 / TP8 EP8']],widths=[4.3,3.3,4.0],row_h=.87,size=20)
s.text('H100 and H200 need separate measurements and settings.',1.0,5.74,11.4,.72,26,ORANGE,bold=True);s.end()

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
s=slide('Several plausible ideas did not improve the service', 'These are scoped negative findings, not universal engine rankings. Full N68 25488 gains only 0.083056% over paired N64 25487, below our predeclared 1% practical gate. Modern full prefill graph/admission factors improve less than 1%; no confirmation was justified. H100 decode FA3 loses 0.812% in the retained pair. Decode-only EAGLE3 loses 4.74% against its short target-only control, although the local screen passes. Close unchanged branches and preserve their raw observations rather than combine small favorable peaks.', '25487/25488 full review; full graph/admission study; 222027/222028 attention pair; 25998 short review')
table(s,['HYPOTHESIS','OBSERVED RESULT','DECISION'],[['More load: N64 to N68','+0.083% full goodput','Keep reproduced N64'],['Prefill graph / admission','Useful gain below 1%','Close unchanged tuning'],['H100 decode FA3','-0.812% goodput','Retain FlashInfer'],['Decode-only EAGLE3','-4.74% short goodput','Do not promote']],widths=[4.0,4.0,3.6],row_h=.72,size=20)
s.text('A valid experiment may be a loss. An incomplete run has no score.',1.0,6.23,11.3,.46,23,ORANGE);s.end()

# 22
s=slide('Latency acceptance is separate from model accuracy', 'Full N64 26766 passes actual runtime, fixed workload and request-level latency checks with 98.580442% joint success. The local output suite passes 7/8 without new regression and retrieval 12/12. These small checks do not establish at least 99% of the organiser reference score on official full-set model-quality benchmarks. FP8 weights and BF16 activation/KV are retained, with no quantized KV or speculative decoding in the selected primary. Official accuracy and organiser re-verification remain open. Do not describe this as an official ranking or contest acceptance.', '26766 full gate; official Qwen rules and goodput clarification')
for i,(title,value,detail) in enumerate([('Service SLA','98.580%','Both limits, every request'),('Local sanity','7/8 + 12/12','No new output regression'),('Official quality','Not verified','At least 99% of reference')]):
 x=.96+i*4.16;s.text(title,x,1.73,3.72,.65,26,bold=True);s.text(value,x,2.91,3.74,.85,34,ORANGE,bold=True);s.text(detail,x,4.18,3.73,1.12,21)
s.text('Preserve the model. Verify quality independently of serving speed.',1.0,6.07,11.4,.60,24);s.end()

# 23
s=slide('EAGLE3: functional progress did not become a speedup', 'The research progressed from draft dtype and full-pool NIXL failures to actual equal-TP H100 transfer and valid H200 decode-only short serving. H200 25998 completes at 2626.71 good output tokens/s versus short target-only control 25947 at 2757.36, a 4.74% loss. Joint SLA is 94.84%; errors/cancellations are zero; smoke 7/8 and retrieval 12/12. Native draft acceptance around 0.12-0.15, approximately 1.24-1.29 accepted tokens per verification, is consistent with overhead not being repaid, but is not a causal kernel decomposition. This is a 20/40/30 unranked screen, not comparable directly with the full N64 frontier. Official accuracy is unknown and the unchanged draft/runtime branch is closed.', '25998 complete short review; 25947 control; H100 225228 equal-TP native observer')
for i,(title,value,detail) in enumerate([('Target-only control','2,757.36','Good tokens/s; short N64'),('Decode-only EAGLE3','2,626.71','Good tokens/s; same screen'),('Measured trade-off','-4.74%','Lower TTFT; higher ITL')]):
 x=.96+i*4.16;s.text(title,x,1.64,3.73,.72,24,bold=True);s.text(value,x,2.82,3.73,.88,37,ORANGE,bold=True);s.text(detail,x,4.15,3.73,1.15,21)
s.text('Functional transfer is a prerequisite; acceptance must repay draft work.',1.0,6.02,11.4,.77,24);s.end()

# 24
s=slide('What the campaign has established', 'Three historical full N64 observations 25366/25373/25487 have mean 3044.400475 good output tokens/s. A later native-runtime observation 26766 independently passes at 3045.501509 and 98.580442% joint SLA. We report these separately rather than pool runtime paths. Valid lower legacy/modern replays around 2802-2831 remain retained; exact parity checks do not establish why the operating regime changed. N64 is chosen for replication, not because of the highest historical individual N68. No official quality certificate, global optimum, speculative speedup or causal native-runtime speedup is claimed.', 'N64 three-run review; 26766 independent full review; lower 26313/26317/26319 retained',cover=True,dark=True)
s.text('Topology → transport → kernels → replication',.90,.95,11.7,.85,29,WHITE,bold=True)
s.text('3,044.40',.90,2.19,11.7,1.15,62,WHITE,bold=True)
s.text('good tokens/s · 16 H200 · N64 · three historical full runs',.96,3.62,11.6,.62,23,'#D5DEDF')
s.text('Fresh native-runtime check: 3,045.50 good tokens/s',.96,4.56,11.5,.74,26,ORANGE,bold=True)
s.line(.96,5.70,12.10,5.70,ORANGE,1.4)
s.text('Keep the reproduced operating point. Test distinct ideas. Verify quality.',.96,6.15,11.4,.62,23,WHITE);s.end()

# 25
s=slide('Appendix · reproduction includes lower observations', 'Historical full N64 runs 25366, 25373 and 25487 are 3044.489701, 3044.074628 and 3044.637094 good tokens/s, mean 3044.400475. Later exact legacy replay 26313 gives 2830.923547, with operational file parity and the same validated model/protocol but other unobserved runtime/node conditions. New native-runtime 26766 gives 3045.501509. Retain the lower result rather than omit it from the story. These runs span launcher and observation differences, so neither the difference from 26313 nor the new approximately 3k result isolates a causal improvement. Highest individual N68 25488=3047.165853 misses the paired useful-gain gate and is not selected.', '25366/25373/25487; 26313 recovery audit; 26766 full review')
table(s,['FULL OBSERVATION','GOOD TOKENS/S','INTERPRETATION'],[['N64 historical run 1','3,044.49','Independent full deployment'],['N64 historical run 2','3,044.07','Independent full deployment'],['N64 historical run 3','3,044.64','Three-run mean 3,044.40'],['Exact legacy replay','2,830.92','Valid lower result retained'],['Fresh native-runtime N64','3,045.50','Separate launcher; local pass']],widths=[4.6,3.0,4.0],row_h=.66,size=18)
s.text('Reproduced level; operating-regime variation is not explained away.',1.0,6.50,11.3,.34,18,GRAY);s.end()

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
s=slide('Appendix · the selected AI deployment is N64', 'The AI primary is updated from stale N62 to the replicated N64 setting, while the HPC package and its slide section are preserved. The package is a portable derivation rather than the historical research job itself; a separate GPU replay of that portable entry has not been performed. Native FP8 target and BF16 activation/KV remain. H200 uses two TP4 DeepGEMM prefills, chunk 8192 and breakable prefill graphs, with one TP8/EP8 HPC-Ops decode, FlashInfer decode attention, MNNVL and dense decode graphs 1 through 64. Round-robin routing and all original fixed-workload goodput limits remain. H100 is a separate point, not an alternate device setting for the same result.', '26766 frozen worker/runtime; 25487 operational settings; staged portable deployment validation')
table(s,['SETTING','H200 SELECTED','H100 RETAINED'],[['Client concurrency','64','54'],['Prefill runner / chunk','DeepGEMM / 8192','HPC-Ops / 4096'],['Decode runner','HPC-Ops','HPC-Ops'],['Prefill / decode TP','4 + 4 / 8','4 + 4 / 8'],['Weights / activation / KV','FP8 / BF16 / BF16','FP8 / BF16 / BF16']],widths=[4.2,3.7,3.7],row_h=.65,size=19)
s.text('Both: TP8 / EP8 decode, FlashInfer + MNNVL, round-robin routing.',1.0,6.37,11.3,.49,19,GRAY);s.end()

# 28
s=slide('Appendix · the first cohort still contains TTFT misses', 'Historical N62 control 25365 has 24 failures starting by 35.444853 ms after profiling begins; N64 25366 has 26 by 33.481316 ms; repeat 25373 has 26 by 30.864687 ms. New native-runtime N64 26766 has 27 TTFT failures, all starting by 13.004085 ms, with zero ITL failures and zero errors/cancellations. The request-start calculation was replayed from the raw profiling JSONL. This is an association with initial admission, not a causal prefill, transport or decode diagnosis. Fixing every miss at unchanged request count/accounting would be a hypothetical ceiling, not an achieved speedup. Keep cold prefixes and every request in the denominator.', 'Raw per-request exports 25365/25366/25373/26766')
table(s,['FULL N64 OBSERVATION','TTFT MISSES','LATEST FAILED START'],[['Historical source','26','33.48 ms'],['Historical repeat','26','30.86 ms'],['Fresh native-runtime check','27','13.00 ms']],widths=[5.8,2.3,3.5],row_h=.87,size=22)
s.text('Initial admission is a useful clue, not a licence to trim the dataset.',1.0,5.76,11.3,.77,25,ORANGE);s.end()

# 29
s=slide('Appendix · what the benchmark actually measures', 'The synthetic serving workload exercises a fixed prompt and answer length; it is not the same dataset as the accuracy evaluation. The client sustains a concurrency target and streams output through the gateway. Workers and every prefill/decode path are warmed separately using different traffic before the official client warmup. Only the scored window feeds the reported metrics, following AIPerf accounting. Grace allows outstanding requests to settle; it is not another steady-state benchmark. Do not recompute goodput by blindly dividing completed requests by 120.', 'Qwen workload and addendum; normalized AIPerf configs')
bullets(s,[('Serving dataset','Synthetic prompts: 4,000 input tokens and 200 requested output tokens.'),('Closed-loop API traffic','Keep N requests in flight; each completion triggers a replacement.'),('Quality checks are separate','Organiser full-set scores must reach at least 99% of its FP8 reference.')],gap=1.55,size=26);s.end()
# 30
s=slide('Appendix · larger prefill chunks did not help', 'All three new R3 arms are full N64, 60/120/30, fixed 4000/200 seed2026 cold prefixes, same model/source/precision and same runtime path. 26766 chunk8192 gives 3045.501509 good output tokens/s; 26768 chunk10240 gives 3034.088251; 26770 chunk12288 gives 3020.943099. All pass local protocol/runtime/SLA/output checks, have zero profiling errors/cancellations, smoke7/8 and retrieval12/12. Mean TTFT rises 1108.869 to 1138.225/1145.943 ms; p95 rises 1311.693 to 1518.870/1624.120 ms. One ordered observation per arm is not a global optimum. Retain8192 and close the bounded larger-chunk branch.', '26766/26768/26770 independent full reviews; sealed raw exports')
table(s,['CHUNK TOKENS','GOOD TOKENS/S','JOINT SLA','p95 TTFT'],[['8192','3,045.50','98.580%','1,311.69 ms'],['10240','3,034.09','98.524%','1,518.87 ms'],['12288','3,020.94','98.310%','1,624.12 ms']],widths=[2.8,3.2,2.5,3.1],row_h=.94,size=22)
s.text('More work per prefill batch did not produce more qualifying output.',1.0,5.87,11.3,.77,25,ORANGE);s.end()

# 31
s=slide('Appendix · reliability is part of a usable result', 'Shared storage pressure blocked default container extraction. A native unprivileged Enroot route under ordinary Slurm cgroups was verified on one GPU and two independent four-GPU groups with eight distinct UUIDs, then passed full serving. The AIPerf image needed an explicit exec command script; private rootfs cleanup was verified after scored runs. The newer tokenizer trials all wrote valid semantic P/D receipts but the outer warmup step timed out before AIPerf. They have no measured speedup. The derived repair retains the semantic120-second command and global17-minute job deadlines while separating rootfs lifecycle timing. These are reproducibility and failure-accounting findings, not inference optimization gains.', 'Native runtime R3, eight-GPU proof, full26766, failed26849/26851/26853 and bounded lifecycle repair')
for i,(title,body) in enumerate([('Allocate correctly','Respect GPU masks and cgroups'),('Verify real work','Source, KV geometry and responses'),('Separate lifecycle time','Extract → serve → remove'),('Accept only complete data','Timeout before scoring has no score')]):
 x=.96+i*3.14;s.text(title,x,1.65,2.85,1.10,25,bold=True);s.text(body,x,3.28,2.85,1.50,21)
s.text('Semantic success alone does not certify a complete benchmark.',1.0,6.10,11.4,.63,25,ORANGE);s.end()

# 32
s=slide('Discussion · the next useful questions', 'The chosen primary remains replicated N64 target-only serving. Larger chunks, unchanged N68 increases and unchanged low-acceptance EAGLE3 are closed at their tested settings. Native asynchronous tokenizer batching is a new bounded hypothesis: CPU-only exact input IDs pass for64 concurrent and one single request, but no complete serving benchmark exists yet because the first full arms failed an outer lifecycle timeout. Repaired trials are submitted, not scored improvements. Evaluate useful matched gains, first-cohort TTFT tails, complete model-quality evaluation, and portable deployment replay. Background photos remain reference infrastructure, not contest-installation photographs. The unchanged HPC section follows.', 'Full research journal through28October2026; tokenizer and lifecycle repair records')
for i,(head,body) in enumerate([('Optimize qualifying work','Use matched controls and complete requests.'),('Explain the remaining tails','Test a cause; keep cold-cache accounting.'),('Prove deployment and quality','Re-run the portable entry and official accuracy suite.')]):
 yy=1.56+i*1.49;s.text(head,1.0,yy,11.3,.61,29,ORANGE,bold=True);s.text(body,1.0,yy+.67,11.3,.66,23)
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
(OUT/'layout-validation.json').write_text(json.dumps(dict(slides=32,main_slides=24,appendix_slides=8,text_within_boxes=True,boxes_within_slides=True,distinct_backgrounds=32,english_only=True,raw_sla_checked=dict(job='26766',requests=len(a),passed=int(good.sum())),render_note='PDF and previews use the same drawing coordinates as PPTX; they are not an Office rendering.'),indent=2)+'\n')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf');thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25));p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(2000,math.ceil(len(thumbs)/4)*300),'#E2E7E8');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f"{i+1:02d} {outline[i]['title'][:68]}",fill=INK)
sheet.save(OUT/'Presentation_Overview.jpg',quality=93)
print(json.dumps(dict(output=str(OUT),slides=len(prs.slides),main_slides=24,appendix=8)))

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
OUT = WORK/'submission-review/research-update-2026-10-22'
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
prs.core_properties.subject = 'Research update through 22 October 2026; H200 and H100 measured separately'
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


POLISHED_NOTES = {'Qwen serving': 'Research through 22 October: topology, request-scoped KV transfer, phase-specific kernels, full-protocol replication and the next load frontier. Full N64 independently repeats at 3044.489701 and 3044.074628 good output tokens/s. Short N68 improves by 2.273457%, but full confirmation remains pending. H100 remains a separate platform. Official full-set accuracy is unverified.', 'Two measured frontiers': 'H200 full N64 source 25366 scores 3044.489701 good output tokens/s. Independent deployment 25373 scores 3044.074628, a difference of -0.013634%; the mean is 3044.282165. Both have about 98.63% joint SLA and zero request errors. Source N64 improves by 1.082867% over fresh observed N62 control 25365. H100 incumbent 222048 remains 2433.019859 at N54 with different hardware and settings. These peaks are local results, not a matched cross-platform algorithmic comparison or official quality pass.', 'H200 journey: recover, specialise, then reproduce': 'This historical progression spans different loads, observation settings and configurations, not a cumulative causal ablation. The campaign recovered disaggregated serving, made NIXL setup request-scoped, combined FlashInfer and MNNVL, then found a DeepGEMM prefill / HPC-Ops decode interaction. N58 and N60 gains repeat. N62 repeats at 3022.034919 / 3023.072304; full observed N64 repeats at 3044.489701 / 3044.074628. The final bar uses the N64 mean, not a new single-run score.', 'The next load step survives a full repeat': 'Fresh equally observed full N62 control 25365 versus full N64 source 25366 improves by 1.082867%. Independent full N64 deployment 25373 differs from the source by -0.013634%; the two-run mean is 3044.282165 good output tokens/s. Both full N64 runs pass runtime, protocol, zero-error SLA, short output non-regression and long retrieval checks. Same sampled GPU UUID sets limit hardware diversity. Two measurements do not establish a confidence interval or global optimum.', 'The remaining losses are first-token tails': 'Independent full N64 job 25373 has 1901 scored requests: 1875 joint-good, 26 TTFT breaches, zero mean-ITL breaches and zero request errors/cancellations. TTFT mean/p95 is 1113.240 / 1309.781 ms; request-mean ITL mean/p95 is 14.993 / 15.160 ms. All 26 failures start within 30.864687 ms of profiling beginning. This localizes the first cohort, not the causal bottleneck. Every request stays in the official denominator.', 'Reproducible latency is not a quality certificate': 'Both full N64 deployments pass local protocol, runtime, zero-error SLA and output non-regression. Repeat joint SLA is 98.632299%. The short diagnostic retains seven of eight passes with the known reverse failure; long retrieval passes 12/12. These do not establish official accuracy at least 99% of the organisers own unchanged FP8 reference score. The official checks include but are not limited to model-card benchmarks and AIPerf checks. No official ranking or accuracy pass is claimed.', 'EAGLE3: small components pass, full serving is open': 'H100 reference 222761 supplies 1600 actual output IDs. Explicit BF16/unquant fixes the reproduced draft norm mismatch; uniform eager prefill addresses rank-divergent graph capture. Full 223055 reaches requests but fails an earlier NIXL remote disconnect. Its old warm marker masked child failure; the final token gate correctly rejects HTTP 500 and zero outputs. Later two-GPU probes 223091, 223097 and 223132 pass small base transfers, actual descriptors, native 190-range registration and DRAM auxiliary writes on different hosts. They do not prove full-pool EAGLE3 correctness. Next prepare a fresh H200 reference and a separately gated candidate with semantic pair receipts. The public nebius draft uses the pinned revision, about 1.146 GB serialized BF16 tensors, with no team training. No speculative speedup is claimed.', 'What the campaign has established': 'Topology recovery and request-scoped KV transfer enabled serving. Phase-specific kernels and controlled load selection extended throughput. Full N64 now repeats at 3044.489701 and 3044.074628 good output tokens/s, with mean 3044.282165. Short N68 improves by 2.273457% and awaits fresh full confirmation. H100 remains independently measured. No global optimum, official quality pass or speculative speedup is claimed.', 'Appendix · exact settings behind the current results': 'The reproduced H200 N64 point uses two TP4/EP1 DeepGEMM prefills with chunk size 8192 and one TP8/EP8 HPC-Ops decode. H100 uses both-phase HPC-Ops and chunk size 4096 at N54. Both retain FA3 prefill attention, FlashInfer decode attention, MNNVL, dense decode graph sizes 1 through 64, native FP8 weights and BF16 KV. Different hardware, runner and load settings prevent interpreting the peaks as a matched platform comparison.', 'Appendix · the first cohort contains the TTFT misses': 'Full N62 control 25365 has 24 failures, all starting by 35.444853 ms after profiling begins. Full N64 source 25366 has 26 by 33.481316 ms; repeat 25373 has 26 by 30.864687 ms. No later TTFT failures or ITL failures occur in these inspected points. This is an association, not proof of a prefill, transport or decode cause. Recovering every failure at unchanged total count and duration would add about 1.2-1.4%, not a promised speedup. Keep every request, the fixed arrival protocol and official warmup.', 'Appendix · what the benchmark actually measures': 'The synthetic serving workload is separate from full-set accuracy evaluation. The client sustains a declared concurrency and streams through the gateway. Every prefill/decode path is warmed with separate traffic before the unchanged official client warmup. The scored window uses AIPerf accounting; grace settles outstanding requests rather than adding another steady-state window. Do not recompute goodput by blindly dividing the completed request count by 120. Accuracy compares benchmark scores with the organisers FP8 reference; no fixed exhaustive public task list is assumed here.', 'Appendix · N68 wins the screen, not a full score': 'Short same-deployment job 25371 measures N64 then N68 with 20/40/30 timing. Both local gates pass and good throughput improves by 2.273457%, while TTFT/ITL rise and joint SLA falls slightly. This fixed-order short evidence is unranked. Actual scored decode running-request maxima 54 / 58 stay below unchanged graph cap 64. Fresh full N64 control 25487 and N68 candidate 25488 are submitted, with no result yet. Require full local gates and at least 1% matched gain before N68 replication.', 'Appendix · losses guide the next hypothesis': 'Full N60 both-HPC job 24965 loses 3.1904% versus fresh control 24964; power-of-two router 25283 loses 3.8067%; locality capture 25051 is only +0.1375%, not a useful gain. Retain these valid results and close unchanged repeats. P12/D4 is withheld before GPU submission: equal TP4-to-TP4 NIXL enumerates whole KV pools, while actual candidate setup geometry, memory, time and reviewer support remain unbounded. This is a source-level risk, not a measured loss. Historical CPU and prefetch trials remain below their prospective practical gates.', 'Discussion': 'Discuss worker balance, request-scoped KV transfer, phase-specific kernels, replication, first-token tails, observer limits and matched platform comparison. N64 independently repeats within 0.014%; short N68 awaits full confirmation. EAGLE3 needs a passing full-model correctness result, and official full-set accuracy remains unverified. Backgrounds are reference infrastructure photographs, not photographs of the contest installation.'}

def slide(title,notes,source='',**kwargs):
    # Sources remain in speaker notes and the research manifest, not folder-tour text.
    return Slide(title,notes=POLISHED_NOTES.get(title,notes)+('\n\nResearch sources: '+source if source else ''),**kwargs)


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
s=slide('Qwen serving', 'Research through 22 October: topology, request-scoped KV transfer, phase-specific kernels, full-protocol replication and the next load frontier. Full N64 independently repeats at 3044.489701 and 3044.074628 good output tokens/s. Short N68 improves 2.273457% but full confirmation remains pending. Keep H100 separate. Official full-set accuracy is unverified.',cover=True)
s.text('APAC HPC-AI 2026  /  QWEN TASK',.8,.8,11,.4,15,ORANGE,bold=True)
s.text('Qwen serving:\nfrom topology to\nreproduced performance',.8,1.65,11.4,2.7,41,bold=True)
s.line(.83,4.85,11.9,4.85,ORANGE,1.6)
s.text('VNUHCM - TripleU',.84,5.19,11,.5,26)
s.text('Research update · 22 October 2026',.86,5.96,11,.4,18,GRAY);s.end()
# 02
s=slide('Two measured frontiers', 'H200 full N64 source 25366 scores3044.489701; independent deployment 25373 scores3044.074628, a difference of−0.013634% and mean3044.282165. Both have about98.63% joint SLA and zero errors. The matched fresh N62 control 25365 scores3011.875113; sourceN64 improves1.082867%. H100 incumbent222048 remains2433.019859 atN54 on different hardware and settings. These are local results, not a cross-platform algorithmic comparison or official accuracy pass.', '25366 and 25373 full reviews; fresh 25365 control; retained H100222048')
for x,label,rate,detail in [(.9,'16 H200','3,044.49','N64 · repeat 3,044.07 · SLA 98.63%'),(7.15,'16 H100','2,433.02','N54 · measured independently')]:
 s.text(label,x,1.52,5.2,.48,24,ORANGE,bold=True);s.text(rate,x,2.33,5.25,1.12,53,bold=True);s.text('good output tokens/s',x,3.68,5.1,.52,24);s.text(detail,x,4.60,5.22,.80,19)
s.line(6.53,1.48,6.53,5.65,PALE)
s.text('N64 reproduced locally · short N68 gain still needs full confirmation',.96,6.13,11.4,.58,20,GRAY);s.end()
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
milestones=[('Initial 07\nN32',1297.02),('Initial 09\nN40',1666.01),('PD split\nN48',1912.30),('FI + MNNVL\nN52',2631.09),('Prefill DG\nN56',2715.84),('DG + HPC\nN58',2938.63),('N60\nrepeated',2989.17),('N62\nrepeated',3022.55),('N64\nrepeated',3044.28)]
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
raw=ROOT/'runs/25373/confirm/n64/artifacts/profile_export.jsonl'
points=[]
for line in raw.open():
 r=json.loads(line)
 if r.get('metadata',{}).get('phase_kind',r.get('metadata',{}).get('benchmark_phase'))!='profiling':continue
 m=r.get('metrics',{});points.append((m['time_to_first_token']['value'],m['inter_token_latency']['value']))
a=np.asarray(points);good=(a[:,0]<=3000)&(a[:,1]<=20)
assert len(a)==1901 and good.sum()==1875,(len(a),good.sum())
def scatter(fig,ax):
 ax.axvspan(0,3000,color='#E8F0ED',alpha=.65);ax.scatter(a[good,0],a[good,1],s=10,alpha=.26,color=INK);ax.scatter(a[~good,0],a[~good,1],s=24,color=ORANGE,alpha=.9)
 ax.axvline(3000,color=RED,ls='--');ax.axhline(20,color=RED,ls='--');ax.set_xlabel('Time to first token (ms)');ax.set_ylabel('Per-request mean ITL (ms)');ax.set_xlim(0,max(3400,a[:,0].max()*1.07));ax.set_ylim(0,max(24,a[:,1].max()*1.08))
p=chart('n64-request-sla',scatter,figsize=(9,4.7))
s=slide('The remaining losses are first-token tails', 'Independent N64 job 25373 has1901 scored requests:1875 joint-good,26 TTFT breaches,0 mean-ITL breaches and0 errors/cancellations. TTFT mean/p95 is1113.240/1309.781ms; request-mean ITL mean/p95 is14.993/15.160ms. All26 failures start within30.864687ms of profiling beginning. This localizes the first cohort, not the causal bottleneck. Every request stays in the official denominator.', '25373 sealed raw request export; full review')
s.image(p,.60,1.38,8.55,4.98);s.text('98.632%',9.38,1.85,3.0,.86,39,ORANGE,bold=True);s.text('1,875 / 1,901 pass\n26 miss TTFT\n0 miss ITL\n0 request errors',9.42,3.10,2.96,2.05,21);s.end()
# 16
s=slide('H100 must find its own kernel and load combination', 'Earlier MNNVL paired repeats improved N32/N34 by 7.52/8.24 percent and combining MNNVL with attention extended useful capacity. The later both-phase HPC-Ops incumbent at N54 reaches 2433.020 as the highest individual observation. Fresh controls remain around 2421 to 2431, not an official rank or confidence interval. H100 uses prefill chunk4096, unlike H200 DeepGEMM chunk8192. Hardware, runner, load and configuration interactions must be measured independently.', 'Historical paired MNNVL reviews; 222048 retained full-protocol export; 222027 fresh control')
bullets(s,[('Control the comparison','MNNVL repeats: +7.52% at N32; +8.24% at N34 versus fresh controls.'),('Keep a platform-specific incumbent','Both-phase HPC-Ops · FlashInfer decode · chunk4096 · N54.'),('Measure the new interaction','Peak 2,433.02; fresh attention control 2,420.95 good tokens/s.')],gap=1.55,size=25);s.end()
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
s=slide('Reproducible latency is not a quality certificate', 'Both full N64 deployments pass local protocol/runtime, zero-error per-request SLA and output non-regression. Repeat joint SLA is98.632299%. Seven of eight short diagnostics pass with the inherited reverse failure; long retrieval passes12/12. These checks do not establish official accuracy at least99% of the organisers own unchanged FP8 reference score. The official check includes but is not limited to model-card benchmarks and AIPerf checks. No official ranking or accuracy pass is claimed.', '25366/25373 full reviews; Qwen addendumQ1')
for x,title,value,body in [(1.0,'Repeated latency SLA','98.63%','Both full deployments pass\nRequired: at least 90%'),(7.1,'Official quality','Not verified','Target: ≥99% of reference\nFull-set evaluation remains')]:
 s.text(title,x,1.56,5.1,.55,29,bold=True);s.text(value,x,2.55,5.25,.95,42,ORANGE,bold=True);s.text(body,x,4.03,5.1,1.15,25)
s.text('Local output checks support research decisions; they do not replace full-set quality.',1.0,6.20,11.3,.65,21,GRAY);s.end()
# 23
s=slide('EAGLE3: small components pass, full serving is open', 'The H100 target-only reference222761 supplies1600 actual output IDs. Explicit BF16/unquant fixes the proven draft norm mismatch; uniform eager prefill fixes a rank-divergent graph path. Full223055 reaches real requests but fails an earlier NIXL remote disconnect; its old warm marker masked child failure, while the final token gate correctly rejected HTTP500/zero outputs. Later two-GPU probes223091,223097,223132 pass base transfer, actual descriptors, native190-range VRAM registration and DRAM auxiliary writes on other hosts and tiny buffers. They do not prove production EAGLE3 equivalence. Next prepare a fresh native H200 reference and separately gated candidate, using independent semantic pair receipts. Public draft nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507, pinned revision,1.146GB serialized BF16, no team training. No speculative speedup claimed.', '222761;223055;223091;223097;223132 sealed reviews; semantic warmup gate')
for i,(number,title,detail) in enumerate([('01','Stable reference','1,600 actual output IDs\nTwo greedy target passes'),('02','Component evidence','Small native KV writes pass\nFull pools remain unproved'),('03','Full integration','Transport failure retained\nFresh H200 proof is next')]):
 x=.95+i*4.16;s.text(number,x,1.57,3.7,.67,37,ORANGE,bold=True);s.text(title,x,2.57,3.7,.55,25,bold=True);s.text(detail,x,3.38,3.7,1.30,21)
 if i<2:s.arrow(x+3.47,2.00,x+3.99,2.00,ORANGE)
s.text('Require semantic pair receipts and complete IDs before a load benchmark.',1.0,5.55,11.3,.74,22)
s.text('Small-buffer success is a prerequisite, not a full-model performance result.',1.0,6.40,11.3,.36,18,GRAY);s.end()
# 24
s=slide('What the campaign has established', 'Topology recovery and request-scoped KV transfer enabled the serving stack; phase-specific kernels and controlled load selection extended throughput. Full N64 is now independently repeated at3044.489701 and3044.074628 good output tokens/s, mean3044.282165. Short N68 improves2.273457% and awaits fresh full confirmation. H100 remains independently measured. No global optimum, official quality pass or speculative speedup is claimed.',cover=True,dark=True)
s.text('Topology → transport → kernels → replication',.90,.95,11.7,.85,29,WHITE,bold=True)
s.text('3,044.28',.90,2.27,11.7,1.15,62,WHITE,bold=True)
s.text('good tokens/s · 16 H200 · N64 · mean of two full runs',.96,3.70,11.6,.62,24,'#D5DEDF')
s.text('Independent runs: 3,044.49 and 3,044.07',.96,4.70,11.5,.57,27,ORANGE,bold=True)
s.line(.96,5.70,12.10,5.70,ORANGE,1.4)
s.text('Confirm N68 at full duration. Prove EAGLE3 correctness. Verify quality.',.96,6.15,11.4,.60,23,WHITE);s.end()
# 25
records=DATA['historical_records']['records']['H200']
rows=[]
for key,label,unit in [('good_output_tokens_s','Goodput ↑','tokens/s'),('ttft_avg_ms','Mean TTFT ↓','ms'),('itl_avg_ms','Mean ITL ↓','ms'),('good_request_fraction','Joint SLA ↑','%')]:
 record=records[key];p=record['ties'][0];v=record['value']*(100 if key=='good_request_fraction' else 1)
 detail='Many tied lower-load points' if len(record['ties'])>1 else ('Repeat within 0.014%' if key=='good_output_tokens_s' and 'H200'=='H200' else 'Different operating point')
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
s=slide('Appendix · exact settings behind the current results', 'The reproduced H200 N64 operating point uses the deployment shown here. H100 highest individual and current incumbent use both-phase HPC-Ops at N54, with FlashInfer decode attention. Both keep FA3 prefill attention, TP4/EP1 prefill replicas and TP8/EP8 decode, native FP8 checkpoint and BF16 KV. MNNVL remains automatic strategy with PDL enabled. CUDA graph decode sizes are dense 1 through 64. Hardware, MoE runners, prefill chunk and load differ, so peaks are not a matched platform comparison.', '24915/24913 submitted payloads and resolved arguments; H100 incumbent records')
table(s,['SETTING','H200 N64','H100 N54'],[['Prefill / decode','2×TP4/EP1 → TP8/EP8','Same layout'],['Prefill chunk','8,192 tokens','4,096 tokens'],['Prefill / decode MoE','DeepGEMM / HPC-Ops','HPC-Ops / HPC-Ops'],['Attention P / D','FA3 / FlashInfer','FA3 / FlashInfer'],['Collective / graphs','MNNVL / dense 1–64','MNNVL / dense 1–64'],['Checkpoint / KV','Native FP8 / BF16','Native FP8 / BF16']],widths=[4.2,3.7,3.7],row_h=.65,size=17);s.end()
# 28
s=slide('Appendix · the first cohort contains the TTFT misses', 'Full N62 control 25365 has24 failures, all starting by35.444853ms after profiling begins. Full N64 source 25366 has26, by33.481316ms; repeat 25373 has26, by30.864687ms. No later TTFT failures and no ITL failures occur in these inspected full points. This is association, not proof of a prefill, transport or decode cause. At unchanged count/duration, recovering all such failures would add about1.2–1.4%, not a promised speedup. Keep every request, fixed arrival protocol and official warmup.', 'Sealed per-request timestamps in 25365/25366/25373')
table(s,['FULL POINT','TTFT MISSES','LATEST FAILED START'],[['N62 control · 25365','24 / 1,879','35.445 ms'],['N64 source · 25366','26 / 1,902','33.481 ms'],['N64 repeat · 25373','26 / 1,901','30.865 ms']],widths=[4.3,3.0,4.3],row_h=.86,size=21)
s.text('Locate the failing cohort; do not delete it or infer a causal bottleneck.',1.0,5.46,11.2,.80,25,ORANGE)
s.text('GPU activity, allocated VRAM and KV token occupancy measure different things.',1.0,6.42,11.3,.36,18,GRAY);s.end()
# 29
s=slide('Appendix · what the benchmark actually measures', 'The synthetic serving workload exercises a fixed prompt and answer length; it is not the same dataset as the accuracy evaluation. The client sustains a concurrency target and streams output through the gateway. Workers and every prefill/decode path are warmed separately using different traffic before the official client warmup. Only the scored window feeds the reported metrics, following AIPerf accounting. Grace allows outstanding requests to settle; it is not another steady-state benchmark. Do not recompute goodput by blindly dividing completed requests by 120.', 'Qwen workload and addendum; normalized AIPerf configs')
bullets(s,[('Serving dataset','Synthetic prompts: 4,000 input tokens and 200 requested output tokens.'),('Closed-loop API traffic','Keep N requests in flight; each completion triggers a replacement.'),('Quality checks are separate','Organiser full-set scores must reach at least 99% of its FP8 reference.')],gap=1.55,size=26);s.end()
# 30
s=slide('Appendix · N68 wins the screen, not a full score', 'Short same-deployment 25371 measures N64 thenN68 with20/40/30. Both local gates pass; good throughput improves2.273457%, but TTFT/ITL rise and joint SLA falls slightly. This is fixed-order short evidence, not a full ranked point. Actual scored decode running-request maxima54/58 remain below unchanged graph cap64. Fresh full N64 control 25487 and N68 candidate 25488 are submitted, no result yet. Require full local gates and at least1% matched gain before N68 replication.', '25371 strict short review and raw timing;25487/25488 receipts')
table(s,['SHORT 20 / 40 / 30','N64','N68'],[['Good tokens/s','2,830.699','2,895.054'],['Joint SLA','95.9311%','95.8904%'],['TTFT mean · ms','1,228.656','1,347.803'],['ITL mean · ms','14.909','15.040'],['Logged decode max','54 requests','58 requests']],widths=[4.8,3.4,3.4],row_h=.70,size=20)
s.text('+2.273% short gain → fresh full confirmation pending',1.0,6.34,11.3,.46,23,ORANGE,bold=True);s.end()
# 31
s=slide('Appendix · losses guide the next hypothesis', 'Full N60 both-HPC8192 job24965 loses3.1904% versus fresh control24964; power_of_two25283 loses3.8067%; locality capture25051 is only+0.1375%, not a useful gain. Retain their raw passing measurements and close unchanged repeats. P12/D4 with current HPC-Ops is withheld before GPU submission: equal TP4→TP4 NIXL enumerates the full KV pool; actual candidate descriptor count/setup memory/time and reviewer support are unbounded. This is a source-level risk, not a measured loss. Historical rejected branches retain their scoped controls.', 'H200 wave review; current P12/D4 source assessment; earlier scoped negatives')
table(s,['BRANCH','OBSERVATION','DECISION'],[['Both-HPC · N60','−3.19% goodput','Close unchanged'],['Power-of-two routing','−3.81% goodput','Keep round-robin'],['Locality capture','+0.14%; diagnostic','No gain claimed'],['P12 / D4 proposal','Full-pool equal-TP setup','Withhold; bound first'],['CPU envelope tuning','+0.289%; below 1% gate','Close unchanged'],['Startup prefetch repeat','9.836% saving; below 10%','No causal promotion']],widths=[3.9,4.5,3.2],row_h=.63,size=16)
s.text('A slow valid run, a failed run and an unsubmitted risk are different outcomes.',1.0,6.42,11.3,.36,18,GRAY);s.end()
# 32
s=slide('Discussion', 'Questions may focus on worker balance, request-scoped NIXL transfer, phase-specific kernels, controlled replication, first-token tails, observer overhead and cross-platform comparison. N64 independently repeats within0.014%; short N68 awaits full confirmation. EAGLE3 still needs a passing full-model correctness result. Official full-set accuracy remains unverified. Source-linked notes and native editable diagrams are retained; background photographs are reference infrastructure imagery, not contest-installation photographs.',cover=False)
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
(OUT/'layout-validation.json').write_text(json.dumps(dict(slides=32,main_slides=24,appendix_slides=8,text_within_boxes=True,boxes_within_slides=True,distinct_backgrounds=32,english_only=True,raw_sla_checked=dict(job='25373',requests=len(a),passed=int(good.sum())),render_note='PDF and previews use the same drawing coordinates as PPTX; they are not an Office rendering.'),indent=2)+'\n')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf');thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25));p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(2000,math.ceil(len(thumbs)/4)*300),'#E2E7E8');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f"{i+1:02d} {outline[i]['title'][:68]}",fill=INK)
sheet.save(OUT/'Presentation_Overview.jpg',quality=93)
print(json.dumps(dict(output=str(OUT),slides=len(prs.slides),main_slides=24,appendix=8)))

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
OUT = WORK/'submission-review/research-update-2026-10-17'
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
prs.core_properties.subject = 'Research update through 17 October 2026; H200 and H100 measured separately'
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
s=slide('Qwen serving', 'We present our complete optimisation path, from the initial topology measurements to the latest phase-specific compute trial. The workload is Qwen3-235B with 4,000 input tokens and 200 generated output tokens. H200 and H100 measurements are kept separate. The headline H200 result is a research candidate awaiting independent confirmation and official accuracy evaluation.',cover=True)
s.text('APAC HPC-AI 2026  /  QWEN TASK',.8,.8,11,.4,15,ORANGE,bold=True)
s.text('Qwen serving:\nfrom topology to\nphase-specific kernels',.8,1.65,11.4,2.7,43,bold=True)
s.line(.83,4.85,11.9,4.85,ORANGE,1.6)
s.text('VNUHCM - TripleU',.84,5.19,11,.5,26)
s.text('Research update · 17 October 2026',.86,5.96,11,.4,18,GRAY)
s.end()
# 02
s=slide('Two measured frontiers', 'The highest observed H200 goodput is 2,715.842 good output tokens per second at N56 with prefill-only DeepGEMM. It passes local protocol, runtime, SLA and research output checks; replication is pending. H100 reaches 2,229.827 at N50 with the combo configuration. Its independent N50 measurements average 2,223.930. These are different hardware and load points, not a matched algorithmic speedup.', '24291 review; H100 221052/221058 sealed reviews')
for x,label,rate,detail in [(.9,'16 H200','2,715.84','N56 · 98.819% joint SLA'),(7.15,'16 H100','2,229.83','N50 · 98.568% joint SLA')]:
 s.text(label,x,1.52,5.2,.48,24,ORANGE,bold=True);s.text(rate,x,2.33,5.25,1.12,53,bold=True);s.text('good output tokens/s',x,3.68,5.1,.52,24);s.text(detail,x,4.60,5.22,.63,20)
s.line(6.53,1.48,6.53,5.65,PALE)
s.text('Measured research results · official accuracy and re-run remain outstanding',.96,6.13,11.4,.58,20,GRAY)
s.end()
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
s=slide('Separate prompt processing from token generation', 'The selected layout dedicates the first node to two prefill workers, each using tensor parallelism four and expert parallelism one. The second node runs one decode worker using TP8 and EP8. Requests enter through the gateway; NIXL transfers KV state between the roles. Tensor parallel groups stay within a node. Round-robin selects a prefill worker; all generated tokens are produced on the decode side.', 'Selected placements in 24291 and 221058')
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
s=slide('FP8 block geometry constrains parallelism', 'A failed TP8/EP1 prefill deployment exposed a block-alignment constraint. The model MoE intermediate size is 1,536 and FP8 block width is 128. With EP1, MoE tensor parallelism eight produces 192-element partitions, which do not divide by 128. With EP2, effective MoE tensor parallelism is four, producing 384-element partitions. This retains all weights and experts. The new N56 TP8/EP2 test is a combined prefill-layout change, not an isolated TP speedup. Failure before benchmarking is not a measured throughput result.', 'Exact staged SGLang source; failed job 24282; corrected trial 24321')
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
jobs=['22197','22219','22415','23904','24190','24291'];vals=[point(j)['good_output_tokens_s'] for j in jobs]
def progression(fig,ax):
 ax.bar(np.arange(len(vals)),vals,color=[GRAY]*3+[INK,INK,ORANGE],width=.65)
 ax.set_xticks(np.arange(len(vals)),['07\nN32','09\nN40','PD split\nN48','Combo\nN52','Combo\nN56','Prefill DG\nN56']);ax.set_ylabel('Good output tokens/s');ax.set_ylim(0,3100)
 for i,v in enumerate(vals):ax.text(i,v+65,f'{v:,.0f}',ha='center',fontsize=13,fontweight='bold')
p=chart('h200-progression',progression)
s=slide('H200 progression: topology, serving, then kernels', 'The H200 campaign progressed from 1,297.018 good tokens/s in the initial reference operating point to 1,912.300 after topology and transfer work, then above 2,630 with serving backends at N52. Load selection reached about 2,670 at N56. Prefill-only DeepGEMM produced the latest 2,715.842 candidate. This is a historical end-to-end progression: it changes topology, load, transfer and backends over time. It is not a single-factor speedup measurement.', 'Full confirmations: '+', '.join(jobs))
s.image(p,.74,1.35,11.93,4.74);s.text('Different stages and loads: historical progression, not isolated component speedups.',1.0,6.32,11.4,.42,18,GRAY);s.end()
# 11
s=slide('Backend combinations matter', 'At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.', '23777; 23778; 23904; 23974')
table(s,['H200 · N52','JOB','GOOD TOKENS/S','SLA'],[['FlashInfer decode only','23777','2,440.39','98.947%'],['MNNVL decode only','23778','2,592.16','99.007%'],['MNNVL fresh control','23974','2,594.03','99.009%'],['MNNVL + FlashInfer','23904','2,631.09','99.022%']],widths=[4.4,1.5,3.2,2.5],row_h=.77,size=20)
s.text('Combine attention and collective tuning; measure the combination directly.',.99,6.13,11.3,.64,24,ORANGE);s.end()
# 12
nsload=[50,52,54,56,58];rates=[point('24272')['good_output_tokens_s'],np.mean([point(j)['good_output_tokens_s'] for j in ['23904','23973','23975','24174']]),np.mean([point(j)['good_output_tokens_s'] for j in ['24131','24175','24189']]),np.mean([point(j)['good_output_tokens_s'] for j in ['24190','24235']]),point('24236')['good_output_tokens_s']]
def loads(fig,ax):
 ax.plot(nsload,rates,'o-',color=ORANGE,lw=2.5);ax.set_xticks(nsload);ax.set_xlabel('Concurrent requests (N)');ax.set_ylabel('Good output tokens/s');ax.set_ylim(2560,2720)
 for n,v in zip(nsload,rates):ax.annotate(f'{v:,.1f}',(n,v),xytext=(0,12),textcoords='offset points',ha='center',fontsize=13)
p=chart('h200-load',loads)
s=slide('More concurrency eventually stops helping', 'The original combo configuration increases goodput as load rises toward N56. The two N56 confirmations average 2,670.456. N58 measures 2,667.966 and increases TTFT to 991.136 ms, providing no observed gain. We do not blindly keep increasing concurrency. The plot aggregates the stated jobs; N50 and N58 have only one observation each. The newer prefill DeepGEMM candidate is not mixed into this control curve.', '24272; 23904/23973/23975/24174; 24131/24175/24189; 24190/24235; 24236')
s.image(p,.78,1.33,11.8,4.72);s.text('Combo N56: mean 2,670.46 · N58: 2,667.97, with higher TTFT',.99,6.26,11.4,.51,23,ORANGE);s.end()
# 13
s=slide('Profile the phase before choosing the kernel', 'After the scored N56 benchmark, job 24263 ran a separate diagnostic at concurrency 48. All 16 rank traces contain kernels, and all 415 diagnostic requests succeeded. On each prefill worker, classified MoE kernels account for about 43% of summed kernel durations, motivating a prefill-only kernel trial. These fractions are not wall-time shares or predicted speedups. Prefill captured four steps and decode 32, so their absolute totals are not comparable. Profiling control warnings are retained, but trace coverage is valid.', '24263 profile review; diagnostic protocol and all-rank traces')
table(s,['ROLE','MoE KERNEL SHARE','COLLECTIVE SHARE'],[['Prefill worker 0','42.84%','23.48%'],['Prefill worker 1','42.77%','23.64%'],['Decode worker','27.99%','23.89%']],widths=[4.0,3.8,3.8],row_h=.82,size=23)
s.text('Hypothesis: change prefill MoE computation; retain the decode stack.',.99,5.45,11.4,.85,24,ORANGE)
s.text('Shares of summed kernel durations, not fractions of end-to-end time.',1.0,6.42,11.3,.37,18,GRAY);s.end()
# 14
s=slide('DeepGEMM for prefill: a new candidate gain', 'Job 24291 changes the prefill MoE runner to deep_gemm, retaining two TP4/EP1 prefill workers, TP8/EP8 decode, MNNVL, FlashInfer, N56 and the full protocol. Against fresh control 24263, goodput improves 1.8136% and mean TTFT drops 107.569 ms. ITL rises slightly, so the gain is not a universal latency improvement. Runtime, raw protocol, short nonregression and 12 long checks pass. A speculative runner field inherits deep_gemm, but speculative_algorithm remains None. An independent repeat is submitted; this candidate is not yet a final validated selection.', '24291-v2.json; 24263; repeat 24327 pending at snapshot')
table(s,['METRIC','CONTROL 24263','PREFILL DG 24291'],[['Good tokens/s ↑','2,667.465','2,715.842'],['Mean TTFT ↓','856.622 ms','749.053 ms'],['Mean ITL ↓','16.257 ms','16.446 ms'],['Joint SLA ↑','98.7995%','98.8194%']],widths=[3.5,4.05,4.05],row_h=.72,size=22)
s.text('+1.81% goodput · same N56 load · independent repeat pending',.99,6.16,11.3,.62,25,ORANGE,bold=True);s.end()
# 15
raw=ROOT/'runs/24291/confirm/n56/artifacts/profile_export.jsonl'
points=[]
for line in raw.open():
 r=json.loads(line)
 if r.get('metadata',{}).get('benchmark_phase')!='profiling':continue
 m=r.get('metrics',{})
 if 'time_to_first_token' in m and 'inter_token_latency' in m:points.append((m['time_to_first_token']['value'],m['inter_token_latency']['value']))
a=np.asarray(points);good=(a[:,0]<=3000)&(a[:,1]<=20)
assert len(a)==1694 and good.sum()==1674,(len(a),good.sum())
def scatter(fig,ax):
 ax.axvspan(0,3000,color='#E8F0ED',alpha=.65);ax.scatter(a[good,0],a[good,1],s=10,alpha=.26,color=INK);ax.scatter(a[~good,0],a[~good,1],s=24,color=ORANGE,alpha=.9)
 ax.axvline(3000,color=RED,ls='--');ax.axhline(20,color=RED,ls='--');ax.set_xlabel('Time to first token (ms)');ax.set_ylabel('Per-request mean ITL (ms)');ax.set_xlim(0,max(3400,a[:,0].max()*1.07));ax.set_ylim(0,max(24,a[:,1].max()*1.08))
p=chart('deepgemm-request-sla',scatter,figsize=(9,4.7))
s=slide('The latency gate is checked request by request', 'The latest DeepGEMM candidate has 1,694 measured requests. A raw-request check finds 1,674 within both limits and 20 that miss a limit; there are no request errors or cancellations. This produces 98.8194% joint SLA. The mean TTFT of 749 ms and mean ITL of 16.446 ms are useful descriptions, but the pass fraction is determined by individual requests. The 90% latency gate passes; the official accuracy gate remains separate.', '24291 raw profile_export.jsonl and reviewed export')
s.image(p,.60,1.38,8.55,4.98);s.text('98.819%',9.38,1.85,3.0,.86,39,ORANGE,bold=True);s.text('1,674 / 1,694 pass\n20 miss a limit\n0 errors\n0 cancellations',9.42,3.10,2.96,2.05,21);s.end()
# 16
s=slide('H100: repeat the tuning on its own hardware', 'The H100 campaign uses the same model and staged image contract, but must find its own capacity frontier. MNNVL repeats at low loads increased goodput by about 7.52% and 8.24% at N32 and N34 versus a fresh control. Standalone FlashInfer was slower in historical tests, while the combination extended useful capacity. MNNVL-only passed N46 but failed N48 in repeated measurements. Combo passed N48 and later reached its best N50 operating point. This is why a winner on one cluster cannot simply be assumed to win on the other.', 'H100 matched pair 220908/220909; 221020/221021; 221052/221058')
bullets(s,[('Fresh same-load control','MNNVL: +7.52% at N32; +8.24% at N34 in the paired repeat.'),('Capacity differs from H200','MNNVL-only N48 failed the SLA gate in repeated trials.'),('Measure combinations','Combo retained passing SLA through N50; standalone choices did not predict it.')],gap=1.55,size=26)
s.end()
# 17
s=slide('H100 load frontier: N50 beats N48 and N52', 'The two independent combo sweep jobs each measured N48, N50 and N52. N50 has the highest mean goodput at 2,223.930 tokens/s, with a peak of 2,229.827. N52 is lower in both repeats and has more first-token waiting. N48 has lower TTFT and a somewhat higher SLA pass fraction. These are operating point tradeoffs, not separate accuracy scores. We select useful throughput under the SLA, rather than the smallest average latency.', '221052 and 221058 sealed reviews')
for key in ['221052.pbs111','221058.pbs111']:
 assert len(DATA['h100'][key])>=3
rows=[]
for n in [48,50,52]:
 aa=point('221052.pbs111',n,'h100');bb=point('221058.pbs111',n,'h100');rows.append([f'N{n}',f"{aa['good_output_tokens_s']:,.2f}",f"{bb['good_output_tokens_s']:,.2f}",f"{(aa['good_output_tokens_s']+bb['good_output_tokens_s'])/2:,.2f}"])
table(s,['LOAD','RUN 221052','RUN 221058','MEAN GOOD TOKENS/S'],rows,widths=[1.4,3.0,3.0,4.2],row_h=.9,size=22)
s.text('N50 peak: 2,229.83 good tokens/s · SLA 98.5684%',1.0,5.42,11.4,.65,29,ORANGE,bold=True);s.text('Two allocations, not six independent repeats: loads share each allocation.',1.0,6.35,11.4,.40,18,GRAY);s.end()
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
s=slide('Negative results narrow the next experiment', 'The search retained losing and failed branches instead of hiding them. FP8 KV at N52 and decode-side DeepGEMM failed the latency gate. Prefill chunks 2,048 and 8,192 were slower than 4,096 in the compared combo tests. Limiting prefill batching to one request reduced goodput 1.73% versus the fresh N56 control, despite slightly lower mean ITL. TP8/EP1 failed before benchmarking. These are different outcomes: a slow passing result, an SLA failure and a deployment failure are not interchangeable.', '23608; 23609; 23905/23906; 24281; 24282')
table(s,['BRANCH','OBSERVATION','DECISION'],[['FP8 KV · N52','10.75% SLA','Close latency branch'],['DeepGEMM on decode','84.72% SLA','Do not infer prefill behaviour'],['Prefill chunks 2048 / 8192','Below chunk4096 goodput','Retain 4096'],['Prefill max requests = 1','−1.73% goodput','Do not repeat'],['Prefill TP8 / EP1','FP8 load failure','Separate EP2 repair']],widths=[4.2,3.9,3.5],row_h=.72,size=18)
s.text('Failed startup is not a completed benchmark. A lower ITL is not always a win.',1.0,6.35,11.4,.44,19,GRAY);s.end()
# 22
s=slide('Latency passes; official accuracy is still open', 'Local research quality checks are separate from official acceptance. The latest candidate has no new short-output failures relative to the independent baseline and passes 12 long-context retrieval checks. The short diagnostic itself is seven of eight, because the baseline already fails one case; we do not hide that. These checks support nonregression research but do not replace full-set MMLU-Pro and GPQA evaluation. Retaining 99% of the reference score is relative accuracy, not 99% absolute question accuracy. No official score or re-run result is claimed.', '24291 short nonregression and long review; Qwen addendum Q1')
for x,title,value,body in [(1.0,'Latency SLA','98.819%','Per-request gate passed\nRequired: at least 90%'),(7.12,'Official quality','Not verified','Target: ≥99% of reference\nFull-set evaluation remains')]:
 s.text(title,x,1.52,5.1,.62,29,bold=True);s.text(value,x,2.57,5.2,1.05,45,ORANGE,bold=True);s.text(body,x,4.13,5.2,1.34,25)
s.text('Local diagnostics: short 7/8, no new failures; long retrieval 12/12.',1.0,6.18,11.3,.59,23,GRAY);s.end()
# 23
s=slide('Next tests follow the remaining uncertainty', 'At the saved queue snapshot, H200 jobs 24320, 24321, 24322 and 24327 are submitted: fresh combo control, TP8/EP2 prefill, prefill weight prefetch and independent DeepGEMM repeat. H100 jobs 221151, 221152 and 221153 form a sequential control, prefill DeepGEMM and prefill prefetch chain. These are pending experiments, not additional results. Prefetch targets startup and credit, not an assumed throughput gain. We will validate useful gains independently and keep quality checks separate from official accuracy.', 'Submission receipts and scheduler snapshot on 17 October 2026')
table(s,['QUESTION','H200','H100'],[['Fresh control','24320 · N56','221151 · N50'],['Prefill compute','24327 · DG repeat','221152 · DG trial'],['Prefill parallelism','24321 · TP8 / EP2','No new matched trial'],['Startup / prefetch','24322','221153']],widths=[4.3,3.65,3.65],row_h=.78,size=21)
s.text('Submitted, not measured. Promote only after runtime, SLA and output review.',1.0,6.18,11.4,.6,22,ORANGE);s.end()
# 24
s=slide('What the campaign has established', 'Our main lesson is that topology, transfer, backend choice and load must be considered together. The selected topology and request-scoped KV descriptors made the deployment usable; phase-specific compute and communication tuning then lifted useful throughput. H200 currently has a promising 2,715.842 candidate; H100 has repeated N50 evidence averaging 2,223.930. Cross-platform extrapolation is narrowly calibrated and checked with a held-out result. The remaining work is independent candidate confirmation and official quality validation. The appendix contains metric records and run details for questions.', dark=True)
s.text('Topology → transport → kernels → load',.95,1.48,11.4,.82,34,WHITE,bold=True)
s.text('2,715.84',.98,2.72,10.9,1.45,76,WHITE,bold=True)
s.text('good tokens/s · 16 H200 · N56 · 98.819% joint SLA',1.02,4.38,11.2,.72,27,WHITE)
s.line(1.0,5.47,12.3,5.47,ORANGE,1.6)
s.text('Replicate the gain. Preserve model computation. Verify official quality.',1.03,5.95,11.1,.86,25,'#D5DFE1');s.end()
# 25
s=slide('Appendix · independent H200 metric records', 'These are separate observed records across the available history of full-duration passing measurements, not one configuration achieving every minimum and maximum. The lowest mean ITL is from the decode-heavy topology at N16. The lowest TTFT is from the older round-robin layout at N53. Highest goodput is the newer prefill DeepGEMM N56 trial. SLA reaches 100% at low load in two tied topology runs. The scan does not re-audit every old runtime or quality condition.', 'All-history metric report and records.json')
table(s,['METRIC','RECORD','JOB / N','CONFIGURATION'],[['Goodput ↑','2,715.842 tokens/s','24291 / 56','TP4→TP8 + prefill DG'],['Mean TTFT ↓','328.900 ms','23773 / 53','Round-robin / chunk4096'],['Mean ITL ↓','13.495 ms','22517 / 16','P4+D12; decode 3×TP4'],['Joint SLA ↑','100% · tied','22416, 22532 / 16','P12+D4 layouts']],widths=[2.3,3.0,2.5,3.8],row_h=.86,size=18)
s.text('N = concurrent requests. Each record belongs to a different operating point.',1.0,6.12,11.4,.65,22,GRAY);s.end()
# 26
s=slide('Appendix · independent H100 metric records', 'The highest H100 goodput is the N50 combo run. The observed TTFT minimum is from early MNNVL job 220720, but empty role logs leave runtime incompletely verified; it is not a fully validated deployment winner. The ITL minimum is from MNNVL repeat 220909 at N32 with later task-side proof. Multiple jobs tie at 100% SLA. These records come from full-protocol exports; they are not a substitute for comparing like-for-like deployments.', 'All-history metric report; pair-review 220909/220908')
table(s,['METRIC','RECORD','JOB / N','INTERPRETATION'],[['Goodput ↑','2,229.827 tokens/s','221058 / 50','Combo; replicated load'],['Mean TTFT ↓','303.288 ms','220720 / 32','Runtime proof incomplete'],['Mean ITL ↓','17.138 ms','220909 / 32','MNNVL repeat'],['Joint SLA ↑','100% · many ties','N32–36','Does not rank capacity']],widths=[2.3,3.0,2.5,3.8],row_h=.86,size=18)
s.text('An observed extreme is not a confidence interval or an official score.',1.0,6.12,11.4,.65,22,GRAY);s.end()
# 27
s=slide('Appendix · exact settings behind the frontiers', 'The best H200 candidate uses the same selected worker layout as the H100 combo, but it adds DeepGEMM only to prefill and operates at a different load. Both use the official FP8 checkpoint and reviewed BF16 KV allocation, with dense decode graph sizes from one through 64. Round-robin routing and the same NIXL descriptor patch remain. Backend names in config are requests; terminal logs and backend-rank initialization establish that the intended runtime actually started.', 'Submitted worker scripts; resolved ServerArgs; all-rank backend reviews')
table(s,['SETTING','H200 24291','H100 221058'],[['Prefill / decode','2×TP4/EP1 → TP8/EP8','Same layout'],['Prefill chunk','4,096 tokens','4,096 tokens'],['Prefill MoE runner','DeepGEMM','Auto'],['Decode attention / collective','FlashInfer / MNNVL','FlashInfer / MNNVL'],['Decode CUDA graph sizes','1–64, dense','1–64, dense'],['Concurrency / KV','N56 / BF16','N50 / BF16']],widths=[4.6,3.5,3.5],row_h=.63,size=17)
s.end()
# 28
s=slide('Appendix · topology failures remain separate', 'In the first 17-job wave, only eight layouts produced measurements and nine failed before a useful benchmark. We corrected the earlier mistake of treating terminal scheduler states as completed measurements. Recovery addressed environment, registration, slow path warmup and FP8 block alignment. The final usable-layout accounting kept 14 compatible originals and three explicitly named EP2 replacements separate from the incompatible TP8/EP1 originals. No failed original receives a replacement result under its name.', 'Historical topology review; recovery records; prior 17-layout presentation')
bullets(s,[('Initial wave','8 layouts measured; 9 failed before a usable benchmark.'),('Recovery work','Fix container launch, worker registration and every P/D warmup path.'),('Keep configuration identity','14 compatible originals + 3 distinct EP2 replacement layouts.')],gap=1.55,size=27);s.end()
# 29
s=slide('Appendix · what the benchmark actually measures', 'The synthetic serving workload exercises a fixed prompt and answer length; it is not the same dataset as the accuracy evaluation. The client sustains a concurrency target and streams output through the gateway. Workers and every prefill/decode path are warmed separately using different traffic before the official client warmup. Only the scored window feeds the reported metrics, following AIPerf accounting. Grace allows outstanding requests to settle; it is not another steady-state benchmark. Do not recompute goodput by blindly dividing completed requests by 120.', 'Qwen workload and addendum; normalized AIPerf configs')
bullets(s,[('Serving dataset','Synthetic prompts: 4,000 input tokens and 200 requested output tokens.'),('Closed-loop API traffic','Keep N requests in flight; each completion triggers a replacement.'),('Quality dataset is separate','Full-set MMLU-Pro / GPQA scoring checks retained model quality.')],gap=1.55,size=26);s.end()
# 30
s=slide('Appendix · the job history behind key decisions', 'These job identifiers make each research decision traceable without putting file packaging instructions into the presentation. The main H200 progression begins with 22197, 22219 and 22415, then uses backend comparisons at N52 and repeated N56 controls before the latest 24291 prefill trial. H100 has a fresh control pair, capacity tests and two final combo sweeps. A configuration version count is not a count of successful measurements or a measure of research quality.', 'Frozen presentation-data.json and terminal reviews')
table(s,['STAGE','H200 JOBS','H100 JOBS'],[['Original topology / PD','22197, 22219, 22415','220562, 220575'],['Backend tuning','23777, 23778, 23904, 23974','220720–220722'],['Matched runtime repeat','23973, 23975, 24174','220908, 220909'],['Load frontier','24131, 24175, 24190, 24235','221020, 221021, 221052, 221058'],['New prefill tests','24281, 24282, 24291','221151–221153 submitted']],widths=[3.3,4.4,3.9],row_h=.75,size=15)
s.text('Raw artifacts retain errors, cancellations, deployment failures and negative results.',1.0,6.31,11.3,.45,19,GRAY);s.end()
# 31
s=slide('Appendix · other branches and what they taught us', 'Early dense decode graphs and chunk4096 trials changed performance modestly at N48 and N52 before the later round-robin and backend work. DeepEP low-latency N52 reached 1,957.15 good tokens/s, below the emerging alternatives. DP-attention variants at N52 reached 2,549.20 and 2,538.08 in independent jobs, but N54 reached only 2,555.42 versus 2,634.03 for the MNNVL operating point. Original CUTLASS deployment produced no scored export. These results are historical observations with different controls over time, not a single uniformly matched ablation. Source-only ideas such as speculative decoding are not measured gains; losslessness and source compatibility must be established before expensive trials.', '23103; 23114; 23272; 23780/23859; 23934/23924; failed 23776')
table(s,['BRANCH','OBSERVED RESULT','LESSON'],[['Dense graphs / chunk4096','Early full N48/N52 trials','Retain in later controls'],['DeepEP low-latency','1,957.15 good tokens/s · N52','Not a new frontier'],['DP attention · two N52 jobs','2,549.20 / 2,538.08 tokens/s','Below combo frontier'],['DP attention · N54','2,555.42 vs MNNVL 2,634.03','Do not scale blindly'],['Original CUTLASS trial','No scored export','Deployment failure']],widths=[3.9,4.4,3.3],row_h=.74,size=17)
s.text('Source compatibility, deployment success and measured gains are different gates.',1.0,6.29,11.3,.48,19,GRAY);s.end()
# 32
s=slide('Discussion', 'Questions can focus on why the chosen worker balance helps, the NIXL descriptor repair, FP8 block geometry, phase-specific kernel effects, per-request latency accounting, or the limits of cross-platform estimation. The current H200 candidate still needs replication and official full-set accuracy evaluation. H100 and H200 remain separate measured systems. Background photographs are reference infrastructure imagery, not photographs of either contest installation. Asset attribution is stored in the deck metadata.',cover=False)
s.text('Questions?',.98,1.75,11.3,1.34,66,bold=True)
for i,(icon,label) in enumerate([('cpu','Parallelism and phase-specific kernels'),('network','KV transfer and cross-platform comparisons'),('timer','Goodput, latency and quality validation')]):
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
(OUT/'layout-validation.json').write_text(json.dumps(dict(slides=32,main_slides=24,appendix_slides=8,text_within_boxes=True,boxes_within_slides=True,distinct_backgrounds=32,english_only=True,raw_sla_checked=dict(job='24291',requests=len(a),passed=int(good.sum())),render_note='PDF and previews use the same drawing coordinates as PPTX; they are not an Office rendering.'),indent=2)+'\n')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf');thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25));p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(2000,math.ceil(len(thumbs)/4)*300),'#E2E7E8');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f"{i+1:02d} {outline[i]['title'][:68]}",fill=INK)
sheet.save(OUT/'Presentation_Overview.jpg',quality=93)
print(json.dumps(dict(output=str(OUT),slides=len(prs.slides),main_slides=24,appendix=8)))

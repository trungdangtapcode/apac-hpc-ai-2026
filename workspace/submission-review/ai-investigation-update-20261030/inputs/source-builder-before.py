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
OUT = WORK/'submission-review/ai-reasoning-update-20261030/slides'
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
prs.core_properties.subject = 'Research update through 30 October 2026; H200 and H100 measured separately'
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
    spec=PLAN[len(prs.slides)]
    role='Reasoning role: '+spec['reasoning_stage']+'. '
    record=TRANSCRIPTS.get(spec['number'])
    if record:
        d=record['en']
        notes=d['purpose']+'\n\n'+d['visual']+'\n\n'+'\n'.join(label.title()+': '+d['tradeoff'][label] for label in ['observation','hypothesis','conclusion','unknown'])+'\n\nSpeaking brief: '+d['brief']+'\n\n'+'\n'.join(d['reading'])
    result=Slide(spec['title'],notes=role+readable_notes(notes)+('\n\nResearch sources: '+source if source else ''),**kwargs)
    if not kwargs.get('cover'):
        result.text(spec['reasoning_stage']+'  |  '+spec['hardware'],.87,1.02,11.6,.28,11,GRAY)
    result.text(spec['hardware'],4.7,7.08,7.2,.24,9,GRAY if not kwargs.get('dark') else '#D5DEDF')
    return result


def table(s,headers,rows,widths=None,y=1.55,row_h=.63,size=18):
    widths=widths or [11.6/len(headers)]*len(headers)
    x0=.86
    s.rect(x0,y,11.6,.54,INK)
    for i,row in enumerate([headers]+rows):
        yy=y+(0 if i==0 else .63+(i-1)*row_h)
        x=x0
        if i:s.line(x0,yy+row_h-.08,12.46,yy+row_h-.08,PALE,.8)
        for val,w in zip(row,widths):
            s.text(str(val),x+.12,yy+.10,w-.24,.40 if i==0 else row_h-.19,13 if i==0 else size,WHITE if i==0 else INK,bold=i==0)
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



PLAN=json.loads((OUT.parent/'reasoning-plan.json').read_text())['slides']
OLD=json.loads((OUT.parent/'inputs/transcript-source-before.json').read_text())['slides']
TRANSCRIPTS={r['slide']:r for r in json.loads((WORK/'reports/ai-final-report-20261030/reasoning-transcript.json').read_text())}
def oldnotes(n):return OLD[n-1]['notes']


# 01 — RQ1–4 · Problem & constraints
s=slide('Research questions', 'Explain how the team reasoned through four questions using the owner-supplied seven-step cycle: problem and constraints; baseline observations; bottleneck evidence; prioritisation and hypothesis; intervention and measurement; causal limits; conclusion and next iteration. The selected service is not a claim of universal optimality or official quality acceptance.', 'Problem-driven presentation plan; retained research journey',cover=True,dark=True)
s.text('QWEN3-235B · 16 H200 · TWO NODES',.9,.8,11.5,.45,19,ORANGE,bold=True)
s.text('How do we reason about\na fast Qwen service?',.9,1.55,11.6,1.5,40,WHITE,bold=True)
for x,y,label,body in [(1.0,3.45,'RQ1 · DISTRIBUTION','Which layout is feasible and useful?'),(7.0,3.45,'RQ2 · LIMITS','What does the evidence identify?'),(1.0,4.8,'RQ3 · INTERVENTIONS','Which changes improve goodput?'),(7.0,4.8,'RQ4 · ROBUSTNESS','Do results survive remeasurement?')]:
 s.text(label,x,y,5.2,.35,15,ORANGE,bold=True);s.text(body,x,y+.47,5.2,.75,22,WHITE)
s.text('Problem → observe → diagnose → hypothesise → intervene → test → decide',1.,6.37,11.5,.5,16,'#D5DEDF');s.end()


# 02 — RQ1 · Problem & constraints
s=slide('Optimise useful throughput under a latency gate', 'Each request must satisfy both time to first token at most 3,000 ms and mean inter-token latency at most 20 ms. At least 90% of evaluated requests must meet both. Errors remain in the denominator. Goodput is qualifying requests per second; multiplying by 200 gives the good output tokens per second reported here. Mean latencies alone do not establish the per-request gate.', 'Qwen task rules and 25 September addendum')
s.text('Qwen3-235B FP8 · 2 nodes × 8 H200',.94,1.43,11.4,.52,26,bold=True)
s.text('Cold prefixes · 4,000 input tokens → 200 requested output tokens',.96,2.04,11.3,.32,17)
table(s,['METRIC','WHAT IT MEASURES','LIMIT / UNIT'],[['TTFT ↓','Wait for the first token','≤ 3,000 ms'],['Mean ITL ↓','Interval between tokens','≤ 20 ms'],['Joint SLA ↑','Requests meeting both limits','≥ 90%'],['Goodput ↑','Qualifying service throughput','req/s × 200 = good tokens/s']],widths=[2.2,5.6,3.8],y=2.46,row_h=.65,size=20)
s.text('Per-request pass/fail decides goodput. Errors count against the service.',.99,6.12,11.5,.57,23,ORANGE)
s.end()


# 03 — RQ1 · Baseline & observation
s=slide('Topology search established the serving layout', 'We explored the balance between replication and parallelism. The original 07 and 09 names were identifiers, not software versions. The 07 configuration used four TP2 prefill workers and two TP4/EP4 decode workers. The next layout widened prefill to TP4. The selected split also widened decode to TP8/EP8. The completed recovery ledger counts 14 measured original layouts plus three measured EP2 replacements. Initial startup, FP8-alignment and transport failures remain separate from usable measurements. A replacement is a changed configuration, not a retroactive pass for its original. These initial operating points differ in load and transport history.', '22197; 22219; 22415; prior topology campaign')
table(s,['LAYOUT','PREFILL','DECODE','N','GOOD TOKENS/S'],[['07','4 × TP2','2 × TP4/EP4','32','1,297.02'],['09','2 × TP4','2 × TP4/EP4','40','1,666.01'],['Selected split','2 × TP4','1 × TP8/EP8','48','1,912.30']],widths=[2.3,2.5,3.0,.8,3.0],row_h=.86,size=19)
s.text('14 original layouts + 3 EP2 replacements = 17 usable configurations',.99,5.17,11.4,.60,25,bold=True)
s.text('Require compatible FP8 shards and valid P/D responses. Loads differ across rows; no one-factor topology ranking is established.',1.0,6.04,11.3,.83,18,GRAY)
s.end()


# 04 — RQ1 · Conclusion from topology evidence
s=slide('Separate prompt processing from token generation', 'The selected layout dedicates the first node to two prefill workers, each using tensor parallelism four and expert parallelism one. The second node runs one decode worker using TP8 and EP8. Requests enter through the gateway; NIXL transfers KV state between the roles. Tensor parallel groups stay within a node. Round-robin selects a prefill worker; all generated tokens are produced on the decode side.', 'Same 2xTP4/EP1 prefill and TP8/EP8 decode layout in current incumbents')
s.text('NODE 0 · PREFILL',.95,1.45,5.1,.5,23,bold=True);s.text('NODE 1 · DECODE',7.55,1.45,5.0,.5,23,bold=True)
for y,label in [(2.38,'P0 · TP4 / EP1'),(4.38,'P1 · TP4 / EP1')]:
 s.rect(.95,y,4.5,1.35,None,GRAY);s.text(label,1.18,y+.17,4.0,.43,23);s.chips(1.42,y+.84,4,.32,ORANGE,.40)
s.rect(7.55,2.38,4.8,3.35,None,GRAY);s.text('D0 · TP8 / EP8',7.86,2.70,4.2,.50,25);s.chips(8.05,3.73,4,.38,INK,.49);s.chips(8.05,4.66,4,.38,INK,.49)
s.arrow(5.48,3.01,7.45,3.01,ORANGE);s.arrow(5.48,4.98,7.45,4.98,ORANGE);s.text('KV state\nNIXL',5.66,3.60,1.75,.96,19,ORANGE)
s.text('Keep TP within each node; specialise prefill and decode independently.',.98,6.10,11.4,.43,20)
s.text('Measured usable layout; differing loads prevent a one-factor topology claim.',.98,6.62,11.4,.30,14,GRAY)
s.end()


# 05 — RQ1 · Observation → validity check
s=slide('Validity before ranking', 'Topology feasibility includes model loading, pair warmup, correct transfer and valid outputs, not just worker readiness. In a heterogeneous-TP recovery branch, prefill P8 TP8/EP2 to decode D8 TP4/EP4, 22271 loaded workers but timed out in pair warmup at 360 seconds before any benchmark. Later patched 22294 completed warmup and measured; this branch is not the selected two-TP4-prefill layout. Other failures included FP8 alignment and port collision; do not attribute every failed topology to descriptors. The 17 usable configurations are evidence for a feasible layout decision, not a count of successful original attempts.', 'TOPOLOGY_REVIEW.md; 22271 pair-warmup.log; 22294; recovery ledger')
table(s,['CHECK','WHAT THE OBSERVATION ESTABLISHES'],[['Model worker loaded','Weights fit and process becomes ready'],['Pair warmup: 22271','Timeout at 360 s; no benchmark result'],['Transfer and response','Must validate both P/D paths and output'],['Topology decision','Compare usable measurements; retain failures']],widths=[4.,7.6],row_h=.83,size=20)
s.text('A process being ready is not evidence that requests can complete.',1.,5.98,11.3,.75,25,ORANGE,bold=True);s.end()


# 06 — RQ2 · Bottleneck analysis
s=slide('Profile the deployed interaction', 'Job 24819 repeats the winning N58 deployment, then collects a separate N48 diagnostic: 425 successful requests and 16 sealed nonempty rank traces. Decode named HPC group GEMM accounts for 21.642%, MNNVL allreduce/RMSNorm 23.479% and FlashInfer paged attention 15.064% of summed recorded kernel duration. They are descriptive sums, not a partition of end-to-end wall time or predicted speedups. Old controller parse/stop errors remain recorded; actual trace coverage is checked separately. The new profiler response fix is deployed only in later derived bundles.', '24819 sealed traces; H200_PROFILE.md; observability correction')
table(s,['DECODE COMPONENT','SUMMED KERNEL TIME','RESEARCH QUESTION'],[['HPC group GEMM','21.64%','MoE implementation'],['MNNVL collective / norm','23.48%','Communication strategy'],['FlashInfer attention','15.06%','Phase-specific backend']],widths=[4.4,3.2,4.0],row_h=.88,size=20)
s.text('Select the next hypothesis from traces, logs and matched outcomes.',1.0,5.47,11.3,.76,25,ORANGE)
s.text('N64 later shows TTFT-only misses; queue / prefill / transfer causes remain unseparated.',1.0,6.44,11.3,.43,16,GRAY);s.end()


# 07 — RQ2 · Prioritisation & hypothesis
s=slide('Prioritisation', 'The historical cold P/D warmup failure motivated inspecting SGLang NIXL heterogeneous-TP descriptor preparation. Source enumerated the whole reserved KV pool; representative geometry gave about 403.8 million source entries per rank, although one 4000-token request required only 188 coalesced ranges. This is a source-level setup-work signal aligned with a pre-score failure, not a timed proof that metadata was the dominant bottleneck. The narrow intervention retained weights, precision, head mapping and notifications. Bandwidth, KV layout and scheduler effects were not experimentally ruled out. The diagnosis applies to that recovery branch, not a claim that the retained N64 system is still bottlenecked by descriptor setup. Detail and actual end-to-end limits are in backup slides24–25.', 'nixl-ondemand/README.md; nixl-ondemand.patch; metadata.json; geometry-test.json;22271')
table(s,['HYPOTHESIS','WHY PRIORITISE / WHAT IS MISSING'],[['Descriptor setup work','Whole-pool enumeration visible in source'],['Request-scoped descriptors','Remove irrelevant work; keep KV mapping'],['Bandwidth / scheduling / layout','Possible alternatives; not excluded by profiling'],['Expected effect','Reach usable transfer; speedup not yet quantified']],widths=[4.0,7.6],row_h=.82,size=19)
s.text('Choose the narrowest source-supported intervention—not an assumed bottleneck.',1.,6.03,11.3,.88,23,ORANGE);s.end()


# 08 — RQ3 · Hypothesis → intervention
s=slide('Backend combinations matter', 'At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.', '23777; 23778; 23904; 23974')
table(s,['H200 · N52','JOB','GOOD TOKENS/S','SLA'],[['FlashInfer decode only','23777','2,440.39','98.947%'],['MNNVL decode only','23778','2,592.16','99.007%'],['MNNVL fresh control','23974','2,594.03','99.009%'],['MNNVL + FlashInfer','23904','2,631.09','99.022%']],widths=[4.4,1.5,3.2,2.5],row_h=.77,size=20)
s.text('Combine attention and collective tuning; measure the combination directly.',.99,6.13,11.3,.64,24,ORANGE);s.end()


# 09 — RQ3 · Matched measurement → causal limits
s=slide('The N60 gain survives an independent deployment', 'Fresh auto-decode control 24912 versus HPC-Ops decode repeat 24913, both DeepGEMM prefill chunk8192 at N60. Goodput rises 5.295%, first-token latency rises 125.335 ms and ITL falls 1.644 ms. The original treatment 24738 scored 2990.151; its independent repeat scores 2989.175, only 0.033% lower. This reproduces the interaction rather than establishing a universal HPC-Ops effect. Runtime, raw per-request SLA, short nonregression and 12 long checks pass; full organiser quality remains open.', '24912/24913 full reviews; 24738 original treatment')
table(s,['METRIC','AUTO CONTROL','HPC-OPS REPEAT'],[['Good tokens/s ↑','2,838.853','2,989.175'],['Mean TTFT ↓','822.292 ms','947.627 ms'],['Mean ITL ↓','16.579 ms','14.934 ms'],['Joint SLA ↑','98.7599%','98.8178%']],widths=[3.5,4.05,4.05],row_h=.72,size=22)
s.text('16 H200 · full N60 · 24912 → 24913: +5.30%; repeat differs by 0.033%',.99,6.16,11.3,.62,20,ORANGE,bold=True);s.end()


# 10 — RQ3 · Intervention & full measurement
s=slide('H200: the N62-to-N64 step survives a full repeat', 'Fresh equally observed full N62 control 25365 versus full N64 candidate 25366 improves1.082867%. Independent N64 deployment 25373 differs from the source by−0.013634%; the two-run mean is3044.282165. Same serving topology, precision, transport and observation; source operational bytes differ only in load/provenance. Same sampled GPU UUID sets limit hardware diversity. Two runs do not establish a confidence interval or a global optimum.', '25365/25366 matched full proof; 25373 replication and telemetry')
table(s,['FULL 60 / 120 / 30','N62 CONTROL','N64 SOURCE','N64 REPEAT'],[['Good tokens/s','3,011.875','3,044.490','3,044.075'],['Joint SLA','98.7227%','98.6330%','98.6323%'],['TTFT mean · ms','1,037.630','1,110.463','1,113.240'],['ITL mean · ms','14.958','15.003','14.993'],['Errors / cancellations','0 / 0','0 / 0','0 / 0']],widths=[3.8,2.6,2.6,2.6],row_h=.70,size=19)
s.text('N64 +1.083% repeats; N68 short +2.27% shrinks to +0.083% full.',1.0,6.35,11.3,.43,22,ORANGE,bold=True);s.end()


# 11 — RQ3 · Evidence & unresolved cause
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



# 12 — RQ3 · Evidence → keep or reject
s=slide('Objective-based decisions', 'These are separate trials on separately identified platforms, not a cross-GPU ranking or one shared control. H200 prefill cache27378 improves0.240921% against27376, below the prospective1% useful-gain gate, with worse p95TTFT. H200 sparse graphs27510 reduce per-rank capture memory1.15 to0.36GB but goodput loses0.370208% against earlier27376; generated engine seeds and time/instrumentation differ. H100 N54 decode FA3 versusFlashInfer222027/222028 reducesTTFT118.922ms but raisesITL0.773ms and loses0.812% goodput. Retain the previous setting in each tested arm. A resource proxy or faster first token is not the end-to-end objective.', '27376/27378;27510;H100222027/222028')
table(s,['INDEPENDENT TRIAL','ATTRACTIVE METRIC','SERVICE RESULT'],[['H200 · prefill cache','Mean TTFT improves','Goodput +0.24%; below 1% gate'],['H200 · sparse graphs','Capture 1.15 → 0.36 GB/rank','Goodput -0.37%; retain dense'],['H100 · FA3 decode','TTFT -118.9 ms','Goodput -0.81%; retain FI']],widths=[3.5,3.9,4.2],row_h=1.01,size=18)
s.text('Decision: keep the setting that improves qualifying service—not a proxy alone.',1.,5.94,11.3,.80,23,ORANGE);s.end()


# 13 — RQ3 · Failed hypothesis → revised test
s=slide('EAGLE3: follow the failed hypothesis through its repairs', 'The all-worker EAGLE3 attempt25948 failed the joint latency gate. Moving the draft to decode only aimed to recover TTFT, but25988 first failed a validator that applied draft KV-region counts to target-only prefill. The role-aware validator repair preserved that failure. Decode-only25998 then passed its short protocol but lost4.74% against its own target-only control. A distinct later one-step/top-k1/two-draft-token full arm27238 passed at2971.628430 versus26949 at3034.761104, losing2.080318%. Low logged acceptance is descriptive, not a causal timing breakdown. Close each tested arm; functional draft transfer alone does not establish speedup or official accuracy.', '25948;25988 role-aware KV repair;25947/25998 short review;26949/27238 full shallow review')
table(s,['STAGE','OBSERVATION','LESSON / DECISION'],[['All-worker draft','Joint latency gate fails','Placement matters'],['Decode-only first attempt','Wrong KV validator rejects','Repair tooling; retain failure'],['Decode-only retry','Short pass; goodput -4.74%','No promotion'],['Shallow full-protocol trial','Full pass; goodput -2.08%','Close tested arm']],widths=[3.8,4.1,3.7],row_h=.78,size=18)
s.text('Attempt → diagnose → repair → remeasure → reject an unhelpful optimization.',1.0,6.23,11.3,.53,21,ORANGE);s.end()



# 14 — RQ4 · Reproducibility & selection
s=slide('Reproduction', 'Historical N64 jobs25366/25373/25487 are three full measurements with mean3044.400475 good output tokens/s. The independent25373 deployment differs from25366 by-0.013634%. Later native26766 is a separate runtime series at3045.501509; do not pool it as a fourth identical historical replicate. Highest complete local27378 is3048.446289, but its cache improvement is only0.240921% versus its own fresh27376 control. This does not beat the prospective1% useful-gain gate. Same sampledGPUUUIDsets limit hardware diversity. Official full-set quality remains unknown; original portable failed jobs remain failed.', '25366/25373/25487;26766;27376/27378')
table(s,['EVIDENCE','OBSERVATION','WHAT IT SUPPORTS'],[['Three full N64 runs','Mean 3,044.40 good tokens/s','Historical repeated operating point'],['New N64 deployment','Differs by -0.0136%','Repeatability in sampled environment'],['Later native runtime','3,045.50; separate series','Similar level, not pooled repeat'],['Isolated cache high','3,048.45; matched gain +0.24%','Not a useful confirmed replacement']],widths=[3.65,3.95,4.0],row_h=.83,size=18)
s.text('Select on comparable repeat evidence; a larger isolated number is insufficient.',1.,6.15,11.3,.57,22,ORANGE);s.end()


# 15 — RQ4 · Robustness & confounder checks
s=slide('Appendix · diagnose performance drift with controlled cells', 'The question was why historical full N64 averaged3044.400475 while a newer short control was about2560. Actual ServerArgs revealed changed prefill graph policy and max-running-request cap, plus harness/observation differences. We froze an exact legacy operational replay and modern full controls isolating graph and admission; a later completed factorial did not establish a single useful cause. Valid legacy replay26313 scored2830.923547, while native26766 reproduced3045.501509. Neither simply restoring a flag nor changing launcher can be credited causally. Keep lower observations and comparable protocol labels rather than select only the larger peak.', 'Incumbent recovery plan;26313 legacy full result;graph/admission factorial;26766 native full review')
table(s,['OBSERVATION / TEST','WHAT WAS HELD OR CHANGED','RESULT'],[['Historical full N64','Replicated original operating point','Mean 3,044.40'],['Later control','Short protocol + graph/cap drift','About 2,560; different'],['Exact legacy full replay','Old operational bytes retained','2,830.92; valid lower run'],['Modern controlled cells','Isolate graph and request cap','No single useful cause'],['Native full recovery','Source/KV/output gates retained','3,045.50; separate series']],widths=[3.6,4.9,3.1],row_h=.67,size=17)
s.text('Inspect effective settings → isolate confounders → preserve unresolved variation.',1.0,6.34,11.3,.51,20,ORANGE);s.end()



# 16 — RQ4 · Frozen forecast → held-out evidence
s=slide('Cross-platform forecast', oldnotes(19)+' '+oldnotes(20), 'H100221052/221058;H20023904/23973/23975/24174;frozenforecast;held-out24272')
table(s,['STEP','RECORDED EVIDENCE','BOUNDARY'],[['Same-combo N52 anchor','H200/H100 = 1.188096805','One configuration and load'],['Frozen H200 N50 forecast','2,642.244 good tokens/s','Recorded before result'],['Measured H200 N50','2,601.629; error -1.5371%','Within team-set ±2% tolerance'],['Uncertainty check','Outside earlier sensitivity range','Model error had been omitted']],widths=[3.55,4.25,3.8],row_h=.84,size=18)
s.text('Useful local check; no universal H100-to-H200 conversion is established.',1.,6.13,11.3,.66,23,ORANGE);s.end()


# 17 — RQ4 · Quality boundary
s=slide('Latency acceptance is separate from model accuracy', 'Full N64 26766 passes actual runtime, fixed workload and request-level latency checks with 98.580442% joint success. The local output suite passes 7/8 without new regression and retrieval 12/12. These small checks do not establish at least 99% of the organiser reference score on official full-set model-quality benchmarks. FP8 weights and BF16 activation/KV are retained, with no quantized KV or speculative decoding in the selected primary. Official accuracy and organiser re-verification remain open. Do not describe this as an official ranking or contest acceptance.', '26766 full gate; official Qwen rules and goodput clarification')
for i,(title,value,detail) in enumerate([('Service SLA','98.580%','Both limits, every request'),('Local sanity','7/8 + 12/12','No new output regression'),('Official quality','Not verified','At least 99% of reference')]):
 x=.96+i*4.16;s.text(title,x,1.73,3.72,.65,26,bold=True);s.text(value,x,2.91,3.74,.85,34,ORANGE,bold=True);s.text(detail,x,4.18,3.73,1.12,21)
s.text('Preserve the model. Verify quality independently of serving speed.',1.0,6.07,11.4,.60,24);s.end()



# 18 — RQ4 · Real replay & failure analysis
s=slide('A real replay can invalidate a static deployment claim', 'Static, mock and raw-reader tests passed before the portable GPU entry was exercised. Real27136 completed both semantic paths and the official client, then failed because AIPerf0.12 placed exports in an immediate child directory. The first reader repair handled that layout. Real27145 completed the GPU client but the summary still failed because canonical /scratch/home and lexical /home paths were mixed. Canonicalizing the input root fixed the second defect. Actual zero-GPU compute27152 then reproduced the original alias exception and passed both corrected readers on both real datasets. Original FAILED scheduler states remain; recovered raw27145 score3055.330517 is not a whole-allocation successful repeat. No new GPU run was purchased just to test that exact tail.', '27136 nested export failure;27145 canonical alias failure;27152 actual compute reader verification')
table(s,['STEP','WHAT HAPPENED','WHAT CHANGED'],[['Static / mock checks','Passed','Real deployment still unproven'],['Real portable GPU replay','Client finishes; nested path fails','Resolve export namespace'],['Second real replay','Client finishes; alias summary fails','Canonicalize input root'],['Compute replay','Both real datasets pass','Repair proved; failures kept']],widths=[3.3,4.6,3.7],row_h=.79,size=17)
s.text('Preserve the failed run, correct the claim, and test the smallest exact repair.',1.0,6.24,11.3,.54,21,ORANGE);s.end()



# 19 — Conclusion · Answer the research questions
s=slide('Conclusions', 'Answer the research questions with explicit evidence boundaries. RQ1: twoTP4prefills plusTP8EP8decode is a feasible useful measuredH200 layout, not a globally optimal topology. RQ2: source-level metadata waste and descriptive GPU work/tails guide tests, but no complete causal time decomposition identifies one universal bottleneck. RQ3: matchedN60HPC-Ops interaction and fullN62toN64 gains support retained settings; cache/graphs/FA3 and speculative trials show proxy gains need not help goodput. RQ4: historicalN64 repeatedmean3044.400475 and separate native26766 support an operating level, while lower replays, limited hardware diversity, incomplete quality and failed portable finalisation limit robustness. No new measurement or organiser acceptance is implied.', 'Four research questions; matched full runs; independent reviews')
table(s,['QUESTION','SUPPORTED DECISION','STILL LIMITED'],[['RQ1 · GPU distribution','Keep 2 × TP4 prefill + TP8/EP8 decode','Not a global topology optimum'],['RQ2 · Performance limits','Use source, profiles and request tails','No full causal time breakdown'],['RQ3 · Useful interventions','Keep matched, repeated goodput gains','Proxy metrics can move oppositely'],['RQ4 · Robustness','Retain repeated N64 operating point','Quality and full portable replay open']],widths=[3.25,4.6,3.75],row_h=.88,size=18)
s.text('Our contribution is a justified sequence of decisions—not only a score.',1.,6.28,11.3,.60,24,ORANGE,bold=True);s.end()


# 20 — Conclusion & next iteration
s=slide('What the evidence supports next', 'The selected primary remains target-only N64 with its replicated historical level, rather than the largest isolated numeric point. The cache, request cap and transfer-polling arms do not demonstrate a useful gain. Full shallow EAGLE loses. Native compile needs a proven RoPE/KV compatibility remedy before another compiled model attempt. Completed sparse compile-off graph27510 passes at3029.861122 good tokens/s,0.370208% below27376; lower capture memory did not improve throughput. Retain dense graphs. C++ CPU fixtures do not establish full model integration. Official full-set accuracy and a complete post-repair portable end-to-end run remain open. These are research conclusions, not a claim that more work was scheduled. Background photographs are reference infrastructure, not contest installation photographs.', 'Reviewed research journey through30October2026; exact source and terminal-run audits')
for i,(head,body) in enumerate([('Retain the reproduced service','Use N64; keep isolated peaks and losing trials visible.'),('Qualify each new execution path','Prove activation, KV transfer and output before scoring.'),('Complete independent validation','Verify official quality and the repaired portable deployment.')]):
 yy=1.56+i*1.49;s.text(head,1.0,yy,11.3,.61,29,ORANGE,bold=True);s.text(body,1.0,yy+.67,11.3,.66,23)
s.end()


# 21 — Backup · Environment
s=slide('One workload, two deployment systems', 'Both platforms provide two eight-GPU nodes, but they are not interchangeable experimental environments. Firmus uses H200, Slurm and Enroot; NSCC ASPIRE 2A+ uses H100 80GB, PBS and Singularity. We stage the same serving and client image artifacts and official FP8 checkpoint. CPU, driver, network, launcher, node cache and timing can still differ. A hardware-specification ratio is not a performance conversion.', 'Qwen rules; NSCC asset contract; matched-anchor audit')
table(s,['','FIRMUS','NSCC ASPIRE 2A+'],[['Allocation','2 × 8 H200','2 × 8 H100 80GB'],['Scheduler','Slurm','PBS'],['Container launcher','Pyxis / native Enroot','Singularity'],['Serving / client','SGLang / AIPerf','Same staged image artifacts'],['Model','Qwen3-235B FP8','Same checkpoint']],widths=[3.1,4.25,4.25],row_h=.70,size=19)
s.text('Keep platform, topology, backend and load in every comparison.',.98,6.28,11.4,.52,23,ORANGE)
s.end()


# 22 — Backup · Compatibility mechanism
s=slide('FP8 block geometry constrains parallelism', 'A failed TP8/EP1 prefill deployment exposed a block-alignment constraint. The model MoE intermediate size is 1,536 and FP8 block width is 128. With EP1, MoE tensor parallelism eight produces 192-element partitions, which do not divide by 128. With EP2, effective MoE tensor parallelism is four, producing 384-element partitions. This retains all weights and experts. The TP8/EP2 replacement is a combined layout change, not an isolated TP speedup. Failure before benchmarking is not a measured throughput result.', 'Exact staged SGLang source; failed job 24282; corrected trial 24321')
for x,title,formula,nblocks,col in [(.98,'TP8 / EP1','1,536 ÷ 8 = 192',1,RED),(7.12,'TP8 / EP2','1,536 ÷ 4 = 384',3,INK)]:
 s.text(title,x,1.54,5.05,.6,30,col,bold=True);s.text(formula,x,2.54,5.1,.65,30)
 for i in range(nblocks):s.rect(x+i*1.63,3.70,1.52,1.0,ORANGE if nblocks==3 else INK);s.text('128',x+.34+i*1.63,3.97,.95,.5,25,WHITE)
 if nblocks==1:s.rect(x+1.65,3.70,.76,1.0,RED);s.text('64',x+1.78,3.99,.6,.4,20,WHITE)
s.text('Partial block → load failure',1.0,5.19,5.2,.85,24,RED);s.text('Three full blocks → compatible geometry',7.14,5.19,5.14,.85,24)
s.text('Compatibility is necessary; startup, SLA and output quality still need testing.',1.0,6.29,11.4,.45,19,GRAY)
s.end()


# 23 — Backup · Chronology as supporting evidence
milestones=[('Initial 07\nN32',1297.02),('Initial 09\nN40',1666.01),('PD split\nN48',1912.30),('FI + MNNVL\nN52',2631.09),('Prefill DG\nN56',2715.84),('DG + HPC\nN58',2938.63),('N60\nrepeated',2989.17),('N62\nrepeated',3022.55),('N64\n3 repeats',3044.40)]
def progression(fig,ax):
 x=np.arange(len(milestones));values=[r[1] for r in milestones]
 ax.bar(x,values,color=[GRAY]*3+[INK]*2+[ORANGE]*4,width=.65)
 for i,y in enumerate(values):ax.text(i,y+42,f'{y:,.0f}',ha='center',fontsize=11,fontweight='bold')
 ax.set_xticks(x,[r[0] for r in milestones],fontsize=10);ax.set_ylim(0,3400);ax.set_ylabel('Good output tokens/s');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
p=chart('h200-research-progression',progression)
s=slide('H200 journey: recover, specialise, then reproduce', 'The historical progression spans different loads and configurations, not a single cumulative causal ablation. We recovered the 16-GPU split and request-scoped NIXL transfer, combined FlashInfer attention with MNNVL, introduced DeepGEMM prefill, increased its chunk to 8192, and found an interaction with HPC-Ops decode. N58 and N60 treatment gains reproduce. N62 repeats at3022.034919/3023.072304; N64 repeats at3044.489701/3044.074628. Observation settings also differ across this historical journey; it is not one cumulative causal ablation.', 'Historical retained milestones; 24724/24737/24819; 24738/24913; 24915')
s.image(p,.78,1.40,11.8,4.68);s.text('Historical milestones · loads and runtime settings change across stages',1.0,6.32,11.3,.43,19,GRAY);s.end()


# 24 — Backup · Intervention & correctness
s=slide('Descriptor intervention', 'Source inspection found whole-pool heterogeneous-TP KV descriptor enumeration. The patch constructs source/destination descriptors for request pages and coalesces adjacent ranges while keeping partial-head token stride. Representative counts are about403.8million source entries per rank for the pool versus188coalesced entries for one contiguous4000-tokenTP8→TP4request; scopes differ.720CPUbyte-range equivalence cases pass, while geometry-test.json explicitly has realGPUtransportvalidationfalse. The patch retains weights/precision/head mapping/notifications and equal-TPpath. GPUresponse andend-to-end measurements are separate evidence in the nextslide.', 'nixl-ondemand/{README.md,nixl-ondemand.patch,metadata.json,geometry-test.json}')
for x,label,value,detail in [(1.0,'WHOLE RESERVED KV POOL','403.8 million','source entries / rank'),(7.0,'ONE 4,000-TOKEN REQUEST','188','coalesced range entries')]:
 s.text(label,x,1.64,5.25,.39,16,ORANGE,bold=True);s.text(value,x,2.35,5.2,1.06,43,bold=True);s.text(detail,x,3.67,5.2,.48,22)
s.text('720 CPU range-equivalence cases pass; real GPU transport is a separate check.',1.,4.85,11.3,.9,22)
s.text('Counts describe setup geometry, not bandwidth or an inference speedup factor.',1.,6.1,11.3,.65,22,ORANGE);s.end()


# 25 — Backup · End-to-end evidence & limits
s=slide('KV recovery evidence', 'Compare historical attempts in the same P8TP8EP2prefill toD8TP4EP4decode topology.22271 loaded workers, timed out in pairwarmup at360s and has noAIPerfscore. With the descriptorpatch22294 completed actualP/Dwarmup paths in0.68–0.70s/request after workerswere ready and fullN32 measured1422.96goodtokens/s,95.87%jointSLA,zeroerrors/cancellations. This establishes patchedpath feasibility. Without a successful unpatched benchmark, separately timed descriptorinitialisation orphase/networktelemetry, no throughput speedup or dominant cause is isolated. This branch is different fromselected2TP4prefillTP8decode. Do not compute360/.7 as an acceleration ratio becauseone observation isatimeout.', '22271/pair-warmup.log;22294/pair-warmup.log;22294/confirm/n32/artifacts/profile_export_aiperf.json')
table(s,['OBSERVATION','BEFORE · 22271','PATCHED · 22294'],[['Topology','Same heterogeneous-TP branch','Same heterogeneous-TP branch'],['Pair warmup','Timeout after 360 s','0.68–0.70 s / request'],['Full benchmark','Not reached; no score','N32: 1,422.96 good tokens/s'],['Joint SLA / errors','No scored result','95.87%; zero errors/cancels']],widths=[3.45,4.1,4.05],row_h=.85,size=18)
s.text('Feasibility demonstrated; descriptor-only end-to-end speedup not measured.',1.,6.14,11.3,.64,23,ORANGE);s.end()


# 26 — Backup · Platform-specific tradeoff
s=slide('H100 attention tradeoff', oldnotes(16)+' '+oldnotes(17), '222027/222028 matched fullH100N54pair;222048historicalpeak;225227freshcontrol')
table(s,['H100 · N54','FLASHINFER CONTROL','FA3 DECODE'],[['Good output tokens/s','2,420.945','2,401.284'],['Mean TTFT','713.199 ms','594.276 ms'],['Mean request ITL','18.214 ms','18.988 ms'],['Mean request latency','4,337.853 ms','4,372.813 ms']],widths=[4.1,3.75,3.75],row_h=.77,size=20)
s.text('First token arrives sooner; accumulated token gaps lower goodput by 0.81%.',1.,5.98,11.3,.71,22,ORANGE)
s.text('Separate H100 context: historical peak 2,433.02; fresh control 2,399.19.',1.,6.69,11.3,.28,13,GRAY);s.end()


# 27 — Backup · Cost hypothesis & confirmation
s=slide('Test the cost hypothesis, then reverse the order', 'Slow prefill loading motivated prefill-only checkpoint read-first experiments. In the first H100 full pair, scheduler walltime fell934 to759 seconds,18.737%, while goodput fell0.659%. Nodes and unknown cache state prevented a cold-storage causal claim. A predeclared reverse-order confirmation required at least10% walltime savings and at most2% lower goodput. Read-first770 versus off854 seconds saved only9.836066%; goodput changed-0.326388%. Close the unchanged branch below its cost gate instead of promoting the favorable first comparison. Separately, a static one-GPU locality probe saw no intersection between allowed CPUs and local NUMA CPUs; that did not establish full-serving bindings or a CPU bottleneck.', 'Startup-prefetch original and reverse-pair reviews; static locality222412')
table(s,['H100 FULL PAIR','FIRST ORDER','REVERSED ORDER'],[['Off / read-first walltime','934 / 759 s','854 / 770 s'],['Observed walltime saving','18.74%','9.84%'],['Goodput change','-0.66%','-0.33%'],['Prospective cost gate','At least 10% saving','Not met: no promotion']],widths=[4.8,3.4,3.4],row_h=.77,size=19)
s.text('Question → bounded pair → reverse check → close below the declared gate.',1.0,6.22,11.3,.57,21,ORANGE);s.end()



# 28 — Backup · Negative measured interventions
s=slide('Use source evidence to test one small hypothesis', 'Native source and actual runtime showed auto prefill collective selected TRT-LLM, not MNNVL. Changing only that selector activated MNNVL on all eight P ranks, but full27138 gained only0.109807%. Native tokenizer batching first passed exact-ID preflight on64 concurrent plus one single input, then two full wait settings gained0.192% and0.270%. These were source-supported trials, not proof of a CPU bottleneck. Prefill FlashInfer page1 lowered ITL but lost6.385% goodput. Cache, request-cap and polling tests also failed the prospective useful-gain gate. Each branch preserves control, actual activation, output gates and stopping decision.', '26949/26951/26953;27138 actual collective source/activation;27077;27365;27376/27378;27270/27272/27274')
table(s,['HYPOTHESIS AND CHECK','FULL OBSERVATION','DECISION'],[['Tokenizer IDs → two waits','+0.19% / +0.27%','Keep tokenizer off'],['Auto selected TRT-LLM → MNNVL','+0.11%; ranks verified','No promotion'],['Prefill radix → ChunkCache','+0.24%; p95 TTFT worse','Retain radix'],['Request cap / polling','+0.26% / negative','Retain defaults'],['Prefill FlashInfer, page 1','-6.39%; ITL lower','Retain FA3']],widths=[4.8,3.8,3.0],row_h=.65,size=18)
s.text('An active flag and a passing run still need a useful matched gain.',1.0,6.28,11.3,.51,22,ORANGE);s.end()



# 29 — Backup · Diagnostics versus full serving
s=slide('Appendix · profiles and source also close attractive detours', 'Architecture and kernel ideas were tested at the scope their evidence supported. H200 attention-DP plus DeepGEMM/DeepEP23780 scored2549.20 atN52, below the retained MNNVL point; several factors changed together, so no one-flag attribution follows. Representative H100 FP8 Triton probes lost to DeepGEMM in tested shapes. H100 SM budgets80/96/120 were mixed or below their consistency gate, so132 was retained without claiming a model gain. An LL-named NCCL kernel had been misread: actual TUNING logs showed Simple selection and a control already using it for large messages; the small0.2315% point did not justify promotion. Full Qwen compile later failed native RoPE; C++ tree CPU fixtures passed but did not establish serving speed. Unsupported model/hardware/library paths and flags without consumers stayed source findings, not benchmarks.', 'JOURNEY stages15,29-31;DeepGEMM representative probes;NCCL source correction;27383;27506')
table(s,['RESEARCH DIRECTION','EVIDENCE','DECISION'],[['Attention-DP package','2,549.20 at N52; coupled changes','No isolated flag claim'],['FP8 kernel alternatives','Representative Triton probes lose','Retain DeepGEMM'],['SM budgets / protocol forcing','Mixed gains; source correction','Keep defaults'],['Real-model torch.compile','RoPE / fused-KV assertion','No score; path blocked'],['C++ cache / unsupported APIs','CPU pass or source findings only','No serving claim']],widths=[4.0,4.8,2.8],row_h=.66,size=17)
s.text('A kernel name, a library headline or a CPU trace is a lead—not proof of speed.',1.0,6.35,11.3,.47,19,ORANGE);s.end()



# 30 — Backup · Exact deployment settings
s=slide('Appendix · the selected AI deployment is N64', 'The selected AI primary retains replicated N64. Real portable jobs27136/27145 completed both semantic routes and the official GPU client, then failed in result-reader path handling. Fixed readers passed compute-only27152 on both actual datasets; a whole-allocation end-to-end run after that repair is not claimed. Native FP8 target and BF16 activation/KV remain. H200 uses two TP4 DeepGEMM prefills, chunk 8192 and breakable prefill graphs, with one TP8/EP8 HPC-Ops decode, FlashInfer decode attention, MNNVL and dense decode graphs 1 through 64. Round-robin routing and all original fixed-workload goodput limits remain. H100 is a separate point, not an alternate device setting for the same result.', '26766 frozen worker/runtime; 25487 operational settings; staged portable deployment validation')
table(s,['SETTING','H200 SELECTED','H100 RETAINED'],[['Client concurrency','64','54'],['Prefill runner / chunk','DeepGEMM / 8192','HPC-Ops / 4096'],['Decode runner','HPC-Ops','HPC-Ops'],['Prefill / decode TP','4 + 4 / 8','4 + 4 / 8'],['Weights / activation / KV','FP8 / BF16 / BF16','FP8 / BF16 / BF16']],widths=[4.2,3.7,3.7],row_h=.65,size=19)
s.text('Both: TP8 / EP8 decode, FlashInfer + MNNVL, round-robin routing.',1.0,6.37,11.3,.49,19,GRAY);s.end()



# 31 — Backup · Fixed protocol & negative result
s=slide('Workload and chunking', oldnotes(29)+' '+oldnotes(30), '4000/200seed2026closedloop;26766/26768/26770 fullreviews')
s.text('Fixed 4,000 / 200 tokens · N64 · 60 s warmup / 120 s profile / 30 s grace',.97,1.53,11.4,.51,19,bold=True)
table(s,['CHUNK TOKENS','GOOD TOKENS/S','JOINT SLA','p95 TTFT'],[['8192','3,045.50','98.580%','1,311.69 ms'],['10240','3,034.09','98.524%','1,518.87 ms'],['12288','3,020.94','98.310%','1,624.12 ms']],widths=[2.8,3.2,2.5,3.1],y=2.36,row_h=.91,size=21)
s.text('Same workload and runtime; larger prefill chunks did not improve service.',1.,6.17,11.3,.67,23,ORANGE);s.end()


# 32 — Backup · Resource metric versus objective
s=slide('Appendix · sparse graphs save memory, not goodput', 'Actual27510 completed0:0 in13:15 on16H200 and passed independent full local gates. Twelve decode graph buckets replace1..64; all eight current ranks prove captures with compile off. Goodput3029.861122 is0.370208% below earlier control27376 at3041.119598. Mean/p95TTFT1102.404/1240.481ms improves, while mean/p95ITL15.136/15.324ms worsens. Capture memory drops1.15 to0.36GB per rank, but capture time only101.46-101.49 to95.98-96.05seconds. Native log units are not total VRAM. One earlier control, generated seed differences and candidate-only startup observation prevent a strong causal claim. Retain dense graphs; official accuracy remains unknown.', '27510 terminal raw/runtime/capture review;27376 prior control')
table(s,['DECODE GRAPH MEASURE','DENSE CONTROL','SPARSE CANDIDATE'],[['Capture buckets','64','12'],['Capture memory / rank','1.15 GB','0.36 GB'],['Capture elapsed time','101.46-101.49 s','95.98-96.05 s'],['Good output tokens/s','3,041.12','3,029.86'],['Mean request ITL','14.991 ms','15.136 ms']],widths=[4.6,3.5,3.5],row_h=.68,size=19)
s.text('A lower resource metric is useful only if the service objective improves.',1.0,6.38,11.3,.49,20,ORANGE);s.end()




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
(OUT/'layout-validation.json').write_text(json.dumps(dict(slides=32,main_slides=20,appendix_slides=12,text_within_boxes=True,boxes_within_slides=True,distinct_backgrounds=32,english_only=True,raw_sla_checked=dict(job='26766',requests=len(a),passed=int(good.sum())),render_note='PDF and previews use the same drawing coordinates as PPTX; they are not an Office rendering.'),indent=2)+'\n')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf');thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25));p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(2000,math.ceil(len(thumbs)/4)*300),'#E2E7E8');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f"{i+1:02d} {outline[i]['title'][:68]}",fill=INK)
sheet.save(OUT/'Presentation_Overview.jpg',quality=93)
print(json.dumps(dict(output=str(OUT),slides=len(prs.slides),main_slides=20,appendix=12)))

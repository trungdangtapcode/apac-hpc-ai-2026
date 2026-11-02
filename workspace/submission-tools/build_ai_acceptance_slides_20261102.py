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
OUT = WORK/'submission-review/ai-acceptance-update-20261102/slides'
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
prs.core_properties.title = 'TripleU — Qwen serving: engineering investigation and final verification'
prs.core_properties.author = 'VNUHCM - TripleU'
prs.core_properties.subject = 'Engineering investigation: constraints, hypotheses, interventions and evidence boundaries'
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
        notes=d['purpose']+'\n\n'+'\n'.join(k.replace('_',' ').title()+': '+v for k,v in d.get('reasoning',{}).items())+'\n\n'+d['visual']+'\n\n'+'\n'.join(label.title()+': '+d['tradeoff'][label] for label in ['observation','hypothesis','conclusion','unknown'])+'\n\nSpeaking brief: '+d['brief']+'\n\n'+'\n'.join(d['reading'])
    result=Slide(spec['title'],notes=role+readable_notes(notes)+('\n\nResearch sources: '+source if source else ''),**kwargs)
    if not kwargs.get('cover'):
        result.text(spec['reasoning_stage']+'  |  '+spec['hardware'],.87,1.02,11.6,.28,11,GRAY)
    
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
TRANSCRIPT_FILE=WORK/'reports/ai-final-report-20261030/investigation-transcript.json'
TRANSCRIPTS={r['slide']:r for r in json.loads(TRANSCRIPT_FILE.read_text())} if TRANSCRIPT_FILE.exists() else {}
def oldnotes(n):return OLD[n-1]['notes']




def panel(s,x,y,w,h,label,body=None,color=INK):
    s.line(x,y,x+w,y,color,2)
    s.text(label,x,y+.15,w,.47,18,color,bold=True)
    if body:s.text(body,x,y+.83,w,h-.84,20)

def arrow_chain(s,labels,y=2.4,x=.95,total=11.4,colors=None):
    gap=.35;cw=(total-gap*(len(labels)-1))/len(labels)
    for i,label in enumerate(labels):
        xx=x+i*(cw+gap);c=(colors or [INK]*len(labels))[i]
        s.rect(xx,y,cw,1.15,None,c,1.6);s.text(label,xx+.12,y+.24,cw-.24,.70,20,c,bold=True)
        if i<len(labels)-1:s.arrow(xx+cw+.04,y+.58,xx+cw+gap-.04,y+.58,GRAY)
    return cw


# 01 — Problem · success criterion
s=slide('Objective', 'The competition objective is qualifying throughput, not unrestricted tokens. Keep Qwen3-235B FP8, two nodes of eight H200, requested4000/200tokens and cold prefixworkload. EachrequestmustsatisfyTTFT≤3000msandmeanITL≤20msjointly;≥90%ofallrequests qualifyincludingerrorsindenominator. Officialmodelquality≥99%reference isseparateandunverified.', 'Qwenrules;officialGoodputclarification',cover=True,dark=True)
s.text('QWEN3-235B FP8 · 16 H200 · TWO NODES',.9,.72,11.5,.44,18,ORANGE,bold=True)
s.text('Fast tokens count only when\nrequests meet both latency limits',.9,1.39,11.6,1.55,36,WHITE,bold=True)
for x,label,value,unit in [(1.0,'FIRST TOKEN','≤ 3,000','ms per request'),(5.1,'TOKEN GAPS','≤ 20','ms mean ITL'),(9.0,'JOINT PASS','≥ 90%','of all requests')]:
 s.text(label,x,3.56,3.7,.35,15,ORANGE,bold=True);s.text(value,x,4.15,3.7,.73,34,WHITE,bold=True);s.text(unit,x,5.05,3.7,.47,17,'#D5DEDF')
s.text('Score = qualifying requests/s × 200 output tokens/request',1.,6.09,11.3,.67,23,WHITE);s.end()


# 02 — Contribution map · ownership and scope
s=slide('Ownership', 'Separateengineeringdecisionsfromteamimplementationandexperimentalfindings. Topology/TP/EP/loadselectionareengineeringchoices. RequestscopedheteroTPNIXLpatchisateamimplementationwhosevalidationestablishesfeasibilitynotisolatedspeedup. DeepGEMM/HPC-Ops/FlashInfer/MNNVLarereusedimplementations;ourcontrolledmeasurementandselectionarethecontribution. EarlycompatibilityandKVrecoveryareeligibilityworkonparticularbranches,notcausalproofeachlatergoodputincrementcamefromthem.', 'investigation-contributions.json;ownerfeedback')
for x,label,headline,detail in [(1.,'ENGINEERING DECISION','Divide the 16 GPUs','Feasible topology and load\nunder model and latency constraints'),(5.0,'TEAM IMPLEMENTATION','Change KV setup work','Request-scoped descriptors\nwith range and response checks'),(9.0,'EXPERIMENTAL FINDING','Test service tradeoffs','Reuse kernels; compare, repeat\nand reject unsupported gains')]:
 s.line(x,1.6,x+3.35,1.6,ORANGE,3);s.text(label,x,1.88,3.35,.66,14,ORANGE,bold=True);s.text(headline,x,2.79,3.35,1.0,25,bold=True);s.text(detail,x,4.,3.35,1.45,19)
s.line(1.1,5.69,12.1,5.69,GRAY,1)
s.text('Eligibility to benchmark',1.,5.96,4.4,.40,18,GRAY);s.arrow(5.05,6.13,7.0,6.13,GRAY);s.text('Controlled performance claims',7.2,5.96,5.2,.60,18,GRAY);s.end()


# 03 — Engineering decision · compare feasible layouts
s=slide('Topologytradeoff', 'QwenFP8compatibilityandKVmemorymakeeligibilityaninitialgate. MoreTPwidthsharesoneworkeracrossmoreGPUsbutreducesreplicasunderfixedbudget. Compareusableobservedlayouts07N32=1297.02;09N40=1666.01;selectedsplitN48=1912.30. Thesearehistoricaloperatingpointswithdifferentloadsandtransferhistory,notonefactorcausalranking.17usable=14original+3EP2replacements;failedoriginalsremainfailed.', 'topologyrecoveryledger;22197/22219/22415')
s.text('Selection gates',1.,1.48,4.1,.55,24,bold=True)
s.text('Feasible observations · different loads',5.85,1.48,6.3,.70,22,bold=True)
for i,(label,detail) in enumerate([('01 · Resource fit','Two nodes × eight H200'),('02 · FP8 compatibility','Supported TP / EP geometry'),('03 · Real P/D path','Request KV transfer completes'),('04 · Operating point','Full-run SLA and later repeats')]):
 y=2.38+i*.93;s.rect(1.,y,4.25,.70,None,ORANGE if i==3 else GRAY,1.1);s.text(label,1.15,y+.09,3.95,.28,15,ORANGE if i==3 else INK,bold=True);s.text(detail,1.15,y+.41,3.95,.25,13,GRAY)
for i,(name,layout,result) in enumerate([('07','P: 4 × TP2  |  D: 2 × TP4 / EP4','N32 · 1,297.02 good tokens/s'),('09','P: 2 × TP4  |  D: 2 × TP4 / EP4','N40 · 1,666.01 good tokens/s'),('Retained split','P: 2 × TP4  |  D: 1 × TP8 / EP8','N48 · 1,912.30 good tokens/s')]):
 y=2.34+i*1.17;s.text(name,5.85,y,6.1,.37,18,ORANGE if i==2 else INK,bold=True);s.text(layout,5.85,y+.40,6.3,.36,17);s.text(result,5.85,y+.82,6.1,.33,15,GRAY)
s.text('17 usable configurations inform a practical choice, not a matched global topology ranking.',1.,6.48,11.3,.42,16,GRAY);s.end()


# 04 — Engineering decision · retained architecture
s=slide('Separate prompt processing from token generation', 'The selected layout dedicates the first node to two prefill workers, each using tensor parallelism four and expert parallelism one. The second node runs one decode worker using TP8 and EP8. Requests enter through the gateway; NIXL transfers KV state between the roles. Tensor parallel groups stay within a node. Round-robin selects a prefill worker; all generated tokens are produced on the decode side.', 'Same 2xTP4/EP1 prefill and TP8/EP8 decode layout in current incumbents')
s.text('NODE 0 · PREFILL',.95,1.45,5.1,.5,23,bold=True);s.text('NODE 1 · DECODE',7.55,1.45,5.0,.5,23,bold=True)
for y,label in [(2.38,'P0 · TP4 / EP1'),(4.38,'P1 · TP4 / EP1')]:
 s.rect(.95,y,4.5,1.35,None,GRAY);s.text(label,1.18,y+.17,4.0,.43,23);s.chips(1.42,y+.84,4,.32,ORANGE,.40)
s.rect(7.55,2.38,4.8,3.35,None,GRAY);s.text('D0 · TP8 / EP8',7.86,2.70,4.2,.50,25);s.chips(8.05,3.73,4,.38,INK,.49);s.chips(8.05,4.66,4,.38,INK,.49)
s.arrow(5.48,3.01,7.45,3.01,ORANGE);s.arrow(5.48,4.98,7.45,4.98,ORANGE);s.text('KV state\nNIXL',5.66,3.60,1.75,.96,19,ORANGE)
s.text('Fits 16 GPUs; TP stays within each node',.99,6.11,5.7,.67,19,INK,bold=True)
s.text('Cost: transfer request KV between roles',6.50,6.11,5.8,.70,19,ORANGE,bold=True)

s.end()




# 05 — Technical contribution · observed transfer failure
s=slide('KVsymptom', 'EarlyheterogeneousTPbranchP8TP8EP2→D8TP4EP4isnotselectedtwoprefillTP4layout.22271modelworkersloadedbutpairwarmuptimedout360swithnoAIPerfexport. Locatesobservedfailurebeforesteady-statebenchmarking,notprovingwhichbootstrapcomponentcausedit. Sourceinspectvisiblemetadataenumerationbeforefirsttuningbandwidth/scheduler. OtherFP8orportfailuresareseparatebranches.', '22271/pair-warmup.log;TOPOLOGY_REVIEW.md')
arrow_chain(s,['Load model','Workers ready','P/D warmup','AIPerf score'],y=2.05,colors=[INK,INK,RED,GRAY])
s.text('Observed',1.,3.72,3.,.45,18,GRAY,bold=True);s.text('Timeout after 360 s',5.05,3.72,6.9,.70,31,RED,bold=True)
s.text('No scored request stream; no before-patch throughput result.',5.05,4.66,6.9,1.05,23)
s.text('Branch: TP8/EP2 prefill → TP4/EP4 decode. This is not the retained split.',1.,6.15,11.3,.75,18,GRAY);s.end()


# 06 — Technical contribution · intervention and checks
s=slide('KVintervention', 'SourceenumeratedwholeKVpoolforheterogeneousTPdescriptors;patchbuildsonlyrequestpagesandcoalescesadjacentbyterangeswhilepreservingheadoffsets,stride,notificationsandprecision. Representative403.8millionsourceentries/rankpoolvs188coalescedrangesforonecontiguous4000tokenrequestdifferinscope.720CPUrangeequivalencecasespass;fixtureexplicitlynotrealGPUvalidation. Nooldcodetimerprovesdominantbottleneckandbandwidth/layout/schedulingnotexcluded.', 'nixl-ondemand/README.md;nixl-ondemand.patch;metadata.json;geometry-test.json')
s.text('Prioritise source-visible setup work with a cheap correctness check.',1.,1.48,11.3,.67,23,INK,bold=True)
s.text('Before · reserved pool',1.,2.33,5.1,.55,22,bold=True);s.text('After · this request only',7.1,2.33,5.1,.55,22,bold=True)
for row in range(3):
 for col in range(7):
  x=1.1+col*.58;y=3.08+row*.41;s.rect(x,y,.44,.28,ORANGE if row==1 and col in [2,3,4] else PALE,GRAY,.65)
s.arrow(5.55,3.60,6.75,3.60,ORANGE)
s.rect(7.45,3.37,2.23,.56,ORANGE);s.text('Coalesce adjacent pages',7.1,4.13,5.1,.40,17,GRAY)
s.text('Pool source entries / rank',1.,4.72,5.1,.42,16,GRAY);s.text('403.8 million',1.,5.24,5.1,.76,34,bold=True)
s.text('Coalesced ranges / 4,000-token request',7.1,4.72,5.1,.61,16,GRAY);s.text('188',7.1,5.35,5.1,.69,34,bold=True)
s.text('720 CPU checks pass. Counts are not speedup; bandwidth and scheduling are not ruled out.',1.,6.38,11.3,.44,15,GRAY);s.end()



# 07 — Technical contribution · end-to-end evidence boundary
s=slide('KVvalidation', 'SamehistoricalheterogeneousTPbranch22271unpatchedtimedout360snobenchmark;patched22294pairwarmup.68–.70safterworkersreadyandfullN32goodtokens1422.96SLA95.87%zeroerrorscancels. Thisisfeasibilityevidenceinthepatchedrun,notcausaldescriptor-onlyspeedup;nosuccessfulunpatchedscoredcontrolorold/newinitializationtimer. Donotdivide360by.7toconverttimeouttospeedratio. Whyitmatters:onlyworkingpathsenterperformancecomparison.', '22271;22294pairwarmup;22294/confirm/n32/artifacts/profile_export_aiperf.json')
panel(s,1.,1.62,4.8,3.3,'BEFORE · 22271','Warmup timeout: 360 s\n\nNo benchmark score',RED)
panel(s,7.05,1.62,5.1,3.6,'PATCHED · 22294','Warmup: 0.68–0.70 s/request\nFull N32: 1,422.96 good tokens/s\n95.87% qualify; zero errors',INK)
s.text('Established',1.,5.45,3.,.43,17,ORANGE,bold=True);s.text('A usable patched serving path',4.1,5.45,7.8,.55,22,bold=True)
s.text('Not isolated',1.,6.14,3.,.43,17,GRAY,bold=True);s.text('Descriptor-only end-to-end speedup or sole cause',4.1,6.14,7.8,.70,20,GRAY);s.end()


# 08 — Experimental evidence · prioritise what to test
s=slide('Profilelimits', 'SeparateN48profile24819retains16ranktraces425requests. NamedGEMM21.642%,collectiveRMSNorm23.479%,FIattention15.064%ofsummedrecordedkerneldurationsarenotwalltimesharesorFLOPutilisation. SamejobN58deploymentrepeatisdistinctphase.N64requesttailprofilelater26766shows27TTFTmissesandzeroITL;nocorrelatedphasetimingprovesqueuevscomputevsKVtransfercause. Profileresourcekernelusagecommunicationhypothesesrequirematchedserviceexperiments.', '24819profile;26766requests;observabilityreview')
s.text('N48 diagnostic · summed kernel durations',1.,1.55,6.6,.60,22,bold=True)
for i,(label,value,color) in enumerate([('MoE group GEMM',21.642,INK),('Collective + norm',23.479,ORANGE),('Paged attention',15.064,GRAY)]):
 y=2.6+i*.95;s.text(label,1.,y,3.3,.42,18);s.rect(4.4,y+.06,value/25*2.1,.28,color);s.text(f'{value:.2f}%',6.7,y,1.2,.42,17)
s.line(8.35,1.55,8.35,6.3,GRAY,.8)
s.text('Choose a bounded test',8.7,1.55,3.6,.85,24,ORANGE,bold=True)
s.text('Supported decode backend\n\nHold serving setup fixed\n\nMeasure goodput and tails',8.7,2.80,3.6,2.95,21)
s.text('Profiles suggest directions; the next controlled test establishes value, not these percentages.',1.,6.28,11.3,.70,17,GRAY);s.end()


# 09 — Experimental method · hypothesis and control
s=slide('Controlledbackendtest', 'TestdecodekernelimplementationinteractionunderfullN60same16H200topologyFP8targetBF16activationKVDeepGEMMprefillchunk8192FlashInferdecodeMNNVLcollectivesandworkload60/120/30. Control24912autodecodeversusHPCOpsrepeat24913,intendedchangedecodeimplementation;independentoriginaltreatment24738supportsrepeat. Reusedkernelsnotteaminvention. Needactualbackendactivationandoutputchecks. Missingdedicatedhardware24913andseed/allocationvariabilitylimitcausalityspecificGPUkernelmechanism.', '24912/24913fullreview;24738;runtimeactivation')
s.text('Independent probe: can a supported decode choice raise qualifying throughput?',1.,1.52,11.3,.84,25,bold=True)
s.rect(1.,2.68,11.2,1.08,None,GRAY,1.3);s.text('HELD FIXED',1.15,2.85,2.1,.37,15,ORANGE,bold=True);s.text('Topology · FP8/BF16 · prefill DeepGEMM / 8192\nN60 · FlashInfer / MNNVL · full 60 / 120 / 30 protocol',3.1,2.84,8.7,.78,19)
panel(s,1.,4.35,4.8,2.0,'CONTROL · 24912','Auto decode implementation')
s.arrow(5.95,5.11,6.9,5.11,ORANGE)
panel(s,7.15,4.35,4.95,2.0,'CANDIDATE REPEAT · 24913','HPC-Ops decode implementation')
s.end()


# 10 — Experimental finding · matched result and repeat
s=slide('Backendresult', 'MatchedfullN60goodtokens2838.853→2989.175+5.295%;meanTTFT822.292→947.627ms+125.335worse;meanITL16.579→14.934ms-1.644better. OriginalHPCOpstreatment24738=2990.150791repeat24913diff−.033%. Supporttestedserviceconfigurationwithlatencytradeoff,notuniversalbackendorderorfinegrainedcausalkernelstory. Kernelprovidedbyruntimeauthors.', '24912/24913;24738;fullreview')
for x,label,before,after,delta,color in [(1.,'GOOD OUTPUT TOKENS/S','2,838.85','2,989.17','+5.30%',ORANGE),(5.1,'MEAN TTFT · ms','822.29','947.63','+125.34 ms',RED),(9.05,'MEAN ITL · ms','16.58','14.93','-1.64 ms',INK)]:
 s.text(label,x,1.64,3.6,.66,15,GRAY,bold=True);s.text(before+' →',x,2.65,3.6,.70,27,GRAY);s.text(after,x,3.62,3.6,.78,35,color,bold=True);s.text(delta,x,4.70,3.6,.62,23,color,bold=True)
s.line(1.,5.7,12.1,5.7,PALE,1);s.text('Independent candidate repeat: -0.033% from the original treatment',1.,6.00,11.3,.78,22,bold=True);s.end()


# 11 — Engineering decision · choose the operating load
s=slide('Loaddecision', 'Hypothesisraisingclientconcurrencyincreasesusefulpipelineworkuntiltailpenaltycounteracts. FullN62control253653011.875113→N64source253663044.489701+1.082867;repeat253733044.074628diff−.013634. MeanTTFTrises1037.630→1110.463ms,meanITL14.958→15.003. N68short+2.27%full+.083056belowgate1%. ChooseN64repeatablefulloperatingpointnotmonotonicloadoptimum,clientNnotdecodebatchorGPUcount.', '25365/25366/25373;fullN68pair')
for x,load,value,detail in [(1.,'N62','3,011.88','full control'),(5.1,'N64','3,044.49','full: +1.083%'),(9.,'N64 repeat','3,044.07','new job: -0.0136%')]:
 s.text(load,x,1.74,3.7,.55,26,ORANGE,bold=True);s.text(value,x,2.65,3.7,.77,31,bold=True);s.text('good output tokens/s',x,3.6,3.7,.40,16,GRAY);s.text(detail,x,4.3,3.7,.65,20)
s.rect(1.,5.46,11.2,.97,None,GRAY,1);s.text('N68: short test +2.27%',1.2,5.68,5.0,.50,21);s.arrow(6.5,5.96,7.2,5.96,ORANGE);s.text('full test +0.083% → stop',7.4,5.68,4.55,.50,20)
s.end()


# 12 — Experimental finding · request-level evidence
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





# 13 — Robustness · complete portable deployment
s=slide('Accepted deployment', 'Historical25366/25373/25487mean3044.400475;separatenative267663045.501509;acceptedportable281973051.518173,COMPLETED0:0in611son16H200N64. Newreadinessgateclosedhealth200/models503race;bothsemanticroutes,unchangedofficialclient,correctedreaders/gateandcleanupcompleted. Theseareseparateobservationclasses,notnewmatchedoptimisationspeedup. Formerhighestcompletecache273783048.446289+0.240921%vsowncontrolnotpromoted. Failedraw271453055.330517remainsfailedoriginaljob. Lowerlegacy2830.923547remainsunexplained. Officialqualityunknown.', '28197raw/gate/terminalreview;N64historicalseries;26766')
for x,label,value,detail,col in [(1.,'HISTORICAL · THREE RUNS','3,044.40','N64 mean',INK),(5.1,'NATIVE · 26766','3,045.50','Separate full run',GRAY),(9.05,'PORTABLE · 28197','3,051.52','Whole entry accepted',ORANGE)]:
 s.text(label,x,1.70,3.7,.69,15,col,bold=True);s.text(value,x,2.85,3.7,.82,34,col,bold=True);s.text('good output tokens/s',x,3.91,3.7,.43,17,GRAY);s.text(detail,x,4.72,3.7,.68,21,col)
s.text('Same retained recipe; a new accepted deployment, not a matched optimisation gain.',1.,5.77,11.3,.75,22,bold=True)
s.text('A valid older replay scored 2,830.92; the cause of that lower level remains unresolved.',1.,6.58,11.3,.36,15,GRAY);s.end()


# 14 — Robustness · direct H200 verification
s=slide('Direct transfer', 'H100 was used to screen compatible alternatives; hardware-specific winners cannot be inferred from H100 scores. Nine actual final allocations on16H200 test the alternatives against explicitH200controls.27777=3038.022907;FA327779=2999.245473(-1.276404%);H100recipeN6427783=2721.815800(-10.408319%);HPCprefill819227806=2900.606831(-4.523207%).Two modeports27828/27830 yield+.006223%/+.130765% against separate27826control3039.167093. No useful>1%win;retainDeepGEMM8192prefillandHPCOps/FI/MNNVLdecodeatN64. Exact9jobledgerbackup34;forecastbackup33. No universalGPUconversion or qualitycertificate.', '27777/27779/27781/27783;27804/27806;27826/27828/27830 final reviews')
s.text('Question: do H100-derived choices improve our H200 service?',1.,1.49,11.3,.68,24,bold=True)
for i,(label,value,detail,col) in enumerate([('Fresh H200 control','3,038.02','27777 · full N64',INK),('H100 recipe port','2,721.82','27783 · -10.41%',RED),('Match chunk 8192','2,900.61','27806 · still -4.52%',GRAY)]):
 x=1.+i*4.05;s.text(label,x,2.63,3.7,.67,21,col,bold=True);s.text(value,x,3.51,3.7,.74,32,col,bold=True);s.text('good output tokens/s',x,4.39,3.7,.40,16,GRAY);s.text(detail,x,5.04,3.7,.55,18,col)
s.text('FA3 loses 1.28%; phase-mode gains ≤0.131% vs a separate fresh control.',1.,5.95,11.3,.52,20,GRAY)
s.text('Decision: retain the H200 recipe. Nine measured allocations; details in backup 34.',1.,6.48,11.3,.42,16,INK,bold=True);s.end()


# 15 — Experimental findings · reject tested alternatives
s=slide('Rejectproxywins', 'SeparateH200trialsnotpairedsamecontrolacrossrows. Sparse27510capturememory1.15→.36GB/rankbutgoodput−.370208%vsprior27376;onecontrolgeneratedseedsandcandidateobservationlimitscausalclaim,paddingnotmeasured. EAGLE27238full2971.628430vs269493034.761104−2.080318%;functionalrepairdoesnotguaranteegain,settingspecificnotuniversalrejection. Retainoldsettingsonlywithinmeasuredscope.', '27510/27376;27238/26949')
panel(s,1.,1.65,5.2,4.6,'SPARSE GPU GRAPHS','Capture memory / rank\n1.15 → 0.36 GB\n\nGoodput: -0.37%\nRetain dense graphs',INK)
panel(s,7.,1.65,5.2,4.6,'SHALLOW EAGLE3','Functional speculative path\nDraft then verify tokens\n\nGoodput: -2.08%\nReject this tested setting',GRAY)
s.end()


# 16 — Conclusion · deployment accepted, quality still organiser-run
s=slide('Accepted entry and remaining quality', '28197wholeentryCOMPLETED0:0in611secondson16H200N64:two semantic routes,official fullclient,correctedsummary/performancegate,cleanup. 1881/1907jointrequests98.63660199%,zeroerrorscancels;goodtok3051.518173. Runtimeacceptanceclosespostreaderreplaygapbutofficialfullsetqualityratio>=.99isUNKNOWNandorganiser-run. Basiccanbesubmittedforrebuild/reviewwithoutclaimingqualityalreadycertified. KeepQwenFP8BF16KVsameN64recipe;nooptimisationorCPUhardwareclaims. HPC35handoff.', '28197gate/summary/semantic/cleanup;officialQ1')
s.text('The complete repaired entry now passes on 16 H200',1.,1.55,11.3,.95,27,bold=True)
panel(s,1.,3.00,5.2,2.9,'VERIFIED · DEPLOYMENT','28197 · 10 min 11 s\nBoth P/D routes; official client\nReaders, performance gate, cleanup',INK)
panel(s,7.,3.00,5.2,2.9,'OPEN · OFFICIAL QUALITY','At least 99% of organiser reference\nFull-set accuracy: not yet evaluated\nSmall local checks are insufficient',ORANGE)
s.rect(1.,6.18,11.2,.64,INK);s.text('Next: OpenFOAM · hand over to the HPC presenter',1.20,6.30,10.8,.39,20,WHITE,bold=True);s.end()


# 17 — Backup · Environment
s=slide('One workload, two deployment systems', 'Both platforms provide two eight-GPU nodes, but they are not interchangeable experimental environments. Firmus uses H200, Slurm and Enroot; NSCC ASPIRE 2A+ uses H100 80GB, PBS and Singularity. We stage the same serving and client image artifacts and official FP8 checkpoint. CPU, driver, network, launcher, node cache and timing can still differ. A hardware-specification ratio is not a performance conversion.', 'Qwen rules; NSCC asset contract; matched-anchor audit')
table(s,['','FIRMUS','NSCC ASPIRE 2A+'],[['Allocation','2 × 8 H200','2 × 8 H100 80GB'],['Scheduler','Slurm','PBS'],['Container launcher','Pyxis / native Enroot','Singularity'],['Serving / client','SGLang / AIPerf','Same staged image artifacts'],['Model','Qwen3-235B FP8','Same checkpoint']],widths=[3.1,4.25,4.25],row_h=.70,size=19)
s.text('Keep platform, topology, backend and load in every comparison.',.98,6.28,11.4,.52,23,ORANGE)
s.end()




# 18 — Backup · Compatibility mechanism
s=slide('FP8 block geometry constrains parallelism', 'A failed TP8/EP1 prefill deployment exposed a block-alignment constraint. The model MoE intermediate size is 1,536 and FP8 block width is 128. With EP1, MoE tensor parallelism eight produces 192-element partitions, which do not divide by 128. With EP2, effective MoE tensor parallelism is four, producing 384-element partitions. This retains all weights and experts. The TP8/EP2 replacement is a combined layout change, not an isolated TP speedup. Failure before benchmarking is not a measured throughput result.', 'Exact staged SGLang source; failed job 24282; corrected trial 24321')
for x,title,formula,nblocks,col in [(.98,'TP8 / EP1','1,536 ÷ 8 = 192',1,RED),(7.12,'TP8 / EP2','1,536 ÷ 4 = 384',3,INK)]:
 s.text(title,x,1.54,5.05,.6,30,col,bold=True);s.text(formula,x,2.54,5.1,.65,30)
 for i in range(nblocks):s.rect(x+i*1.63,3.70,1.52,1.0,ORANGE if nblocks==3 else INK);s.text('128',x+.34+i*1.63,3.97,.95,.5,25,WHITE)
 if nblocks==1:s.rect(x+1.65,3.70,.76,1.0,RED);s.text('64',x+1.78,3.99,.6,.4,20,WHITE)
s.text('Partial block → load failure',1.0,5.19,5.2,.85,24,RED);s.text('Three full blocks → compatible geometry',7.14,5.19,5.14,.85,24)
s.text('Compatibility is necessary; startup, SLA and output quality still need testing.',1.0,6.29,11.4,.45,19,GRAY)
s.end()




# 19 — Backup · Chronology as supporting evidence
milestones=[('Initial 07\nN32',1297.02),('Initial 09\nN40',1666.01),('PD split\nN48',1912.30),('FI + MNNVL\nN52',2631.09),('Prefill DG\nN56',2715.84),('DG + HPC\nN58',2938.63),('N60\nrepeated',2989.17),('N62\nrepeated',3022.55),('N64\n3 repeats',3044.40)]
def progression(fig,ax):
 x=np.arange(len(milestones));values=[r[1] for r in milestones]
 ax.bar(x,values,color=[GRAY]*3+[INK]*2+[ORANGE]*4,width=.65)
 for i,y in enumerate(values):ax.text(i,y+42,f'{y:,.0f}',ha='center',fontsize=11,fontweight='bold')
 ax.set_xticks(x,[r[0] for r in milestones],fontsize=10);ax.set_ylim(0,3400);ax.set_ylabel('Good output tokens/s');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
p=chart('h200-research-progression',progression)
s=slide('H200 journey: recover, specialise, then reproduce', 'The historical progression spans different loads and configurations, not a single cumulative causal ablation. We recovered the 16-GPU split and request-scoped NIXL transfer, combined FlashInfer attention with MNNVL, introduced DeepGEMM prefill, increased its chunk to 8192, and found an interaction with HPC-Ops decode. N58 and N60 treatment gains reproduce. N62 repeats at3022.034919/3023.072304; N64 repeats at3044.489701/3044.074628. Observation settings also differ across this historical journey; it is not one cumulative causal ablation.', 'Historical retained milestones; 24724/24737/24819; 24738/24913; 24915')
s.image(p,.78,1.40,11.8,4.68);s.text('Historical milestones · loads and runtime settings change across stages',1.0,6.32,11.3,.43,19,GRAY);s.end()




# 20 — Backup · Intervention & correctness
s=slide('Descriptor intervention', 'Source inspection found whole-pool heterogeneous-TP KV descriptor enumeration. The patch constructs source/destination descriptors for request pages and coalesces adjacent ranges while keeping partial-head token stride. Representative counts are about403.8million source entries per rank for the pool versus188coalesced entries for one contiguous4000-tokenTP8→TP4request; scopes differ.720CPUbyte-range equivalence cases pass, while geometry-test.json explicitly has realGPUtransportvalidationfalse. The patch retains weights/precision/head mapping/notifications and equal-TPpath. GPUresponse andend-to-end measurements are separate evidence in the nextslide.', 'nixl-ondemand/{README.md,nixl-ondemand.patch,metadata.json,geometry-test.json}')
for x,label,value,detail in [(1.0,'WHOLE RESERVED KV POOL','403.8 million','source entries / rank'),(7.0,'ONE 4,000-TOKEN REQUEST','188','coalesced range entries')]:
 s.text(label,x,1.64,5.25,.39,16,ORANGE,bold=True);s.text(value,x,2.35,5.2,1.06,43,bold=True);s.text(detail,x,3.67,5.2,.48,22)
s.text('720 CPU range-equivalence cases pass; real GPU transport is a separate check.',1.,4.85,11.3,.9,22)
s.text('Counts describe setup geometry, not bandwidth or an inference speedup factor.',1.,6.1,11.3,.65,22,ORANGE);s.end()




# 21 — Backup · End-to-end evidence & limits
s=slide('KV recovery evidence', 'Compare historical attempts in the same P8TP8EP2prefill toD8TP4EP4decode topology.22271 loaded workers, timed out in pairwarmup at360s and has noAIPerfscore. With the descriptorpatch22294 completed actualP/Dwarmup paths in0.68–0.70s/request after workerswere ready and fullN32 measured1422.96goodtokens/s,95.87%jointSLA,zeroerrors/cancellations. This establishes patchedpath feasibility. Without a successful unpatched benchmark, separately timed descriptorinitialisation orphase/networktelemetry, no throughput speedup or dominant cause is isolated. This branch is different fromselected2TP4prefillTP8decode. Do not compute360/.7 as an acceleration ratio becauseone observation isatimeout.', '22271/pair-warmup.log;22294/pair-warmup.log;22294/confirm/n32/artifacts/profile_export_aiperf.json')
table(s,['OBSERVATION','BEFORE · 22271','PATCHED · 22294'],[['Topology','Same heterogeneous-TP branch','Same heterogeneous-TP branch'],['Pair warmup','Timeout after 360 s','0.68–0.70 s / request'],['Full benchmark','Not reached; no score','N32: 1,422.96 good tokens/s'],['Joint SLA / errors','No scored result','95.87%; zero errors/cancels']],widths=[3.45,4.1,4.05],row_h=.85,size=18)
s.text('Feasibility demonstrated; descriptor-only end-to-end speedup not measured.',1.,6.14,11.3,.64,23,ORANGE);s.end()




# 22 — Backup · Platform-specific tradeoff
s=slide('H100 attention tradeoff', oldnotes(16)+' '+oldnotes(17), '222027/222028 matched fullH100N54pair;222048historicalpeak;225227freshcontrol')
table(s,['H100 · N54','FLASHINFER CONTROL','FA3 DECODE'],[['Good output tokens/s','2,420.945','2,401.284'],['Mean TTFT','713.199 ms','594.276 ms'],['Mean request ITL','18.214 ms','18.988 ms'],['Mean request latency','4,337.853 ms','4,372.813 ms']],widths=[4.1,3.75,3.75],row_h=.77,size=20)
s.text('First token arrives sooner; accumulated token gaps lower goodput by 0.81%.',1.,5.98,11.3,.71,22,ORANGE)
s.text('Separate H100 context: historical peak 2,433.02; fresh control 2,399.19.',1.,6.69,11.3,.28,13,GRAY);s.end()




# 23 — Backup · Cost hypothesis & confirmation
s=slide('Test the cost hypothesis, then reverse the order', 'Slow prefill loading motivated prefill-only checkpoint read-first experiments. In the first H100 full pair, scheduler walltime fell934 to759 seconds,18.737%, while goodput fell0.659%. Nodes and unknown cache state prevented a cold-storage causal claim. A predeclared reverse-order confirmation required at least10% walltime savings and at most2% lower goodput. Read-first770 versus off854 seconds saved only9.836066%; goodput changed-0.326388%. Close the unchanged branch below its cost gate instead of promoting the favorable first comparison. Separately, a static one-GPU locality probe saw no intersection between allowed CPUs and local NUMA CPUs; that did not establish full-serving bindings or a CPU bottleneck.', 'Startup-prefetch original and reverse-pair reviews; static locality222412')
table(s,['H100 FULL PAIR','FIRST ORDER','REVERSED ORDER'],[['Off / read-first walltime','934 / 759 s','854 / 770 s'],['Observed walltime saving','18.74%','9.84%'],['Goodput change','-0.66%','-0.33%'],['Prospective cost gate','At least 10% saving','Not met: no promotion']],widths=[4.8,3.4,3.4],row_h=.77,size=19)
s.text('Question → bounded pair → reverse check → close below the declared gate.',1.0,6.22,11.3,.57,21,ORANGE);s.end()





# 24 — Backup · Negative measured interventions
s=slide('Use source evidence to test one small hypothesis', 'Native source and actual runtime showed auto prefill collective selected TRT-LLM, not MNNVL. Changing only that selector activated MNNVL on all eight P ranks, but full27138 gained only0.109807%. Native tokenizer batching first passed exact-ID preflight on64 concurrent plus one single input, then two full wait settings gained0.192% and0.270%. These were source-supported trials, not proof of a CPU bottleneck. Prefill FlashInfer page1 lowered ITL but lost6.385% goodput. Cache, request-cap and polling tests also failed the prospective useful-gain gate. Each branch preserves control, actual activation, output gates and stopping decision.', '26949/26951/26953;27138 actual collective source/activation;27077;27365;27376/27378;27270/27272/27274')
table(s,['HYPOTHESIS AND CHECK','FULL OBSERVATION','DECISION'],[['Tokenizer IDs → two waits','+0.19% / +0.27%','Keep tokenizer off'],['Auto selected TRT-LLM → MNNVL','+0.11%; ranks verified','No promotion'],['Prefill radix → ChunkCache','+0.24%; p95 TTFT worse','Retain radix'],['Request cap / polling','+0.26% / negative','Retain defaults'],['Prefill FlashInfer, page 1','-6.39%; ITL lower','Retain FA3']],widths=[4.8,3.8,3.0],row_h=.65,size=18)
s.text('An active flag and a passing run still need a useful matched gain.',1.0,6.28,11.3,.51,22,ORANGE);s.end()





# 25 — Backup · Diagnostics versus full serving
s=slide('Appendix · profiles and source also close attractive detours', 'Architecture and kernel ideas were tested at the scope their evidence supported. H200 attention-DP plus DeepGEMM/DeepEP23780 scored2549.20 atN52, below the retained MNNVL point; several factors changed together, so no one-flag attribution follows. Representative H100 FP8 Triton probes lost to DeepGEMM in tested shapes. H100 SM budgets80/96/120 were mixed or below their consistency gate, so132 was retained without claiming a model gain. An LL-named NCCL kernel had been misread: actual TUNING logs showed Simple selection and a control already using it for large messages; the small0.2315% point did not justify promotion. Full Qwen compile later failed native RoPE; C++ tree CPU fixtures passed but did not establish serving speed. Unsupported model/hardware/library paths and flags without consumers stayed source findings, not benchmarks.', 'JOURNEY stages15,29-31;DeepGEMM representative probes;NCCL source correction;27383;27506')
table(s,['RESEARCH DIRECTION','EVIDENCE','DECISION'],[['Attention-DP package','2,549.20 at N52; coupled changes','No isolated flag claim'],['FP8 kernel alternatives','Representative Triton probes lose','Retain DeepGEMM'],['SM budgets / protocol forcing','Mixed gains; source correction','Keep defaults'],['Real-model torch.compile','RoPE / fused-KV assertion','No score; path blocked'],['C++ cache / unsupported APIs','CPU pass or source findings only','No serving claim']],widths=[4.0,4.8,2.8],row_h=.66,size=17)
s.text('A kernel name, a library headline or a CPU trace is a lead—not proof of speed.',1.0,6.35,11.3,.47,19,ORANGE);s.end()





# 26 — Backup · Exact deployment settings
s=slide('Appendix · the selected AI deployment is N64', 'The selected AI primary retains replicated N64. Real portable jobs27136/27145 completed both semantic routes and the official GPU client, then failed in result-reader path handling. Fixed readers passed compute-only27152 on both actual datasets; a whole-allocation end-to-end run after that repair is not claimed. Native FP8 target and BF16 activation/KV remain. H200 uses two TP4 DeepGEMM prefills, chunk 8192 and breakable prefill graphs, with one TP8/EP8 HPC-Ops decode, FlashInfer decode attention, MNNVL and dense decode graphs 1 through 64. Round-robin routing and all original fixed-workload goodput limits remain. H100 is a separate point, not an alternate device setting for the same result.', '26766 frozen worker/runtime; 25487 operational settings; staged portable deployment validation')
table(s,['SETTING','H200 SELECTED','H100 RETAINED'],[['Client concurrency','64','54'],['Prefill runner / chunk','DeepGEMM / 8192','HPC-Ops / 4096'],['Decode runner','HPC-Ops','HPC-Ops'],['Prefill / decode TP','4 + 4 / 8','4 + 4 / 8'],['Weights / activation / KV','FP8 / BF16 / BF16','FP8 / BF16 / BF16']],widths=[4.2,3.7,3.7],row_h=.65,size=19)
s.text('Both: TP8 / EP8 decode, FlashInfer + MNNVL, round-robin routing.',1.0,6.37,11.3,.49,19,GRAY);s.end()





# 27 — Backup · Fixed protocol & negative result
s=slide('Workload and chunking', oldnotes(29)+' '+oldnotes(30), '4000/200seed2026closedloop;26766/26768/26770 fullreviews')
s.text('Fixed 4,000 / 200 tokens · N64 · 60 s warmup / 120 s profile / 30 s grace',.97,1.53,11.4,.51,19,bold=True)
table(s,['CHUNK TOKENS','GOOD TOKENS/S','JOINT SLA','p95 TTFT'],[['8192','3,045.50','98.580%','1,311.69 ms'],['10240','3,034.09','98.524%','1,518.87 ms'],['12288','3,020.94','98.310%','1,624.12 ms']],widths=[2.8,3.2,2.5,3.1],y=2.36,row_h=.91,size=21)
s.text('Same workload and runtime; larger prefill chunks did not improve service.',1.,6.17,11.3,.67,23,ORANGE);s.end()




# 28 — Backup · Resource metric versus objective
s=slide('Appendix · sparse graphs save memory, not goodput', 'Actual27510 completed0:0 in13:15 on16H200 and passed independent full local gates. Twelve decode graph buckets replace1..64; all eight current ranks prove captures with compile off. Goodput3029.861122 is0.370208% below earlier control27376 at3041.119598. Mean/p95TTFT1102.404/1240.481ms improves, while mean/p95ITL15.136/15.324ms worsens. Capture memory drops1.15 to0.36GB per rank, but capture time only101.46-101.49 to95.98-96.05seconds. Native log units are not total VRAM. One earlier control, generated seed differences and candidate-only startup observation prevent a strong causal claim. Retain dense graphs; official accuracy remains unknown.', '27510 terminal raw/runtime/capture review;27376 prior control')
table(s,['DECODE GRAPH MEASURE','DENSE CONTROL','SPARSE CANDIDATE'],[['Capture buckets','64','12'],['Capture memory / rank','1.15 GB','0.36 GB'],['Capture elapsed time','101.46-101.49 s','95.98-96.05 s'],['Good output tokens/s','3,041.12','3,029.86'],['Mean request ITL','14.991 ms','15.136 ms']],widths=[4.6,3.5,3.5],row_h=.68,size=19)
s.text('A lower resource metric is useful only if the service objective improves.',1.0,6.38,11.3,.49,20,ORANGE);s.end()




# 29 — RQ4 · Robustness & confounder checks
s=slide('Appendix · diagnose performance drift with controlled cells', 'The question was why historical full N64 averaged3044.400475 while a newer short control was about2560. Actual ServerArgs revealed changed prefill graph policy and max-running-request cap, plus harness/observation differences. We froze an exact legacy operational replay and modern full controls isolating graph and admission; a later completed factorial did not establish a single useful cause. Valid legacy replay26313 scored2830.923547, while native26766 reproduced3045.501509. Neither simply restoring a flag nor changing launcher can be credited causally. Keep lower observations and comparable protocol labels rather than select only the larger peak.', 'Incumbent recovery plan;26313 legacy full result;graph/admission factorial;26766 native full review')
table(s,['OBSERVATION / TEST','WHAT WAS HELD OR CHANGED','RESULT'],[['Historical full N64','Replicated original operating point','Mean 3,044.40'],['Later control','Short protocol + graph/cap drift','About 2,560; different'],['Exact legacy full replay','Old operational bytes retained','2,830.92; valid lower run'],['Modern controlled cells','Isolate graph and request cap','No single useful cause'],['Native full recovery','Source/KV/output gates retained','3,045.50; separate series']],widths=[3.6,4.9,3.1],row_h=.67,size=17)
s.text('Inspect effective settings → isolate confounders → preserve unresolved variation.',1.0,6.34,11.3,.51,20,ORANGE);s.end()





# 30 — RQ3 · Failed hypothesis → revised test
s=slide('EAGLE3: follow the failed hypothesis through its repairs', 'The all-worker EAGLE3 attempt25948 failed the joint latency gate. Moving the draft to decode only aimed to recover TTFT, but25988 first failed a validator that applied draft KV-region counts to target-only prefill. The role-aware validator repair preserved that failure. Decode-only25998 then passed its short protocol but lost4.74% against its own target-only control. A distinct later one-step/top-k1/two-draft-token full arm27238 passed at2971.628430 versus26949 at3034.761104, losing2.080318%. Low logged acceptance is descriptive, not a causal timing breakdown. Close each tested arm; functional draft transfer alone does not establish speedup or official accuracy.', '25948;25988 role-aware KV repair;25947/25998 short review;26949/27238 full shallow review')
table(s,['STAGE','OBSERVATION','LESSON / DECISION'],[['All-worker draft','Joint latency gate fails','Placement matters'],['Decode-only first attempt','Wrong KV validator rejects','Repair tooling; retain failure'],['Decode-only retry','Short pass; goodput -4.74%','No promotion'],['Shallow full-protocol trial','Full pass; goodput -2.08%','Close tested arm']],widths=[3.8,4.1,3.7],row_h=.78,size=18)
s.text('Attempt → diagnose → repair → remeasure → reject an unhelpful optimization.',1.0,6.23,11.3,.53,21,ORANGE);s.end()





# 31 — Backup · a deployment claim requires a complete real run
s=slide('Complete portable acceptance', '27136GPUclientfinishedbutnestedexportreaderfailed;27145GPUclientfinishedbutcanonicalaliasreaderfailed;27152CPUcheckedbothcorrectedreadersonsavedraw.28194thenfailedprebenchmarkhealth200/models503asyncregistrationrace. R2changesonlygateway-readinessandchecksum;fiveCPUfixturespass.28197COMPLETED0:0in611s:gatewayqwen333s,twosemanticroutes375s,officialclient/summary/perfgate603s,allcleanupterminal.3051.518173goodtokens/s1881/1907errors0. Earlierfailuresnotrelabeled;qualityunknown. ActualtopGPUhours2.715556for28197plus1.484444failed28194,notruntimeoptimisationclaim.', '28194failure;28197completeindependentreview;27136/27145/27152')
table(s,['RUN / STAGE','WHAT FAILED OR PASSED','LESSON'],[['27136 · GPU/client complete','Nested export reader fails','Resolve export namespace'],['27145 · GPU/client complete','Canonical path alias fails','Canonicalise reader input'],['27152 · CPU data replay','Both readers pass saved data','Still not a new GPU run'],['28194 · startup attempt','Health up; models returns 503','Wait for registered qwen'],['28197 · full repaired entry','COMPLETED; all gates pass','Accepted deployment evidence']],widths=[3.4,4.5,3.7],row_h=.78,size=17)
s.text('Retain failures; qualify each repair; a complete run closes the deployment gap.',1.,6.38,11.3,.46,18,ORANGE);s.end()


# 32 — RQ3 · Hypothesis → intervention
s=slide('Backend combinations matter', 'At N52 on H200, the standalone FlashInfer trial reached 2,440.386 good tokens/s and MNNVL reached 2,592.162. The combo reached 2,631.085. A later MNNVL control at the same load reached 2,594.028, putting the combo about 1.43% higher in those observations. These same-load comparisons motivate combining the decode attention and collective choices; they do not mean component gains add linearly. Runtime checks and later repetitions support the combo operating range.', '23777; 23778; 23904; 23974')
table(s,['H200 · N52','JOB','GOOD TOKENS/S','SLA'],[['FlashInfer decode only','23777','2,440.39','98.947%'],['MNNVL decode only','23778','2,592.16','99.007%'],['MNNVL fresh control','23974','2,594.03','99.009%'],['MNNVL + FlashInfer','23904','2,631.09','99.022%']],widths=[4.4,1.5,3.2,2.5],row_h=.77,size=20)
s.text('Combine attention and collective tuning; measure the combination directly.',.99,6.13,11.3,.64,24,ORANGE);s.end()





# 33 — Backup · frozen forecast and held-out check
s=slide('Forecast', 'Same-comboN52meansH1002215.4602allocH2002632.1814allocratio1.188096805localcalibrationnotuniversal. FrozenbeforeheldoutH200N50predict2642.244,actual242722601.629,error−1.5371%withinteam±2%tolerancebutoutsidepreviousinputsensitivityrangeomittingmodelerror. DoNotrefitorconvertTTFTITLpeaksotherconfigs. TwosystemsGPUdrivernetworkruntimeallvary.', 'frozenN52calibration;held-out24272')
s.text('Same configuration · N52 anchor',1.,1.56,5.0,.91,24,bold=True)
s.text('H200 / H100 = 1.1881',1.,2.57,5.1,.90,30,ORANGE,bold=True)
s.arrow(6.0,3.0,7.1,3.0,GRAY)
s.text('H200 N50 held out',7.5,1.56,4.7,.73,24,bold=True)
s.text('Predicted   2,642.24\nMeasured  2,601.63',7.5,2.59,4.7,1.6,27)
s.text('good output tokens/s',7.5,4.30,4.7,.45,17,GRAY)
s.line(1.,5.35,12.1,5.35,PALE,1)
s.text('Error -1.54%: inside practical ±2% tolerance, outside the earlier incomplete sensitivity range.',1.,5.80,11.3,1.0,23)
s.end()


# 34 — Backup · complete final H200 allocation ledger
s=slide('Final verification ledger', 'All nineOct31allocations runon16H200 and passfullteamlocalgates; zero scored errors/cancellations,smoke7/8nonregression,retrieval12/12;officialfullqualityunknown.27777control3038.022907;27779FA32999.245473;27781H100recipeN542738.940099;27783sameN642721.815800;27804HPCprefill61442821.884862;27806HPCprefill81922900.606831.27826separatenogradcontrol3039.167093;27828decodeinference3039.356215;27830prefillinference3043.141258.Fouradditionaldistinctports27804/06/28/30notfourprovenH100wins; controlsnotcandidates. Actual28.337778GPUhours,zeroPBS_SU. Preservefailed/negativehistoricalbranchesinjourney. No usefulnewwinner.', 'Final transfer, chunk and phase review reports; integrity audit20261101')
headers=['JOB / CHANGE','N','GOOD TOKENS/S','CONTROL / DECISION']
rows=[['27777 · native control','64','3,038.023','H200 control'],['27779 · FA3 decode','64','2,999.245','-1.276% vs 27777'],['27781 · H100 recipe / 4096','54','2,738.940','Different load; no matched gain'],['27783 · H100 recipe / 4096','64','2,721.816','-10.408% vs 27777'],['27804 · HPC prefill / 6144','64','2,821.885','-7.114% vs 27777'],['27806 · HPC prefill / 8192','64','2,900.607','-4.523% vs 27777'],['27826 · explicit no_grad','64','3,039.167','Separate mode control'],['27828 · decode inference_mode','64','3,039.356','+0.006% vs 27826'],['27830 · prefill inference_mode','64','3,043.141','+0.131% vs 27826']]
table(s,headers,rows,widths=[4.8,.6,2.6,3.6],y=1.50,row_h=.48,size=15)
s.text('All nine: full local pass; zero request errors. No new useful gain; official quality unknown.',1.,6.59,11.3,.38,14,GRAY);s.end()

assert len(prs.slides)==34
for b in bounds:
    assert b['x']>=0 and b['y']>=0 and b['x']+b['w']<=W+.01 and b['y']+b['h']<=H+.01,b
assert len({r['sha256'] for r in BACKGROUNDS})==34
for r in BACKGROUNDS:assert hashlib.sha256((EXTERNAL/r['file']).read_bytes()).hexdigest()==r['sha256']
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
from pptx.opc.constants import RELATIONSHIP_TYPE as RT, CONTENT_TYPE as CT
credit='Theme adaptation: Metropolis, Matthias Vogelgesang and contributors, CC BY-SA 4.0, https://github.com/matze/mtheme. Original TripleU research charts and presentation content are separate from the theme licence. Icons: Lucide ISC. Backgrounds are separately sourced reference infrastructure photographs, not contest-installation photographs. Full attribution: '+json.dumps(BACKGROUNDS)
e=etree.Element('assetCredits');e.text=credit
part=Part(PackURI('/customXml/assetCredits.xml'),CT.XML,prs.part.package,etree.tostring(e,encoding='UTF-8',xml_declaration=True));prs.part.relate_to(part,RT.CUSTOM_XML)
prs.save(OUT/'TripleU_APAC2026_Presentation.pptx');pdf.save()
(OUT/'slide-content.json').write_text(json.dumps(outline,indent=2)+'\n')
(OUT/'layout-validation.json').write_text(json.dumps(dict(slides=34,main_slides=16,appendix_slides=18,text_within_boxes=True,boxes_within_slides=True,distinct_backgrounds=34,english_only=True,raw_sla_checked=dict(job='26766',requests=len(a),passed=int(good.sum())),render_note='PDF and previews use the same drawing coordinates as PPTX; they are not an Office rendering.'),indent=2)+'\n')
doc=fitz.open(OUT/'TripleU_APAC2026_Presentation.pdf');thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.25,1.25));p=ASSETS/f'slide-{i+1:02d}.png';pix.save(p)
    im=Image.open(p).convert('RGB');im.thumbnail((480,270));thumbs.append(im)
sheet=Image.new('RGB',(2000,math.ceil(len(thumbs)/4)*300),'#E2E7E8');draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    x=(i%4)*500+10;y=(i//4)*300+10;sheet.paste(im,(x,y));draw.text((x,y+274),f"{i+1:02d} {outline[i]['title'][:68]}",fill=INK)
sheet.save(OUT/'Presentation_Overview.jpg',quality=93)
print(json.dumps(dict(output=str(OUT),slides=len(prs.slides),main_slides=16,appendix=18)))

#!/usr/bin/env python3
"""Preserve the established talk design; make the AI decision stories explicit."""
from pathlib import Path
source_path=Path(__file__).with_name('build_ai_acceptance_slides_20261102.py')
source=source_path.read_text()
def replace(start,end,new):
 global source
 a=source.index(start);b=source.index(end,a);source=source[:a]+new+'\n\n'+source[b:]
replace('# 03 —','# 04 —', r'''# 03 — Architecture reasoning before benchmark history
s=slide('Topology decision','Select a feasible phase split under the fixed two-node budget. Earlier layouts and loads were not a matched global ranking. The old slide incorrectly paired topology 09 with job 22219; no such attribution is repeated here.','Topology results; retained architecture and repeated N64 service')
s.text('Why separate prompt work from token generation?',1.,1.55,11.2,.62,26,bold=True)
for x,label,body in [(1.,'PREFILL','Read the whole prompt\nProcess many tokens together'),(7.,'DECODE','Generate one token at a time\nAdvance many active requests')]:
 panel(s,x,2.57,5.15,2.2,label,body,ORANGE if x==1. else INK)
s.text('One budget: 2 nodes × 8 GPUs',1.,5.05,6.2,.5,23,bold=True)
s.text('Wider workers use more GPUs; more replicas share fewer GPUs each.',1.,5.85,11.2,.7,21)
s.end()
''')
replace('# 05 —','# 06 —', r'''# 05 — Explain the first symptom before naming the patch
s=slide('Setup failure','Historical heterogeneous-TP recovery branch 22271: workers loaded, pair warmup timed out at360s before any AIPerf score. KV is intermediate attention state; NIXL is the existing library used to transfer that state. Ready processes do not establish completed requests.','22271 logs; retained NIXL recovery source')
s.text('The model loaded. The first split request still did not finish.',1.,1.55,11.2,.95,27,bold=True)
arrow_chain(s,['Prefill reads\nthe prompt','NIXL moves\nKV state','Decode generates\nthe answer'],y=3.0,colors=[INK,ORANGE,INK])
s.text('KV = the attention state decode reuses from prefill',1.,4.65,11.2,.53,22)
s.text('Observed: workers ready → warmup timeout after 360 s',1.,5.50,11.2,.55,23,RED,bold=True)
s.text('First question: what work happens before the transfer becomes usable?',1.,6.27,11.2,.48,19,GRAY)
s.end()
''')
replace('# 06 —','# 07 —', r'''# 06 — Ownership and source-supported hypothesis
s=slide('Request-scoped metadata','NIXL is reused. Our text patch changes descriptor construction for a particular heterogeneous-TP path. Descriptors are address/range metadata, not KV bytes. Restrict construction to this request and coalesce adjacent ranges. 720 CPU equivalence cases pass; real distributed validation remains necessary.','nixl-ondemand.patch; geometry-test.json')
s.text('The source prepared address lists for the reserved KV pool.',1.,1.50,11.2,.76,25,bold=True)
s.text('Could we describe only the pages this request needs?',1.,2.35,11.2,.68,24,ORANGE,bold=True)
for x,label,body,color in [(1.,'BEFORE · WHOLE RESERVED POOL','Prepare metadata for pages\nthis request may never use',GRAY),(7.,'TEAM CHANGE · THIS REQUEST','Select request pages\nMerge adjacent byte ranges',INK)]:
 panel(s,x,3.45,5.1,1.95,label,body,color)
s.text('Correctness invariant: transfer the same byte ranges',1.,5.66,11.2,.53,22,bold=True)
s.text('720 CPU cases passed before trying the patched distributed path.',1.,6.35,11.2,.40,18,GRAY)
s.end()
''')
replace('# 07 —','# 08 —', r'''# 07 — A bounded conclusion, not a speedup invented from timeout
s=slide('Transfer validation','22271 unpatched warmup timeout; new patched22294 completes real P/D warmup and full N32 benchmark. Supports usable patched path. Missing successful unpatched scored control prevents isolated descriptor speedup. This is a particular historical recovery branch, not the explanation for every later score.','22271;22294;range-equivalence review')
panel(s,1.,1.75,5.15,2.95,'UNPATCHED ATTEMPT','Workers ready\nWarmup timed out\nNo benchmark score',RED)
panel(s,7.,1.75,5.15,2.95,'PATCHED ATTEMPT','Real prefill → decode requests\nFull benchmark completed\nNo scored request errors',INK)
s.text('Contribution: a request-scoped metadata implementation',1.,5.14,11.2,.59,24,ORANGE,bold=True)
s.text('Evidence: byte-range checks + a usable distributed serving path',1.,5.91,11.2,.53,21)
s.text('An isolated descriptor-only throughput gain was not measured.',1.,6.57,11.2,.36,16,GRAY)
s.end()
''')
replace('# 08 —','# 09 —', r'''# 08 — Investigation choices, with profile limits explicit
s=slide('Choose the next question','Separate N48 diagnostic records GEMM, collectives and attention activity. Summed kernel time is not a per-request wall-time budget and does not prove a unique bottleneck. Available supported backend choices permit a bounded matched experiment. The phase/shape argument is a retrospective engineering explanation where no original pre-run rationale survives.','24819 profile; phase-specific backend reviews; thinking-process guide')
s.text('A profile gave candidates, not a single proven culprit.',1.,1.52,11.2,.73,27,bold=True)
for x,label,body in [(1.,'COMPUTE','MoE matrix operations'),(5.1,'COMMUNICATION','Collectives and synchronisation'),(9.05,'ATTENTION','Reading cached KV state')]:
 s.line(x,2.75,x+3.35,2.75,ORANGE,2);s.text(label,x,3.0,3.4,.62,17,bold=True);s.text(body,x,3.93,3.4,1.0,20)
s.text('Why test execution choices separately for prefill and decode?',1.,5.40,11.2,.66,24,ORANGE,bold=True)
s.text('Different token shapes can favor different implementations. Test the service.',1.,6.30,11.2,.51,19)
s.end()
''')
replace('# 11 —','# 12 —', r'''# 11 — Keep only numbers needed to explain the operating decision
s=slide('Load selection','Full N62/N64 comparison gains1.082867%; independentN64repeat differs0.013634%; N68shortsignal2.27% becomesfull0.083056%, belowteam1%usefulgain threshold. Raisingconcurrency canincreasequeueing; noisolatedcauseclaimed.','25365/25366/25373;25487/25488')
for x,label,value,meaning in [(1.,'N62 → N64','+1.08%','Full-run goodput gain'),(5.1,'N64 REPEAT','0.014%','Difference from first N64 run'),(9.05,'N64 → N68','+0.08%','Full-run gain: too small')]:
 s.text(label,x,1.85,3.6,.56,21,GRAY,bold=True);s.text(value,x,2.96,3.6,.8,35,ORANGE if x<9 else GRAY,bold=True);s.text(meaning,x,4.05,3.6,1.1,20)
s.text('Decision: keep N64; do not promote the short-test N68 peak.',1.,5.75,11.2,.80,24,bold=True)
s.end()
''')
replace('# 13 —','# 14 —', r'''# 13 — Explain why packaging validation changes confidence
s=slide('Portable acceptance','28194health200/models503readinessrace repaired via boundedmodelregistrationwait;28197fullentrycompleted611seconds16H200N64,3051.518173goodtokens/s,1881/1907jointSLApases. Oneacceptedportabledeployment, notmatchedspeedup. Historicalmean3044.400475 separate; lowerlegacy2830.923547unresolved.','28194 failure;28197 reviewed acceptance;historical repeats')
s.text('A fast research run is not yet a verified submission entry.',1.,1.52,11.2,.80,27,bold=True)
arrow_chain(s,['Wait for a\nregistered model','Serve both\nP/D routes','Run client, read\nresults, clean up'],y=3.0)
s.text('3,051.52',1.,4.83,5.0,.83,38,ORANGE,bold=True)
s.text('good output tokens/s · accepted packaged entry',5.05,5.03,7.1,.65,23)
s.text('The complete entry passed once; this verifies execution, not a new speedup.',1.,6.25,11.2,.57,18,GRAY)
s.end()
''')
replace('# 14 —','# 15 —', r'''# 14 — Transferability is a question, not a hardware conversion
s=slide('Transferability','H100 settings were hypotheses to verify directly on H200. Nine final allocations include controls and ports. RecipeN64-10.4083%,samechunk8192HPCprefill-4.5232%;phase-modepointspositivebut<.14% againstowncontrol. Noneclears1%usefulgate. Donotsayallcandidateswerelower.','31October transfer/chunk/phase reviews')
s.text('Could an H100-derived choice improve the H200 service?',1.,1.52,11.2,.76,27,bold=True)
for x,label,value,detail in [(1.,'RECIPE PORT','−10.41%','Worse than its H200 control'),(5.1,'REFINE CHUNK','−4.52%','Recovers part of the loss'),(9.05,'PHASE MODES','< +0.14%','Small positive points')]:
 s.text(label,x,2.84,3.6,.61,18,GRAY,bold=True);s.text(value,x,3.76,3.6,.73,32,RED if x<9 else INK,bold=True);s.text(detail,x,4.82,3.6,1.,19)
s.text('Decision: retain the H200 recipe; no useful improvement above 1%.',1.,6.13,11.2,.75,23,bold=True)
s.end()
''')
replace('# 16 —','# 17 —', r'''# 16 — Final synthesis: decisions supported by separate evidence
s=slide('The retained recipe survives performance and quality checks','The team contribution combines a bounded metadata implementation, controlled phase-specific serving selection and reproduciblevalidation. Reusedkernels/transferlibrarynotteaminventions. Performance28197=3051.518173goodtokens/s in611seconds; localMMLUPro9452/9460=99.915433%retention,notBTCcertification. Noadditionalinferenceperformedforthispresentation.','accepted28197;fullqualitycomparison;matchedbackend/loadreviews')
for x,label,value,unit in [(1.,'VERIFIED SERVING ENTRY','3,051.52','good output tokens/s'),(7.,'FULL LOCAL QUALITY CHECK','99.9154%','of measured stock-reference accuracy')]:
 s.line(x,1.70,x+5.1,1.70,ORANGE if x==1 else INK,2);s.text(label,x,1.96,5.1,.42,16,GRAY,bold=True);s.text(value,x,2.65,5.1,.83,36,ORANGE if x==1 else INK,bold=True);s.text(unit,x,3.57,5.1,.61,18)
for i,text in enumerate(['Choose implementations for the phase and hardware.','Keep gains that survive full comparisons and repeats.','Validate deployment and answer quality separately.']):
 y=4.67+i*.56;s.rect(1.,y+.07,.10,.20,ORANGE);s.text(text,1.3,y,10.9,.45,20,bold=i==1)
s.text('Local MMLU-Pro verification; the organiser quality decision remains separate.',1.,6.59,11.2,.33,15,GRAY)
s.end()
''')
replace('# 19 —','# 20 —', r'''# 19 — Full quality detail belongs in Q&A
s=slide('Backup · full-set accuracy verification','Same16H200 bothroles,stockreference9460/12032candidate9452/12032. Accuracy78.623670/78.557181%;retention99.915433%. All16jobscomplete0errors,101invalidperrole,1484/1468lengthcapsretainedscorednormally. Onepassperrole,876discordantcorrectnessoutcomes,categorylossesretained. NotBTCcertification.','quality-verification-20261102 completecomparison andindependentreplay')
s.text('Same checkpoint · same questions · same 16 H200',1.,1.53,11.2,.56,24,bold=True)
for x,label,accuracy,count,col in [(1.,'STOCK FP8 REFERENCE','78.6237%','9,460 correct /12,032',INK),(7.,'OPTIMISED SERVICE','78.5572%','9,452 correct /12,032',ORANGE)]:
 s.line(x,2.53,x+5.1,2.53,col,2);s.text(label,x,2.75,5.1,.42,17,col,bold=True);s.text(accuracy,x,3.43,5.1,.73,34,col,bold=True);s.text(count,x,4.38,5.1,.48,21)
s.text('Accuracy retention = 9,452 /9,460 = 99.9154%',1.,5.40,11.2,.65,28,bold=True)
s.text('All 16 jobs completed · zero service errors · local 99% point gate passes',1.,6.32,11.2,.49,18,GRAY)
s.end()
''')
exec(compile(source,str(source_path),'exec'),globals())

from pathlib import Path
import datetime,hashlib,json,re
W=Path('/home/apacsc42/workspace');J=W/'reports/research-journey-20261019/journal';O=W/'submission-review/ai-journey-update-20261030'
text=(J/'JOURNEY.md').read_text();stages=re.findall(r'^## (\d+)\. (.+)$',text,re.M);assert len(stages)==32
mapping={
1:('3','Direct','Official objective and per-request gates'),
2:('4, 31','Condensed','Platform/launcher explanation; routine shell learning stays in tutorial'),
3:('6','Direct','07/09 measured comparison'),
4:('6, 8','Direct','14 measured originals plus three EP2 replacements; failures retained'),
5:('7, 8','Direct','Separate block incompatibility, startup and transport'),
6:('7','Direct','Whole pool to request-scoped transfer with geometry checks'),
7:('7, 22','Condensed','Real transfer and response gates; repaired paths are not automatically selected'),
8:('5, 15, 27','Direct','Selected roles and observed decode operating range'),
9:('28, 30','Direct','Capture/padding and chunk experiments'),
10:('22','Direct','Local output baseline versus official accuracy'),
11:('12, 21','Direct','Load range and short-to-full stopping decision'),
12:('5, 11; speaker context','Condensed','Round-robin admission motivation; historical pilot is not a current isolated gain'),
13:('11, 14','Direct','Backend effects depend on pipeline and operating point'),
14:('13, 17, 26','Direct','Profile-driven collective and attention questions'),
15:('26','Direct','DP-attention package changes several factors; no competitor-result inference'),
16:('11, 14','Direct','Interactions and independent repeats'),
17:('4, 16, 19, 20','Direct','Commission and compare platforms separately'),
18:('18','Direct','Startup question, reversed pair and failed cost gate'),
19:('2, 16, 26; notes','Condensed','Observed frontier separated from design/source-only alternatives'),
20:('10, 14, 26','Direct','Phase-specific DeepGEMM, with representative-kernel detours qualified'),
21:('15, 28; notes','Direct','Raw first-cohort TTFT evidence remains in score'),
22:('13, 25, 28; notes','Condensed','Graph choices and kernel-classifier corrections; kernel sums are not wall time'),
23:('16, 26; notes','Condensed','H100 HPC-Ops decode path has a separate platform series'),
24:('16, 26; notes','Condensed','H100 prefill/chunk path and negative followups; no pooled hardware score'),
25:('30','Direct','Larger H200 prefill chunks lose in the retained pair'),
26:('7, 22; notes','Direct','Quarantine superficially running equal-TP path on SLA/output evidence'),
27:('10, 14','Direct','H200 runner/chunk interaction'),
28:('12, 14, 25','Direct','Exact configuration and protocol replication'),
29:('17, 26; notes','Condensed','H100 prefill/collective/attention branches close at tested settings'),
30:('13, 26, 31; notes','Direct','Correct reviewer and symbol-based interpretations without rewriting raw runs'),
31:('18, 26; notes','Condensed','CPU/static locality and phase hypotheses are leads, not CPU-bottleneck proof'),
32:('9; this coverage record','Outside visible narrative','Full reasoning and provenance live in journal, report and source index'),
}
later=[
('N62/N64 replication and N68 short/full reversal','12, 25','Question → prospective full test → repeat → reject a short-only apparent gain'),
('EAGLE dtype/KV/transport and role-aware validator recovery','7, 22, 23','Failed placement → validator defect → corrected short trial → full shallow loss'),
('Modern-regime recovery and graph/admission controls','25','Observed drift → resolved-argument inspection → isolated controls → unresolved causal variation'),
('Source-supported tokenizer and prefill collective choices','21','Exact-ID preflight and actual native dispatch → full paired points → no useful gain'),
('Portable replay namespace and canonical alias corrections','31','Static pass → real client success but failed postprocessing → second defect → compute verification'),
('Sparse capture tradeoff, model compile and C++ prerequisite','26, 28; notes','Activation/build proof remains separate from model correctness and goodput'),
]
families=[
('EAGLE and draft integration',[7,22,23],r'eagle|draft|s61|aux-slot|full-span|exit-boundary|login-shell|nonlogin'),
('Transport, KV and semantic correctness',[7,8,22],r'nixl|descriptor|registration|peer|kv-|pd-|pair-warmup|prefill-readiness|source-location'),
('Topology and layout',[5,6,8,26],r'topology|two-decode|p12|five-rank|s62|fanout'),
('Replication, load and regime recovery',[10,12,25],r'n62|n64|n68|incumbent|legacy|full-load|load-bracket|factorial|s70|s73|s68|s63'),
('Tokenization, routing and collectives',[11,21,26],r'tokeniz|routing|collective|fusion'),
('Graph, chunk, attention and cache choices',[17,21,26,28,30],r'graph|chunk|cache|backend|attention|cap64|poll|recv'),
('Model compile and prerequisites',[26,31],r'compile|cpp|delayer|continuous-decode'),
('Runtime, portability and reader recovery',[4,25,31],r'portable|artifact|reader|mount|storage|native-entry|gpu-map|runtime|warmup'),
('Measurement, profiling and quality',[3,9,13,15,22,29],r'observability|kernel|cpu-envelope|locality|output|correctness|reference|token-count|precision|fp8'),
]
manual={'20261020-deepinfer-review': ('Source/library feasibility', [26]), '20261020-h100-restored': ('Operations and documentation', [4, 9, 31]), '20261020-h200-homebind': ('Runtime, portability and reader recovery', [31]), '20261020-observer-results': ('Measurement, profiling and quality', [13, 26]), '20261020-prefetch-reverse-confirmation': ('Startup and resource-cost hypotheses', [18]), '20261020-research-priorities': ('Research method and decisions', [9, 24, 32]), '20261020-startup-prefetch': ('Startup and resource-cost hypotheses', [18]), '20261020-upstream-review': ('Source/library feasibility', [3, 26]), '20261021-bash-dispatch-repair-submission': ('Runtime, portability and reader recovery', [31]), '20261021-complete-submission': ('Operations and documentation', [31]), '20261022-h200-full-asset-identity': ('Measurement, profiling and quality', [22, 27]), '20261022-h200-wave-review': ('Research method and decisions', [9, 21]), '20261023-h100-geometry-gate-correction': ('Transport, KV and semantic correctness', [7, 22, 23]), '20261023-h100-production-geometry-submitted': ('Transport, KV and semantic correctness', [7, 23]), '20261023-h200-worker-byte-identity-repair': ('Runtime, portability and reader recovery', [25, 31]), '20261024-five-job-hypothesis-wave': ('Research method and decisions', [9, 21]), '20261024-observer-preflight-submitted': ('Measurement, profiling and quality', [13, 26]), '20261025-configured-n-and-first-transfer-fix': ('Transport, KV and semantic correctness', [7, 12, 31]), '20261025-h200-router-matched-plan': ('Tokenization, routing and collectives', [5, 11, 21]), '20261026-h100-225306-launcher-failure-and-repair': ('Runtime, portability and reader recovery', [31]), '20261026-h100-control-and-equal-tp-functional-pass': ('Transport, KV and semantic correctness', [7, 16, 23]), '20261026-h100-followups-225227-225228': ('Replication, load and regime recovery', [16, 23]), '20261026-h100-scored-resource-window': ('Measurement, profiling and quality', [13, 16]), '20261026-recovery-offline-reviewer-prepared': ('Replication, load and regime recovery', [25, 31]), '20261030-final-ai-report-and-sparse-result': ('Graph, chunk, attention and cache choices', [24, 28])}
index=[];unrouted=[]
for p in sorted((J/'entries').glob('*.md')):
 body=p.read_text();name=p.stem.lower();title=next((l.lstrip('# ') for l in body.splitlines() if l.startswith('# ')),p.stem)
 if re.search(r'(^|-)hpc-|openfoam|iris-',name):
  scope='Independent HPC record; excluded from AI coverage';slides=[];family='Other track'
 elif re.search(r'presentation|slide|learning|track-routing|session-track|access|vpn|budget|credit|owner-removes|registration|source-freeze',name):
  scope='Supporting operations/provenance; not a visible research-result claim';slides=[4,9,31];family='Operations and documentation'
 else:
  found=manual.get(name) or next(((n,s) for n,s,pattern in families if re.search(pattern,name)),None)
  if found:family,slides=found;scope='Supporting scientific arc; grouped navigation, not a claim of full paragraph-by-paragraph slide coverage'
  else:family='Unclassified supporting record';slides=[];scope='Needs manual routing if selected for a detailed oral account';unrouted.append(p.name)
 index.append({'path':str(p),'title':title,'family':family,'slides':slides,'scope':scope,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
lines=['# AI journal to presentation coverage','',
'Updated 30 October 2026. This is an honest content audit, not a claim that every journal paragraph is visible in the deck. The shared journal also contains independent HPC records and routine submission/access records. A plan, receipt, correction and result for one hypothesis are grouped into one scientific arc.','',
'## Audit conclusion','',
'The previous 32 AI slides covered the architecture and result spine, but compressed several hypothesis/diagnosis/decision sequences. This update makes the transport recovery, reversed startup test, failed EAGLE progression, source-guided small trials, regime-recovery controls and real deployment corrections explicit. The talk remains 32 AI slides plus the unchanged eight HPC slides.','',
'“Direct” means the scientific turn is visible on the named slides. “Condensed” means the visible narrative and notes summarize a broader branch; it is not every trial. “Outside visible narrative” identifies material retained in the journal/tutorial/report rather than presented as a scientific achievement. No unsupported completeness percentage is reported.','',
'## All 32 stages in the initial retrospective','',
'The retrospective was assembled from retained written records through 19 October; it is not a verbatim reconstruction of every past conversation.','',
'| Stage | Research turn | Slides | Coverage | What is explained |','|---|---|---|---|---|']
for n,title in stages:
 s,status,explain=mapping[int(n)];lines.append(f'| {n} | {title} | {s} | {status} | {explain} |')
lines+=['','## Later research arcs','', '| Arc | Slides | Reasoning retained |','|---|---|---|']
lines.extend(f'| {a} | {b} | {c} |' for a,b,c in later)
lines+=['','## Supporting entry index','',
'The following index routes source entries to a research family. Routing uses titles/filenames to make navigation reviewable; it is not semantic certification that each entry is completely narrated. The curated stage/arc tables above define the assessed presentation coverage. Administrative records and the independent HPC track are explicitly distinguished.','']
for family in dict.fromkeys(r['family'] for r in index):
 lines+=['### '+family,'']
 for r in index:
  if r['family']!=family:continue
  target=Path(r['path']).relative_to(W)
  lines.append(f"- [{r['title']}](../../{target.as_posix()}) — "+('slides '+', '.join(map(str,r['slides'])) if r['slides'] else r['scope'])+'.')
lines+=['','## Limits and use in the talk','',
'Use the main talk to explain why the team changed direction, what control made a result interpretable, what failed and what was learned. Use speaker notes and this index for questions about a particular run. No startup, CPU primitive or library-feasibility result is promoted to a serving improvement. Official model-quality acceptance remains unverified.','',
'This audit does not certify every retained historical claim, fill missing original reasoning, or resume research. No new job, authentication or HPC update is performed.']
report='\n'.join(lines)+'\n'
# Relative links above are designed from workspace/reports/ai-final-report-20261030/.
report=report.replace('](../../reports/research-journey-','](../research-journey-')
out=W/'reports/ai-final-report-20261030/JOURNEY_COVERAGE.md';out.write_text(report)
(O/'JOURNEY_COVERAGE.md').write_text(report)
(O/'journal-source-index.json').write_text(json.dumps({'entries':index,'unclassified':unrouted,'scope':'Title-based navigation with curated stage-level content audit, no completeness percentage.'},indent=2)+'\n')
print(json.dumps({'retrospective_stages':len(stages),'shared_journal_entries_indexed':len(index),'unclassified_titles':unrouted}))

# Replicate MNNVL + FlashInfer and refresh the matched control

2026-10-16: continuous-research scope extended after all wave9 measurements
completed. Earlier handoffs saying no new repeat were wave9 stopping decisions,
not a user cancellation of the continuing optimization request.

23904 N52=2631.0854goodt/s,SLA99.022%,ITL16.233ms,0errors/cancel.
MNNVL23778/23839 mean2592.543: gain1.4867%, currently single observation.
Chunk2048/8192 were slower; do not spend slots repeating losing chunks.

Fill three available slots under sharedcap5 with two independent N52 combo
replications and one fresh MNNVL N52 control. Preserve23924/23934 queue positions.
Compare every run, baseline means and time drift; do not select only peak score.
Full60/120/30 and frozen model,KV,placement,engine flags remain unchanged.
Second combo run includes12 synthetic~3800token retrieval checks AFTER ranked
measurements; retain raw results and explicit failure/deferred marker.
No new higher-load gate or N56 is introduced. Existing wave7/8 N54 continues.

Decision: require each combo repeat full protocol,SLA>=90%,0errors/cancel and
no new short-output failures before calling gain reproduced. Compare against
all three MNNVL controls; new long failures block quality claims and require
investigation. Accuracy99%reference remains unverified regardless of result.
After these runs, select the next load based on repeated goodput and ITL
headroom, record an explicit next-step plan, and keep useful queue slots filled.

## Bounded extension after sealed N54 result — 16Oct2026 05:20 UTC

23924 completed successfully at04:31:37UTC. Independent sealed/raw/runtime review
finds2634.0344goodt/s,SLA98.9024%,TTFT600.4446ms,ITL17.1102ms,zero request
errors/cancellations and no new short failures. Versus both MNNVL N52 controls
and their mean, gain is+1.6153%/+1.5855%/+1.6004%; mean TTFT rises88.1784ms.
One observation does not establish a repeatable load gain. Comparison with
FlashInfer N52 is confounded by both load and backend; do not attribute kernels.

Use the single freed shared-cap5 slot for exactly ONE independent MNNVL N54
repeat, s10-mnnvl-repeat-n54. This is an explicitly planned continuation of the
authorized research, not an automatic continuation of the closed wave7 plan.
Keep all12 execution files, actual N54 load and60/120/30 protocol identical to
23924; only experiment/purpose and launcher name/path change. The config's
wave7/matched_concurrency52 fields remain inherited provenance; the actual
launcher and planned_ns specify54. Existing queued bundles remain frozen.
Reuse the live watcher's prepared-pilot loader; no second watcher or controller.
No new automatic retry or higher-load gate is added by this extension.
The existing watcher still permits budget-deferred replacement attempts (at
most three total attempts), only for an incomplete point with deferred markers.
This is one independent confirmation point, not a promise of one allocation.
Preserve every failed attempt; a further successful confirmation is not planned.

Review the repeat against23924, both historical N52 controls and the fresh
23974 control. Report each result and means, full SLA/error/output/runtime,
TTFT/ITL tradeoffs and control drift. Same-backend N52-to-N54 comparisons
measure load; DP N54 awaits23934. An incomplete/failed repeat remains evidence,
and no third repeat is planned here. No N56 or configuration promotion.
Combo N54 still requires the existing wave10 repeat and long-diagnostic gates;
this MNNVL repeat does not waive them. Accuracy99% remains unverified.

Evidence and staging validation: nscc-pbs/inspection/wake-20261016-0520UTC/.

Watcher419440 submitted24009 at05:23UTC; checked05:24:11UTC it and23934,
23973–23975 are PENDING(Resources),5/5slots. Stored24009 launcher matches frozen.
Use review-mnnvl-n54-repeat.py after sealing; if replacement attempts occur,
the reviewer explicitly requires manual review rather than silently picking one.

## Next-step decision after DP N54 —16Oct2026 10:28UTC

23934 final review passes full protocol/runtime/outputs at2555.4232goodt/s,
SLA98.7484%, but gains only0.4633%over its N52mean whileTTFT rises145.1971ms.
It is2.9844%below23924 MNNVL at the sameN54. Close the bounded DP wave here;
no extraDP repeat or blindN56. [Evidence](../serving-tuning-08/DP_N54_RESULT.md).

Fresh scheduler10:25UTC has23973/23974/23975/24009 PENDING(Resources),4/5slots;
watcher419440 remains alive. Preserve all four frozen jobs and queue positions.
Next useful step is review-wave10.py after each seal and
review-mnnvl-n54-repeat.py for24009; do not rerun unchanged waiting-path audits.
Read23975 long PASSED/FAILED/DEFERRED separately and compare both combo repeats
with fresh23974 and all controls. Only if the existing full combo gain/SLA95%/
ITL19.3/zeroerror/short/long gate passes, write a bounded comboN54 plan with
one point, unchanged execution except actual load52→54 and experiment labels,
maximum17minutes/16H200, source review and fresh ownqueue before arming via
existing watcher. This conditional plan is not a submitted job or promotion.
If gates fail or freshcontrol drift removes gain, retain negative evidence and
investigate the observed cause; do not fill a slot with arbitrary variants.
MNNVL24009 is the one planned confirmation; no third successfulrepeat/N56.

## Bounded combo N54 — 2026-10-16T17:26:33.814483+00:00

Three combo N52 measurements2631.085/2632.065/2632.610; mean2631.920,
+1.4995%vs three MNNVL controls mean2593.038. Freshcontrol drift+0.0573%.
Full protocol/runtime/short checks pass;23975 long12/12PASSED. SLA>=95%,
ITL<=19.3ms gate satisfied. Source review: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/manual-20261016-status/wave10.json

Arm exactly one new combo N54 point via existing watcher. Same execution as
23975 including long diagnostic; only load52→54 and experiment metadata/path
change.16H200/17min, cap5 own jobs; no N56, third repeat or promotion.
Compare with all comboN52 runs and MNNVL N54 runs (23924 and24009 when ready).
Review every raw/sealed protocol, errors/SLA/short/long and runtime; preserve
failed/deferred attempts. Existing bounded incomplete-point retry policy remains.
Accuracy99% organiser reference remains unverified.

## User-authorised confirmation pair — 2026-10-17T00:54:59.624020+00:00

User requested auth and more submissions.24131 fullprotocol/runtime/short/long
passes at2654.172goodtok/s,SLA98.9117%,TTFT736.693ms,ITL16.2688ms.
N54 gain vs23975N52 is0.8190%,single observation. Submit exactly TWO points:
comboN52 freshcontrol followed by independent comboN54 repeat (independent
allocations; no scheduler dependency needed for Slurm capacity). Same execution
including12longretrievals,model/backend/topology/seed policy; onlyexperiment/path
and actual concurrency differ.16H200/17min each,sharedcap5. NoN56, no newMNNVL-only
repeat or promotion. Review allcomboN52/N54 observations,drift,SLA/errors/short/long.
A secondN54 allocation tests replication rather than assuming the small gain.
Existing deterministic watcher may be restarted for this explicitly requested
GPU work; Codexautopilot and cron remain disabled.

## Bounded continuation — 2026-10-17T02:23:59.415386+00:00

User requests immediate continued submissions. Amend old noN56 restriction based
on two sealed passing comboN54 runs2654.172/2658.195, SLA98.91%, ITL16.25ms,
short/runtime passes and both12longpass. Submit freshN54 control and exactlyone
N56 capacity probe,16H200/17min each,cap5. Same execution/model/backend/long checks;
only load and labels change. Compare allN54 controls; report TTFT/ITL/goodput/SLA,
not only peak. NoN58, auto retry expansion or promotion; full accuracy unverified.

H100:sealed220999fullprotocol/short/long passes,N48=2204.528/SLA98.766%;
MNNVLaloneN48failed80.49%,whileN46ties. Actual combo task log confirms MNNVL
ranks0..7,FlashInferattentionranks0..7,BF16KV. Submit matched independent
MNNVL46/48 thencombo46/48,stoploadincreaseonfail. This confirms frontier
interaction instead of assuming causality from one fail/pass. Each16H100/45min,
strictafterany,max1running,3072SUmaxreserve;noN50. Budgetused10598.401SU,
remaining5785.599 before newreserves,projectbalance53401.599,InDoubt0.
No new Codex automation; deterministicSlurmwatcher restarted only for this GPUwork.

# Bounded continuation — 2026-10-17T06:51:34.960356+00:00

User asks continue within existingbudget; noCodexautopilot. All source jobs now
terminalexit0. H200sealedfullprotocol/runtime/short/long passes:24189N54=2658.547,
24190N56=2671.109,SLA98.800%,TTFT847.849ms,ITL16.287ms,long12/12. ModestN56gain
is provisional. Send exactlyoneN56repeat andoneN58probe16H200/17min; this amends
previousnoN58basedonnewN56evidence. Sameexecutionexceptload/metadata;noN60.

H100repeat221021comboN48=2190.538/SLA98.759%,versusprior2209992204.528/98.766%.
MNNVLaloneN48againfailsSLA64.211%;N46passes2182.281. ComboN46slower2143.069,
so no universal speedupclaim. Bothlonglogs12/12;fullsealed review mustpassbeforeqsub.
Two useful nextpoints: MNNVLN47 midpoint (between repeated46pass/48fail), and
combo48anchor/50/52capacitysweep,stopfirstfailedSLA/error. Sameexecution/quality.
Do not promote or claimaccuracy99%; no automaticrepeat orN54H100.

EachH100allocation16GPU45minmax1536SU;strictafteranychain,max1running,cap3.
Used12487.681SU,remaining3896.319;newmaxreserve3072leaves824.319SU. Preserveproject
13000SU. Reconcile old1889.280SUcharges andfreshqueue/credit underbudget.lock.
No further45minH100jobfits afterreserves withoutactualcostreconciliation.

## Profile new winner after load plateau — 2026-10-17T08:59:31.479322+00:00

N56replicate24235=2669.803,SLA98.801%,long12/12;N58/24236=2667.966,
SLA98.683%,TTFT991.136vsN56~850ms. Bothsealedruntime/protocol/shortpass.
Close blindloadincrease;noN60. One useful17min16H200allocation:unchanged
comboN56benchmark followed by separate52-requestdiagnosticprofile onall16ranks
using existingprofile-serving.py. Oldprofile23607predatesMNNVL/FlashInfer;
newtraceguidesnextkernel/communicationhypothesis. Sameweights/protocol/flags,
onlypostmeasurementprofilingenabled.12longchecksafterprofilingmaydefer ifslow;
reportdeferred,nevercountprofilingtrafficintorankedresult. Maxoneprofileallocation,
noautomaticprofilingretry/promotion. Inspectall16ranktracesbeforekernelsummary.

## Empirical cross-platform estimate validation — 2026-10-17T09:13:02.173974+00:00

UserasksestimateH100resultsontoH200andvisualcomparison. Calibrate SAMEcomboN52:
H200mean2632.1809(23904/23973/23975/24174),H100mean2215.4600(221052/221058),
ratio1.1880968. PredictH100winningN50mean2223.9295→H200N50~2642.2435.
Oneanchoronly,loaddependent,notuniversalhardwarefactor/officialscore.
SubmitexactlyoneH200N50fullprotocol+short/longpoint16GPU17min,samefrozencombo
executionexceptload/labels tovalidatepredictionandcomparesameN50. Existing
profile24263queuepositionpreserved,noadditionalH100creditneeded. Noautomatic
repeat,newloadorpromotion. Aftermeasurementreportpredictionerrorandlatencies.

# Prefill interaction pilots — 2026-10-17T09:57:45.486189+00:00

User asks whether existing evidence justifies more H200experiments. Yes, two
bounded new interactions, independent of pendingprofile/holdout. No claim that
TTFT growth identifies a bottleneck by itself.

Evidence: N52combo ITL~16.23ms/TTFT~634ms;N56~16.27ms/~850ms;N58~16.27ms/~991ms
withgoodputplateau. Wholeprefillworkerlogs contain far more multi-sequence steps
atN56/N58 thanN52 (prefill-observations.json). Logs mixstartup/warmup/measure/long,
so counts are descriptive, not isolated phase-level causal evidence.

A. Same2xTP4prefills, addonly--prefill-max-requests1,chunk4096unchanged.
Hypothesis: fewer carried-over requestfragments improve firsttoken latency and
continuousdecodefeed;counterhypothesis:lostMoEbatchingreducesgoodput. Old23324
showedonly0.34%single-run gain undercacheawarerouting BEFOREcurrentRR/MNNVL/
FlashInfer;itdoesnotestablishinteractioninthenewwinner. This isexplicitlyone
newinteractiontrial,notrepeatoflosingchunk2048/8192jobs.

B. Same8P+8DGPUs,replace2prefillworkersTP4EP1with1prefillworkerTP8EP1.
DecodeTP8EP8/MNNVL/FlashInferunchanged. Hypothesis:lowerperrequestprefilllatency
orlessreplicaimbalancereducesTTFT;counterhypothesis:loseprefillparallelismand
additionalTPcommunicationhurts. Resourcefactorisparallelism/replicationplan,
notasinglescalarflag. KVtransfernowequalTP8;originalequalTPpatchpathretained.
Launcherderivesplacementandwarmup1pair;manualreviewmustexpect1P/Dpathand
prefilllogTP8,notreusehardcoded2workerreviewerblindly. Modelheads/runtimecompatibility
stillrequireactualGPUstartup;do notcountfaileddeploymentasmeasurement.

Primaryrefs:DistServe https://arxiv.org/abs/2401.09670v3 supportsphase-specific
parallelism/resourceoptimization,notaspeeduppredictionforQwen.
SGLang https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning
motivatesrequest/compute/memorytradeoffs;offlinebatchsaturationadviceisnotourSLO.
Exactstagedserver_args.py snapshotdeclaresprefill_max_requestsOptional[int],
unlimiteddefault. Runtimeworkerlogsandfrozenpayloadarequantitativeevidence.

BothfullN56,16H20017min,BF16KV/officialFP8/routerRR/client60/120/30+short+12long
unchanged. Existing24263N56benchmark(beforeprofiler)servesfreshcontrol;also
compare24190/24235andallcontrolsfor drift. Requirezerorequesterrors/cancel,
SLA>=90%,shortnonregression,longPASSED,correctruntime. Reportnegativefindings.
Anywinnerneedsindependentrepeatbeforepromotion;noautomaticrepeat,newloador
H100qsub. Twoexistingpendingjobs+two new=4/5cap;preservequeuepositions.
Profilemayoverturnthesehypotheses;do notattributekernelcausewithouttraces.

## Prefill-only DeepGEMM — 2026-10-17T10:57:00.099377+00:00

[Evidence and bounded plan](profile-review-24263/RESULTS.md). One N56 trial,
16H200/17min, full protocol and quality checks. This changes prefill, whereas
the previous rejected DeepGEMM trial changed decode. No automatic repeat.

# Parallel experiments on H100 and H200

The user authorised continued submissions on both servers after clarification that the previous 16,384 SU campaign cap was an assistant planning choice, not the competition quota. H100 has 48,463.075 SU remaining in the last project ledger. Reserve at most 4,608 SU for this batch and retain a conservative 13,000 SU project buffer. H200 has no credit constraint reported by the user; the scheduler still limits active jobs.

| Platform | Job | Experiment | Maximum allocation |
|---|---|---|---|
| H100 | 221151 | Fresh combo control, concurrency 50 | 16 GPUs, 45 minutes |
| H100 | 221152 | DeepGEMM for prefill only, concurrency 50 | 16 GPUs, 45 minutes |
| H100 | 221153 | Weight prefetch for prefill only, concurrency 50 | 16 GPUs, 45 minutes |
| H200 | 24320 | Fresh combo control, concurrency 56 | 16 GPUs, 17 minutes |
| H200 | 24321 | One TP8/EP2 prefill worker, concurrency 56 | 16 GPUs, 17 minutes |
| H200 | 24322 | Weight prefetch for prefill only, concurrency 56 | 16 GPUs, 17 minutes |

H100 jobs form a verified afterany chain: 221151 → 221152 → 221153. The first job waits for resources; the other two have dependency holds. These holds are expected. H200 jobs are submitted by the existing non-AI watcher, with at most five active jobs.

## Questions and controls

DeepGEMM changes only the prefill MoE runner. Decode retains MNNVL and FlashInfer. H200 profile traces motivated the hypothesis; they do not prove a wall-time bottleneck or an H100 gain. Job 24291 has now passed full protocol, runtime, SLA, short output and 12 long checks: 2,715.842 good tokens/s, SLA 98.8194%, or +1.8136% versus control 24263. An independent H200 repeat is armed to confirm the gain against the new control. This does not verify the organisers' full accuracy requirement.

Weight prefetch targets startup time and allocated GPU cost. It need not improve benchmark throughput. Compare weight loading timestamps and allocation walltime with the new controls. Node storage, file cache and sequential ordering remain confounders; one observation is not causal proof of faster loading.

The TP8/EP2 prefill trial repairs the failed TP8/EP1 geometry in job 24282. The model has MoE intermediate size 1,536. MoE tensor parallelism is TP / EP / DP: TP8/EP1 gives 192 elements per partition, incompatible with the FP8 block size 128. TP8/EP2 gives 384, divisible by 128. This changes the prefill parallel layout without changing the checkpoint or precision. GPU startup and output quality still need validation. Treat it as a combined layout change, not an isolated TP speedup.

## Evidence and stopping rules

Keep the full 60-second warmup, 120-second measurement, 30-second grace, 4,000 input tokens and 200 output tokens. Preserve FP8 model weights, BF16 KV cache and the output checks. Require sealed raw evidence, intended runtime settings, no request errors or cancellations, and quality checks before accepting results. Useful gains need independent confirmation before selection.

Do not repeat the single-request prefill branch: job 24281 lost 1.73% goodput. Do not blindly increase concurrency beyond the observed plateau. Preserve all failed attempts. No Codex autopilot or new background AI session is enabled.

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

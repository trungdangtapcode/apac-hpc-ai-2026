# Profile the actual H200 interaction

## Question and measurement

Does the source-backed H200 interaction still spend meaningful GPU time in communication, MoE and attention? Job 24819 repeats the exact N58 HPC-Ops decode/DeepGEMM prefill chunk8192 deployment, scores 2937.148, then profiles separate N48 diagnostic traffic. All 16 rank traces are nonempty and match the terminal seals; 425/425 diagnostic requests succeed. The ranked score and profiler traffic remain separate.

## Observations

On decode, named HPC group GEMM contributes **21.642%** of summed recorded kernel duration. Named MNNVL all-reduce/RMSNorm kernels contribute **23.479%**; named FlashInfer paged-attention kernels contribute **15.064%**. Prefill traces show named DeepGEMM kernels, FA3 attention and collective work. The NCCL LL-labelled symbol does not identify selected protocol; retain the 19 October correction.

These are descriptive sums across ranks/events, not elapsed critical-path shares or predicted speedups. The separate N48 diagnostic does not reproduce every ranked N58 batch or queueing event. The name-based DeepGEMM field is not an asserted partition of all MoE computation.

## Assessment and next decision

The actual winning platform still has a relevant collective cost, so source-supported collective and MoE implementation research is justified after the N60/N62 controlled wave. The cheap H100 MNNVL strategy screen can narrow hypotheses, but cannot establish H200 performance. Do not force a strategy across platforms from one microbenchmark or convert a kernel fraction into model throughput. Require actual platform-specific model/control and output/latency checks for a serving claim.

Raw sealed traces are under runs/24819/diagnostic-profile; h200-winning-n58-profile.json retains rank hashes, top kernels and recorded protocol. No new model score or official accuracy claim is made by this analysis.

## Instrumentation-control clarification — 20 October 2026

A later log audit confirms three start-profile HTTP 200 calls were misclassified by the helper's unconditional JSON decoder; stop calls returned HTTP 500 with `Profiling is not in progress`. These controller errors are distinct from the 425 successful diagnostic generation requests. All 16 sealed trace files remain available for the descriptive kernel analysis above, but the controller flow was not clean. A derived response-parsing fix is prepared and locally tested for future bundles, not retroactively deployed. [Error triage and limits](../observability-review-20261020/REPORT.md). Do not infer that all recorded errors were Slurm cleanup or that the parser fix suppresses stop failures.

# DP + DeepEP N54: final review, 16Oct2026 10:28 UTC

Job23934 completed exit0 at08:11:21UTC after9m17s. Fresh sacct10:25 agrees
with the terminal seal. All47sealed files rehash, frozen submitted payload and
12execution files match BOTH DP N52 controls23780/23859. Full60/120/30 and
actual phase timing pass:802warmup,1598profiling requests, zero errors/cancel.
Eight NIXL decode ranks and both P/D warmups pass. Resolved ServerArgs match
both controls except engine random_seed: TP8/DP8/EP8, attentionDP, DeepGEMM,
DeepEP low_latency, dispatcherFP8. Raw132baseline and8candidate output cases
were rescored; candidate remains7/8, only the known reverse failure.

| Point | Good tokens/s | SLA | TTFT ms | ITL ms |
|---|---:|---:|---:|---:|
|DP N52 mean23780/23859|2543.6386|see individual runs|606.7911|16.9590|
|DP N54 23934|2555.4232|98.7484%|751.9882|16.8873|
|MNNVL N54 23924|2634.0344|98.9024%|600.4446|17.1102|

DP N54 vs EACH N52:+0.2443%/+0.6833%; vs mean:+0.4633%, TTFT+145.1971ms,
ITL−0.0717ms. Versus MNNVL at the SAME N54:−2.9844%goodput,
TTFT+151.5435ms, ITL−0.2229ms. One N54 observation per package does not prove
repeatability, statistical significance or an isolated kernel effect. Engine
seed/node/time can confound. Observed199–200tokens; metric convention stays
200tokens per good request. KV auto is not independent proof of effective dtype.

Decision: close the existing bounded three-point DP branch at N54; do not open
another DP repeat or N56 on this small load gain. Prioritize the queued MNNVL
N54 confirmation and combo N52 replications/fresh control/long diagnostic.
No promotion or organiser accuracy claim. Leave the fifth slot free until a
useful next experiment meets the documented gates; queue capacity alone is not
a research hypothesis. No scheduler/payload/watcher changes in this review.

Evidence: [full N54 review](../nscc-pbs/inspection/wake-20261016-1025UTC/n54-23934-review.json),
[same-load and raw output crosscheck](../nscc-pbs/inspection/wake-20261016-1025UTC/n54-same-load-and-output-review.json),
[fresh scheduler](../nscc-pbs/inspection/wake-20261016-1025UTC/slurm_accounting.json).

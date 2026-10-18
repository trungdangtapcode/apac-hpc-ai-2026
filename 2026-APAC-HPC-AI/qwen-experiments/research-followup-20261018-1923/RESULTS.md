# Warmup stall: no accepted measurement; one bounded retry — 18 October 2026, 19:25 UTC

## What happened

H200 repeat **24588** reached the 17-minute allocation limit (Slurm TIMEOUT, elapsed 17:07). Both prefills and decode became ready normally around 302–308 seconds; pair warmup completed at 426 seconds. The benchmark then sent 858 warmup requests. Its raw export contains **857 warmup records and zero scored records**. AIPerf repeatedly reported 857/858 returned, one request outstanding, while waiting for warmup credits with an infinite wait. Thus the client never reached a usable scored phase before Slurm terminated services.

The profiling phase-start log appears only during shutdown, followed by connection refusals. Those refusals are consequences of terminated services, not evidence of the initial cause. Workers continued answering health checks; that does not prove the outstanding stream completed or identify whether transport, router, backend or client completion handling caused the problem. The underlying cause is **not isolated**. Do not label this a slow model load or derive throughput from warmup records.

No canonical full AIPerf export or quality diagnostics exist for this attempt. It is **TIMEOUT_NO_ACCEPTED_MEASUREMENT**, not a completed benchmark or SLA result. Raw logs and request records remain preserved and sealed; 24588-diagnosis.json stores relevant phase events, counts and source hashes.

## One bounded diagnostic retry

Submitted **24647**, same DeepGEMM prefill / auto decode, chunk 8192, concurrency 58. The only operational client change is a **360-second limit around the entire AIPerf invocation**, with a 15-second forced-stop fallback. This is a containment measure, **not a proven repair** for the outstanding warmup request. No request timeout, benchmark phase, dataset, concurrency, precision, latency threshold or output filtering changes.

If the client finishes normally, the original complete 60/120/30 protocol and all request/error/output gates still apply. If it exceeds the outer limit, the job records a failure marker and exits nonzero; partial output is retained and rejected. No stalled request is dropped to manufacture a valid score. Shell failure propagates to the existing cleanup trap, ending the serving allocation earlier instead of waiting until its full Slurm walltime.

The bound is 360 seconds for this full-client invocation, including its configuration/warmup/scoring/export stages, compared with roughly 3–4 minutes for passing clients. GNU timeout exists in the exact frozen AIPerf image. Validation checks syntax, frozen hashes and an exact inverse patch proving the guard is the only benchmark script difference. Worker, launcher, transport and quality scripts are byte-identical to the failed source. See validation.json and the submitted bundle. Future review must explicitly allow this operational wrapper while still requiring identical AIPerf configuration, every full phase and zero raw request errors/cancellations.

This is **one** diagnostic retry of the failed replication. If the stall recurs, stop this retry path and inspect the affected request/stream lifecycle; do not repeat unchanged or keep extending the allocation. This does not establish failure of the prior accepted peak 24544, but that peak remains unconfirmed by independent N58 replication and fresh same-load control.

## Live queue and access

At 19:24 UTC, own H200 jobs **24589, 24639, 24640, 24641, 24647** are pending Resources. Five active jobs, each 16 GPUs / 17 minutes; no sixth. Existing queue positions are retained. 24589 is the fresh chunk 4096 N58 control, 24639 the HPC-Ops decode N58 trial, 24640 the HPC-Ops prefill/chunk 6144 combination, and 24641 the both-phase HPC-Ops N56 trial.

H100 remains inaccessible because no live VPN process exists; the wrapper fails before SSH. No new PBS results/credit are verified this turn. Authentication cache remains intact; no reauthentication/DUO request. Keep existing conservative reservations until live accounting can be checked. Last validated peaks remain H200 2786.696 and H100 2371.961 good tokens/s, with the previously documented repeat/accuracy limitations. Official full-set accuracy remains unverified.

No background Codex, AI schedule, watcher, slides, official package or organiser upload changed. Existing non-AI Slurm refresh/submission functions ran interactively under their lock. Raw failed artifacts are never replaced by the new attempt.

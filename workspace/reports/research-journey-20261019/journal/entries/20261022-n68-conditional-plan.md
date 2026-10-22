# 22 October: prepare a guarded next load question while full confirmation runs

Recorded 2026-10-22T00:09:02.033944+00:00. Prospective CPU work only; no extra GPU submission or spending.

Question: if full N64 survives local checks, does N68 improve goodput with the
same serving configuration? Existing N60 profiling samples show decoderunning
40–52, not automatically the client concurrency60. Client concurrency and
captured decode graph batch size are different quantities. This permits asking
a higher-load question without assuming that graphmax64 either supports or
forbids every client load above64. Actual decode batches/fallback need inspection.

[Conditional plan and guard](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261022-n68/PLAN.md) derive a same-deployment short N64/N68
20/40/30 screen from the immutable accepted short recipe, preserving all native
backends, precision, routing and observation. At most16H200/two nodes/17minutes,
no PBS SU. Default preparation refuses unless fresh full25366 has a formal
local protocol/SLA/output pass with zero errors/cancellations and full60/120/30
protocol evidence. No such completed review exists at writing.

CPU self-tests execute the actual inherited shell gate: pass64/68, SLA fail
stops after64, error stops after64, deadline defers both. Review guard rejection
fixtures pass. No candidate is frozen, reserved or submitted. A future short
candidate must gain>=1% over same-job N64 and pass all local gates before full
N68 confirmation. Full organiser accuracy remains unverified.

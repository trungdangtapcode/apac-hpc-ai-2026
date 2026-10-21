# Full PD correctness after uniform eager-prefill readiness

The isolated native TP4 probe 223005 passes sealed payload/semantic/runtime
review after 406 seconds. Both target/draft prefills avoid capture in every
rank, all four NIXL ranks initialize and HTTP/native readiness passes. The
preceding full 222780 BF16 repair already gets decode target-verification,
draft-decode and draft-extend graphs to readiness, but its prefills diverge at
a rank-local automatic memory gate. This combined evidence supports a distinct
full-PD repair; neither a one-role probe nor decode readiness proves PD output
equality or a speedup. Physical nodes differ, so do not claim a matched causal
startup improvement from these two observations.

## Exact derived change and control

Derive a separately frozen bundle from 222780. Add only native
--cuda-graph-backend-prefill disabled to each prefill worker's role-specific
flags; the same worker serves both TP4/EP1 replicas on node 0. Decode on node 1
remains TP8/EP8 with exactly the same target verification, draft graph choices,
HPC-Ops, FlashInfer/MNNVL and capacity. Published FP8 target, BF16/unquant draft,
pinned public draft identity, chunk 4096, NIXL patch, round-robin, CPU policy,
resource collector and precision stay unchanged. The workers use native eager
prefill math; do not force graph capture below its guard or patch model work.

Byte-identical controls: worker placement, native token client, frozen corpus,
sealed 222761 target reference, independent result checker, benchmark script
(not invoked for this diagnostic) and NIXL source. The required token check
remains four prompt cases including exactly 4000 input IDs, 200 actual output
IDs each, repeated twice: 1600 actual IDs. No text-retokenization substitute,
softened comparison, target/model change or throughput ranking.

## Bound readiness and preserve the diagnostic window

Retain the original 16-H100/30-minute allocation ceiling, maximum 1024 SU. This
is a reservation ceiling, not an estimate that initialization must take 30 minutes.
A shorter allocation is not chosen before heterogeneous full-PD transfer passes.
Instead shorten the absolute worker readiness cutoff from 1650 to 1200 seconds.
Use one immutable deadline at script start: 1800 seconds less 40 seconds cleanup.
Do not renew it for each endpoint or launch. Router readiness remains bounded
by 120 seconds. Pair warmup is bounded by the lesser of 480 seconds and remaining
time less 360 seconds reserved for locality capture, new client-container launch
and actual token checks. Failure to retain that window fails before spending
more setup time. The token client retains its own 120-second minimum, 240-second
cap and internal 210-second total diagnostic guard. No timeout extends PBS walltime.

Five fixtures execute the actual shell budget function, including exact boundary
rejection; nine adversarial token-result fixtures remain unchanged and pass.
The planned observed procedure is still readiness, router, separate connection
warmup, bounded locality capture, then exact-ID diagnostic. This is not an
AIPerf score or matched throughput experiment. Source/graph/state/memory and
role telemetry still require inspection after actual completion; missing fields
or an exit 0 alone never establish success.

## Budget, ownership and next decision

This GPU session owns AI/Qwen. Preserve the other session's HPC payloads, jobs,
HPC_CURRENT and CPU ledger. Before qsub, hold the AI budget lock, refresh own
GPU queue, published project 59010042 ledger and known unposted job accounting.
Reconcile 223005 only if the published delta uniquely matches; otherwise retain
its maximum. Read the separate CPU queue only for the combined own-account cap,
without mutating or authenticating it. Require an empty own GPU queue and the
combined cap <=3. Keep at most one running 16-GPU allocation, 51000 cap/13000 buffer.
Upload once, reserve first, record the definite receipt and never repeat an
uncertain qsub. No additional grant, background schedule or automatic chat alert.

On success, inspect actual prefill/decode dtype/graphs/state, all 16 GPU roles,
auxiliary/heterogeneous KV transfer evidence, real ID equality, runtime errors,
resource coverage and cost. Native pointer identity is not directly instrumented
in the full worker; distinguish source/fixture proof from real runtime evidence.
Only a valid useful full-PD candidate permits the separately planned fresh
N54 matched-capacity short screen, its >=3% goodput gate and then full official
confirmation. On failure retain it and select a concrete source-supported repair
or close this branch; no blind retry or unchanged load run. The accepted H200
N62 submission and official-accuracy gap remain unchanged.

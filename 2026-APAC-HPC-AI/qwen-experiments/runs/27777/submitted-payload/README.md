# Verify a hardware-dependent H100 attention tradeoff on H200

Owner authorisation: 31 October 2026, Vietnam time. After stopping broad research,
the owner requested testing promising H100 ideas on H200 to answer the panel's
cross-hardware comparison question. This reopens only bounded H200 verification;
it does not restart H100 spending, authentication, schedules or background Codex.

## Question and prior evidence

Does changing only decode attention from FlashInfer to FA3 help our current H200
deployment? H100 jobs 222027/222028 measured 2420.945479/2401.283565 good output
tokens/s. FA3 reduced mean TTFT by 118.922270 ms, but increased mean request ITL
by 0.773278 ms and reduced goodput by approximately 0.812%. It was rejected for
that H100 deployment. It is a latency tradeoff worth checking after changing
hardware, not an H100 winning configuration or a prediction of an H200 win.

Evidence: [H100 full pair](../research-followup-20261020-0132/RESULTS.md).
CPU-envelope balancing gained only 0.289035% on H100 and is not a priority here.
The earlier H200 FlashInfer experiment 27077 changed prefill attention; this
study changes decode attention, while preserving FA3 prefill.

H100 was useful for screening runtime compatibility, failure mechanisms and
tradeoffs. Scores on different GPUs do not rank configurations on the same
hardware. We will compare both arms on H200 with identical hardware count,
software, workload and operating point. No H100-to-H200 multiplier is used.

## How many jobs?

Start with two independent jobs: a fresh FlashInfer control and one FA3 decode
candidate. Each uses two nodes / 16 H200 for at most 17 minutes, maximum
4.533334 GPU-hours. Stage maximum is 9.066667 GPU-hours, zero PBS SU, own active
or pending cap five. Four jobs is a possible full confirmation sequence, not an
instruction to spend all four immediately. If a valid candidate gains more than
1% with acceptable tails and unchanged output gates, prepare an independent
second control/candidate pair. A loss or sub-threshold result closes this exact
branch without a wider grid. Queue wait is additional to allocated walltime.

## Intervention and controls

Derive both arms from the actual frozen payload of H200 control 27376. Keep
two TP4/EP1 prefill workers and one TP8/EP8 decode worker, DeepGEMM prefill,
HPC-Ops decode, MNNVL, chunk 8192, dense decode graphs 1..64, RadixCache prefill /
ChunkCache decode, polling1, the pinned image/model/NIXL patch and native Enroot.
Change only the decode attention backend for the candidate. Both remain
non-speculative: the inherited harness field `arm=control` denotes no draft;
the new `study_arm` field identifies the actual attention-study treatment.

Use N64 closed-loop, fixed requested 4000/200, seed 2026, no prefix reuse and
60/120/30-second warmup/measurement/grace. Freeze manifests before admission.
Actual backend, graphs, source/runtime, BF16 physical KV allocations and both
semantic P/D paths must pass before scoring. Replay the raw-log runtime gate;
do not require a hybrid-attention marker when both phases resolve to FA3.

## Review and claim boundaries

Official good output tokens/s equals exported Goodput requests/s times 200.
At least 90% of ALL requests, including errors, must jointly meet TTFT <= 3000 ms
and request-mean ITL <= 20 ms. Also require zero errors/cancellations, inherited
smoke >= 7/8 without regression and retrieval 12/12. These are local gates; full
official model accuracy remains UNKNOWN, not certified 99% of reference.

Review request tails and breaches, role queues/batches/KV, transport/runtime
logs, five-second CPU/GPU telemetry, startup and allocated cost. Missing data
is uncollected, not zero. No heavy kernel profiler is added to ranked traffic.
Resolved backend plus pinned implementation and successful inference verifies
the tested path; no per-kernel causal attribution is claimed without traces.
One pair is exploratory; independent repetitions are required for promotion.
Generated engine seeds and unmeasured host/cache state remain limitations even
though the client workload seed is fixed. Keep H100 and H200 results separate.

Prepared, submitted, running and reviewed are distinct. Record actual job IDs,
frozen manifests, reservations and scheduler receipts; no submission is claimed
by this plan alone. Preserve failed attempts and do not modify old payloads.

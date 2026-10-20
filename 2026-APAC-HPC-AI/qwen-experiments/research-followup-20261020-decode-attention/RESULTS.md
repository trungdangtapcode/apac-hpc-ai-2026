# Decode attention comparison: submitted, not measured

Submitted on 20 October 2026 at 00:47 UTC. The live check at 00:52 UTC shows **222027.pbs111 running** and **222028.pbs111 dependency-held**. These states are a dated snapshot, not benchmark acceptance.

| Job | Change | Control and purpose |
|---|---|---|
| 222027.pbs111 | Native FlashInfer decode | Fresh N54 control on the current HPC-Ops deployment |
| 222028.pbs111 | Native FA3 decode | Change only the decode attention backend; run after 222027 |

Both retain the pinned runtime, both-phase HPC-Ops MoE runner, N54 load, chunk4096, BF16 KV cache, native MNNVL AUTO strategy with PDL enabled, explicit default no_grad, full scoring/output protocol and separate post-score CPU/GPU profiling. No result exists yet. Activation, payload, raw requests, joint latency SLA, errors and output checks must pass before ranking. Local output checks do not establish official 99%-reference accuracy.

## Why spend credit here?

Earlier attention trials used different runner/load conditions, so their ranking need not transfer to the current interaction. Recorded kernel-time sums show a meaningful attention component, but do not prove its critical-path share. FA3 is registered in the actual pinned source and already used for prefill. This pair tests the native decode implementation without a custom kernel patch. See [the plan, source evidence and references](PLAN.md).

The preceding collective screens reject forcing one-shot and disabling PDL. Those options are deliberately excluded. A useful full-model improvement must be independently repeated; a loss closes this tested option rather than triggering an unchanged retry. Backend failure is preserved as a failure, not a completed valid measurement.

## Resource bound and evidence

Two serial 16-H100 allocations, each capped at 45 minutes: **3072 SU maximum combined reserve**, not actual consumption. At submission the published Used was 34035.199 SU; two completed microbenchmarks still retained conservative maximum reservations until their charges appear. Total unreleased maximum reserve was 3413.333 SU and internal headroom 13551.468 SU under the unchanged 51000-SU cap and 13000-SU project buffer. Reported Balance already excludes In Doubt prepayment; do not deduct it twice.

[Definite submission receipts](pbs-receipts.json), [post-submit dependency check](pbs-post-submit.txt), [dated live check](pbs-live-0052.txt), [payload hashes](pilots.json), [preparation validation](validation.json). Frozen submitted bundles are unchanged.

One initial read-only status command omitted the login-shell wrapper and returned `qstat: command not found`. The corrected `bash -lc` command immediately returned the real PBS states; this was a command environment issue, not a VPN or authentication failure. No reauthentication or job resubmission was performed.

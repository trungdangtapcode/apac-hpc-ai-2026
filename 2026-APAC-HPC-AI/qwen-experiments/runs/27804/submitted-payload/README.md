# Two distinct H100 chunk variants: verify the current H200 interaction

## Correct the job-count interpretation

The owner asked whether the next four best H100 configurations were being tested
on H200. The first wave was four measurements, not four distinct H100 recipes:
27777 was a H200 control, 27779 an attention tradeoff, and 27781/27783 the same
H100 recipe at two loads. Earlier statements equating those counts are corrected.

A source-linked audit finds one H100 frontier recipe with many repeats, not four
distinct winning untested recipes. Do not fabricate a top-four list or submit
duplicates to meet that count. Two actual measured H100 chunk variants remain
informative under the current native H200 N64 deployment. Submit these two within
the owner's requested verification scope; the requested four distinct new
configurations are not yet established or fulfilled.

## Prior evidence and the new question

- H100 HPC-Ops prefill chunk 6144, job 221828: 2411.995 good tokens/s versus
  matched 4096 control 221827: 2413.802, -0.0749%, no established gain.
- H100 HPC-Ops prefill chunk 8192, job 222282: 2382.811874 versus matched 4096
  job 222281: 2401.577649, -0.7814%, no established gain.
- H200 current-native both-HPC-Ops/chunk 4096 job 27783 at N64:
  2721.815800 good tokens/s. Mean TTFT 1591.493 ms; prefill sampled queue means
  7.3750/4.4583 requests. Raising client load from N54 did not improve goodput.
- H200 current-native DeepGEMM/chunk 8192 control 27777 at N64:
  3038.022907 good tokens/s. The recipe comparison changed runner and chunk
  together; it did not isolate either factor.

Question: can larger chunks relieve the observed prefill waiting work while
retaining HPC-Ops, and does HPC-Ops remain slower when both runners use 8192?
H200 older HPC-prefill trials include different N56/decode settings; they are
historical support, not the exact current-native N64 comparison. DeepGEMM 6144
measurements do not settle the HPC-Ops 6144 interaction. This is a changed
hardware/load/runner interaction, not an unchanged H100 retry or a claimed win.

Derive S114 chunk 6144 and S115 chunk 8192 from the actual frozen H200 27783
payload. Change only prefill chunk and its native dependent prefill capture
maximum/buckets. Both retain N64, HPC-Ops for both phases, FlashInfer decode,
FA3 prefill, MNNVL, round-robin, dense decode graphs 1..64, decode cap 256,
polling 1, pinned image/model/transport, BF16 physical KV and all original caches.
Compare against 27783 for chunk sensitivity. Compare S115 against 27777 as a
same-chunk prefill-runner comparison, retaining generated-seed/state caveats.

## Bounds and gates

Two independent jobs, each 16 H200 / two nodes / at most 17 minutes, maximum 4.533334
GPU-hours each; combined 9.066667 GPU-hours, zero PBS SU. Own pending/running cap 5.
No old job is cancelled, requeued or mutated. No H100 authentication/spending,
HPC changes, background Codex or schedules. An admission needs a definite
scheduler receipt and frozen manifest; preparation is not a submission.

Keep full 60/120/30, N64 closed-loop, requested 4000/200 tokens, seed 2026, cold
prefixes, joint TTFT <= 3000 ms / request-mean ITL <= 20 ms on >= 90% of all requests,
zero errors/cancellations, smoke >= 7/8 without regression and retrieval 12/12.
Official full-set accuracy remains UNKNOWN. Preserve source/runtime, all-rank
actual HPC-Ops/graph/cache/KV and both semantic P/D gates. Explicitly verify the
new native prefill graph maximum and bucket list, not only the CLI chunk flag.

Inspect raw tails/errors, role batch/queue/KV, transport/runtime logs and existing
five-second CPU/GPU/power/clocks/thermal samples. No heavy trace is added to
scored traffic. More GPU activity does not prove a causal bottleneck; missing
per-request time decomposition remains missing. These are single runs with
different generated engine seeds. A result below the fresh H200 incumbent or
below a useful 1% gain does not qualify for default/submission promotion or an
unchanged winning repeat. Preserve losing and failed outcomes.

Sources: [H100 6144 pair](../research-followup-20261019-1418/RESULTS.md),
[H100 8192 pair](../h100-prefill-hpc-chunk-interaction-20261020/PAIR_REVIEW.md),
[current H200 evidence](../h200-h100-transfer-review-20261031/FINAL_RESULTS.md).

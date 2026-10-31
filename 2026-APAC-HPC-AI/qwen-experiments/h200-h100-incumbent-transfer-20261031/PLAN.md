# Port the retained H100 serving recipe to H200

## Owner request and bounded scope

On 31 October 2026, Vietnam time, the owner explicitly requested four promising
H100-related trials on H200. Existing H200 jobs 27777 (fresh native FlashInfer
control) and 27779 (FA3 decode tradeoff) retain their queue positions. Add only
two jobs, for four measurements total in this wave, including the control.
This supersedes the earlier agent-created two-job initial stage; it does not
require pretending four independent H100 winning methods exist.

Each new job reserves two nodes / 16 H200 / at most 17 minutes, maximum
4.533334 GPU-hours, zero PBS SU. New pair maximum is 9.066667 GPU-hours; all four
jobs together maximum 18.133334 GPU-hours and 68 allocated minutes if serial,
plus queue wait. Preserve the own active/pending cap five. No H100 spending,
authentication, HPC changes, background Codex or schedules are introduced.

## Question, prior evidence and hypothesis

Does the recipe selected on H100 remain competitive on H200, and does its load
limit transfer? The retained H100 peak is job 222048 at N54,
2433.019859 good output tokens/s. Fresh H100 reproduction 225227 measured
2399.186728 good output tokens/s; preserve both instead of selecting only the
historical peak. The accepted H100 serving recipe uses two TP4/EP1 prefills and
one TP8/EP8 decoder, HPC-Ops for both phases, prefill chunk 4096, FA3 prefill,
FlashInfer decode, MNNVL decode collectives and round-robin prefill routing.

H200's incumbent uses DeepGEMM prefill and chunk 8192. Earlier H200 investigations
support that selection; this port is not advertised as an untested invention or
an expected winner. It answers the owner's explicit same-hardware validation
question under the current native runtime and output gates. Source recipe and
load sensitivity can interact with hardware. Two trials test the best H100
recipe at its retained N54 and at H200's current N64 operating point.

Primary retained evidence:

- [H100 fresh full recipe and limits](../h100-review-225227-225228-20261026/REVIEW.md).
- [H100 chunk-setting pair](../h100-prefill-hpc-chunk-interaction-20261020/PAIR_REVIEW.md).
- [Retained platform results](../SERVING_TUNING_RESULTS.md).
- [Current H200 attention control and FA3 trial](../h200-h100-attention-transfer-20261031/STATUS.md).

## Exact comparisons

| Arm | Prefill MoE runner / chunk | Decode attention | Concurrency | Role |
|---|---|---|---:|---|
| 27777 | DeepGEMM / 8192 | FlashInfer | 64 | Fresh H200 incumbent control |
| 27779 | DeepGEMM / 8192 | FA3 | 64 | Existing single-factor attention trial |
| S112 | HPC-Ops / 4096 | FlashInfer | 54 | H100 serving recipe at retained H100 load |
| S113 | HPC-Ops / 4096 | FlashInfer | 64 | Same recipe at H200 load |

Compare S113 against 27777 as a **coupled serving-recipe comparison**, not the
isolated contribution of HPC-Ops or chunk size. Compare S112 against S113 for
load sensitivity with the same recipe. S112 versus 27777 changes both recipe
and load and must not be described as a one-factor ablation. Comparisons against
historical H100 measurements are descriptive; native launch, host affinity and
machine state differ, so these jobs do not establish a pure GPU speed ratio.

This ports serving choices into the current H200 harness, rather than copying
H100 NUMA CPU IDs, PBS launchers or site paths. Preserve the current pinned
image, target FP8 weights, BF16 KV, physical KV geometry, NIXL patch, native
Enroot lifecycle, tokenizer policy, polling 1, RadixCache prefill/ChunkCache
decode, memory fraction, decode cap 256 and dense decode graphs 1..64. N54 is a
client-load change, not a graph-capacity reduction. Chunk 4096 naturally changes
the prefill capture range; do not claim that dependent graph settings stay
numerically identical. Require actual HPC-Ops activation on all serving roles.

## Qualification and decisions

Freeze and verify each manifest; reject the wrong runner, chunk, load, physical
KV/cache/source/graph/runtime state before interpreting a result. In particular,
N54's actual client command, expected input configuration and raw-export gate
must agree; an N64 measurement cannot qualify as N54. Keep full 60/120/30,
requested 4000/200, seed 2026, cold prefixes, all-request joint TTFT <= 3000 ms /
request-mean ITL <= 20 ms fraction >= 0.90, zero errors/cancellations, smoke >= 7/8 with
no regression and retrieval 12/12. Full official quality remains UNKNOWN.

Inspect tails/breaches, role queues/batches/KV, runtime/transport logs, five-second
hardware/server samples and allocation/startup cost. Missing telemetry is missing,
not healthy. Do not infer a kernel-level cause from sampled GPU activity.
Require a valid useful gain above 1% and acceptable tails before a separately
reviewed independent confirmation. Otherwise retain the loss and close the exact
recipe/load branch. No automatic additional sweep, default promotion or published
slide/submission edit follows merely from queue acceptance.

# Bounded H100-to-H200 verification

On 31 October 2026 the owner reopened AI research specifically to verify
promising H100 ideas on H200 after the panel challenged cross-hardware
comparisons. The prior global research stop is superseded only for this scope.
No H100 authentication or spending, HPC work, schedules or background Codex is
authorised by this change.

H100 is a screening platform for hypotheses, compatibility and tradeoffs. A
higher or lower score on a different GPU does not establish which configuration
wins on H200. The decisive comparison runs both alternatives on H200 under the
same workload, software and resource count. Calibration estimates are forecasts,
not substitutes for these measurements.

## How many jobs are enough?

Start with **two H200 jobs**, a fresh incumbent control and one candidate.
The candidate changes only decode attention from FlashInfer to FA3. H100 showed
a real tradeoff: mean TTFT improved 118.922270 ms, but goodput fell about 0.812%
and request-mean ITL worsened 0.773278 ms. This is not a winning H100 method; it is
a hardware-dependent question that has not been established on the current H200
deployment. CPU-envelope balancing's 0.289035% H100 gain does not justify another
priority trial. A four-job first wave was considered before the evidence audit;
the audit supports two, avoiding weak candidates merely to fill the queue.

If the valid candidate improves goodput by more than 1% with acceptable tails and
unchanged output gates, run a second independent control/candidate pair: **four
jobs total**. Otherwise stop this branch after two and retain the loss. Two runs
per arm are a practical confirmation checkpoint, not statistical proof of a
global optimum. Near-threshold noisy results need qualification, not rounding
into a win.

Each job uses 16 H200, two nodes, at most 17 minutes: maximum 4.533334 GPU-hours.
The initial pair reserves at most 9.066667 GPU-hours and no PBS SU. Four jobs would
take at most 68 allocated minutes if serial, plus queue wait; the initial pair
at most 34. Actual charges and elapsed time come from completed allocations.

The frozen full N64 protocol retains requested 4000/200 tokens, seed 2026,
60/120/30 seconds, joint TTFT <= 3000 ms and request-mean ITL <= 20 ms on at least 90% of
all requests, zero errors/cancellations and inherited output checks. Official
full-set quality remains UNKNOWN. No score improvement is claimed by submission.

[Plan, exact controls, validation and later receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-attention-transfer-20261031/PLAN.md).
The latest actual acceptance state belongs in AI_CURRENT and the study STATUS.

## Accepted jobs

At 2026-10-31T10:26:03.546470+07:00, Slurm accepted **27777** (FlashInfer control) and **27779**
(FA3 decode). Both are Resources-pending in the dated observation. No new
measurement or improvement yet. [Actual admission record](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-attention-transfer-20261031/STATUS.md).

## Owner expands the wave to four measurements

Later on 31 October the owner explicitly requested four promising H100-related
jobs on H200. Preserve 27777/27779 and prepare two additional ports of the retained
H100 recipe: HPC-Ops prefill and decode, chunk 4096, FA3 prefill / FlashInfer
decode, MNNVL and round-robin, at N54 and N64. This supersedes the previous
agent-created two-job initial envelope; it is not four independent H100 wins.
The four-job wave includes one incumbent control. The new pair maximum is
9.066667 GPU-hours and total wave maximum 18.133334 GPU-hours, zero PBS SU.

N54 retains the H100 operating point. N64 tests the same recipe at the current
H200 load. Compare N64 against 27777 as a coupled recipe, not isolated runner or
chunk causality; compare N54/N64 as load sensitivity. Existing earlier H200
investigations favour the current DeepGEMM/chunk 8192 recipe, so no gain is
promised. This current native remeasurement answers the requested hardware
transfer question. Do not copy H100 CPU masks or PBS launchers into H200.
Twenty CPU runtime/client-load fixtures pass; actual GPU acceptance is not yet
claimed for the additional ports. [Exact preparation plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-incumbent-transfer-20261031/PLAN.md).

## Definite additional acceptances

Slurm accepted **27781** (H100 recipe at N54) and **27783** (same recipe at N64).
Together with 27777/27779 this fulfils the four-measurement wave, with one control.
Preparation/20-fixture review was committed and pushed in 538bd026 before sbatch.

Queue checked 2026-10-31T10:34:46.460360+07:00:

```text
27783|ap42-s113-h100n64|PENDING|0:00|2|(Resources)
27781|ap42-s112-h100n54|PENDING|0:00|2|(Resources)
27779|ap42-s111-fa3|PENDING|0:00|2|(Resources)
27777|ap42-s110-flashinfer|RUNNING|4:08|2|g[1,4]
```

[Definite reservations and receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-incumbent-transfer-20261031/STATUS.md). No new performance claim.

## First reviewed control

Checked 2026-10-31T10:53:26.134276+07:00: 27777 completed 0:0 in 13:08 and passed the full local
protocol at 3038.022907 good tokens/s; 1872/1898 good, 26 TTFT/0 ITL breaches, zero
scored errors/cancellations. Actual FlashInfer decode, physical KV, both semantic
routes, smoke 7/8 non-regression and retrieval 12/12 pass. Two initial setup 503
responses were retried successfully before scoring; do not call every log
error-free. Sampled decode GPU activity 100% and KV token usage 0.12 are different
quantities and do not identify a kernel bottleneck. Full official quality is
UNKNOWN. Actual allocated 3.502222 GPU-hours, zero PBS SU.

27779 is running with actual FA3 decode passed by the runtime gate; 27781/27783
are Resources-pending in the dated observation. Three candidate trials remain
unfinished, so no fifth job or duplicate baseline is justified by this status
check. [Raw-backed control review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-attention-transfer-20261031/CONTROL_RESULTS-27777.md).

## Three reviewed measurements

**Latest AI review — 2026-10-31T11:24:39.696311+07:00, Vietnam time (UTC+7):** **3/4 reviewed local passes**: 27777 control 3038.022907; 27779 FA3 decode 2999.245473 good tokens/s (**-1.276404%** versus fresh control); 27781 H100 recipe N54=2738.940099. All have zero scored errors/cancellations, smoke 7/8 non-regression, retrieval 12/12. Keep FlashInfer decode and close this FA3 candidate; official quality UNKNOWN. 27783 H100 recipe N64 is running; do not isolate recipe effects from N54 versus N64. [Full review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/RESULTS.md). Preserve its admitted position; no redundant fifth trial.

Fresh queue:

```text
27783|ap42-s113-h100n64|RUNNING|9:24|2|g[1,4]
```

## Final four-job outcome

**Final H200 verification — 2026-10-31T13:05:20.255825+07:00, Vietnam time (UTC+7):** **4/4 reviewed local passes, own queue empty.** 27777 fresh control **3038.022907**; 27779 FA3 **2999.245473 (-1.276404%)**; 27781 H100 recipe N54 **2738.940099**; 27783 H100 recipe N64 **2721.815800 (-10.408319%)**, all good output tokens/s. Keep the existing H200 DeepGEMM/chunk 8192 prefill and HPC-Ops/FlashInfer/MNNVL decode at N64; no new winner or promotion. H100-recipe N54->N64 does not improve goodput and increases mean TTFT 896.156 -> 1591.493 ms with larger sampled prefill queues; no direct causal time decomposition. Official quality UNKNOWN. Actual wave 12.671111 GPU-hours, zero PBS SU. [Final review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md). The requested four-job verification is complete; no useful-gain repeat qualifies. Unrelated research remains stopped, no background Codex/schedule, H100 authentication/spending or HPC change. Published slides/ZIP unchanged.


## Clarify that there is no next four-job wave yet

Checked 2026-10-31T13:13:20.513610+07:00, Vietnam time (UTC+7), after the owner asked whether the
next four jobs were already measuring on H200. The actual own Slurm queue is
empty. Accounting lists completed 27777, 27779, 27781 and 27783; no next wave
has been submitted. These are the completed original four, not an additional
set of four. No candidate from that wave qualified a useful-gain repeat.
The queue check does not constitute a new submission, broader research restart,
H100 login/spending or background automation. [Fresh scheduler record](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/post-wave-queue-check.json).

## Correct distinct-configuration count and continue justified trials

The owner's repeated question clarifies that four distinct H100 configurations
were intended. The prior answer counted four allocations, including a H200
control and two loads of one H100 recipe. That did not fulfil the requested
distinct-configuration count. Do not count incumbent repeats or load points as
new technical methods, and do not call the H100 FA3 losing variant a winner.

A retained-source audit finds two ready informative ports: HPC-Ops prefill
chunks 6144 and 8192 under current native H200 N64, keeping FlashInfer decode.
They address the coupled runner/chunk ambiguity in the preceding H200 loss.
The earlier H100 measurements were near-flat/losing, not wins; changed hardware,
load and decode runner plus actual H200 prefill queues motivate this interaction
check. Existing DeepGEMM 6144 or older N56/HPC-prefill measurements are not the
same experiment. The two trials preserve all original gates and add explicit
chunk-derived prefill capture maximum/buckets verification.

Two further distinct qualified ports have not been identified. CPU-envelope,
forced-protocol and phase inference-mode suggestions have weak/sub-threshold
evidence, and attention/MNNVL alternatives already have H200 tests. Do not fill
the missing count with duplicates or relabel prepared work as submitted.

[Current plan and audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/PLAN.md).

# Complete the four distinct H100-derived ports with phase-specific inference mode

## Scope, evidence and the reconsidered decision

The owner requested four distinct H100 configurations on H200. The first wave
counted controls and load repeats incorrectly. The two distinct additional
chunk ports 27804/27806 are now reviewed; both improve the HPC-Ops branch but
remain below the H200 incumbent. Two candidate slots remain.

Revisit the provisional exclusion of phase-specific inference mode. H100
221923 explicit-default control measured 2424.365 good tokens/s; decode-only
221924 measured 2430.657 (+0.2596%); prefill-only 221966 measured 2424.089 (-0.0114%).
Those are actual distinct tested configurations, not H100 established wins.
Their H100 branch remains closed. The owner's hardware-transfer request permits
one current-native H200 test of each setting; the H100 gain threshold is not
proof that the effect is identical on H200. This is a changed platform/load/
serving-recipe test, not an unchanged H100 repeat. The earlier claim that no
further qualified configurations existed was too strong; source qualification
and explicit scope make these two bounded trials possible.

The pinned native DynamicGradMode defaults to no_grad and selects inference_mode
when SGLANG_ENABLE_TORCH_INFERENCE_MODE=1 before import. Both scheduler loops
use this provider. It changes tensor bookkeeping; it does not change target
weights, arithmetic precision, output length or concurrency. Reduced host work
is a hypothesis, not evidence of current CPU starvation or promised throughput.

Source evidence: [H100 full three-arm review](../research-followup-20261020-0028/H100_RESULTS.md),
[pinned native mechanism](../research-followup-20261019-inference-mode/PLAN.md).

## Three jobs: one control, two distinct candidates

| Arm | Prefill provider | Decode provider | Counts toward four candidates? |
|---|---|---|---|
| S116 | no_grad | no_grad | No; fresh explicit control |
| S117 | no_grad | inference_mode | Yes; decode-only port |
| S118 | inference_mode | no_grad | Yes; prefill-only port |

S117/S118 plus the already measured chunk 6144/chunk 8192 ports make four
distinct H100-derived intervention configurations. They are ports into the
current H200 recipe, not byte-identical copies of H100 PBS/CPU placement or a
claim of four independent winning H100 algorithms. Do not count S116 or load
repeats as extra candidates. Do not combine the two phase settings automatically.

Derive all three from actual frozen H200 control 27777: two TP4/EP1 prefills,
DeepGEMM/chunk 8192, FA3 prefill attention; TP8/EP8 HPC-Ops decode, FlashInfer,
MNNVL, round-robin; native Enroot, pinned image/model/NIXL/cache, BF16 physical
KV, decode cap 256, polling 1 and dense decode graphs 1..64. Add identical native
source/context preflight machinery to all three; change only the phase flag
between arms. A fresh control is necessary because the old frozen worker did
not record explicit provider activation and inherited ambient mode must not be
silently assumed. The new control also measures equally instrumented launch.

The source H100 phase studies used both-phase HPC-Ops, chunk 4096 and N54.
These tests port only their phase-mode interventions into the current H200
DeepGEMM/chunk 8192, N64 incumbent. They are explicitly not full H100-recipe
reproductions. Keeping the stronger H200 base avoids coupling the mode test
with the already measured losing runner/chunk transfer.

## Native activation and validation

Export phase flags before server import. In each serving role, verify exact
common.py/scheduler.py hashes, the native provider's resolved boolean, grad
disabled inside its context, expected inference mode and restoration after
exit. Print one bounded role-level receipt and require it in the independent
raw-log gate. The server inherits the same exported environment and unchanged
source. This verifies the provider preflight, not a per-rank/per-kernel trace;
actual distributed graph/KV/semantic/output compatibility must still pass.

The CPU fixtures test source binding and reject wrong, absent or duplicate
phase receipts and unrelated backend/graph mutations. Host Torch is absent;
no host fixture is represented as a real native Torch or GPU execution. The
real provider check is mandatory inside each allocated serving container.

## Bounds, protocol and decision

Three independent 16 H200/two-node allocations, each at most 17 minutes and
4.533334 GPU-hours; maximum 13.600000 GPU-hours combined, zero PBS SU. This is
two remaining requested candidates plus necessary control, not a fourth/fifth
candidate. Own cap 5, frozen hashes, locked fresh queue/site/admission and
definite receipts remain mandatory. Do not alter old payloads or queue positions.

Keep N64 closed-loop, full 60/120/30, requested 4000/200, seed 2026, cold prefixes,
all-request joint TTFT <= 3000 ms / mean-request ITL <= 20 ms fraction >= 0.90, zero
errors/cancellations, smoke >= 7/8 non-regression and retrieval 12/12. Retain all
source/runtime/physical-KV/both-semantic-route gates. Full official quality is
UNKNOWN, not certified 99% of reference. Inspect tails, role queues/batches/KV,
runtime/transport logs and current five-second CPU/GPU/power/clocks telemetry.
No heavy profile is added to scoring, and missing diagnostics stay missing.

Compare candidates only after fresh S116 control passes. A useful gain > 1% with
acceptable tails and output must be independently confirmed before promotion.
Sub-threshold results or losses close the exact H200 phase arm without an
unchanged repeat, combined-flag sweep or arbitrary new jobs. Generated seeds,
single observations and unmeasured node/cache state remain explicit limits.
No H100 authentication/spending, HPC changes, background Codex, schedules or
published submission edits are implied by this stage.

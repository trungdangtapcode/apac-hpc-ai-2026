# Reverse-order Iris confirmation: hierarchical xzy versus Scotch

Actual deployment, reservation and scheduler acceptance are tracked separately in STATUS.md and the submission receipt. Payload review alone does not establish submission. This is a separately bounded reverse-order confirmation of the small XZY signal in job 2294643. It is not an automatic retry or proof that the prior sub-1% difference is real.

## Prior result and reason for the follow-up

The completed BAAB job 2294643 measured 40 solver steps / 39 timing intervals per arm. XZY was faster by 1.19% in the first adjacent pair, 0.24% in the reverse adjacent pair and 0.71% pooled. This direction is favorable but too small to call a stable gain. The XZY sample recommendations were 50 and 44 timing samples; each arm had 39 and emitted the native warning that the run was shorter than recommended. Its p95/max tails were also wider than Scotch. Thus the prior result is a hypothesis signal only.

The native recommendation applies to the observed arm variability; collecting 51 intervals here exceeds the largest prior recommendation of 50 by one. A future run can recommend a larger count. This does not establish significance for a 0.7% effect or guarantee the new sample requirement will be ≤51. Any remaining shortfall is reported, not hidden.

## Reverse-order fixed-work comparison

| Order | Source | Treatment |
|---|---|---|
| A1 | Accepted initialized Scotch | Default Scotch control |
| B1 | Accepted initialized XZY | Hierarchical `(7 4 2)`, `order xzy` |
| B2 | Independent XZY copy | Same candidate repeat |
| A2 | Independent Scotch copy | Same control repeat |

Every arm runs 52 solver steps and retains 51 native timing intervals. This ABBA order reverses XZY and Scotch placement relative to job 2294643's BAAB. It balances linear position effects; it cannot remove nonlinear time trends or provide independent node-level replication. All four arms keep the default MPI launch, uncollated I/O, same Iris node/ranks/build, original physical problem, fixed iteration counts and native output checks. Each method keeps its own accepted initialized partition and fields; the xzy 1,040-file manifest from reviewed job 2294642 is distinct from the Scotch manifest.

Report pooled means by method, both adjacent pairs, within-method repeat differences, p95/p99/max and native sample recommendations. Retain every timing. Inspect Cd trajectories and tail/resource logs descriptively; no new output tolerance is invented. A native warning for insufficient sample count, inconsistent adjacent pairs or material repeat/drift prevents a stable-win claim.

## Time and admission boundary

One exclusive Iris node, 56 CPUs, zero GPUs, at most 10,800 seconds (168 allocated CPU-hours). Internal deadline 10,650 seconds, outer timeout 10,770 seconds and 300 seconds of final reserve. Each solver arm has a 2,150-second cap, while its protected planning window is 2,500 seconds including source copies, checks and field seals. The initial source phase must finish within the 350-second allowance before protected windows. An arm that cannot receive its full cap is not run as a truncated substitute.

This is a conditional local CPU-hour maximum, not billed Iris SU. Current queue, actual previous-job reconciliation, budget extension, exact frozen hashes and one-active-allocation policy are root admission gates. No job is submitted by this prepared bundle. A result is an Iris native comparison only, not a Gadi/NSCC or official score; seconds cannot be extrapolated across systems.

Initial source subprocess caps are 90 seconds for each complete manifest check and 15 seconds for each canonical-text check, plus 30 seconds for payload hashes. Their total is 240 seconds; the 350-second initial window leaves 110 seconds for field/runtime work. The preceding job used 69.4 seconds for that complete initial phase. No source check is skipped. If the window is exceeded, fail before an arm rather than silently shorten it.

Stop this confirmation branch if direction reverses, drift dominates or sampling remains inadequate; do not add repeated allocations solely to obtain a favorable sign. A consistent small difference still requires appropriate independent/full-length validation before a stable optimization or Gadi claim.

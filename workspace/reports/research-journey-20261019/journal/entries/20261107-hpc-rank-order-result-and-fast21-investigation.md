# Return to the fast 21-second state

Recorded 07 November 2026, 17:14 Vietnam (UTC+7). HPC-only; AI and NSCC work unchanged.

## Question and prior evidence

The owner asks why we did not keep improving the 21–22 s/step state. Job 2295090 B2 genuinely completes 40 steps at 21.085907685 s/step, but its identical-map B1 takes 32.001684128. The previous interpretation correctly rejected pooled promotion, but shifted toward new mappings too soon. A pooled loss is not a reason to abandon the fast-state investigation.

## Completed distinct rank-order result

Job 2295091 COMPLETED 0:0 in 4,861 seconds on iris001. Four fresh 40-step/39-interval BAAB arms preserve the N48 source, fixed work, binary and uncollated I/O; candidate `ppr:24:package`, rank-by span and core binding alternate rank NUMA membership on the same CPU set 0–47. B1/A1/A2/B2 means are 23.473843110 /27.513559057 /32.555344669 /26.748581194 s/step. Candidate pooled 25.111212152 versus control 30.034451863, 16.391975% lower within the allocation. Both adjacent comparisons favor candidate; repeat drift and lack of independent confirmation prevent a stable-winner claim.

Root replay verifies 469 raw hashes, 57 payload hashes, 240 actual rank records and native/source/runtime/field/force gates. See [complete result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-interleaved48-20261107/completed-2295091/RESULTS.md). Additional telemetry inspection finds3,300 MHz sampled node median in all arms, substantial differing fault/allocation counters and no monotonic single-counter explanation. Per-process memory residency is absent, not zero.

## Hypothesis and actual next measurement

The exact seed's recorded CPU map is identical in its slow and fast arms. Retained whole-node NUMA allocation misses/migrations and launcher-tree faults differ, motivating measurement of process residency rather than another blind map. These are correlations, not an established mechanism. [Retained evidence](../../hpc-fast21-investigation-20261107/RETAINED_EVIDENCE.md) preserves metrics and kernel references.

**New job 2295106 accepted and observed RUNNING**, source verification phase at 17:13:26 Vietnam, 7 November. Frozen 59-file bundle repeats exact 2295090 B2 three times in fresh clones, each 40 steps /39 intervals. Runtime/native argv/observed map must match the seed. Optional separate observer reads selected same-job/same-UID process metadata at steps 1/15/30 with two-second snapshot budgets. Rank identity is inferred from affinity; no raw addresses, environment, command lines or file paths saved. Failure or partial coverage must leave native trial independent. Diagnostic timings may be perturbed, so no ranked promotion claim.

All three means and spread will be retained. If reproducibly fast, confirm longer and without the new observer; if split, compare locality/faults before a targeted paired remedy. Keep 2295091 as a promising secondary branch.

## Accounting and preservation

2295091 actual 75.615556 allocated CPU-hours, conservatively 76; its 140 maximum retired once. New2295106 reserves 112 maximum:1,914 consumed+112 reserved, internal stage1,978→2,026 (+48). This is an agent planning envelope, not site SU or new owner allowance. One own allocation cap remains. New fast-repeat bundle/receipt stays local until substantive reviewed result. The completed2295091 result is eligible for a result-backed checkpoint. No schedules, automatic MFA retries or submission-material edits.

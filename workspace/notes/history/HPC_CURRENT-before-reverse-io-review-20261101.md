# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 06:05 Vietnam** (1 November 23:05 UTC) from actual queue and scheduler dependency fields. HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502; AI remains separate. No Codex background process or schedule.

## Current accepted jobs

| Job | Actual state at 06:05 Vietnam | Work |
|---|---|---|
| **2294635** | RUNNING on iris001, 27:50 elapsed | Existing reversed I/O pair: collated then default, 40 steps each, maximum 75 minutes |
| **2294637** | PENDING / Dependency, AllocCPUS 0, no node | New direct organizer/teammate ABBA, 40 steps each, maximum 2.5 hours |

**2294637 is actually accepted**, not merely prepared. Receipt 23:04:50.480660 UTC on 1 November = 06:04:50 Vietnam on 2 November. Actual dependency **afterany:2294635(unfulfilled)**. Only 2294635 currently allocates CPU; successor will be scheduled by Slurm when predecessor terminates. Preserve both jobs; do not cancel or bypass the dependency. No automatic Codex/chat wake-up is promised. [New receipt/frozen payload/status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/STATUS.md).

New remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-recipes40-20261101T230311Z`; evidence/cases root/kit/runs/2294637. Frozen 57 files, one exclusive node, 56 ranks, zero GPUs, 140 CPU-hours maximum. The test-only log's 2294636 is not an actual accepted job.

## Owner-requested controlled comparison

Same Iris node within one allocation, same v2512 double-precision build, same initialized Scotch 56-rank partition/fields, same 40 steps / 39 timings, fixedIter, original physics/function objects. Four isolated copies in **A1 organizer → B1 teammate → B2 teammate → A2 organizer** order.

- A: organizer Gadi runtime, plain default MPI / uncollated I/O.
- B: teammate runtime, --map-by socket --bind-to core / -fileHandler collated.

Common launcher binding/map diagnostics and passive pre/post CPUinfo/procfs snapshots. Full raw outputs and source/field/copy/runtime checks are retained. This tests combined runtime settings, not attribution to individual flags, end-to-end teammate preparation or Gadi/NSCC absolute times. Teammate MPI flags also affect its preparation, but shared canonical initialization deliberately controls initial state here. Source-reference.json pins both recipes and their hashes.

Offline recipe/math/financial/idempotency tests pass; live test-only accepts allocation and a CLI version probe accepts diagnostic options on Open MPI 5.0.10rc2. No full native runtime result yet. Review both adjacent comparisons, repeated controls, tails and nonlinear drift before promoting pooled means. Hold every slow sample; 40-step Iris data is not a scored 4-node 150-step result.

## Queue-policy correction and accounting

The governing execution policy (workspace/research-autopilot/POLICY.md line 61) says one own **active CPU allocation** per cluster; initial iris-scotch56 PLAN.md line 13 agrees. Earlier helper code rejected every own queued entry too, and older handoffs repeated that stricter implementation as a blanket cap. The new requested experiment permits **only the exact owned predecessor plus one afterany successor**, keeping one active allocation. This corrects that earlier interpretation; it does not authorize arbitrary queued waves or increase running concurrency. Fresh squeue, predecessor ownership receipt and ledger checks are under the existing lock, and actual scheduler fields confirm no successor allocation. NSCC active/pending PBS cap 3 is unchanged.

Iris local ledger: **560 consumed + 210 reserved = 770 CPU-hours** (predecessor 70-hour + new 140-hour). One-shot new intent/reservation was durable before sbatch; uncertainty would retain maximum and block replay. The agent transparently extended its internal 630-hour stage by 140 to 770 for this current explicit comparison request, not an owner numerical cap or site grant. No known SU balance/rate, no NSCC/AI debit. [Bounded authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/budget-authorisation.json). Retire each maximum once only from actual terminal accounting; pending reservation is not billed usage. Keep unknown old NSCC commitments.

## Results still qualified

Parent 2294634 passed 116 hashes and native 40-step replays: default 31.600735680 vs collated 29.681757101 s/step, **6.0726% lower collated mean in one A/B pair**, unconfirmed because B accelerates 34.4078→26.8189 s across first/last 10 means and its native recommendation 192 exceeds 39 samples. All 40 Cd rows equal, final Cd 0.436959331. Reverse 2294635 is running; do not invent completed results. [Parent review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-20261101/completed-2294634/RESULTS.md).

Older graph-placement branch is closed after 2294390 reversal failed to reproduce the attractive aggregate; no robust gain. Standalone exact-mapping ABBA kit iris-placement40-20261101 remains deferred/unsubmitted/unreserved, separate from actual direct combined comparison 2294637.

Best reviewed full NSCC remains **3.364622070 s/step**, job 25940700, baseline reproduction; organizer NSCC 3.210832548 separate. Teammate Gadi 2.079045460 is supplied internally consistent evidence; no independent rerun or cross-platform gain claim. NSCC VPN/queue/credit unavailable in latest read-only check; no Gadi identity supplied. Other-track work and submission materials remain unchanged.

## Next action

Collect/replay terminal 2294635 and reconcile its 70-hour maximum under Iris budget.lock while preserving queued/running 2294637. Slurm starts the latter independently of Codex after dependency clears. On 2294637 completion, run its collect_completed.py once and review_completed.py; inspect all four native outputs, actual commands/I/O/map reports, field/Cd invariants, drift/resources/warnings, then reconcile 140-hour maximum once. No further own trial is admitted while this pair remains outstanding. Prefer national-supercomputer confirmation when authorized access and fresh budget permit.

[Current journal](../reports/research-journey-20261019/journal/entries/20261101-hpc-matched-organizer-teammate-submitted.md); [historical handoff](history/HPC_CURRENT-before-direct-recipes-20261101.md). Safe captures/commits/pushes remain explicit; external binary objects still need separate off-host backup.

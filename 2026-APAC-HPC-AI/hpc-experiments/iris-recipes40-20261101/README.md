# Organizer-style versus teammate-style runtime on the same Iris setup

The owner explicitly requested a relative comparison on the same Iris hardware. This job compares the two **solver runtime recipes**, using the same reviewed initialized input for every arm.

| Treatment | MPI options | File handler |
|---|---|---|
| A: organizer-style Gadi Scotch | Default mapping/binding | Uncollated |
| B: teammate Gadi Scotch | --map-by socket --bind-to core | Collated |

Both use the same Iris OpenFOAM v2512 double-precision build, one exclusive node, 56 ranks, identical initialized Scotch partition/fields, original fixedIter and function objects, 40 solver steps and 39 measured intervals. Ranks are normalized from Gadi's 416 across four nodes to Iris's full 56-core node. Common --report-bindings and --display-map options collect launcher diagnostics before timed steps. Source references and hashes are in source-reference.json.

The order is **A1 organizer, B1 teammate, B2 teammate, A2 organizer**. The primary ratio is pooled teammate mean divided by pooled organizer mean; negative percent means lower seconds per step. Both first and reverse adjacent comparisons, repeated controls, timing trends, tails, native sample warnings and all Cd outputs must be reviewed. ABBA balances linear drift, not arbitrary time effects or independent run-to-run variation. No outlier removal. This is not a contest score, an absolute Gadi/NSCC reproduction, or proof of which individual flag causes a difference.

The supplied teammate wrapper also applies MPI flags during preparation. This controlled solver-stage comparison deliberately holds the already-reviewed canonical initialization identical; it does not claim an end-to-end rerun of that wrapper. No missing fvSolution or changed timer from the ZIP is imported. The original full mandatory preparation ran in reviewed predecessor work; all 1,040 initialized source files, canonical text inputs, 336 time-zero fields and isolated-copy inodes are verified again.

Request: one node / 56 CPUs / zero GPUs / maximum 2.5 hours = 140 allocated CPU-hours. Each solver gets a full 1,800-second window; no valid result from a truncated arm. Four protected 2,100-second arm windows plus final reserve leave 330 seconds for initial checks under the 8,850-second internal deadline. Slow setup can fail closed; preserve partial evidence. Require 64 GiB filesystem free for isolated copies; this is not a user-quota reservation.

## Safe dependent admission

The governing shared execution policy at workspace/research-autopilot/POLICY.md states: “allow one own active CPU allocation per cluster.” The original campaign PLAN.md states one active own allocation per CPU cluster too. The older helper rejected any own queued entry as an extra conservative implementation check. This requested comparison preserves **one running Iris allocation** by using a Slurm dependency, **afterany:2294635**. It permits only that exact owned predecessor already in the queue, and exactly one successor; no unrelated own job is allowed. The predecessor is not cancelled or mutated. The new job can only allocate after it terminates and then applies its own fresh source/correctness gates. No Codex background process or schedule is created; this is a normal authorized Slurm dependency. NSCC's separate active/pending PBS cap is unchanged.

The local maximum commitment before admission is 560 consumed + 70 reserved for 2294635 + 140 new maximum = 770 CPU-hours. The current owner's explicit request authorizes this one bounded comparison. An agent-selected internal stage of 770 replaces 630, a transparent 140-hour extension, not an owner numerical cap or a known site SU grant. Do not debit NSCC/AI, infer extra monetary balance, or submit additional jobs. Exact predecessor ownership, queue state, ledger maxima and frozen root review are checked under the existing Iris lock. Intent and reservation are durable before one sbatch call; an uncertain outcome retains the maximum and blocks retry.

Preserve the passing frozen kit. Preparation/deployment/test-only acceptance do not count as submission. Only a durable actual scheduler receipt and job ID count. Terminal collection, independent native replay, matched resource inspection and one-time ledger reconciliation are still required.

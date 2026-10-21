# Full PD correctness after a validated Bash dispatch repair

The sealed 223053 run reaches native readiness on both TP4/EP1 prefills and TP8/EP8 decode, with BF16 target/draft KV, all 16 NIXL ranks and preserved decode graph captures. Workers and router are ready at 490 seconds. The next invocation fails before pair warmup because external GNU timeout cannot execute the PBS adapter's exported srun Bash function. The failed integration costs an estimated 288.426667 SU over 507 allocated seconds; keep actual posting separate. [Parent review](../eagle3-pd-eager-prefill-r2-20261021/REVIEW.md).

## Exact repair and controls

This separately frozen R3 changes only the warmup launch expression: timeout invokes child Bash, which calls the inherited exported srun function with individually quoted arguments. It preserves the existing timeout duration, TERM/KILL policy, head EXIT cleanup, absolute allocation deadline and output-check reserve. It does not use a concatenated command string, change container launch/placement, or remove the deadline.

Worker flags, PBS shim, container launcher, NIXL source, phase-budget function, actual-token client/checker, prepared prompts, target reference, placement and benchmark script are byte-identical to R2. Thus BF16/unquant EAGLE3, native eager prefill, TP8 graphs, public target/draft identities, exact 1600-ID comparison and all numerical inference remain unchanged. No official target precision conversion or output shortcut is introduced. Updating the bundle name and provenance does not change model computation.

## CPU validation before spending

Six fixtures execute the actual warmup block and actual exported PBS shim. Isolated PATH reproduces the original exit 127 even on this Slurm host, confirms function import into child Bash, checks dry-run argument forwarding including paths with spaces, tests mocked pbsdsh exits 0 and 23 under set -e, and verifies timeout returns 124, terminates a local mocked step and child, and cannot print ALL_PAIRS_WARM. [Results](launcher-validation.json), [test](test-launcher.py).

The initial local test setup found executable Slurm srun on PATH; it was corrected to model the PBS environment with an isolated command PATH. Before freezing, preparation also corrected an omitted copy of the local submitter. These are preparation failures, without GPU jobs or reservations. Nine reference-derived semantic guard fixtures pass unchanged. Python parse, shell syntax and frozen payload hashes are validated. Local mocked cleanup does not prove real remote PBS task termination; job-level walltime and head cleanup remain final bounds.

## Bounded allocation and decision

Only after review: refresh project 59010042 and own GPU queue under the existing budget lock; reconcile 223053 only if a unique posted delta matches, otherwise retain its old maximum. Require empty own GPU queue, keep a conservative external one-CPU-slot allowance without any HPC access, and reserve one 16-H100 allocation for at most 30 minutes / **1024 SU maximum** under the unchanged 51000 cap / 13000 reserve. No uncertain qsub retry or background schedule. Current H200 jobs keep their queue positions.

After terminal state, seal artifacts and require actual pair warmup, heterogeneous transport, exact 1600 actual output IDs, native speculative counters and valid runtime/resource evidence. Readiness alone has already proved insufficient. No ranked speedup is claimed. Only a valid useful candidate permits the separately budgeted matched-capacity short N54 control/candidate screen with zero errors, joint SLA at least 0.90 and at least 3% goodput gain before full official scoring. Preserve and diagnose a distinct new failure instead of repeating unchanged.

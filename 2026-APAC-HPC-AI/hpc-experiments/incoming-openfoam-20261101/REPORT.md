# Verification of the supplied Gadi OpenFOAM package

The supplied logs support **2.079045460 seconds per step** on four Gadi Sapphire Rapids nodes. Independently recalculating all 149 printed intervals reproduces the reported mean. This is a verification of supplied evidence, **not a solver rerun by this worker**. No new job was submitted.

## What was checked

The original ZIP is preserved as `original.zip`, SHA-256 `ae6b692ea16f38655c8d894e2dd94cb081c15486ce71f60c00c894e804dfe7f0`. `audit_package.py` records member hashes, rejects unsafe archive paths, and replays the full 1/2/4-node logs. Run it with `python3 audit_package.py`; results are in `audit.json`.

| Nodes | MPI ranks | Solver steps | Measured intervals | Mean (s/step) | Population SD (s) | Final Cd |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 104 | 40 | 39 | 8.418059236 | 0.038930342 | 0.438060067 |
| 2 | 208 | 80 | 79 | 4.212764600 | 0.024110157 | 0.339635627 |
| 4 | 416 | 150 | 149 | **2.079045460** | 0.015434865 | 0.291876135 |

For every run, all solver steps appear in order; Ux/Uy/Uz use 15 iterations, pressure 12, and k/omega 8 at each step. Decomposition logs sum to 65,334,765 cells. All coefficient rows are present and finite; the solver logs end normally and have no observed fatal marker. These are internal consistency checks on text, not authentication of a remote execution or a substitute for source/mesh hashes.

The four-node median is 2.078045568 s, nearest-rank P95 2.104722572 s, minimum 2.032332158 s and maximum 2.128578559 s. The 980-second script duration includes preparation and other overhead; it is not the contest per-step metric. The native timer omits the first step and measures intervals through steps 2–150.

## The actual configuration

The final variant is `scotch_r416_numa`: default Scotch decomposition, four nodes with 104 MPI ranks each, OpenFOAM v2512 double precision, `--map-by socket --bind-to core`, and `-fileHandler collated`. The PBS file is named `4node.sbatch` but contains **PBS directives** and would be submitted with `qsub` on Gadi. Its project is qw53 and queue normalsr. The solver header explicitly identifies four `gadi-cpu-spr-*` hosts, the v2512 build, scalar=64 and collated I/O.

The script includes the complete decompose / restore / renumber / potentialFoam / applyBoundaryLayer / simpleFoam chain with the prescribed flags and `-ybl 0.0450244`. It depends on a base case under the teammate's `/scratch/qw53/tl1237/TripleU-official` directory. Those paths and the project/account are not portable to this worker's NSCC account.

The separate `ftol` / `ftol2` configurations change solver tolerances and work per step. Despite their comments describing them as Bonus, these changes are **prohibited in every tier** by F2/F4 of the current contest rules. They are not selected by the final 2.079-second variant and were not executed by this audit. MPI collective flags are Basic runtime tuning; a file's comment calling them Bonus does not determine classification.

## Why this does not prove a 38% optimization over our NSCC result

Our 3.364622070 s/step result is on NSCC AMD EPYC 7713, four nodes and 512 ranks. This package uses Gadi Intel Sapphire Rapids, four nodes and 416 ranks, with a different MPI/site build. Absolute times across those platforms cannot isolate configuration improvements. The [official rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/2.%20OpenFOAM%20HPC%20Task%20Rules.md) explicitly assess the two platforms separately rather than directly comparing their absolute metrics.

The retained organizer **Gadi** references already contain 2.126043416 s/step for Scotch and 2.087688606 s/step for a separate reuse-Scotch run. The supplied result is respectively 2.2106% and 0.4140% lower. These are separate jobs, not matched repeats; neither percentage establishes a causal improvement. See `../reference-analysis-20261021/reference-results.csv` for the pinned source log paths. The result is plausible on Gadi without implying that copying its flags makes NSCC reach 2.079 seconds.

## Qualifications before using this as a fully reproduced result

1. The ZIP does not contain the actual `fvSolution.fixedIter`, `fvSchemes`, complete base case or mesh hashes. Printed iteration counts support fixed work but cannot prove that all solver settings and inputs are unchanged.
2. The embedded timer's code differs from our pinned official-case snapshot: Welford bookkeeping and optional stopping fields replace a stored timing array. Both retain one `elapsedTime()` call and one timer reset per callback, and stopping is disabled in the supplied dictionary. Recalculated means agree. Nevertheless, function objects are protected case content: establish the teammate's exact upstream source revision before claiming the expanded dictionary is unmodified. Current upstream timer retrieval failed during this review, so its origin is unresolved. This is not an accusation of fabricated timing.
3. Only one final four-node run is supplied. Low variation among its consecutive steps is not independent run-to-run reproducibility.
4. The README's cache-fit, compute-bound and transport-optimality explanations are hypotheses. Cache misses, memory bandwidth, frequency and actual rank/thread binding were not collected in this package. Core binding alone does not prove NUMA-local memory placement. A GAMG setting losing on one node does not establish that it wins on multiple nodes.
5. Scheduler receipts, accounting output and realized CPU affinity are not supplied. The summary asserts exit status zero; the solver and phase logs support normal completion, but scheduler state was not independently queried on Gadi.

## What was actually tried and what remains

At **04:09–04:11 Vietnam time on 2 November 2026** (21:09–21:11 UTC on 1 November), the NSCC transport namespace was unavailable. A first local retry helper failed before authentication because it referenced the former Codex session directory. Its private path was repaired without retaining credentials; one actual bounded authentication attempt then returned `Authentication failed`. That message does not establish whether the cause was MFA, password expiry or another server policy. No repeated MFA loop was started.

The verified interactive Iris bridge exited before reaching an Iris prompt; another bounded interactive connection timed out after 18 seconds. Iris scheduler state is unknown, including old job 2294390. Its historical 29 October running snapshot must not be presented as live. No reservation was retired without terminal evidence.

No Gadi SSH login/key was supplied to this worker. The owner was asked for existing Gadi access, without passwords. **Runtime reproduction is blocked by cluster access, not by a failed benchmark.** No solver ran on the local login node, no new allocation was accepted, and no resource credit was spent by a submitted test in this review.

The useful next test is a same-Gadi matched comparison at 416 ranks: original fixed-work Scotch baseline versus the supplied socket/core binding plus collated I/O, each with a fresh full preparation and 150 steps. Preserve the approved function objects and all output. Reverse order or repeat allocations before attributing a small difference to the flags. Admission still requires actual scheduler capacity, project balance/rate, an explicit bounded cost reservation and a recorded job ID; Gadi access alone does not authorize arbitrary project spending. Repeating on NSCC would test portability on AMD, not reproduce the Gadi absolute number.

The submission folders, slides, AI queues and all frozen prior payloads were left unchanged. Raw supplied evidence remains preserved separately from this review.

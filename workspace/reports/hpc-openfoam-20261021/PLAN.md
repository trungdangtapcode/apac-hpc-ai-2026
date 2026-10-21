# A bounded HPC research plan

**Access update:** [Interactive login now reaches the actual Iris cluster](IRIS_ACCESS.md). Earlier gateway-only observations below are historical; they did not establish a submission restriction.

The first goal is one reproducible Basic result, not a large parameter sweep.
Another person supports AI. Preserve their jobs/payloads and coordinate any
shared-account expenditure before a reservation. This plan does not authorise
new service units or convert the AI project's remaining balance into an HPC
allocation. The toy gate has passed. The first 65M serial decomposition is now job
2293752; see the dated [live handoff](../../notes/HPC_CURRENT.md) and
[bounded baseline plan](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/PLAN.md).
Older access/pre-submit wording below is historical planning.

## Current milestone, 21 October

Iris practice is complete: 2293754 passes the complete chain at 21.965354 s/step. ASPIRE-2A CPU access, project 59000042, native v2512/DP and full mesh archive/member hashes are verified. First native CPU baseline 25905114 passes initialization plus 40 steps: hierarchical (16 4 2), 128 ranks, 14.9219814004 s/step, Cd 0.4389323284, 728 seconds allocation. No four-node score or measured speedup yet.

First wave stays capped at 100 SU, one CPU allocation active at a time. Five terminal allocations estimate 27.880 SU, consistent with the reported amount delta 27.879 SU; retain a conservative 29-SU consumed ceiling. Individual posted charges and the inconsistent site report timestamp remain limitations.

Default Scotch preparation 25907236 passes. Same-node H→S pair 25907325 passes both 40-step solves: hierarchical 14.787224 vs Scotch 14.640233 s/step (observed 0.994% reduction), but Scotch has a 21.120703-second step and native confidence warning. Do not claim a stable win. Native graph analysis maps logical groups of sixteen to diagnostic NUMA CPU sets, not actual memory residency or measured communication.

After all seven allocations finished, locked terminal resource reconciliation estimates 79.995556 SU and uses conservative 81 SU consumed. The project usage report is stale, so exact individual posted charges are not claimed. Native NUMA-aware Scotch prep **25907688** now runs with domains (8 16), synthetic weights 10:1, full 8-SU maximum. Planning commitment **89 / 100 SU**. Apply the preregistered graph/balance filter before a separately affordable solver. No cap increase or AI changes. Source and exact reasoning: hpc-experiments/nscc-cpu-numa-scotch128-20261021. Stage descriptions below retain original planning context; earlier gateway/baseline-pending wording is historical.

## Stage 0: establish the actual practice and contest environments

Resolve the supplied endpoint's next hop, if any. It currently logs into an
ordinary VM without the expected Iris scheduler or practice kit. Identify our
own Iris and Gadi or ASPIRE-2A CPU account/project, not another relay user's
account. Confirm scheduler/queue, module, CPU and NUMA topology, MPI version,
limits, scratch quota, budget and published charging before allocating work.
Use a read-only login check first. Existing AI VPN/SSH sessions stay running.

Copy the Iris kit into our own work area when genuinely accessible. Read its
README and ladder instructions. Retain the original case and exact Allrun.
Historical first-pass limitation, now resolved in [case recovery](CASE_RECOVERY.md): the external case repository initially could not be fetched here: original endpoints
failed and the attempted relocated committee project returned a sign-in page.
Do not treat HTML as downloaded source. The retained public reference dictionaries
are useful evidence but are not a complete runnable case.

Stage the official 3.2-GB mesh archive outside Git, verify its published MD5
50393a15d84f53255fda85ac702390e9 and record SHA256 for our copy. The unpacked
mesh is around 7 GB. Budget scratch for separate prepared runs; do not submit
binary processor trees. Prefer an existing official shared copy on the correct
cluster; the ASPIRE-2A CPU path is not readable from our current 2A+ login.

## Stage 1: obtain a valid Basic baseline

On Iris, first practise the complete preparation and semantic checks using its
own supplied examples. Practice values and short runs are not official results.
On the chosen contest system, reproduce hierarchical and scotch at the documented
full-rank settings before tuning. Start with one method's baseline and only add
the comparator after validating it. Preserve fresh independent run directories.

Use a small serial decomposePar/restore0Dir job and an afterok parallel job for
renumberMesh, potentialFoam, applyBoundaryLayer and simpleFoam. This preserves
all work while avoiding idle full-node billing during serial decomposition.
Record total billed SU separately from solver Average. Reusing a prepared
immutable decomposition can accelerate exploratory runtime comparisons, but
the final submission must document the complete preparation chain.

If ASPIRE-2A is selected, the public logs reproduce an MPI_Finalize SIGBUS under
default XRC. One documented remedy is FI_VERBS_PREFER_XRC=0; another is
FI_OFI_RXM_USE_SRX=0. Select one for a controlled reliability baseline; do not
combine flags blindly or claim a speed gain. Inspect every step's exit status,
End marker and expected output. Preserve any failure; do not accept arbitrary
nonzero exits simply because End appears. A small MPI-only probe comes before
a repeated expensive failure, when appropriate to the actual site MPI stack.
Gadi's Open MPI stack is different; do not transplant these MPICH/libfabric flags.

## Stage 2: identify the bottleneck before the next full run

Collect actual rank-to-host/core/NUMA mapping, CPU affinity, RSS, page locality,
per-step timing distribution and semantic outputs. Review partition cells,
interface-face counts and per-rank neighbor counts. Hardware counters and MPI
profiling, when site tools permit them, should distinguish time in sparse
matrix work, neighbor exchange and reductions. Do not infer a memory or network
bottleneck from an aggregate alone. Heavy profiling runs are separate from
ranked measurements, with original function objects and logging retained.

Our public-log analysis verifies 21 runs. ASPIRE hierarchical is nearly perfectly
cell-balanced but has a much larger worst interface surface than scotch. This
supports a partition/communication hypothesis; it does not prove the actual
network cut or identify one rank as the critical path without rank mapping.

## Stage 3: test one distinct hypothesis at a time

| Priority | Hypothesis and change | Control and useful evidence |
|---|---|---|
| 1 | Node-aware native scotch coefficients reduce expensive cross-node cuts | Default scotch, same ranks/placement; actual rank-host map and interface graph |
| 2 | A different hierarchical factorization/order improves the surface/volume balance | Current hierarchical, same ranks; geometry/partition statistics first |
| 3 | Fewer ranks per node reduce memory contention or small-message overhead | Best method at full ranks; retain four allocated nodes and all numerical work |
| 4 | Explicit rank binding improves NUMA locality | Same method/ranks and allocation, verified actual core/memory mapping |
| 5 | A measured MPI collective/runtime change improves a known hotspot | Matched stack and placement; communication profile, output and return codes |
| 6 | Safe compiler or runtime/I/O changes address a measured remaining cost | Version/flags frozen, double precision, same case and work |

The source review verifies native v2512 scotch reads domains and domainWeights
and builds a tree architecture. Its processorWeights branch takes precedence;
do not retain a nonempty processorWeights field while expecting the tree branch.
For a verified four-node 128-rank/node layout, a candidate is domains (4 128)
with domainWeights (1 0.01). For 104 ranks/node on Gadi, use (4 104), not 512
subdomains. These are unmeasured candidates. Confirm rank numbering actually
matches the intended node groups; syntax alone cannot enforce physical placement.
The site library/build must support this native branch.

Do not run a Cartesian product. Partition candidates are initially assessed
on practice resources for cell/face/neighbor balance. At a time, promote one
feasible candidate and a fresh control to the contest machine. Underfilled
rank counts must be chosen for the actual sockets/NUMA layout and MPI launcher;
128 or 104 is a baseline convention, not a compulsory per-node occupancy.

## Stage 4: separate screening from final acceptance

A 21-step diagnostic can screen gross runtime regressions on a prepared case,
consistent with the organisers' published exploratory analysis. Label it short;
its Cd is not comparable to the 40/80/150-step endpoints and it is not a score.
It also cannot screen decomposition quality without actually preparing that
new decomposition. Before a run, choose a small fixed shortlist and maximum
reserved cost; log every attempted branch and failure.

Promote a candidate only after complete semantic gates. For final performance,
use the official 150-step four-node run. Obtain at least two candidate/control
pairs, reversing order for the second pair where budget permits. Report all
representative runs, per-step tails, node sets and cost. Retain slow steps in
the printed Average. A gain must survive matched repetition and be interpreted
against the observed spread; the ASPIRE public range is about 12%, so a single
1–3% result does not establish an improvement. Organiser re-verification is
the reference score; there is no published noise correction.

Finally complete the 1-node/40-step and 2-node/80-step cases for the selected
configuration. Plot speedup T1/Tn and efficiency T1/(n*Tn) using seconds per
step. Different iteration counts mean total job durations are not scaling
speedups. Compare only within the same machine and explain rank differences.

## Cost planning and stop conditions

Public historical examples, not our reservations:

| Machine | CPU rate | Four-node 40-minute maximum at full ranks | Published split Scotch 1/2/4 set |
|---|---:|---:|---:|
| Gadi normalsr | 2 SU/core-hour | 554.667 SU at 416 cores | about 217 SU |
| ASPIRE-2A CPU | 1 SU/core-hour | 341.333 SU at 512 cores | about 167 SU |

Actual jobs often finish sooner, but reserve requested maxima and include serial
preparation separately. Published setup uses about 16 cores/64 GB for the serial
step. These values are starting evidence, not a guaranteed memory/runtime limit
for every partition. Confirm our account's policy and charging before qsub.

Stop a branch when it violates the work/precision rules, produces an unresolved
numerical error, cannot reproduce a useful gain, or exceeds its predeclared
reservation. Closing a losing branch does not stop the whole programme. Start
Bonus only after a deliverable Basic result and a concrete remaining bottleneck.

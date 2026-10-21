# Accepted ASPIRE-2A one-node CPU baseline

Job **25905114.pbs101** finished F / exit 0 on x1001c2s5b1n0, with 128 MPI ranks, native OpenFOAM v2512 and double precision. All three mandatory initialization stages and 40 fixed-work simpleFoam steps pass the retained reviewer. This is a one-node baseline, not the four-node/150-step contest score.

| Quantity | Observed value |
|---|---:|
| Native Average, 39 measured steps | 14.9219814004 s/step |
| Median / p95 | 14.920225 / 15.074989 s/step |
| Final Cd | 0.4389323284, dimensionless |
| Whole allocation | 728 s = 12 min 8 s |
| Batch maximum RSS | 121.7611 GiB |
| Estimated base allocation charge | 25.884444 SU |

Renumber, potential, boundary and solver native clocks were 9, 49, 5 and 643 seconds respectively. All 40 steps used fixed iterations U=15, p=12, omega/k=8. Eight omega bounding messages are retained; no timing confidence warning. Review includes every stage's End/exit, source identities, architecture, steps, native timer data, force output and accounting. `review.py` reproduces `review.json`; raw text is sealed under collected/25905114.pbs101.

Aggregate CPU time is 25:01:24, 96.673% of allocated core-seconds. This does not identify a bandwidth, MPI, cache or NUMA bottleneck. GNU time wraps the PALS launcher; its 0% CPU must not be interpreted as solver inactivity. The placement probe saw all ranks and CPU masks 0–127 but interleaved lines prevent reconstructing per-rank mapping. NUMA masks are permissions, not page placement. Hardware counters, bandwidth, power and page locality were not collected. A derived probe should emit one atomic record per rank outside solver timing.

The public one-node hierarchical value is 14.668759 s/step; our single run is about 1.726% slower. This is not a matched comparison or proof of a cause. Native Scotch is the next distinct hypothesis: test graph partitioning while retaining fixed physics and numerical work. A same-node H→S pair reduces host differences, with order/cache/repetition limits reported explicitly.

CPU accounting now reports Used 250.033 SU, an amount delta of 27.879 SU from 222.154. All five terminal allocation estimates sum to 27.880 SU. The site's displayed timestamp is chronologically inconsistent and detailed usage is incomplete: no exact individual posted charge is claimed. Conservative consumed planning ceiling is 29 SU, with no outstanding CPU jobs. This retires historical requested maxima without raising the unchanged 100-SU wave ceiling. Future submission guards must include consumed plus outstanding plus new maximum.

The earlier queue snapshots below are historical. The job started at 14:48:58 UTC, after about 13 minutes 5 seconds queued, and finished after 728 seconds. No queue resubmission occurred.

## Historical submission and queue record

# First full ASPIRE-2A CPU baseline submitted

**25905114.pbs101** accepted at 2026-10-21T14:35:53.856665+00:00. The retained
14:37:48 UTC PBS snapshot is Q in qdev. One exclusive CPU node, 128 CPUs and
MPI ranks, 440 GB, zero GPUs, maximum 35 minutes. This allocation runs all
mandatory parallel initialization and then 40 simpleFoam steps from the accepted
N128 hierarchical split; no decomposition is repeated.

Fresh source hash verification, project/own-queue/combined PBS cap checks,
pre-submit intent and 74.666667-SU maximum reservation occur under the CPU
budget lock. Conservative whole-wave maxima total 93.333334 SU below 100 SU.
No posted-charge reconciliation or AI ledger/payload change is implied.

The solver's actual duration is not measured yet. Queue waiting is separate
from the requested 35-minute execution cap. Next collect the real native
stages, placement, per-step distribution, Cd and terminal resource accounting;
submission or exit alone does not establish a score.

Two preceding backup attempts encountered concurrent shared Git staging: an
index lock, then unrelated pending paths from this worker's earlier checkpoint.
Both captures had already screened/verified their files. Recover them as two
path-scoped commits, preserving other staged work; both are now pushed. No
source, raw evidence or scheduler receipt was lost. Future HPC checkpoints use
one serialized capture/stage/commit/push scope with selected-path commits.

## Live queue inspection — 2026-10-21T14:48:23.781917+00:00

25905114 remains Q in qdev. PBS explicitly reports: Not Running: would exceed
overall limit on resource ncpus in queue qdev. The queue allows 256 active CPU
cores across all users and currently assigns 148, leaving 108; this job needs
128. At least 20 assigned cores must be released before this request can fit
that limit. This is a scheduler capacity restriction, not a running solver hang.
No execution start or new numerical/performance result exists at this check.

About 12 minutes 30 seconds has elapsed since submission. The 35-minute
walltime applies after the job starts and does not bound queue waiting. Preserve
the pending position; no unchanged resubmit or resource/queue/budget change is
made. One own CPU allocation remains the wave cap and its maximum reservation
stays retained. The full current safe scheduler reason/capacity is preserved
in queue-inspection-20261021T1448Z.json; dated snapshots are not live monitors.

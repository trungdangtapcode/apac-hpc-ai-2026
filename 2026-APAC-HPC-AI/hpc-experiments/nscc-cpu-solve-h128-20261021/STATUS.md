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

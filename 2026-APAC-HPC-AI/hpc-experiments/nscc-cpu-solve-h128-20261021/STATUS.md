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

# Iris reversed full-length order confirmation

Job **2294262** was accepted by Slurm at **2026-10-28T15:40:09.431273+07:00 (Vietnam, UTC+7)**. This is an actual submission, with a receipt and a reserved maximum of 168 allocated CPU-hours. Live state is recorded separately in `post-submit-status.json`; submission alone is not a valid measurement.

The frozen 49-file kit runs **xyz then zyx**, 150 steps and 149 timer samples per arm, on one exclusive Iris node with 56 CPU ranks, zero GPUs and a three-hour limit. The new allocation tests whether the first full pair's 21.2371% timing reduction persists after reversing serial order. Physics, fixed iterations, source case and executable selection are unchanged.

Parent job 2294234 completed cleanly in 7,585 seconds. Root replay verified both full native outputs and all 129 retained file hashes. Parent final Cd differs by 1.6185% between orders; this remains an output qualification limitation, not an established accuracy equivalence or a contest score.

Remote root: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-reverse150-20261028T083845Z`. Frozen kit: `root/kit`; run records: `root/runs/2294262`; cases: `root/cases/xyz` and `root/cases/zyx`. Preserve this kit and all old jobs.

## Accounting and limits

Previous planning consumption is 337 CPU-hours. One new maximum reservation of 168 makes a total commitment of 505 under a transparently documented 505-hour internal stage envelope. The owner authorized continued HPC research; the numeric stage amount was selected by the agent for this one job. It is not a site SU balance or an unlimited allocation. No NSCC CPU or AI budget was charged. One own active Iris allocation is the cap.

After terminal status, collect raw native outputs, timer and force tables, source/copy/field seals, runtime identities, resources and phases. Compare means, tails and Cd trajectories against the parent; reconcile the reservation once using actual terminal allocation time. Keep missing hardware telemetry explicit and do not transfer raw Iris seconds into NSCC rankings.

NSCC CPU SSH reuse reported no live VPN session during this turn; no additional MFA prompt was sent. Old NSCC job states remain unknown. The separate native NSCC bundle is still unsubmitted.

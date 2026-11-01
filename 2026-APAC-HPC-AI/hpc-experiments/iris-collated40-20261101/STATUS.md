# Actual submission and live state

Job **2294634**, tu-iris-io40, accepted 2026-11-01T21:46:50.651491Z (**2 November 04:46:50 Vietnam**). Actual scheduler at 21:48:06 UTC reports RUNNING on iris001, one node / 56 CPUs, 76 seconds elapsed. Payload and accepted initialized 1,040-file source plus official input pins pass; A-default isolated copy is being checked. No solver result is claimed yet. Keep its 70 CPU-hour maximum reserved until terminal accounting.

Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40-20261101T214618Z`; frozen runtime under `kit`, run evidence under `kit/runs/2294634`, cases under `kit/runs/2294634/arms/A-default` and `B-collated`.

A-default then B-collated; Scotch, same initialized source, same `--map-by socket --bind-to core`, 40 steps / 39 native intervals per arm. Only B adds `-fileHandler collated`. Maximum75min. This is an Iris one-node measurement, not Gadi four-node reproduction or an NSCC improvement.

After terminal, run `python3 collect_completed.py` once, then `PYTHONDONTWRITEBYTECODE=1 python3 review_completed.py`. Review all intervals/Cd, native I/O headers, runtime/source stability, stderr/resources and timing drift; reconcile once under `iris-scotch56-20261025/budget.lock`. No promotion from one A/B pair without a matched reverse/repeat. Old graph branch is closed after BAAB +5.3685% slower, not a robust gain.

## Native solver confirmed, 2 November 04:49:59 Vietnam

Actual scheduler still reports RUNNING on iris001 (189 seconds elapsed). Payload/source/input and isolated-copy hash/inode checks pass. A-default native simpleFoam started at21:48:12UTC and reached step2/40; its header confirms uncollated I/O, with no observed fatal marker and no scheduler stderr. This confirms actual solver execution, not a finished measurement. B-collated remains pending within the same allocation.

## Progress checked at 2 November 04:58:10 Vietnam

Job **2294634 remains RUNNING on iris001**, 680 seconds into the allocation. Native A-default is at **step 18/40**, with no observed fatal marker or scheduler stderr. B-collated has not started; this is not a completed metric or improvement. The one-own-allocation cap remains occupied and the full 70 CPU-hour maximum stays reserved. Read-only NSCC transport at 04:58:27 Vietnam still reports namespace unavailable; no additional authentication was triggered in this checkpoint. Current NSCC/Gadi performance results are unchanged. Preserve this job and review both complete native outputs before another decision.

# Actual submission and live state

Job **2294634**, tu-iris-io40, accepted 2026-11-01T21:46:50.651491Z (**2 November 04:46:50 Vietnam**). Actual scheduler at 21:48:06 UTC reports RUNNING on iris001, one node / 56 CPUs, 76 seconds elapsed. Payload and accepted initialized 1,040-file source plus official input pins pass; A-default isolated copy is being checked. No solver result is claimed yet. Keep its 70 CPU-hour maximum reserved until terminal accounting.

Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40-20261101T214618Z`; frozen runtime under `kit`, run evidence under `kit/runs/2294634`, cases under `kit/runs/2294634/arms/A-default` and `B-collated`.

A-default then B-collated; Scotch, same initialized source, same `--map-by socket --bind-to core`, 40 steps / 39 native intervals per arm. Only B adds `-fileHandler collated`. Maximum75min. This is an Iris one-node measurement, not Gadi four-node reproduction or an NSCC improvement.

After terminal, run `python3 collect_completed.py` once, then `PYTHONDONTWRITEBYTECODE=1 python3 review_completed.py`. Review all intervals/Cd, native I/O headers, runtime/source stability, stderr/resources and timing drift; reconcile once under `iris-scotch56-20261025/budget.lock`. No promotion from one A/B pair without a matched reverse/repeat. Old graph branch is closed after BAAB +5.3685% slower, not a robust gain.

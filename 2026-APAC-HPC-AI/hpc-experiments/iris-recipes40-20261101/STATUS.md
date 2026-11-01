# Direct comparison is running

Actual **2294637 RUNNING on iris001**, observed 2026-11-01T23:31:42 UTC (2 November 06:31:42 Vietnam), elapsed 1,184 seconds. Predecessor 2294635 completed 0:0 in 2,069 seconds; dependency cleared and Slurm started this job automatically without an overlapping allocation.

**A1 organizer completed 40 steps / 39 intervals**, runtime review mean 25.581958377 s/step. B1 teammate copy was being verified at that snapshot; by 06:34:43 Vietnam its native solver reached step 5/40. B2 and A2 remain pending in the same allocation. No observed fatal marker or scheduler stderr. **This is partial data, not a final recipe winner.**

The first A1/B1 launcher reports contain all 56 ranks and identical package/logical-core assignment maps. This is launcher evidence, not worker-thread affinity or memory locality. I/O headers confirm uncollated A1 and collated B1. No separate duplicate placement-only allocation is justified; its prepared proposal is closed unsubmitted. Full four-arm performance/Cd/runtime/tail review remains required.

Frozen 57-file runtime remains unchanged. Maximum 140 CPU-hours remains reserved; global ledger 593 consumed + 140 reserved = 733 CPU-hours under internal stage 770. Source files/logs and exact commands are retained. Collect/review after terminal; do not infer completion from one arm or compare these Iris seconds directly with Gadi/NSCC results.

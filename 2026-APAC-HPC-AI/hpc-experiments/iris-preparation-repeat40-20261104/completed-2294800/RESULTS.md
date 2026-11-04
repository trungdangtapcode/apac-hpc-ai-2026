# Independent same-horizon ABBA repeat rejects stable preparation-only gain

Reviewed at the dated checkpoint on 5 November 2026 Vietnam time. Job 2294800 COMPLETED 0:0 in 4,925 seconds on iris001 /56 CPUs. All 237 collected hashes and frozen deployed files verify. Four independent native replays pass exactly 40 steps /39 finite timing intervals, expected fixed iteration counts, zero exit and identical force trajectories. All top-level stage statuses return 0; source/copy/policy/input/payload checks pass and runtime identity is stable.

| ABBA arm | Mean seconds/step | Maximum seconds/step |
|---|---:|---:|
| A1 inherited |24.758152088|26.069623802|
| B1 interleaved |29.279149851|29.979897396|
| B2 interleaved |28.730517360|36.313042791|
| A2 inherited |29.917717071|30.973212982|

Candidate pooled mean **29.004833605 s/step**, control **27.337934579 s/step**: **6.097384649% slower**. Adjacent contrasts are +18.26064% and −3.96822%, so directions conflict. Control drift is +20.83986%; candidate drift −1.87380%. Both candidates have slower medians than A1; the B2 maximum exceeds either control. Retain all measured intervals.

This changes only order at the same 40-step horizon as parent 2294735: the earlier BAAB reduction of 30.60191% is not reproduced by this fresh ABBA allocation. The smaller 20-step screen also had inconsistent signs. Close the unchanged preparation-child-only performance branch. The earlier 30.60% remains a valid within-job observation, not a stable optimization; no cross-job score, official 150-step result or gain against teammate/NSCC/Gadi is claimed. Native correctness passing does not mean the candidate wins.

The diagnostics collect 206/241/237/246 whole-node samples. All required CPU/memory/vmstat sources are present, no collection errors; pressure files are unavailable. Median reported CPU frequency is about 3.30 GHz in three arms and 3.20 GHz in B2; this is not effective-cycle measurement or a proven cause. Minimum available memory is 36.2–39.7 GiB. Maximum read duration 4.57 ms is not measured interference. Per-rank memory policy, anonymous page residency and bandwidth remain unmeasured. Allocation/time/NUMA effects cannot be isolated from the pooled result.

Cost **76.611111 allocated CPU-hours**, conservatively 77 planning hours. Retire 112 reserved once under lock: 1,175 consumed /zero reserved /1,210 internal stage. Not billed SU. No blind preparation-only repeat is justified. A distinct low-cost next qualification can inspect actual MPI-rank policy and first-touch anonymous-page residency under a solver-launcher policy change; that tests an unverified mechanism, not another speed claim. Any such test needs its own sealed input, acceptance and small budget within the current stage.

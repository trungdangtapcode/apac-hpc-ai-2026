# Direct recipe comparison actually submitted

**Job 2294637**, tu-iris-rec40, accepted **2026-11-01T23:04:50.480660Z** (**2 November 06:04:50 Vietnam**). At **06:05:19 Vietnam**, actual Slurm reports **PENDING / Dependency**, `afterany:2294635(unfulfilled)`. Predecessor 2294635 remains RUNNING on iris001. New job's **AllocCPUS=0**, no node assigned and AllocTRES null: no simultaneous allocation.

One exclusive Iris node / 56 ranks / zero GPUs, maximum **2.5 hours / 140 allocated CPU-hours**. Four independent 40-step copies in order **organizer / teammate / teammate / organizer**, with the same canonical initialized Scotch source and OpenFOAM build. A uses default MPI mapping with uncollated I/O; B adds socket/core mapping and collated I/O. Both collect common launcher reports. This is a normalized solver-runtime comparison, not literal Gadi reproduction or a rerun of teammate preparation flags.

Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-recipes40-20261101T230311Z`; frozen 57-file runtime in root/kit; evidence/cases root/kit/runs/2294637. Slurm will release the dependency after 2294635 terminates, then schedule the job normally. No Codex background process, schedule or automatic chat notification was enabled.

The test-only message mentioned 2294636; that was **not an accepted allocation or experiment**. Actual accepted receipt is 2294637. Test-only predicted wall-clock text is not a live start observation; actual owner-facing times use recorded UTC converted to Vietnam.

Local Iris planning ledger is **560 consumed +210 reserved =770 CPU-hours**, including both predecessor 70-hour and successor 140-hour maxima. The current explicit request funds this one bounded successor. One active CPU allocation is preserved per POLICY.md line 61 and initial campaign PLAN.md line 13; the new admission allows only its exact dependent successor, not unrelated own queued jobs. Keep both reservations until actual terminal reconciliation. PBS caps and NSCC/AI accounting are unchanged.

After terminal, collect with collect_completed.py and replay with review_completed.py. Review all four raw timelines/Cd, actual I/O headers and commands, control repeats, adjacent effect directions, launcher diagnostics, resource snapshots and confidence warnings before claiming a relative winner. No measured result yet.

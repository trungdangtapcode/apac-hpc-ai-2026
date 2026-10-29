# Current HPC/OpenFOAM handoff

Updated from actual scheduler observation **2026-10-29T10:40:05.719413+07:00 (Vietnam, UTC+7)**. HPC fork 01a17c4b-65e6-75e0-be95-c5bea1b25502 continues parent 01a1508d-26b0-7dd0-9dc1-f217ce0aff40. AI is separate. No background Codex, schedules or automatic notifications.

## Actual running work

**Iris 2294390 RUNNING on iris005**, accepted 2026-10-29T10:39:33.187519+07:00, one exclusive node, 56 CPUs, zero GPUs, 50-minute maximum. It runs **B1 graph / A1 identity / A2 identity / B2 graph**, 14 steps / 13 timings each. At the stated observation it was sealing source, not yet a completed solver result. Native mapping and accepted source must qualify before any solver. [Receipt and exact status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/STATUS.md).

Remote root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-gmap14r-20261029T033908Z`. Evidence/cases `root/kit/runs/2294390`; scheduler logs `root/kit/runs/2294390.out/.err`. Frozen 57-file derived payload changes only order/labels, job name and README from actual completed 2294366. Preserve parent and new kits. One own Iris allocation is the cap; own prefix tu-. Shared rdmaworkshop30 jobs are not ours and must not be altered.

## Latest reviewed solver screen

**2294366 completed 0:0**, iris009, 1,758 seconds / 56 CPUs. All 397 selected file hashes, four 14-step native replays, mapping/source/field/runtime checks pass. A1/B1/B2/A2 means: **21.095162  / 21.136731  / 22.841273  / 32.867341 s/step**. Aggregate candidate ratio **-18.5027% is UNCONFIRMED**: first B/A +0.1971%, control repeat +55.8051%, candidate repeat +8.0644%; last control has 69.1669 s max and 28.0303 median. Native recommendations 0 / 0 / 11 / 1258 versus 13 samples. Keep every slow sample. Same-treatment Cd repeats exactly; cross-treatment total Cd differs by ~1e-15. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-screen-20261029/completed-2294366/RESULTS.md).

Current BAAB tests treatment positions before promoting the favorable aggregate. Both cycles are non-scored short screens, not 150 steps, independent confidence intervals, NSCC gains or official scores. Actual solver helper affinity, frequency, hardware bandwidth and NUMA page residency were not collected. A main-thread C MPI probe is not a solver-thread observation.

## Budget

Iris ledger `iris-scotch56-20261025/budget.json`, sibling `budget.lock`: consumed **485**, reserved maximum **46.666667**, commitment **531.666667**, internal stage **532**, headroom **0.333333 CPU-hours**. Parent 2294366 actual 27.346667 hours conservatively counted 28; its maximum retired once. New internal ceiling adds 27 to prior 505 solely for this owner-authorized single confirmation; the owner did not specify 532 numerically. No site SU rate/balance is known and no NSCC/AI credit was moved. [Bounded authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-graphmap-reverse-20261029/budget-authorisation.json). Do not infer another automatic budget increase or submit beyond current caps.

## Full-result history and NSCC objective

Large hierarchy-order gain failed reversal: 2294234 on iris024 zyx-first 21.229594 then xyz 26.953799 ; 2294262 on iris005 xyz-first 21.823904 then zyx 26.610796. Do not promote 21% as stable tuning. Cross-order Cd differs 1.61846%; same-order repeats are exact. Native MPI probe 2294358 then showed default/core-fill CPU maps identical, so that duplicate branch was closed; span worsened face proxies and was not benchmarked. Offline balanced zyx rank placement reduced the logical cross-NUMA face proxy 129700→90953 with unchanged group loads; that motivated the current screens, not a speed prediction.

Best own reviewed full **NSCC 3.364622070 s/step**, 25940700, 4 nodes / 512 ranks / default Scotch / 150 steps, remains a reproduction of the organizer recipe. External organizer 3.210832548 is separate. No own new NSCC configuration has demonstrated a matched improvement below 3.3646. Do not substitute Iris seconds for this goal.

Fresh VPN retry at about 10:33 Vietnam on 29 October failed Authentication failed. Current NSCC queue/credit/old-job states are unknown, not empty. No new NSCC deployment/reservation/receipt. Captain holds DUO; do not ask the owner to inspect that phone repeatedly. Health gate requires actual tunnel/SSH transport then authenticated host-key-verified command; namespace existence alone was a corrected false positive. Preserve private caches; no indefinite MFA loop.

The native 61-file S0/Hxyz/Hzyx NSCC bundle remains ready and independent of optional PMPI work. Before admission, refresh CPU and AI queues, project 59000042 credit/rate and all old commitments under CPU-before-AI locks; CPU cap 1, combined PBS cap 3 including holds. AI 59010042 is separate. Old 26019383 and shared 26023372/373/382/383 need safe provenance/terminal review; do not cancel, duplicate or erase reservations.

## Next step and backup

Query actual 2294390. On terminal, run its dynamic `collect_completed.py` and `review_completed.py`, inspect all four arms jointly with parent ABBA, tails/errors/Cd/resource limits and source/mapping/runtime identity, then reconcile once. Select a distinct next measurement from that evidence within limits; preserve queue positions. NSCC native trials remain first when access and admission recover. [New journal](../reports/research-journey-20261019/journal/entries/20261029-hpc-abba-review-and-baab-submitted.md); [previous detailed handoff](history/HPC_CURRENT-before-baab-2294390-20261029.md).

Capture only reviewed safe selections, verify, commit and push. Selected text and rebuild provenance are retained; large meshes/fields remain remote and external artifacts are not uploaded by Git. No submission or other-track payload was changed.

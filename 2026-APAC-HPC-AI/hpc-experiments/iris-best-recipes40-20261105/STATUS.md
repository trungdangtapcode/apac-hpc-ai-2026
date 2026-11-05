# Direct best-recipe comparison accepted

Iris accepted **2294920** at `2026-11-05T17:53:40.285250Z` UTC. At 00:56 on 6 November 2026 Vietnam time it was RUNNING on iris001, elapsed 2:20, with no batch stderr. This is scheduler/setup status, not a new solver score. Frozen source and runtime gates precede native measurements.

## Objective and evidence for the change

The owner requested actual improvement, not an attractive percentage against a slower control. The 48-versus-56 default-runtime finding remains valid at 17.38% and 19.21% lower time in its two scoped 40-step jobs. However, 26-second pooled time has not beaten historical teammate 22.39695 seconds in a completed 40-step arm (its second arm 27.09361, pooled 24.74528). The retained old and recent records share iris001, simpleFoam/mpirun hashes, all 48 linked-library identities and the N56 core source hashes. That rules out changes in those recorded components, not every runtime state, and does not establish why timings vary. Reproduce the comparison with ../iris-absolute-time-audit-20261105/audit.py.

## Exact six-arm native trial

| Order | Recipe | MPI ranks | MPI mapping/binding | File handler |
|---|---|---:|---|---|
|T1|Teammate56|56|socket /core|collated|
|O1|Original48|48|default|uncollated|
|H1|Hybrid48|48|socket /core|collated|
|H2|Hybrid48|48|socket /core|collated|
|O2|Original48|48|default|uncollated|
|T2|Teammate56|56|socket /core|collated|

Every arm must complete 40 steps /39 timing intervals with identical original physical 65,334,765-cell problem, fixed iteration work, native double-precision build and accepted rank-specific initialization. This tests whether combining the promising 48-rank partition with the teammate mapping/I/O recipe beats both credible controls in **absolute seconds per step**. It is a bundled configuration test, not proof of an isolated mapping or file-handler cause. No historical absolute record or performance gain is declared before actual results.

Matching rank probes and native solver reports retain the actual mapping for each recipe. Native headers must confirm the requested collated/uncollated handler. Same-recipe repeats and same-source original48/hybrid48 force differences use the existing internal numerical regression tolerance; cross-partition teammate56-versus48 Cd differences remain recorded without an invented universal Basic equality gate. Preserve initialized fields, source/payload/runtime identities before/after, all slow timings, fixed iterations, finite force rows, errors, resources and whole-node telemetry. Python OS-affinity probes are pre-MPI_Init, not solver-thread residency proof. Missing pressure/counters are not healthy zero readings.

## Review, limits and budget

Root imported the runner and replayed exact six-arm wiring, complete-window rejection, source transforms, synthetic label-based absolute mean/delta arithmetic, a recipe/rank mismatch rejection, and the actual historical collated 56-rank native parser/header. Synthetic fixture times are tests, not measurements. All 100 operational hashes verify; only run.py, prepare_arm.py and job.sbatch differ from the valid parent. A helper rank/recipe consistency guard was added before sealing. The payload is frozen; no submitted source was changed.

One exclusive node /56 allocated CPUs /zero GPUs /maximum 4 hours: **224 allocated CPU-hours reserved**. Each solver cap is 1,800 seconds, each prep 150, final reserve 480, internal deadline 13,900 and wrapper 14,340. Six complete windows need 12,180 seconds; no arm may be shortened to fit. Require 96 GiB filesystem free, not a user quota claim. Observed Iris partition is UP/unlimited wall time; low QoS permits 12 hours, so 4 hours fits.

The valid 40-domain preparation 2294919 used 3.966667 CPU-hours, conservatively 4, and its 37.333333 maximum retired once. Its initialization remains deferred and cannot block this independent test of already initialized 48/56 sources. Ledger before admission was 1,396 consumed /zero reserved. This one 224-hour request extends the internal stage 1,450→1,620 (+170), not a new owner numerical budget or known billed site SU. NSCC/AI accounts remain separate, one-own allocation cap preserved. A fresh queue check and exact deployment hashes precede the durable receipt; no blind resubmission.

## Decision after measurement

Report absolute per-recipe means, both repeat arms, tails and errors first. Compare hybrid against both teammate56 and original48; keep historical 22-second and other retained observations visible as unmatched references. A relative win alone does not mean the historical absolute record improved. Keep losing configurations and diagnose failures; incomplete results are not valid completed benchmarks. Review repeated/control drift before promoting any configuration. No background Codex, automatic follow-up or chat wake-up was enabled.

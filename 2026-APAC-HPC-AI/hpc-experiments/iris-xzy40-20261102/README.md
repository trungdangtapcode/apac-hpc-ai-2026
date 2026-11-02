# Native Iris screen: hierarchical xzy versus Scotch

The accepted initialized xzy manifest comes from completed, independently reviewed job **2294642**, not from the old zyx source. Actual deployment, reservation and scheduler acceptance are tracked in STATUS.md and the submission receipt. A reviewed payload alone does not establish submission.

## Question and prior evidence

Does the standard hierarchical `(7 4 2)` decomposition with `order xzy` improve native solver time over default Scotch on one Iris node? This tests a real configuration that has not yet had a solver comparison. It is not a new decomposition algorithm.

The four-cut screen in job 2294097 found xzy had 1,256,287 unique interface faces and at most 12 neighbor patches, versus 1,269,961 / 13 for zyx and 1,326,716 / 14 for fresh xyz. However, xzy's busiest rank had 98,522 interface faces, above zyx's 91,721 and xyz's 93,343. These competing graph metrics motivate one bounded native screen; they do not predict a speedup. Scotch's lower interface count also failed to predict faster solving in an earlier censored comparison.

The recent complete zyx-versus-Scotch ABBA run 2294640 did not support the zyx hypothesis and had substantial timing drift. This xzy test changes the hierarchy order and is a distinct, still unmeasured configuration. It must not be presented as confirmation of zyx or as evidence that all hierarchical layouts win.

## Fixed-work comparison

| Arm | Source | Treatment |
|---|---|---|
| B1 | Accepted initialized xzy source | Hierarchical `(7 4 2)`, `order xzy` |
| A1 | Accepted initialized Scotch source | Default Scotch |
| A2 | Independent Scotch copy | Default Scotch repeat |
| B2 | Independent xzy copy | Hierarchical `(7 4 2)`, `order xzy` repeat |

All arms use one exclusive Iris node, 56 ranks, OpenFOAM v2512 double precision, the original 65M mesh and physics, fixed solver iterations, default MPI launch and uncollated I/O. Each arm runs 40 steps and retains 39 native timing intervals. The two methods use their own accepted initialized processor partitions and fields; only the canonical physical inputs and solver work are shared. Each arm gets an independent filesystem copy and integrity/field seals.

The primary comparison pools equal-length repeats by method. The report also shows both adjacent comparisons, repeat drift, per-arm nearest-rank p95/p99 and maximum, native sample recommendations, complete Cd rows and descriptive within-method Cd repeat differences. No outlier is dropped. A single BAAB allocation can balance linear timing drift, but not nonlinear changes or independent-run variation. A large drift or conflicting adjacent comparisons makes the result inconclusive.

## Gates and limits

Every arm must pass native 40-step/39-interval timing, exact fixed-iteration checks, finite native outputs, successful solver exit, source and copy manifests, unchanged initialized fields, actual uncollated I/O header, runtime/library identity and transfer hashes. Cd differences are descriptive, not a newly invented task tolerance. Collect CPU/resource logs and available node snapshots; missing bandwidth, helper-thread affinity or page-residency telemetry must remain marked uncollected.

The scheduler maximum is 9,000 seconds (140 allocated CPU-hours) on 56 CPUs with zero GPUs. This is a conservative local planning reservation, not a claim about billed Iris SU. Fresh queue, budget, exact source manifest, frozen payload review and the one-active-allocation cap are root admission gates. A terminal job alone is not a valid measurement.

This is an Iris result only. Sub-22-second Iris observations do not predict performance against the teammate's 2.079-second-per-step Gadi result. No Gadi/NSCC result, score or cross-platform speedup is claimed.

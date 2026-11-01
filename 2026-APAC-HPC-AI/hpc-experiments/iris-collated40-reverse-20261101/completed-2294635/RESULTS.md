# Reversal does not confirm the collated I/O gain

Job **2294635 completed 0:0** on iris001 in 2,069 seconds, 56 CPUs. All 116 transferred files passed hash verification; both native 40-step / 39-interval outputs passed independent replay, source/copy/field/runtime identity and actual I/O checks. The original fixed numerical work and every Cd row are identical across all four completed arms in both jobs.

| Job and execution order | Default mean (s/step) | Collated mean (s/step) | Collated relative to default |
|---|---:|---:|---:|
| 2294634: default then collated | 31.600735680 | 29.681757101 | 6.0726% lower |
| 2294635: collated then default | 21.431810307 | 23.435621344 | 9.3497% higher |

**The later arm wins in both orderings.** The first apparent gain is not reproduced. Pooling both jobs gives collated 0.159963% higher mean, a descriptive summary across allocations rather than causal proof of a small regression. Do not promote 6.07% as an optimization or selectively drop slow intervals. Close the unchanged isolated-I/O gain branch.

The reverse collated median is 23.230112357 s and maximum 24.779420931 s; default median 21.403943358 s and maximum 22.293726484 s. Native sample recommendations are 10 and 1 against 39 observations. Passing those within-run recommendations does not resolve order effects or provide independent run-level confidence. Final Cd is 0.436959331 in every arm; Basic sanity is not a universal numeric tolerance gate.

INSPECTION.json retains first/last timing-window means, population SD, nearest-rank P95, selected GNU time counters and before/after reported CPU MHz. Both commands report around 55 aggregate CPU equivalents in GNU time, which does not establish compute versus MPI busy-wait bottlenecks. Collated reports 4,471,004 kbytes maximum RSS versus default 2,851,272; the same direction appeared in the parent pair. This is command-reported maximum RSS, not summed node memory or a measured cause of timing differences. Command swap counters are recorded as zero; no general memory-health claim follows.

CPUinfo samples are **outside solver execution**. Some report a 4,000 MHz median and the final idle snapshot around 1,000 MHz; they cannot establish sustained frequency during measured steps or explain the time drift. Hardware bandwidth/cycles, actual solver helper affinity and NUMA page residency were not collected. Runtime and transport stderr were inspected; no native fatal marker or scheduler stderr was observed.

Cost: 32.184444 allocated CPU-hours, conservatively counted 33. The original 70-hour maximum was retired once. Local planning ledger becomes 593 consumed plus the running direct-comparison maximum 140, commitment 733 under internal stage 770. No site SU claim or NSCC debit.

The owner-requested direct recipe ABBA **2294637 already started automatically after this job**, without overlapping allocations. It must complete before a full recipe winner is reported. Its first launcher reports show identical rank/package/logical-core placement for the first organizer and teammate arms; that is not worker-thread affinity proof. A standalone mapping-only candidate is closed unsubmitted because no distinct placement has been observed. This does not prove Gadi behaves identically to Iris.

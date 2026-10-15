# MNNVL repeat review and next queued point — 2026-10-15 21:01 UTC

Independent CPU audit of original23778 and repeat23839 passed: all sealed
artifact checksums match, full60/120/30 protocol is recorded, and all eight
decode ranks explicitly initialized MNNVL. Submitted worker, client, launcher,
NIXL patch, warmup and smoke scripts match; configs differ only in experiment
name and purpose. No new GPU job was submitted by this review.

| Job | N | Good tokens/s | SLA | TTFT mean ms | ITL mean ms |
|---|---:|---:|---:|---:|---:|
| 23778 | 52 | 2592.16 | 99.0068% | 516.28 | 17.1273 |
| 23839 | 52 | 2592.92 | 99.0074% | 508.25 | 17.1545 |

Mean2592.54goodtokens/s, repeat change+0.0294%; gain+8.02% over N52 control23607
and+6.32% over N53 repeat23773. Against23607, mean ITL decreases2.384ms while
mean TTFT increases165.43ms. Two runs reproduce this configuration under these
conditions; they do not estimate all-cluster variability or prove accuracy.
Both diagnostics remain7/8, only known reverse failure, no new failed cases.

4000/200 is the requested synthetic protocol. Exports report mean input3986.004
and output approximately200 with199–201 extrema in both runs; do not relabel
the requested4000 as an observed exact input length. No benchmark setting was
changed. Runtime initialization evidence is not a new kernel profile.

Existing gate passed and watcher submitted23924(N54) at21:00:05UTC. At21:01:24UTC
it and23859/23904–23906 are PENDING(Priority); shared cap5 is full.

When23924 finishes, collect full export, phase manifest, output diagnostics,
backend initialization and sealed artifacts. Compare against mean2592.54 and
both N52 runs, preserve TTFT/ITL tradeoffs and errors/cancellations. A failed
startup without export is INCOMPLETE; a complete latency failure is a measured
load boundary. A faster single N54 point still needs independent confirmation
before selection. Existing wave7 scope ends at this N54; do not invent an
ungated N56 continuation. Keep wave9 interaction comparisons against both
MNNVL N52 runs. Organiser accuracy remains unverified.

Evidence: [audit JSON](../nscc-pbs/inspection/wake-20261015-2100UTC/mnnvl-repeat-review.json).

# Four-node OpenFOAM native evidence review

This offline review covers six sealed 150-step runs across Scotch and hierarchical decomposition at 64, 96 and 128 MPI ranks per node. The collection preserves native files, but PBS history is unavailable: PBS returns `UnknownJobId` for all six. The results below are candidate native observations, not accepted scores.

## Integrity and per-run checks

The 406 local collection entries and 404 remote file hashes passed SHA-256 verification; the raw archive contains 405 unique, safe file members. Each run passed source comparison against the accepted baseline (allowing only decomposition method, rank count, hierarchical factors and endTime), native OpenFOAM 2512 / v2512 scalar64 labels, mesh cell total, solver rank count, four distinct native hosts with the expected per-host rank grouping, full 150-step sequence, all five native `End` markers, no fatal or MPI signal marker, fixed iteration work, finite 150-row force coefficients, and all 149 timed samples cross-checked between solver log and wallClockTime data.

| Job | Method | MPI ranks/node (total) | Requested CPUs | Mean s/step | p95 s | Max s (Time) | Final Cd | Mean/median | Top three timed steps (Time: seconds) | Largest-step share | Min recommended samples | Short-sample warning |
|---|---|---:|---:|---:|---:|---|---:|---:|---|---:|---:|---|
| 25921488.pbs101 | scotch | 128 (512) | 512 | 3.677906731 | 3.795740 | 35.883552 (T119) | 0.2839830076 | 1.115 | 119: 35.884, 40: 10.658, 76: 9.014 | 6.55% | 5491 | yes |
| 25921517.pbs101 | scotch | 64 (256) | 256 | 10.309943538 | 19.637053 | 72.923052 (T86) | 0.2891997282 | 1.485 | 86: 72.923, 46: 67.263, 47: 60.710 | 4.75% | 8329 | yes |
| 25921518.pbs101 | scotch | 96 (384) | 384 | 7.146018748 | 15.816692 | 31.677264 (T130) | 0.2858085996 | 1.223 | 130: 31.677, 124: 26.215, 146: 20.365 | 2.98% | 2696 | yes |
| 25921692.pbs101 | hierarchical | 128 (512) | 512 | 3.819929017 | 5.224630 | 12.925347 (T129) | 0.2739197432 | 1.085 | 129: 12.925, 100: 9.923, 29: 9.344 | 2.27% | 943 | yes |
| 25921905.pbs101 | hierarchical | 96 (384) | 512 | 4.922347604 | 11.762667 | 38.847831 (T97) | 0.2755638858 | 1.408 | 97: 38.848, 65: 19.745, 67: 18.595 | 5.30% | 6685 | yes |
| 25921906.pbs101 | hierarchical | 64 (256) | 512 | 4.488921327 | 9.882991 | 20.984311 (T35) | 0.2734412525 | 1.265 | 35: 20.984, 100: 20.451, 108: 16.053 | 3.14% | 3805 | yes |

## Earlier endpoint context

Earlier handoff values were 13.880988254 s/step for one-node Scotch at 128 ranks/node, and 7.169996913 / 7.462835189 s/step for two-node hierarchical / Scotch at 128 ranks/node. Those observations used separate allocations and different endpoints; this is context for the research presentation, not a matched scaling curve or causal comparison.

The lowest native Average is **25921488.pbs101** at **3.677906731 s/step**. By ranks per node, the observed means favor 64: 25921906.pbs101 (4.488921327 s/step), 96: 25921905.pbs101 (4.922347604 s/step), 128: 25921488.pbs101 (3.677906731 s/step). These are descriptive comparisons among separate allocations, without scheduler completion or accounting records.

The p95 uses linear interpolation. Mean/median ratios and top-three step lists describe the observed time-series tail. Largest-step share is that step’s portion of the untrimmed 149-sample sum (and of the arithmetic mean); it is a diagnostic only. No step is removed or downweighted from Average. Full time-indexed samples, corrected IQR fences and outliers, Cd ranges, rank-to-host groups, selected runtime flags, stage tails/warnings and per-run checks are retained in [review.json](review.json). The decomposePar algorithm timer plus three initialization `ClockTime` measurements is a **partial** preparation sum; it omits decomposePar transfer/write, I/O and unaccounted setup time, so it is not an initialization-duration estimate or a setup winner.

## Interpretation limits

The collection metadata retains the prior PBS snapshot as queued and explicitly has no final state or exit status. Current `UnknownJobId` responses do not establish completion or failure. No final elapsed time or actual charge can be recovered from these logs, and no full-slot billing comparison is made. Requested CPU counts are recorded; Scotch 64 requested 256 CPUs while hierarchical 64 requested 512 despite both using 256 MPI ranks.

Native `End` markers show the solver logs ended normally, but the history-free collection lacks frozen submission proofs, individual command return codes, final zero-field seals and affinity evidence. Four-host placement is parsed from the solver’s own `Hosts` list and Pstream header, not from a rank-affinity map. These limitations prevent acceptance as scored results. The native sample recommendation exceeds 149 timed steps in each case; emitted short-sample warnings and recommendation counts are preserved, not treated as formal confidence intervals.

No hardware counters, memory bandwidth, page residency, MPI wait/traffic or authoritative final mesh/field identity were collected. The comparison does not identify a causal bottleneck.

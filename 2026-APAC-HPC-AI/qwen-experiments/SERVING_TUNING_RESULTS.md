# Qwen serving tuning — next wave

Updated UTC: 2026-10-18T19:24:16.365875+00:00

Control: measured job 22415, TP4 prefill → TP8/EP8 decode, BF16 KV, request-scoped NIXL patch.
Every ranked point uses 60 s warmup, 120 s measurement, 30 s grace. Profiling traffic is separate.
Full results are required; FAILED/TIMEOUT without an export is never a completed benchmark.

| Experiment | Jobs / states | Missing N | Status |
|---|---|---|---|
| control-load | 23102:COMPLETED, 23106:COMPLETED | [] | MEASURED |
| dense-decode-graphs | 23103:COMPLETED, 23109:COMPLETED | [] | MEASURED |
| profile-control | 23104:COMPLETED | [] | MEASURED |
| load-best-repeat | 23113:COMPLETED | [] | MEASURED |
| prefill-chunk4096 | 23114:COMPLETED | [] | MEASURED |
| decode-deepgemm | 23115:COMPLETED | [] | MEASURED |
| s2-control-n52 | 23128:COMPLETED | [] | MEASURED |
| s2-chunk4096-n52 | 23129:COMPLETED | [] | MEASURED |
| s2-chunk4096-dense-n52 | 23130:COMPLETED | [] | MEASURED |
| s2-chunk16384-n52 | 23131:COMPLETED | [] | MEASURED |
| s2-deepgemm-control-n52 | 23264:COMPLETED | [] | MEASURED |
| s2-fp8-kv-n52 | 23265:COMPLETED | [] | MEASURED |
| s2-repeat-best | 23266:COMPLETED | [] | MEASURED |
| s2-repeat-runner | 23267:COMPLETED | [] | MEASURED |
| s2-deepep-ll-n52 | 23272:COMPLETED | [] | MEASURED |
| s3-control-n52 | 23286:COMPLETED | [] | MEASURED |
| s3-best-n54 | 23287:COMPLETED | [] | MEASURED |
| s4-prefill-single-n52 | 23324:COMPLETED | [] | MEASURED |
| s4-prefill-roundrobin-n52 | 23325:COMPLETED | [] | MEASURED |
| s3-best-n56 | 23437:COMPLETED | [] | MEASURED |
| s3-best-n60 | 23495:COMPLETED | [] | MEASURED |
| s3-midpoint | 23505:COMPLETED | [] | MEASURED |
| s3-best-load-repeat | 23516:COMPLETED | [] | MEASURED |
| s5-rr-repeat-n52 | 23576:COMPLETED | [] | MEASURED |
| s5-rr-n50 | 23577:COMPLETED | [] | MEASURED |
| s5-rr-n54 | 23583:COMPLETED | [] | MEASURED |
| s6-rr-profile-n52 | 23607:COMPLETED | [] | MEASURED |
| s6-rr-fp8kv-n52 | 23608:COMPLETED | [] | MEASURED |
| s6-rr-deepgemm-n52 | 23609:COMPLETED | [] | MEASURED |
| s5-rr-midpoint | 23616:COMPLETED | [] | MEASURED |
| s5-rr-best-repeat | 23773:COMPLETED | [] | MEASURED |
| s7-rr-cutlass-n52 | 23776:FAILED | [52] | INCOMPLETE |
| s7-rr-flashinfer-n52 | 23777:COMPLETED | [] | MEASURED |
| s7-rr-mnnvl-n52 | 23778:COMPLETED | [] | MEASURED |
| s8-rr-dpa8-deepep-n52 | 23780:COMPLETED | [] | MEASURED |
| s7-mnnvl-repeat-n52 | 23839:COMPLETED | [] | MEASURED |
| s8-dpa8-repeat-n52 | 23859:COMPLETED | [] | MEASURED |
| s9-mnnvl-flashinfer-n52 | 23904:COMPLETED | [] | MEASURED |
| s9-mnnvl-chunk2048-n52 | 23905:COMPLETED | [] | MEASURED |
| s9-mnnvl-chunk8192-n52 | 23906:COMPLETED | [] | MEASURED |
| s7-mnnvl-n54 | 23924:COMPLETED | [] | MEASURED |
| s8-dpa8-n54 | 23934:COMPLETED | [] | MEASURED |
| s10-combo-repeat1-n52 | 23973:COMPLETED | [] | MEASURED |
| s10-mnnvl-control-n52 | 23974:COMPLETED | [] | MEASURED |
| s10-combo-repeat2-long-n52 | 23975:COMPLETED | [] | MEASURED |
| s10-mnnvl-repeat-n54 | 24009:COMPLETED | [] | MEASURED |
| s10-combo-n54 | 24131:COMPLETED | [] | MEASURED |
| s10-combo-fresh-n52 | 24174:COMPLETED | [] | MEASURED |
| s10-combo-repeat-n54 | 24175:COMPLETED | [] | MEASURED |
| s10-combo-control-n54-v2 | 24189:COMPLETED | [] | MEASURED |
| s10-combo-probe-n56 | 24190:COMPLETED | [] | MEASURED |
| s10-combo-repeat-n56 | 24235:COMPLETED | [] | MEASURED |
| s10-combo-probe-n58 | 24236:COMPLETED | [] | MEASURED |
| s10-combo-profile-n56 | 24263:COMPLETED | [] | MEASURED |
| s10-cross-platform-n50 | 24272:COMPLETED | [] | MEASURED |
| s10-combo-prefill-single-n56 | 24281:COMPLETED | [] | MEASURED |
| s10-combo-prefill-tp8-n56 | 24282:FAILED | [56] | INCOMPLETE |
| s10-prefill-deepgemm-n56 | 24291:COMPLETED | [] | MEASURED |
| s10-combo-control-n56-v3 | 24320:COMPLETED | [] | MEASURED |
| s10-prefill-tp8ep2-n56 | 24321:FAILED | [56] | INCOMPLETE |
| s10-prefill-prefetch-n56 | 24322:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-repeat-n56 | 24327:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-n58 | 24352:COMPLETED | [] | MEASURED |
| s10-prefill-tp8ep2-equal-n56 | 24375:COMPLETED | [] | MEASURED |
| s10-prefill-no-graph-n56 | 24376:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-chunk8192-n56 | 24425:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-no-graph-n56 | 24426:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-n54 | 24428:COMPLETED | [] | MEASURED |
| s10-prefill-deepgemm-profile-n56 | 24429:COMPLETED | [] | MEASURED |
| s11-dg-control-n56 | 24526:COMPLETED | [] | MEASURED |
| s11-dg-chunk8192-repeat-n56 | 24527:COMPLETED | [] | MEASURED |
| s11-dg-chunk6144-n56 | 24528:COMPLETED | [] | MEASURED |
| s11-hpc-prefill-n56 | 24529:COMPLETED | [] | MEASURED |
| s11-hpc-decode-n56 | 24538:COMPLETED | [] | MEASURED |
| s11-dg-chunk8192-n58 | 24544:COMPLETED | [] | MEASURED |
| s12-dg-chunk6144-repeat-n56 | 24573:COMPLETED | [] | MEASURED |
| s12-hpc-prefill-repeat-n56 | 24574:COMPLETED | [] | MEASURED |
| s12-dg-fresh-control-n56 | 24575:COMPLETED | [] | MEASURED |
| s12-dg-chunk8192-repeat-n58 | 24588:TIMEOUT | [58] | INCOMPLETE |
| s12-dg-fresh-control-n58 | 24589:PENDING | [58] | ACTIVE |
| s13-hpc-decode-n58 | 24639:PENDING | [58] | ACTIVE |
| s13-hpc-prefill-chunk6144-n56 | 24640:PENDING | [56] | ACTIVE |
| s13-hpc-both-n56 | 24641:PENDING | [56] | ACTIVE |

| Job | Experiment | N | Good tokens/s | SLA | TTFT mean ms | ITL mean ms | Errors | Cancelled | Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 23102 | control-load | 48 | 1911.08 | 97.46% | 1470.60 | 16.78 | 0 | 0 | PASS |
| 23102 | control-load | 52 | 2096.88 | 98.86% | 1383.15 | 17.27 | 0 | 0 | PASS |
| 23106 | control-load | 56 | 2057.87 | 97.05% | 1813.44 | 16.93 | 0 | 0 | PASS |
| 23103 | dense-decode-graphs | 48 | 1933.05 | 97.47% | 1525.35 | 16.29 | 0 | 0 | PASS |
| 23103 | dense-decode-graphs | 52 | 2123.30 | 98.73% | 1449.42 | 16.61 | 0 | 0 | PASS |
| 23109 | dense-decode-graphs | 56 | 2069.20 | 96.48% | 1837.46 | 16.52 | 0 | 0 | PASS |
| 23104 | profile-control | 48 | 1910.32 | 97.47% | 1470.16 | 16.79 | 0 | 0 | PASS |
| 23113 | load-best-repeat | 52 | 1986.39 | 97.24% | 1633.31 | 16.97 | 0 | 0 | PASS |
| 23114 | prefill-chunk4096 | 48 | 1962.70 | 97.60% | 1245.64 | 17.33 | 0 | 0 | PASS |
| 23114 | prefill-chunk4096 | 52 | 2140.10 | 98.81% | 1173.18 | 17.84 | 0 | 0 | PASS |
| 23115 | decode-deepgemm | 48 | 1904.20 | 97.44% | 1458.15 | 16.97 | 0 | 0 | PASS |
| 23115 | decode-deepgemm | 52 | 2085.67 | 98.78% | 1373.60 | 17.46 | 0 | 0 | PASS |
| 23128 | s2-control-n52 | 52 | 1977.08 | 97.14% | 1639.15 | 17.07 | 0 | 0 | PASS |
| 23129 | s2-chunk4096-n52 | 52 | 2033.03 | 97.39% | 1420.60 | 17.41 | 0 | 0 | PASS |
| 23130 | s2-chunk4096-dense-n52 | 52 | 2078.96 | 97.43% | 1430.49 | 16.93 | 0 | 0 | PASS |
| 23131 | s2-chunk16384-n52 | 52 | 1741.20 | 90.92% | 2147.07 | 16.07 | 0 | 0 | PASS |
| 23264 | s2-deepgemm-control-n52 | 52 | 2018.01 | 97.37% | 1407.68 | 17.67 | 0 | 0 | PASS |
| 23265 | s2-fp8-kv-n52 | 52 | 1996.26 | 97.33% | 1355.69 | 18.27 | 0 | 0 | PASS |
| 23266 | s2-repeat-best | 52 | 2079.18 | 97.43% | 1432.37 | 16.93 | 0 | 0 | PASS |
| 23267 | s2-repeat-runner | 52 | 2032.13 | 97.39% | 1419.36 | 17.42 | 0 | 0 | PASS |
| 23272 | s2-deepep-ll-n52 | 52 | 1957.15 | 96.35% | 1317.64 | 18.71 | 0 | 0 | PASS |
| 23286 | s3-control-n52 | 52 | 2075.11 | 97.42% | 1437.63 | 16.94 | 0 | 0 | PASS |
| 23287 | s3-best-n54 | 54 | 2111.91 | 97.33% | 1517.78 | 16.99 | 0 | 0 | PASS |
| 23324 | s4-prefill-single-n52 | 52 | 2082.09 | 97.44% | 1412.99 | 16.96 | 0 | 0 | PASS |
| 23325 | s4-prefill-roundrobin-n52 | 52 | 2402.64 | 98.93% | 333.25 | 19.57 | 0 | 0 | PASS |
| 23437 | s3-best-n56 | 56 | 2141.20 | 97.22% | 1610.94 | 17.06 | 0 | 0 | PASS |
| 23495 | s3-best-n60 | 60 | 2133.30 | 94.51% | 1780.49 | 17.35 | 0 | 0 | PASS |
| 23505 | s3-midpoint | 58 | 2157.31 | 96.76% | 1687.40 | 17.20 | 0 | 0 | PASS |
| 23516 | s3-best-load-repeat | 58 | 2159.79 | 96.83% | 1691.06 | 17.19 | 0 | 0 | PASS |
| 23576 | s5-rr-repeat-n52 | 52 | 2397.72 | 98.93% | 365.29 | 19.46 | 0 | 0 | PASS |
| 23577 | s5-rr-n50 | 50 | 2350.25 | 99.04% | 335.48 | 19.23 | 0 | 0 | PASS |
| 23583 | s5-rr-n54 | 54 | 2358.64 | 95.34% | 428.19 | 19.51 | 0 | 0 | PASS |
| 23607 | s6-rr-profile-n52 | 52 | 2400.02 | 98.93% | 346.84 | 19.52 | 0 | 0 | PASS |
| 23608 | s6-rr-fp8kv-n52 | 52 | 254.47 | 10.75% | 342.90 | 20.07 | 0 | 0 | FAIL / incomplete |
| 23609 | s6-rr-deepgemm-n52 | 52 | 2021.39 | 84.71% | 394.50 | 19.63 | 0 | 0 | FAIL / incomplete |
| 23616 | s5-rr-midpoint | 53 | 2433.41 | 98.88% | 339.35 | 19.66 | 0 | 0 | PASS |
| 23773 | s5-rr-best-repeat | 53 | 2438.47 | 98.88% | 328.90 | 19.67 | 0 | 0 | PASS |
| 23777 | s7-rr-flashinfer-n52 | 52 | 2440.39 | 98.95% | 438.05 | 18.71 | 0 | 0 | PASS |
| 23778 | s7-rr-mnnvl-n52 | 52 | 2592.16 | 99.01% | 516.28 | 17.13 | 0 | 0 | PASS |
| 23780 | s8-rr-dpa8-deepep-n52 | 52 | 2549.20 | 98.87% | 596.44 | 16.96 | 0 | 0 | PASS |
| 23839 | s7-mnnvl-repeat-n52 | 52 | 2592.92 | 99.01% | 508.25 | 17.15 | 0 | 0 | PASS |
| 23859 | s8-dpa8-repeat-n52 | 52 | 2538.08 | 98.87% | 617.14 | 16.96 | 0 | 0 | PASS |
| 23904 | s9-mnnvl-flashinfer-n52 | 52 | 2631.09 | 99.02% | 635.23 | 16.23 | 0 | 0 | PASS |
| 23905 | s9-mnnvl-chunk2048-n52 | 52 | 2331.35 | 98.77% | 1188.77 | 15.81 | 0 | 0 | PASS |
| 23906 | s9-mnnvl-chunk8192-n52 | 52 | 2547.85 | 98.87% | 735.56 | 16.32 | 0 | 0 | PASS |
| 23924 | s7-mnnvl-n54 | 54 | 2634.03 | 98.90% | 600.44 | 17.11 | 0 | 0 | PASS |
| 23934 | s8-dpa8-n54 | 54 | 2555.42 | 98.75% | 751.99 | 16.89 | 0 | 0 | PASS |
| 23973 | s10-combo-repeat1-n52 | 52 | 2632.06 | 99.02% | 632.66 | 16.24 | 0 | 0 | PASS |
| 23974 | s10-mnnvl-control-n52 | 52 | 2594.03 | 99.01% | 518.90 | 17.09 | 0 | 0 | PASS |
| 23975 | s10-combo-repeat2-long-n52 | 52 | 2632.61 | 99.02% | 634.42 | 16.23 | 0 | 0 | PASS |
| 24009 | s10-mnnvl-repeat-n54 | 54 | 2629.51 | 98.90% | 615.90 | 17.06 | 0 | 0 | PASS |
| 24131 | s10-combo-n54 | 54 | 2654.17 | 98.91% | 736.69 | 16.27 | 0 | 0 | PASS |
| 24174 | s10-combo-fresh-n52 | 52 | 2632.96 | 99.02% | 637.78 | 16.21 | 0 | 0 | PASS |
| 24175 | s10-combo-repeat-n54 | 54 | 2658.20 | 98.91% | 734.65 | 16.25 | 0 | 0 | PASS |
| 24189 | s10-combo-control-n54-v2 | 54 | 2658.55 | 98.91% | 739.13 | 16.23 | 0 | 0 | PASS |
| 24190 | s10-combo-probe-n56 | 56 | 2671.11 | 98.80% | 847.85 | 16.29 | 0 | 0 | PASS |
| 24235 | s10-combo-repeat-n56 | 56 | 2669.80 | 98.80% | 852.28 | 16.26 | 0 | 0 | PASS |
| 24236 | s10-combo-probe-n58 | 58 | 2667.97 | 98.68% | 991.14 | 16.27 | 0 | 0 | PASS |
| 24263 | s10-combo-profile-n56 | 56 | 2667.46 | 98.80% | 856.62 | 16.26 | 0 | 0 | PASS |
| 24272 | s10-cross-platform-n50 | 50 | 2601.63 | 99.13% | 505.18 | 16.37 | 0 | 0 | PASS |
| 24281 | s10-combo-prefill-single-n56 | 56 | 2621.29 | 98.78% | 936.61 | 16.19 | 0 | 0 | PASS |
| 24291 | s10-prefill-deepgemm-n56 | 56 | 2715.84 | 98.82% | 749.05 | 16.45 | 0 | 0 | PASS |
| 24320 | s10-combo-control-n56-v3 | 56 | 2670.32 | 98.80% | 851.83 | 16.27 | 0 | 0 | PASS |
| 24322 | s10-prefill-prefetch-n56 | 56 | 2665.57 | 98.80% | 859.13 | 16.26 | 0 | 0 | PASS |
| 24327 | s10-prefill-deepgemm-repeat-n56 | 56 | 2716.79 | 98.82% | 748.99 | 16.45 | 0 | 0 | PASS |
| 24352 | s10-prefill-deepgemm-n58 | 58 | 2718.08 | 98.71% | 872.26 | 16.49 | 0 | 0 | PASS |
| 24375 | s10-prefill-tp8ep2-equal-n56 | 56 | 28.33 | 2.00% | 5013.77 | 16.56 | 0 | 0 | FAIL / incomplete |
| 24376 | s10-prefill-no-graph-n56 | 56 | 2530.83 | 98.43% | 1079.94 | 16.07 | 0 | 0 | PASS |
| 24425 | s10-prefill-deepgemm-chunk8192-n56 | 56 | 2722.28 | 98.94% | 755.65 | 16.40 | 0 | 0 | PASS |
| 24426 | s10-prefill-deepgemm-no-graph-n56 | 56 | 1590.31 | 72.72% | 1998.40 | 15.09 | 0 | 0 | FAIL / incomplete |
| 24428 | s10-prefill-deepgemm-n54 | 54 | 2693.16 | 98.93% | 661.67 | 16.35 | 0 | 0 | PASS |
| 24429 | s10-prefill-deepgemm-profile-n56 | 56 | 2715.55 | 98.82% | 741.42 | 16.49 | 0 | 0 | PASS |
| 24526 | s11-dg-control-n56 | 56 | 2715.83 | 98.82% | 751.28 | 16.44 | 0 | 0 | PASS |
| 24527 | s11-dg-chunk8192-repeat-n56 | 56 | 2718.69 | 98.94% | 770.05 | 16.37 | 0 | 0 | PASS |
| 24528 | s11-dg-chunk6144-n56 | 56 | 2737.01 | 98.94% | 720.38 | 16.48 | 0 | 0 | PASS |
| 24529 | s11-hpc-prefill-n56 | 56 | 2732.46 | 98.94% | 715.07 | 16.53 | 0 | 0 | PASS |
| 24538 | s11-hpc-decode-n56 | 56 | 2733.20 | 98.83% | 1037.10 | 14.86 | 0 | 0 | PASS |
| 24544 | s11-dg-chunk8192-n58 | 58 | 2786.70 | 98.85% | 774.06 | 16.51 | 0 | 0 | PASS |
| 24573 | s12-dg-chunk6144-repeat-n56 | 56 | 2737.41 | 98.94% | 717.26 | 16.47 | 0 | 0 | PASS |
| 24574 | s12-hpc-prefill-repeat-n56 | 56 | 2728.96 | 98.82% | 714.98 | 16.54 | 0 | 0 | PASS |
| 24575 | s12-dg-fresh-control-n56 | 56 | 2714.10 | 98.82% | 750.64 | 16.46 | 0 | 0 | PASS |

## Backend pilots

| Pilot | Matched control | State | Job |
|---|---|---|---|
| s2-deepgemm-control-n52 | s2-chunk4096-n52 | MEASURED | 23264 |
| s2-deepep-ll-n52 | s2-deepgemm-control-n52 | MEASURED | 23272 |
| s2-fp8-kv-n52 | s2-chunk4096-n52 | MEASURED | 23265 |

## Load refinement

| Trial | N | State | Job |
|---|---:|---|---|
| s3-control-n52 | 52 | MEASURED | 23286 |
| s3-best-n54 | 54 | MEASURED | 23287 |
| s3-best-n56 | 56 | MEASURED | 23437 |
| s3-best-n60 | 60 | MEASURED | 23495 |
| s3-midpoint | 58 | MEASURED | 23505 |
| s3-best-load-repeat | 58 | MEASURED | 23516 |

## Prefill routing/admission pilots

| Trial | State | Job |
|---|---|---|
| s4-prefill-single-n52 | MEASURED | 23324 |
| s4-prefill-roundrobin-n52 | MEASURED | 23325 |

[Research and measured TTFT failure analysis](serving-tuning-04/RESEARCH.md). Same N52 benchmark, one prefill factor per pilot.

## Round-robin confirmation and load refinement

| Trial | N | State | Job |
|---|---:|---|---|
| s5-rr-repeat-n52 | 52 | MEASURED | 23576 |
| s5-rr-n50 | 50 | MEASURED | 23577 |
| s5-rr-n54 | 54 | MEASURED | 23583 |
| s5-rr-midpoint | 53 | MEASURED | 23616 |
| s5-rr-best-repeat | 53 | MEASURED | 23773 |

## Round-robin backend/profile experiments

| Trial | State | Job |
|---|---|---|
| s6-rr-profile-n52 | MEASURED | 23607 |
| s6-rr-fp8kv-n52 | MEASURED | 23608 |
| s6-rr-deepgemm-n52 | MEASURED | 23609 |

## Backend follow-ups

| Trial | State | Job |
|---|---|---|
| s6-fp8kv-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s6-fp8kv-n54 | SKIPPED_NO_REPEAT | — |
| s6-deepgemm-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s6-deepgemm-n54 | SKIPPED_NO_REPEAT | — |

## MNNVL + FlashInfer replication

| Trial | State | Job |
|---|---|---|
| s10-combo-repeat1-n52 | MEASURED | 23973 |
| s10-mnnvl-control-n52 | MEASURED | 23974 |
| s10-combo-repeat2-long-n52 | MEASURED | 23975 |
| s10-mnnvl-repeat-n54 | MEASURED | 24009 |
| s10-combo-n54 | MEASURED | 24131 |
| s10-combo-fresh-n52 | MEASURED | 24174 |
| s10-combo-repeat-n54 | MEASURED | 24175 |
| s10-combo-control-n54-v2 | MEASURED | 24189 |
| s10-combo-probe-n56 | MEASURED | 24190 |
| s10-combo-repeat-n56 | MEASURED | 24235 |
| s10-combo-probe-n58 | MEASURED | 24236 |
| s10-combo-profile-n56 | MEASURED | 24263 |
| s10-cross-platform-n50 | MEASURED | 24272 |
| s10-combo-prefill-single-n56 | MEASURED | 24281 |
| s10-combo-prefill-tp8-n56 | INCOMPLETE | 24282 |
| s10-prefill-deepgemm-n56 | MEASURED | 24291 |
| s10-combo-control-n56-v3 | MEASURED | 24320 |
| s10-prefill-tp8ep2-n56 | INCOMPLETE | 24321 |
| s10-prefill-prefetch-n56 | MEASURED | 24322 |
| s10-prefill-deepgemm-repeat-n56 | MEASURED | 24327 |
| s10-prefill-deepgemm-n58 | MEASURED | 24352 |
| s10-prefill-tp8ep2-equal-n56 | MEASURED | 24375 |
| s10-prefill-no-graph-n56 | MEASURED | 24376 |
| s10-prefill-deepgemm-chunk8192-n56 | MEASURED | 24425 |
| s10-prefill-deepgemm-no-graph-n56 | MEASURED | 24426 |
| s10-prefill-deepgemm-n54 | MEASURED | 24428 |
| s10-prefill-deepgemm-profile-n56 | MEASURED | 24429 |
| s11-dg-control-n56 | MEASURED | 24526 |
| s11-dg-chunk8192-repeat-n56 | MEASURED | 24527 |
| s11-dg-chunk6144-n56 | MEASURED | 24528 |
| s11-hpc-prefill-n56 | MEASURED | 24529 |
| s11-hpc-decode-n56 | MEASURED | 24538 |
| s11-dg-chunk8192-n58 | MEASURED | 24544 |
| s12-dg-chunk6144-repeat-n56 | MEASURED | 24573 |
| s12-hpc-prefill-repeat-n56 | MEASURED | 24574 |
| s12-dg-fresh-control-n56 | MEASURED | 24575 |
| s12-dg-chunk8192-repeat-n58 | ACTIVE | 24588 |
| s12-dg-fresh-control-n58 | ACTIVE | 24589 |
| s13-hpc-decode-n58 | SUBMITTED | 24639 |
| s13-hpc-prefill-chunk6144-n56 | SUBMITTED | 24640 |
| s13-hpc-both-n56 | SUBMITTED | 24641 |

## MNNVL interaction pilots

| Trial | State | Job |
|---|---|---|
| s9-mnnvl-flashinfer-n52 | MEASURED | 23904 |
| s9-mnnvl-chunk2048-n52 | MEASURED | 23905 |
| s9-mnnvl-chunk8192-n52 | MEASURED | 23906 |

## DP-attention architecture pilot

| Trial | State | Job |
|---|---|---|
| s8-rr-dpa8-deepep-n52 | MEASURED | 23780 |

## DP-attention architecture follow-ups

| Trial | State | Job |
|---|---|---|
| s8-dpa8-repeat-n52 | MEASURED | 23859 |
| s8-dpa8-n54 | MEASURED | 23934 |

## Profile-guided decode kernels

| Trial | State | Job |
|---|---|---|
| s7-rr-cutlass-n52 | INCOMPLETE | 23776 |
| s7-rr-flashinfer-n52 | MEASURED | 23777 |
| s7-rr-mnnvl-n52 | MEASURED | 23778 |

## Profile-guided kernel follow-ups

| Trial | State | Job |
|---|---|---|
| s7-cutlass-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s7-cutlass-n54 | SKIPPED_NO_REPEAT | — |
| s7-flashinfer-repeat-n52 | SKIPPED_NO_VALIDATED_GAIN | — |
| s7-flashinfer-n54 | SKIPPED_NO_REPEAT | — |
| s7-mnnvl-repeat-n52 | MEASURED | 23839 |
| s7-mnnvl-n54 | MEASURED | 23924 |

## Interpretation

Dense graph N48 versus mean of 2 new N48 controls: +1.17%. One candidate run remains provisional; repeated confirmation is needed before promotion.
Highest new load point: N52, 2096.88 good tokens/s, 98.86% SLA (+9.65% versus job 22415). Provisional until independently repeated; the submission is unchanged.
Highest single full measurement: s11-dg-chunk8192-n58 / job 24544 / N58: 2786.70 good tokens/s, 98.85% SLA. Backend/FP8 quality remains unverified; the largest single run is not automatically the final configuration.
Repeated BF16 chunk4096/dense-graph candidate at N52: 2079.07 mean good tokens/s across jobs 23130, 23266 (range 2078.96–2079.18). Two deployments agree closely; this does not establish accuracy or variability under all cluster conditions.
Round-robin prefill pilot / job 23325: 2402.64 good tokens/s, 98.93% SLA, mean TTFT 333.25ms and ITL 19.57ms. ITL is close to its20ms limit; independent confirmation and a lower-load comparison are required before selection.

Standalone measurements above begin directly at their listed concurrency; they do not run a lower-load benchmark first.
Job 23128 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23129 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23130 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23131 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23264 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23265 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23266 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23267 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23272 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23286 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23287 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23324 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23325 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23437 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23495 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23505 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23516 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23576 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23577 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23583 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23616 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.
Job 23773 output sanity: 7/8. These eight cases are not the organiser accuracy gate.
No newly failed cases versus the independent monolithic baseline; eligible for further research only. The reverse answer is still wrong and full accuracy is unverified.

## Traces

profile-control: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.
s6-rr-profile-n52: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.
s10-combo-profile-n56: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.
s10-prefill-deepgemm-profile-n56: 16 trace files; kernel summaries are beside the traces. Summed GPU time is not wall-time speedup.

## Next steps

- Prefill chunk 4096/16384 after control.
- MoE runner after profiler identifies compute cost.
- Expert communication after profiler identifies dispatch/collective cost.
- FP8 KV with separate quality check.
- Engine comparison after reproducible current-stack baseline.

Wave5: independently repeat round-robin N52 and compare N50 for ITL headroom; N54 only after the N52 repeat passes. Optional midpoint and best-new-point repeat, at most five deployments. See [round-robin plan](serving-tuning-05/PLAN.md).

Accuracy against the organiser reference remains unverified. No official score is claimed.

Output diagnostic job 23146: COMPLETED; 132/132 responses recorded. [Status and purpose](serving-tuning-02/OUTPUT_DIAGNOSTIC.md). Not a ranked benchmark.

## 19 October 2026 — recovered measurements and new controlled batch

[Accepted source results](research-followup-20261019-0400/RESULTS.md): H200 24647 repeats 2780.483 good tokens/s; H100 221341 N52 reaches 2398.728, awaiting repeat. All local gates pass; full organiser accuracy remains unverified. [New plan and receipts](research-followup-20261019-0412/RESULTS.md): H200 24721–24724 and PBS 221589→221590 submitted. New jobs have no accepted measurement yet. Preserve all raw runs and use platform-matched controls.

## 19 October 2026 — new load observations and independent repeats

H200 24722 = 2839.532 good tokens/s, +2.1266% versus fresh N58 control 24721. H100 221590 = 2430.891, +0.8123% versus N52 repeat 221589. All local gates pass; new operating points await independent repeats and official accuracy remains unverified. Submitted H200 24732/24733 and PBS 221645→221646. [Full measurements, units, control mapping and receipts](research-followup-20261019-0527/RESULTS.md).

## 19 October 2026 — prefill/decode interaction

H200 24724 passes at 2938.628 good tokens/s (+5.6907% versus same-N58 control 24721); 24723 chunk 12288 loses 2.3789% and is closed. New H200 24736–24738 repeat/control/load trials, plus H100 prefill Tree N54 job 221669 after existing221645→221646. [Full report and source references](research-followup-20261019-0600/RESULTS.md). All new jobs await complete GPU gates; official accuracy unverified.

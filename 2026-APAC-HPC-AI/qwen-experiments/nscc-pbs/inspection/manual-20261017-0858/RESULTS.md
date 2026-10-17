# Frontier results — 17 October 2026

All numbers below are from completed, sealed, protocol/runtime/short/long-reviewed runs.
Full organiser accuracy99% remains unverified. No submission promotion is claimed.

| Platform/config | Concurrent requests | Runs good output tokens/s | Mean |
|---|---:|---|---:|
| H200 MNNVL+FlashInfer |56|2671.109,2669.803|2670.456|
| H200 MNNVL+FlashInfer |58|2667.966|2667.966 (one run)|
| H100 MNNVL+FlashInfer |48|2191.114,2197.808|2194.461|
| H100 MNNVL+FlashInfer |50|2218.032,2229.827|2223.930|
| H100 MNNVL+FlashInfer |52|2215.247,2215.673|2215.460|

H200N58 has lower measured goodput and higher meanTTFT991ms versusN56~850ms;
stop blind load escalation. H100N50 wins both new sweeps;N52 increasesTTFT to
~700ms versusN50~509–538ms, without goodput benefit. All these points pass SLA;
no error/cancellation and each run has12/12synthetic long retrieval checks pass.
Synthetic checks do not establish the organiser full-set accuracy threshold.

H100campaignused15536.925SU/16384cap,847.075remaining,allchargesreconciled.
No additional16GPUallocation fits the observed25+minute startup+fullbenchmark.
H20024263profilingqueued;diagnostic traffic only AFTER the full ranked window.
Use traces to choose next factor;do not treat kernel sums as wallclock shares.

Raw evidence, reviews and pair comparisons remain under this inspection directory.

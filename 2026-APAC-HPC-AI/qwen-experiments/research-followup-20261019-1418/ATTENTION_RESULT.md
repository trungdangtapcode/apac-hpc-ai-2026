# Dense FlashInfer prefill result — H100, 19 October 2026

Job **221880.pbs111** passes full local terminal, payload, 60/120/30 protocol, 4000/200 workload, request/error/SLA, runtime, short-output and all 12 long-output checks. It scores **2227.031 good output tokens/s**, **-7.7376%** versus fresh same-N54 default-FA3 prefill control 221827 at 2413.802. This is a valid measured regression, not a failed allocation or a new best.

| Metric | Fresh FA3 prefill control | FlashInfer prefill |
|---|---:|---:|
| Joint latency success (%) | 98.6120 | 98.2270 |
| Mean TTFT (ms) | 717.698 | 1185.763 |
| Mean ITL (ms) | 18.255 | 17.559 |
| Good output tokens/s | 2413.802 | 2227.031 |

Lower mean ITL does not outweigh the longer first-token wait in the measured closed-loop workload. This tradeoff explains the direction plausibly, not a profiled causal decomposition of the ranked interval. Close this tested prefill-attention branch; retain FA3 in the accepted baseline and do not repeat this unchanged loss.

Resolved runtime differs only in the declared prefill attention override and random seeds. External decode remains HPC-Ops, MNNVL and FlashInfer on all eight ranks, with unchanged precision and speculation disabled. The separate N48 post-score diagnostic has **16 sealed nonempty rank traces and 363/363 successful requests**. Named FlashInfer prefill kernels appear on all eight prefill ranks, so this treatment did execute. Diagnostic kernel-duration shares are not wall-time bottleneck fractions or ranked N54 timings.

Evidence: 221880.pbs111-review.json, 221880.pbs111-gates.json, collect-221880.json, h100-prefill-attention-profile.json and attention-profile-summary.txt. Its immutable collection includes raw exports, request records, logs, payloads and checksums. The highest individual H100 observation remains 2430.891 good tokens/s. Official full-set accuracy at 99% of the organiser reference is still unverified.

Research continues with the submitted instrumented global-protocol pair and the prepared CPU/GPU profile direction. Losing this candidate does not stop other research. This report changes no frozen payload or official submission material.

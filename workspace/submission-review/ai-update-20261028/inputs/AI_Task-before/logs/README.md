# Measured results and reproduction status

The primary job now declares H200 N62 from reviewed job 24915, not the historical
N48 job. results.json and results.csv give exact units and evidence paths for
recent controls, N60 repeats, N62 and the separate H100 frontier. Historical
22197/22219/22415/22809 evidence remains in measured/. The former package's
metadata is preserved under historical-package-20261020/ and is not the current
deployment declaration. Original logs retain their original dates and paths.

## Latest H200 result

Job 24915: 3022.034919 good output tokens/s; 15.110174596 good requests/s.
1860 of 1884 scored requests jointly meet TTFT<=3000 ms and request-mean
ITL<=20 ms: 98.726115%, with zero request errors or cancellations. Mean TTFT
is 1022.927941 ms; mean ITL is 14.971161 ms. Its fresh same-N auto-decode
control 24914 yields 2890.878 good tokens/s; the observed increase is 4.536934%.
N62 remains a single observation, with independent repeat 24962 pending.
N60 independently yields 2990.150791 and 2989.174711 good output tokens/s.

The score is the canonical profile_export_aiperf.json goodput.avg (requests/s)
multiplied by 200, never raw output throughput or an assumed completed/120.
The SLA is per request and joint; mean latencies alone do not prove acceptance.
AIPerf's reported output length is 199–200 for this run despite fixed 200-token
request settings; the official multiplier remains 200. Warmup/diagnostic
traffic is excluded from raw profiling counts.

## Evidence supplied

The recent H200 folders include canonical exports, raw per-request JSONL,
client logs, worker/router logs, actual frozen submitted payloads and output
checks. Large generated inputs.json files are omitted, with source hashes
and sizes recorded in source-provenance.json. Full rank traces stay in the
research archive; an inspected profile summary is included. Original raw
bytes are unchanged. Paths inside original evidence may name the research
account; the portable primary scripts do not depend on those paths.

H100 job 222048 is separate: 2433.019859 good output tokens/s at N54,
98.687664% joint SLA. Hardware, kernels and load differ. Do not divide these
peaks to claim an algorithmic speedup or a universal H100-to-H200 conversion.

## Interpretation and remaining checks

research-reviews/ records tail latency, queues, KV observations, runtime and
transport review, rejected CPU/startup hypotheses and EAGLE3 integration.
H200 24915 has no continuous hardware telemetry; kernel-time sums are not
GPU activity or critical-path fractions. Later observation coverage does not
retroactively fill its missing CPU/GPU/power/network samples.

The EAGLE3 layer fixture validates a dtype repair, not serving speedup.
Its full PD repair result is uncollected while VPN access is unavailable.
No speculative configuration is promoted into the primary deployment.

The portable N62 package has shell/static checks and a GPU-free orchestration
mock replaying measured artifacts. It has not been separately GPU-replayed.
The required organiser full-set accuracy check >=99% of reference and final
re-verification remain unverified. Hand-written output checks are not that test.
The primary portable command uses 60/120/30, seed 2026, fixed 4000/200,
cold prefixes and exactly one declared concurrency. There is no parameter sweep.

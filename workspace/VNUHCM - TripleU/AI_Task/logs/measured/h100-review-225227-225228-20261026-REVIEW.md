# Independent review of H100 jobs 225227 and 225228

Collected 26 October through the existing authenticated AI SSH path after both PBS records became terminal. Filtered qstat reports each job F, exit status 0. Raw run logs, selected AIPerf exports, phase markers, per-role resource samples, pre/post observer gates and transfer markers are preserved under curated-r2/; COLLECTION-curated-r2.json records file hashes and filtered scheduler fields. The first collection attempt hit the artifact-size guard and only retained two preliminary files. It remains preserved as an incomplete attempt; findings below use the subsequent bounded curated collection. The large synthetic prompt input dump was excluded. No authentication material or runtime cache was collected.

## 225227: current full N54 control

The full N54 confirmation ran on two H100 nodes for 15:38 of its 30-minute maximum. The immutable submission recipe corresponds to accepted N54 control 222551. I replayed its local check-control.py against the 8-case reference; output sanity, CPU-envelope receipts and 12-case retrieval checks pass.

| Measure | Result |
|---|---:|
| Profiling requests | 1,512 |
| Good requests | 1,482 (98.015873%) |
| AIPerf Goodput | 11.995933638 requests/s |
| Good output throughput | 2,399.186728 tokens/s (Goodput × 200) |
| Mean / p95 TTFT | 733.085 / 1,089.080 ms |
| Mean / p95 request ITL | 18.185831 / 18.883753 ms |
| TTFT / ITL breaches | 22 / 8 requests; 30 jointly bad |
| Request errors / cancellations | 0 / 0 |
| Small output sanity / retrieval | 7/8 / 12/12 |

All score gates pass: at least 90% meet TTFT ≤3,000 ms and mean per-request ITL ≤20 ms, with the full request denominator retained. The new score is 0.3471% below accepted full N54 job 222551 (2,407.544052 tokens/s). The older best individual 2,433.019859 is further above. This is a valid contemporary control, not a gain. The one failed smoke item, reverse, also failed the inherited reference; the run adds no regression. Official full-set 99%-reference accuracy is still unknown.

The raw profile contains 2,267 rows: 755 warmup plus 1,512 profiling, matching the export and summary. There were no cancellations or overflow skips. TTFT and ITL breach counts recomputed from profiling request records are 22 and 8; the sets do not overlap. The scored serving logs contain no transport failure or OOM. Each serving role has a post-score profile-stop traceback ending RuntimeError: Profiling is not in progress; these diagnostic stop errors are not included in the 1,512 scored requests. The AIPerf client has no traceback/errors and completed export.

The sampled resource logs have 162–163 five-second samples per role, covering allocation startup through teardown rather than only scoring. Decode sampled eight GPUs at mean 34.67% active, mean 66.15 GiB used and 40.72 C; each prefill role sampled four GPUs around 29% active and 63–63.3 GiB mean used, 41.9 C. SM clock averages are 1,879–1,889 MHz, memory clock 2,619 MHz. Samples include idle startup/teardown, so these means are not scored-phase utilization. No causal bottleneck follows. PBS node-level gpu_usage strings aggregate eight devices and report roughly 387 GB maximum across the node; do not read that as memory on one H100. Raw per-GPU samples max around 78 GiB. The collector did not inspect full kernel traces.

The active frozen config has no submission-status field. Its qsub receipt, qstat and matching run artifacts independently establish execution. Frozen payload bytes were left intact.

## 225228: equal-TP native EAGLE observation

The 8-H100 same-node P4/D4 allocation ran 6:39. qstat records exit status 0. The corrected pre-warmup gate passes eight rank metadata receipts, four disjoint unique H100 UUIDs per role (eight total), and pinned runtime source hashes. During one semantic P/D request, the corrected post-semantic gate passes exactly four send_kvcache starts and four returned-handle markers plus four send_aux starts and returns across prefill TP ranks 0–3, with no observer exceptions. The independently validated semantic receipt has one completed pair and an eight-token response.

This resolves the previous 224560 evidence gap: equal-TP native KV method invocation was observed on every sender rank. Returned NIXL handles are not transfer-completion receipts; the separate successful semantic response establishes that this one request completed. It proves a bounded functional path for the tested same-node topology and source/runtime pins, not full workload reliability, throughput, official accuracy or multi-node scale-out. The two PRI * HTTP/2.0 404/invalid-request warnings are from health traffic; the semantic request is separately logged as HTTP 200. Remaining hybrid-attention and PyTorch barrier warnings are logged, but did not prevent this request. The frozen config metadata still says PREPARED_NOT_SUBMITTED although qsub receipt, qstat and run artifacts prove execution; this is stale metadata, not scheduler state. Sampled GPU activity averages 14–17% across the entire short allocation, including nearly six minutes startup; do not compare that with scored workload utilization.

## Next decision

The N54 reference does not justify another unchanged H100 baseline. The observer hypothesis passed, so the next informative step is an 8-GPU N24 EAGLE P4/D4 feasibility run with full output, latency and source/runtime gates. It measures whether this route can serve a reduced per-replica load; it is not a matched comparison against the 16-GPU N54 result and establishes no scale-up claim. Only after feasibility passes should a 16-GPU EAGLE evaluation be compared with a same-resource N54 control using the identical full workload and output gates. Do not treat the one-request prerequisite as a leaderboard improvement. Preserve the lower repeat when comparing. Do not infer SU reconciliation from observed runtimes; retain existing reservations until a fresh locked accounting reconciliation is available.

Evidence paths: submission-receipts.json in h100-followups-20261026, h100-review-225227-225228-20261026/COLLECTION-curated-r2.json, the two run trees beneath curated-r2/, local control validator h100-incumbent-n54-refresh-20261026/check-control.py, and corrected observer bundle eagle3-h100-equal-tp-observer-r2-20261026/. This review is independent analysis of collected raw artifacts; full per-dispatch GPU traces remain uninspected.

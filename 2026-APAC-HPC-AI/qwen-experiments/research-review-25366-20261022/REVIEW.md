# Full observed H200 N64 passes local checks

Job **25366** completed with exit 0 in 00:11:38. All terminal raw evidence hashes pass against the run manifest. The full native payload, 60-second warmup / 120-second measurement / 30-second grace protocol, zero-error score, local short-output non-regression and long retrieval 12/12 checks pass. The frozen execution files are byte-identical to fresh N62 control 25365 except job identity and configuration; resolved worker arguments differ only in per-process random seeds.

| Metric | Fresh N62 control 25365 | Full N64 candidate 25366 |
|---|---:|---:|
| Good output tokens/s | 3011.875113 | 3044.489701 |
| Joint-good requests / all scored requests | 1855 / 1879 | 1876 / 1902 |
| Joint SLA fraction | 98.722725% | 98.633018% |
| Request errors / cancellations | 0 / 0 | 0 / 0 |
| TTFT mean / p95, ms | 1037.629662 / 1316.527172 | 1110.463377 / 1351.632306 |
| Request-mean ITL mean / p95, ms | 14.957663 / 15.209486 | 15.002881 / 15.163328 |

The matched full gain is **1.082867%**, just above the 1% practical confirmation gate. It is about 0.708465% above prior observer-off individual maximum 24962. The latter is a cross-observer context comparison; the matched N62 measurement is the primary control. This is one full N64 deployment, not a repeatability or global-optimality claim. Independent full repeat 25373 is submitted; short N64/N68 screen 25371 explores the next load step.

All 26 bad requests breach TTFT; none breaches request-mean ITL. The official score retains every scored request and uses exported AIPerf Goodput × 200. Nominal requested output is 200 tokens. Exported length counts are 1898 at 200, three at 199, and one at 198. These counters are not proof of actual generated-ID count; actual per-response output IDs were not retained. No change to requested length, scoring denominator, workload or seed is made.

Role logs retain native BF16 KV and contain no inspected NIXL_ERR or CUDA out-of-memory pattern. This bounded search does not establish universal transport/GPU health. Resource samples, phase markers, server scrapes and separate diagnostic profiles were collected. Their deeper phase-aligned inspection is recorded separately in `observability.md` when available; profile-control errors must not be conflated with scored request errors. Trace file presence alone does not show kernel behavior. Missing or uninspected diagnostics are not zero.

**Official accuracy at least 99% of reference remains unverified.** Local smoke and retrieval checks do not replace MMLU-Pro/GPQA accuracy evaluation. The submission primary remains reviewed N62 while N64 replication is pending. Preserve the raw run, histogram, full control and failures; do not infer a prefill/decode causal bottleneck from score or average GPU activity alone.
